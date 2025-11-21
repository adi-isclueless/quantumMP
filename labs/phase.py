import streamlit as st
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit.circuit.library import QFT
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
from certificate import store_simulation_data, save_figure_to_data


def run():
    import streamlit.components.v1 as components

    components.html(
        """
        <script>
            window.parent.document.documentElement.scrollTop = 0;
        </script>
        """,
        height=0,
    )
    st.title("Quantum Phase Estimation")
    st.markdown("### Estimate Eigenvalue Phase of Unitary Operators")

    # Configuration
    col1, col2 = st.columns(2)
    with col1:
        precision_qubits = st.slider("Precision Qubits", 2, 8, 4)
    with col2:
        shots = st.selectbox("Number of Shots", [100, 500, 1000, 5000, 10000], index=3)

    st.markdown("### Unitary Operator Selection")
    operator_type = st.selectbox(
        "Select Operator",
        ["T Gate (π/4)", "S Gate (π/2)", "Z Gate (π)", "Custom Phase"]
    )

    if operator_type == "Custom Phase":
        phase_input = st.number_input(
            "Phase (in units of π)",
            min_value=0.0,
            max_value=2.0,
            value=0.25,
            step=0.05
        )
        true_phase = phase_input
    else:
        phase_map = {
            "T Gate (π/4)": 0.25,
            "S Gate (π/2)": 0.5,
            "Z Gate (π)": 1.0
        }
        true_phase = phase_map[operator_type]

    if st.button("Run Phase Estimation", type="primary"):
        with st.spinner("Running quantum phase estimation..."):
            # Create quantum circuit
            counting = QuantumRegister(precision_qubits, 'counting')
            target = QuantumRegister(1, 'target')
            c = ClassicalRegister(precision_qubits, 'measurement')

            qc = QuantumCircuit(counting, target, c)

            # Initialize target qubit in eigenstate |1>
            qc.x(target[0])

            # Initialize counting qubits in superposition
            for i in range(precision_qubits):
                qc.h(counting[i])

            qc.barrier()

            # Apply controlled unitary operations
            for i in range(precision_qubits):
                repetitions = 2 ** i
                angle = 2 * np.pi * true_phase * repetitions
                qc.cp(angle, counting[precision_qubits - 1 - i], target[0])

            qc.barrier()

            # Apply inverse Quantum Fourier Transform
            qft = QFT(num_qubits=precision_qubits, inverse=True, do_swaps=True)
            qc.append(qft, counting)

            qc.barrier()

            # Measure counting qubits
            for i in range(precision_qubits):
                qc.measure(counting[i], c[i])

            # Execute
            simulator = AerSimulator()
            job = simulator.run(qc, shots=shots)
            result = job.result()
            counts = result.get_counts()

            # Display results
            st.markdown("### Circuit Diagram")
            fig_circuit = qc.draw(output='mpl', style='iqp', fold=-1)
            st.pyplot(fig_circuit)
            plt.close()

            st.markdown("### Measurement Results")

            # Create histogram
            fig_hist = plot_histogram(counts, color='#1f77b4',
                                      title='Phase Estimation Measurement Outcomes')
            st.pyplot(fig_hist)
            plt.close()

            # Convert to phase estimates
            st.markdown("### Phase Estimation Analysis")

            phase_estimates = {}
            for bitstring, count in counts.items():
                measured_int = int(bitstring, 2)
                estimated_phase = measured_int / (2 ** precision_qubits)
                phase_estimates[estimated_phase] = phase_estimates.get(estimated_phase, 0) + count

            # Find most likely phase
            most_likely_phase = max(phase_estimates.items(), key=lambda x: x[1])[0]

            # Create phase distribution plot
            fig, ax = plt.subplots(figsize=(10, 6))
            phases = sorted(phase_estimates.keys())
            probs = [phase_estimates[p] / shots for p in phases]

            ax.bar(phases, probs, width=0.01, color='#2ca02c', alpha=0.7,
                   edgecolor='black', label='Estimated')
            ax.axvline(true_phase, color='red', linestyle='--', linewidth=2,
                       label=f'True Phase ({true_phase}π)')
            ax.axvline(most_likely_phase, color='blue', linestyle=':', linewidth=2,
                       label=f'Measured ({most_likely_phase:.4f}π)')

            ax.set_xlabel('Phase (in units of π)', fontsize=12)
            ax.set_ylabel('Probability', fontsize=12)
            ax.set_title('Phase Estimation Distribution', fontsize=14)
            ax.legend()
            ax.grid(True, alpha=0.3)

            st.pyplot(fig)
            plt.close()

            # Statistics
            st.markdown("### Estimation Results")

            error = abs(most_likely_phase - true_phase)
            relative_error = error / true_phase if true_phase != 0 else 0

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("True Phase", f"{true_phase:.4f}π")
            with col2:
                st.metric("Estimated Phase", f"{most_likely_phase:.4f}π")
            with col3:
                st.metric("Absolute Error", f"{error:.4f}π")

            # Precision analysis
            theoretical_precision = 1 / (2 ** precision_qubits)
            st.markdown(f"""
            **Theoretical Precision:** {theoretical_precision:.6f}π (1/2^{precision_qubits})

            **Relative Error:** {relative_error * 100:.2f}%

            **Success Probability:** {phase_estimates[most_likely_phase] / shots * 100:.1f}%
            """)

            # Detailed measurements table
            with st.expander("View Detailed Phase Measurements"):
                phase_data = []
                for phase, count in sorted(phase_estimates.items(), key=lambda x: x[1], reverse=True):
                    phase_data.append({
                        "Phase (π)": f"{phase:.6f}",
                        "Binary": format(int(phase * (2 ** precision_qubits)), f'0{precision_qubits}b'),
                        "Count": count,
                        "Probability": f"{count / shots:.4f}"
                    })
                st.table(phase_data[:10])

            # Raw data
            with st.expander("View Raw Measurement Data"):
                st.json(counts)
            
            # Store simulation data for PDF report
            from lab_config import LABS
            lab_id = None
            for name, config in LABS.items():
                if config.get('module') == 'phase':
                    lab_id = config['id']
                    break
            
            if lab_id:
                metrics = {
                    'Precision Qubits': str(precision_qubits),
                    'Number of Shots': str(shots),
                    'Operator Type': operator_type,
                    'True Phase': f"{true_phase:.4f}π",
                    'Estimated Phase': f"{most_likely_phase:.4f}π",
                    'Absolute Error': f"{error:.4f}π",
                    'Relative Error': f"{relative_error * 100:.2f}%",
                    'Theoretical Precision': f"{theoretical_precision:.6f}π",
                    'Success Probability': f"{phase_estimates[most_likely_phase] / shots * 100:.1f}%"
                }
                
                figures = [
                    save_figure_to_data(fig_circuit, 'Phase Estimation Circuit'),
                    save_figure_to_data(fig_hist, 'Measurement Results'),
                    save_figure_to_data(fig, 'Phase Distribution')
                ]
                
                store_simulation_data(lab_id, metrics=metrics, measurements=counts, figures=figures)


if __name__ == "__main__":
    run()
