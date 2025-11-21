"""
Multi-Qubit Superposition Lab
Prepare a 3-qubit equal superposition state using Hadamard gates
"""

import streamlit as st
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_histogram, plot_state_city
from qiskit_aer import AerSimulator
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
        num_qubits = st.selectbox("Number of Qubits", [2, 3, 4, 5], index=1)
        shots = st.slider("Number of Shots", 100, 10000, 1024, 100)
    with col2:
        show_circuit = st.checkbox("Show Circuit Diagram", value=True)
        show_statevector = st.checkbox("Show Statevector", value=False)
    
    # Create circuit
    qc = QuantumCircuit(num_qubits)
    
    # Apply Hadamard to all qubits
    for i in range(num_qubits):
        qc.h(i)
    
    qc.measure_all()
    
    # Display circuit
    if show_circuit:
        st.subheader("Quantum Circuit")
        fig_circuit = qc.draw(output='mpl', fold=-1)
        st.pyplot(fig_circuit)
        plt.close()
    
    # Run simulation
    backend = AerSimulator()
    job = backend.run(qc, shots=shots)
    result = job.result()
    counts = result.get_counts()
    
    # Calculate theoretical probabilities
    num_states = 2 ** num_qubits
    theoretical_prob = 1.0 / num_states
    
    # Display results
    st.subheader("Measurement Results")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Probability Distribution")
        fig_hist = plot_histogram(counts)
        st.pyplot(fig_hist)
        plt.close()
        
        # Add theoretical line
        st.markdown(f"**Theoretical probability per state:** {theoretical_prob:.4f} (1/{num_states})")
    
    with col2:
        st.markdown("### Statistics")
        
        # Calculate statistics
        total_measurements = sum(counts.values())
        observed_probs = {state: count / total_measurements for state, count in counts.items()}
        
        st.metric("Total States Observed", len(counts))
        st.metric("Total Possible States", num_states)
        st.metric("Theoretical Probability", f"{theoretical_prob:.4f}")
        
        # Calculate uniformity
        if len(counts) == num_states:
            max_prob = max(observed_probs.values())
            min_prob = min(observed_probs.values())
            uniformity = 1 - (max_prob - min_prob) / theoretical_prob
            st.metric("Uniformity Score", f"{uniformity * 100:.2f}%")
        
        # Show state probabilities
        with st.expander("View State Probabilities"):
            for state in sorted(counts.keys()):
                obs_prob = observed_probs[state]
                diff = abs(obs_prob - theoretical_prob)
                st.write(f"|{state}⟩: {obs_prob:.4f} (diff: {diff:.4f})")
    
    # Show statevector if requested
    if show_statevector:
        st.subheader("Statevector Representation")
        qc_no_measure = QuantumCircuit(num_qubits)
        for i in range(num_qubits):
            qc_no_measure.h(i)
        
        state = Statevector.from_instruction(qc_no_measure)
        fig_state = plot_state_city(state)
        st.pyplot(fig_state)
        plt.close()
        
        # Display statevector amplitudes
        with st.expander("Statevector Amplitudes"):
            st.write("The statevector is:")
            st.latex(r"|\psi\rangle = \frac{1}{\sqrt{2^n}} \sum_{x=0}^{2^n-1} |x\rangle")
            st.write(f"For n={num_qubits}, this gives equal superposition of all {num_states} states.")
    
    # Analysis
    st.divider()
    st.subheader("Analysis")
    
    st.markdown("""
    **Key Observations:**
    
    1. **Equal Superposition**: Each Hadamard gate creates an equal superposition of |0⟩ and |1⟩
    
    2. **Product State**: The final state is a product of individual superpositions:
       - |ψ⟩ = (|0⟩ + |1⟩)/√2 ⊗ (|0⟩ + |1⟩)/√2 ⊗ ... 
       - = (1/√2ⁿ) Σ|x⟩ for all x from 0 to 2ⁿ-1
    
    3. **Uniform Distribution**: All 2ⁿ basis states have equal probability (1/2ⁿ)
    
    4. **Entanglement**: This state is NOT entangled - it's a product state of independent superpositions
    """)
    
    # Verification
    st.markdown("### Verification")
    if len(counts) == num_states:
        chi_square = sum((counts[state] - shots/num_states)**2 / (shots/num_states) 
                        for state in counts.keys())
        st.success(f"All {num_states} states observed!")
        st.info(f"Chi-square statistic: {chi_square:.2f} (lower is better for uniformity)")
    else:
        st.warning(f"Only {len(counts)} out of {num_states} states observed. Increase shots for better coverage.")
    
    # Store simulation data for PDF report
    from lab_config import LABS
    lab_id = None
    for name, config in LABS.items():
        if config.get('module') == 'multi_qubit_superposition':
            lab_id = config['id']
            break
    
    if lab_id:
        metrics = {
            'Number of Qubits': str(num_qubits),
            'Number of Shots': str(shots),
            'Total States Observed': str(len(counts)),
            'Total Possible States': str(num_states),
            'Theoretical Probability': f"{theoretical_prob:.4f}",
        }
        if len(counts) == num_states:
            max_prob = max(observed_probs.values())
            min_prob = min(observed_probs.values())
            uniformity = 1 - (max_prob - min_prob) / theoretical_prob
            metrics['Uniformity Score'] = f"{uniformity * 100:.2f}%"
        
        figures = []
        if show_circuit:
            fig_circuit = qc.draw(output='mpl', fold=-1)
            figures.append(save_figure_to_data(fig_circuit, 'Quantum Circuit'))
            plt.close(fig_circuit)
        figures.append(save_figure_to_data(fig_hist, 'Probability Distribution'))
        if show_statevector:
            qc_no_measure = QuantumCircuit(num_qubits)
            for i in range(num_qubits):
                qc_no_measure.h(i)
            state = Statevector.from_instruction(qc_no_measure)
            fig_state = plot_state_city(state)
            figures.append(save_figure_to_data(fig_state, 'Statevector Representation'))
            plt.close(fig_state)
        
        store_simulation_data(lab_id, metrics=metrics, measurements=counts, figures=figures)

