import streamlit as st
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
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
    st.title("Quantum Error Correction")
    st.markdown("### Bit Flip Code Implementation")

    # Configuration
    col1, col2 = st.columns(2)
    with col1:
        error_rate = st.slider("Error Probability", 0.0, 1.0, 0.1, 0.05)
    with col2:
        shots = st.selectbox("Number of Shots", [100, 500, 1000, 5000], index=2)

    initial_state = st.radio("Initial Qubit State", ["0", "1", "+", "-"])

    if st.button("Run Simulation", type="primary"):
        with st.spinner("Running quantum error correction simulation..."):
            # Create quantum circuit for bit flip code
            data = QuantumRegister(1, 'data')
            ancilla = QuantumRegister(2, 'ancilla')
            syndrome = ClassicalRegister(2, 'syndrome')
            result = ClassicalRegister(1, 'result')

            qc = QuantumCircuit(data, ancilla, syndrome, result)

            # Initialize state
            if initial_state == "1":
                qc.x(data[0])
            elif initial_state == "+":
                qc.h(data[0])
            elif initial_state == "-":
                qc.x(data[0])
                qc.h(data[0])

            qc.barrier()

            # Encoding: create logical qubit using 3 physical qubits
            qc.cx(data[0], ancilla[0])
            qc.cx(data[0], ancilla[1])

            qc.barrier()

            # Simulate errors
            for qubit in [data[0], ancilla[0], ancilla[1]]:
                qc.rx(error_rate * np.pi, qubit)

            qc.barrier()

            # Syndrome measurement
            temp_syn1 = QuantumRegister(1, 'temp_syn1')
            temp_syn2 = QuantumRegister(1, 'temp_syn2')
            qc.add_register(temp_syn1, temp_syn2)

            qc.cx(data[0], temp_syn1[0])
            qc.cx(ancilla[0], temp_syn1[0])
            qc.cx(ancilla[0], temp_syn2[0])
            qc.cx(ancilla[1], temp_syn2[0])

            qc.measure(temp_syn1[0], syndrome[0])
            qc.measure(temp_syn2[0], syndrome[1])

            qc.barrier()

            # Error correction based on syndrome
            with qc.if_test((syndrome, 1)):
                qc.x(data[0])
            with qc.if_test((syndrome, 2)):
                qc.x(ancilla[1])
            with qc.if_test((syndrome, 3)):
                qc.x(ancilla[0])

            qc.barrier()

            # Decode
            qc.cx(data[0], ancilla[0])
            qc.cx(data[0], ancilla[1])

            # Final measurement
            qc.measure(data[0], result[0])

            # Execute
            simulator = AerSimulator()
            job = simulator.run(qc, shots=shots)
            counts = job.result().get_counts()

            # Display results
            st.markdown("### Circuit Diagram")
            fig_circuit = qc.draw(output='mpl', style='iqp', fold=-1)
            st.pyplot(fig_circuit)
            plt.close()

            st.markdown("### Measurement Results")

            # Process results
            corrected_counts = {}
            for bitstring, count in counts.items():
                result_bit = bitstring.split()[0]
                corrected_counts[result_bit] = corrected_counts.get(result_bit, 0) + count

            fig_hist = plot_histogram(corrected_counts, color='#1f77b4', title='Corrected State Distribution')
            st.pyplot(fig_hist)
            plt.close()

            # Statistics
            st.markdown("### Statistics")
            total_counts = sum(corrected_counts.values())
            expected_state = "0" if initial_state in ["0", "+"] else "1"

            if initial_state in ["+", "-"]:
                st.info("Note: For superposition states, both outcomes are expected.")
            else:
                fidelity = corrected_counts.get(expected_state, 0) / total_counts
                st.metric("Fidelity", f"{fidelity:.3f}")
                st.metric("Error Rate Used", f"{error_rate:.2f}")

            # Raw syndrome data
            with st.expander("View Raw Measurement Data"):
                st.json(counts)
            
            # Store simulation data for PDF report
            from lab_config import LABS
            lab_id = None
            for name, config in LABS.items():
                if config.get('module') == 'error':
                    lab_id = config['id']
                    break
            
            if lab_id:
                total_counts = sum(corrected_counts.values())
                metrics = {
                    'Error Rate': f"{error_rate:.2f}",
                    'Number of Shots': str(shots),
                    'Initial State': initial_state,
                }
                if initial_state not in ["+", "-"]:
                    expected_state = "0" if initial_state in ["0", "+"] else "1"
                    fidelity = corrected_counts.get(expected_state, 0) / total_counts
                    metrics['Fidelity'] = f"{fidelity:.3f}"
                
                figures = [
                    save_figure_to_data(fig_circuit, 'Error Correction Circuit'),
                    save_figure_to_data(fig_hist, 'Corrected State Distribution')
                ]
                
                store_simulation_data(lab_id, metrics=metrics, measurements=corrected_counts, figures=figures)


if __name__ == "__main__":
    run()