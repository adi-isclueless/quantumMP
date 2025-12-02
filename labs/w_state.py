"""
W State Lab
Create and analyze the W state (|001⟩ + |010⟩ + |100⟩)/√3
"""

import streamlit as st
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_histogram, plot_state_city
from qiskit_aer import AerSimulator
import matplotlib.pyplot as plt
from certificate import store_simulation_data, save_figure_to_data
from lab_utils import display_formulas

def create_w_state():
    """Exact 3-qubit W state with only standard gates (no leakage)."""
    qc = QuantumCircuit(3)

    # Step 1: Put amplitude on |..1> (q0) : sin(θ0/2)=1/√3  ⇒ θ0 = 2*arcsin(1/√3)
    theta0 = 2 * np.arcsin(1 / np.sqrt(3))
    qc.ry(theta0, 0)  # acts only on q0

    # State now:  sqrt(2/3)|000> + 1/√3 |001>

    # Step 2: Move exactly 1/√3 from |000> → |010>, without touching |001>
    # Do a CRY on q1 controlled by q0=0  ⇒ surround control with X
    # Need sin(θ1/2) = 1/√2  ⇒ θ1 = π/2
    theta1 = np.pi / 2
    qc.x(0)
    qc.cry(theta1, 0, 1)  # control=q0 (now "1" only when original q0==0), target=q1

    # State now:  (1/√3)|001> + (1/√3)|010> + (1/√3)|000>

    # Step 3: Convert the remaining |000> amplitude → |100>
    # Flip q2 iff (q0==0 AND q1==0): implement zero-controls by X, then CCX, then un-X
    qc.x(1)
    qc.ccx(0, 1, 2)   # fires only for original |000>, turning it into |100>
    qc.x(1)
    qc.x(0)

    return qc


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
    
    st.divider()
    
    # User controls
    col1, col2 = st.columns(2)
    with col1:
        shots = st.slider("Number of Shots", 100, 10000, 1024, 100)
    with col2:
        show_circuit = st.checkbox("Show Circuit Diagram", value=True)
        show_statevector = st.checkbox("Show Statevector", value=False)
        compare_ghz = st.checkbox("Compare with GHZ State", value=True)
    
    # Create W state circuit
    qc = create_w_state()

    
    # Display circuit
    if show_circuit:
        st.subheader("Quantum Circuit for W State")
        st.markdown("""
        **W State:** (|001⟩ + |010⟩ + |100⟩)/√3
        
        **Properties:**
        - Equal superposition of states with exactly one qubit in |1⟩
        - All three qubits are entangled
        - More robust to qubit loss than GHZ state
        """)
        fig_circuit = qc.draw(output='mpl', fold=-1)
        st.pyplot(fig_circuit)
        plt.close()
    
    # Measure all qubits
    qc_measure_all = qc.copy()
    qc_measure_all.measure_all()
    
    # Run simulation
    backend = AerSimulator()
    job = backend.run(qc_measure_all, shots=shots)
    result = job.result()
    counts = result.get_counts()
    
    # Display measurement results
    st.subheader("Measurement Results")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Full State Measurements")
        fig_hist = plot_histogram(counts)
        st.pyplot(fig_hist)
        plt.close()
        
        # Analysis
        expected_states = ['001', '010', '100']
        observed_states = list(counts.keys())
        st.markdown(f"**Observed states:** {observed_states}")
        
        # Check if we have the right states
        if all(state in counts for state in expected_states):
            if len(counts) == 3:
                st.success("W state created! Only states with one |1⟩ observed.")
            else:
                st.warning(f"W state partially created. Expected 3 states, got {len(counts)}.")
        else:
            st.error("❌ W state creation failed")
            st.info("💡 **Troubleshooting**: Try increasing the number of shots or check if noise is affecting the simulation.")
    
    with col2:
        st.markdown("### Statistics")
        
        total = sum(counts.values())
        theoretical_prob = 1.0 / 3.0
        
        for state in ['001', '010', '100']:
            if state in counts:
                prob = counts[state] / total
                diff = prob - theoretical_prob
                st.metric(f"P(|{state}⟩)", f"{prob:.4f}", f"{diff*100:.2f}%")
            else:
                st.metric(f"P(|{state}⟩)", "0.0000", "-33.33%")
        
        # Uniformity check
        if all(state in counts for state in expected_states):
            probs = [counts[state] / total for state in expected_states]
            max_diff = max(abs(p - theoretical_prob) for p in probs)
            st.metric("Uniformity", f"{(1 - max_diff/theoretical_prob)*100:.2f}%")
            # Display formulas
            display_formulas(title="Formulas", formulas=[
                r"|W\rangle = \frac{|001\rangle + |010\rangle + |100\rangle}{\sqrt{3}}",
                r"P(1\;\text{on a given qubit}) = \frac{1}{3}"
            ])
    
    # Single qubit measurements
    st.divider()
    st.subheader("Single Qubit Measurements")
    
    st.markdown("""
    **Measuring Individual Qubits:**
    When we measure a single qubit in the W state, we get interesting results:
    """)
    
    cols = st.columns(3)
    single_qubit_results = {}
    
    for i, col in enumerate(cols):
        with col:
            st.markdown(f"### Qubit {i}")
            
            # Create new circuit with proper classical register
            qc_single = QuantumCircuit(3, 1)
            
            # Recreate W state using the selected method
            qc_single.x(2)
            theta = 2 * np.arccos(np.sqrt(2/3))
            qc_single.ry(theta, 1)
            qc_single.cswap(1, 0, 2)
            phi = 2 * np.arccos(np.sqrt(1/2))
            qc_single.cry(phi, 1, 0)

            
            # Measure the selected qubit
            qc_single.measure(i, 0)
            
            job_single = backend.run(qc_single, shots=shots)
            result_single = job_single.result()
            counts_single = result_single.get_counts()
            
            fig_single = plot_histogram(counts_single)
            st.pyplot(fig_single)
            plt.close()
            
            total_single = sum(counts_single.values())
            prob_0 = counts_single.get('0', 0) / total_single
            prob_1 = counts_single.get('1', 0) / total_single
            
            st.metric("P(0)", f"{prob_0:.4f}")
            st.metric("P(1)", f"{prob_1:.4f}")
            
            single_qubit_results[i] = (prob_0, prob_1)
    
    # Show statevector if requested
    if show_statevector:
        st.divider()
        st.subheader("Statevector Representation")
        state = Statevector.from_instruction(qc)
        fig_state = plot_state_city(state)
        st.pyplot(fig_state)
        plt.close()
        
        with st.expander("Statevector Details"):
            st.write("The W state is:")
            st.latex(r"|W\rangle = \frac{|001\rangle + |010\rangle + |100\rangle}{\sqrt{3}}")
            st.write("**Amplitudes:**")
            for i, amp in enumerate(state):
                if abs(amp) > 1e-10:
                    state_label = format(i, '03b')
                    st.write(f"|{state_label}⟩: {amp:.6f}")
    
    # Comparison with GHZ
    if compare_ghz:
        st.divider()
        st.subheader("W State vs GHZ State")
        
        comparison_data = {
            "Property": [
                "State",
                "Entanglement",
                "Qubit Loss Robustness",
                "Single Qubit Measurement",
                "Applications"
            ],
            "W State": [
                "(|001⟩ + |010⟩ + |100⟩)/√3",
                "All 3 qubits entangled",
                "Robust - retains entanglement",
                "P(1) = 1/3 for each qubit",
                "Quantum communication, error correction"
            ],
            "GHZ State": [
                "(|000⟩ + |111⟩)/√2",
                "All 3 qubits entangled",
                "Fragile - loses all entanglement",
                "P(1) = 1/2 for each qubit",
                "Quantum teleportation, tests"
            ]
        }
        
        st.table(comparison_data)
        
        st.markdown("""
        **Key Differences:**
        
        1. **Robustness to Qubit Loss:**
           - **W State**: If one qubit is lost, the remaining two qubits are still entangled
           - **GHZ State**: If one qubit is lost, the remaining two qubits become completely mixed (no entanglement)
        
        2. **Measurement Outcomes:**
           - **W State**: Always measures exactly one qubit in |1⟩ state
           - **GHZ State**: Either all qubits are |0⟩ or all are |1⟩
        
        3. **Entanglement Structure:**
           - **W State**: Robust bipartite entanglement persists after qubit loss
           - **GHZ State**: All entanglement is destroyed by qubit loss
        """)
    
    # Analysis
    st.divider()
    st.subheader("W State Properties")
    
    st.markdown("""
    **Key Characteristics:**
    
    1. **Symmetric Entanglement**: The W state is symmetric under permutation of qubits
    
    2. **Robustness**: More robust to particle loss than GHZ state
    
    3. **Entanglement Persistence**: If one qubit is traced out, the remaining two qubits are still entangled
    
    4. **Measurement**: Measuring any single qubit gives P(1) = 1/3
    
    **Applications:**
    - Quantum communication protocols where robustness is important
    - Quantum error correction
    - Quantum networking
    - Fundamental studies of multipartite entanglement
    """)
    
    # Verify W state
    st.markdown("### W State Verification")
    
    if all(state in counts for state in ['001', '010', '100']):
        if len(counts) == 3:
            probs = [counts[state] / sum(counts.values()) for state in ['001', '010', '100']]
            theoretical = 1.0 / 3.0
            max_error = max(abs(p - theoretical) for p in probs)
            
            if max_error < 0.1:
                st.success("W state successfully created! All three states observed with approximately equal probabilities.")
            else:
                st.warning(f"W state created but probabilities are not uniform. Max error: {max_error:.3f}")
        else:
            st.error(f"❌ W state verification failed: Expected 3 states (|001⟩, |010⟩, |100⟩), but got {len(counts)} states")
            st.info("💡 This could be due to noise or measurement errors. Try running the simulation again.")
    else:
        st.error("W state not properly created. Missing expected states.")
    
    # Store simulation data for PDF report
    from lab_config import LABS
    lab_id = None
    for name, config in LABS.items():
        if config.get('module') == 'w_state':
            lab_id = config['id']
            break
    
    if lab_id:
        total = sum(counts.values())
        metrics = {
            'Number of Shots': str(shots),
        }
        for state in ['001', '010', '100']:
            if state in counts:
                prob = counts[state] / total
                metrics[f'P(|{state}⟩)'] = f"{prob:.4f}"
        
        # Add single qubit probabilities
        for i, (prob_0, prob_1) in single_qubit_results.items():
            metrics[f'P(Qubit {i}=0)'] = f"{prob_0:.4f}"
            metrics[f'P(Qubit {i}=1)'] = f"{prob_1:.4f}"
        
        figures = []
        if show_circuit:
            fig_circuit = qc.draw(output='mpl', fold=-1)
            figures.append(save_figure_to_data(fig_circuit, 'W State Circuit'))
            plt.close(fig_circuit)
        figures.append(save_figure_to_data(fig_hist, 'Full State Measurements'))
        if show_statevector:
            state = Statevector.from_instruction(qc)
            fig_state = plot_state_city(state)
            figures.append(save_figure_to_data(fig_state, 'Statevector Representation'))
            plt.close(fig_state)
        
        # Combine all measurements
        all_measurements = dict(counts)
        for i in range(3):
            if i in single_qubit_results:
                all_measurements[f'Qubit_{i}_0'] = int(single_qubit_results[i][0] * shots)
                all_measurements[f'Qubit_{i}_1'] = int(single_qubit_results[i][1] * shots)
        
        store_simulation_data(lab_id, metrics=metrics, measurements=all_measurements, figures=figures)
