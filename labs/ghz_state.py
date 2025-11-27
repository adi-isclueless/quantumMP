"""
GHZ State Lab
Create and analyze the GHZ state (|000⟩ + |111⟩)/√2
"""

import streamlit as st
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, partial_trace
from qiskit.visualization import plot_histogram, plot_state_city
from qiskit_aer import AerSimulator
import matplotlib.pyplot as plt
from certificate import store_simulation_data, save_figure_to_data
from lab_utils import display_formulas

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
        measure_qubit = st.selectbox("Measure Qubit (others traced out)", [0, 1, 2], index=0)
    with col2:
        show_circuit = st.checkbox("Show Circuit Diagram", value=True)
        show_statevector = st.checkbox("Show Statevector", value=False)
        analyze_correlation = st.checkbox("Analyze Correlations", value=True)
    
    # Create GHZ state circuit
    qc = QuantumCircuit(3)
    
    # Step 1: Create superposition on first qubit
    qc.h(0)
    
    # Step 2: Entangle qubits
    qc.cx(0, 1)
    qc.cx(0, 2)
    
    # Display circuit
    if show_circuit:
        st.subheader("Quantum Circuit for GHZ State")
        st.markdown("""
        **Circuit Steps:**
        1. Apply H gate to qubit 0: creates superposition (|0⟩ + |1⟩)/√2
        2. Apply CNOT(0,1): entangles qubits 0 and 1
        3. Apply CNOT(0,2): entangles qubit 2 with the pair
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
        expected_states = ['000', '111']
        observed_states = list(counts.keys())
        st.markdown(f"**Expected states:** {expected_states}")
        st.markdown(f"**Observed states:** {observed_states}")
        
        if set(observed_states) == set(expected_states):
            st.success("Only |000⟩ and |111⟩ observed - GHZ state confirmed!")
        else:
            st.warning("Unexpected states observed. This may indicate errors or noise.")
    
    with col2:
        st.markdown("### Statistics")
        
        total = sum(counts.values())
        for state in ['000', '111']:
            if state in counts:
                prob = counts[state] / total
                st.metric(f"P(|{state}⟩)", f"{prob:.4f}", f"{(prob - 0.5) * 100:.2f}%")
            else:
                st.metric(f"P(|{state}⟩)", "0.0000", "-50.00%")
        display_formulas(title="Formulas", formulas=[
            r"|GHZ\rangle = \frac{|000\rangle + |111\rangle}{\sqrt{2}}"
        ])
        
        # Correlation analysis
        if analyze_correlation:
            st.markdown("### Correlation Analysis")
            st.info("""
            **Perfect Correlation:**
            - If qubit 0 = 0, then qubits 1 and 2 must be 0
            - If qubit 0 = 1, then qubits 1 and 2 must be 1
            - Measuring any one qubit determines the others
            """)
    
    # Single qubit measurement
    st.divider()
    st.subheader(f"Measuring Qubit {measure_qubit} (Tracing Out Others)")
    
    # Create circuit that only measures selected qubit
    qc_single = QuantumCircuit(3, 1)  # 3 qubits, 1 classical bit
    qc_single.h(0)
    qc_single.cx(0, 1)
    qc_single.cx(0, 2)
    qc_single.measure(measure_qubit, 0)
    
    job_single = backend.run(qc_single, shots=shots)
    result_single = job_single.result()
    counts_single = result_single.get_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### Qubit {measure_qubit} Measurement")
        fig_single = plot_histogram(counts_single)
        st.pyplot(fig_single)
        plt.close()
        
        # Show what this implies
        total_single = sum(counts_single.values())
        prob_0 = counts_single.get('0', 0) / total_single
        prob_1 = counts_single.get('1', 0) / total_single
        
        st.metric("P(0)", f"{prob_0:.4f}")
        st.metric("P(1)", f"{prob_1:.4f}")
    
    with col2:
        st.markdown("### Implications")
        st.markdown(f"""
        **When Qubit {measure_qubit} = 0:**
        - The other qubits collapse to |00⟩
        - Full state becomes |000⟩
        
        **When Qubit {measure_qubit} = 1:**
        - The other qubits collapse to |11⟩
        - Full state becomes |111⟩
        
        **Key Property:**
        Measuring any single qubit in a GHZ state immediately determines the state of all other qubits, demonstrating maximum entanglement.
        """)
    
    # Show statevector if requested
    if show_statevector:
        st.divider()
        st.subheader("Statevector Representation")
        state = Statevector.from_instruction(qc)
        fig_state = plot_state_city(state)
        st.pyplot(fig_state)
        plt.close()
        
        with st.expander("Statevector Details"):
            st.write("The GHZ state is:")
            st.latex(r"|\text{GHZ}\rangle = \frac{|000\rangle + |111\rangle}{\sqrt{2}}")
            st.write("**Amplitudes:**")
            for i, amp in enumerate(state):
                if abs(amp) > 1e-10:
                    state_label = format(i, f'0{3}b')
                    st.write(f"|{state_label}⟩: {amp:.6f}")
    
    # Comparison with other states
    st.divider()
    st.subheader("GHZ State Properties")
    
    st.markdown("""
    **Key Characteristics:**
    
    1. **Maximal Entanglement**: All three qubits are maximally entangled
    2. **Perfect Correlations**: Measuring any qubit determines the others
    3. **Bipartite Entanglement**: Tracing out one qubit leaves the other two in a mixed state
    4. **Fragility**: Losing one qubit destroys all entanglement
    
    **Applications:**
    - Quantum teleportation
    - Quantum error correction
    - Quantum communication protocols
    - Fundamental tests of quantum mechanics
    """)
    
    # Verify entanglement
    st.markdown("### Entanglement Verification")
    
    # Check if we only see |000⟩ and |111⟩
    if set(counts.keys()) == {'000', '111'}:
        ratio_000 = counts.get('000', 0) / sum(counts.values())
        ratio_111 = counts.get('111', 0) / sum(counts.values())
        
        if abs(ratio_000 - 0.5) < 0.1 and abs(ratio_111 - 0.5) < 0.1:
            st.success("GHZ state successfully created! Equal probabilities for |000⟩ and |111⟩.")
        else:
            st.warning(f"GHZ state created but probabilities are not equal: P(|000⟩)={ratio_000:.3f}, P(|111⟩)={ratio_111:.3f}")
    else:
        st.error("GHZ state not properly created. Expected only |000⟩ and |111⟩ states.")
    
    # Store simulation data for PDF report
    from lab_config import LABS
    lab_id = None
    for name, config in LABS.items():
        if config.get('module') == 'ghz_state':
            lab_id = config['id']
            break
    
    if lab_id:
        total = sum(counts.values())
        metrics = {
            'Number of Shots': str(shots),
            'Measured Qubit': str(measure_qubit),
        }
        for state in ['000', '111']:
            if state in counts:
                prob = counts[state] / total
                metrics[f'P(|{state}⟩)'] = f"{prob:.4f}"
        
        # Single qubit probabilities
        total_single = sum(counts_single.values())
        prob_0 = counts_single.get('0', 0) / total_single
        prob_1 = counts_single.get('1', 0) / total_single
        metrics[f'P(Qubit {measure_qubit}=0)'] = f"{prob_0:.4f}"
        metrics[f'P(Qubit {measure_qubit}=1)'] = f"{prob_1:.4f}"
        
        figures = []
        if show_circuit:
            fig_circuit = qc.draw(output='mpl', fold=-1)
            figures.append(save_figure_to_data(fig_circuit, 'GHZ State Circuit'))
            plt.close(fig_circuit)
        figures.append(save_figure_to_data(fig_hist, 'Full State Measurements'))
        figures.append(save_figure_to_data(fig_single, f'Qubit {measure_qubit} Measurement'))
        if show_statevector:
            fig_state = plot_state_city(Statevector.from_instruction(qc))
            figures.append(save_figure_to_data(fig_state, 'Statevector Representation'))
            plt.close(fig_state)
        
        # Combine all measurements
        all_measurements = dict(counts)
        for key, val in counts_single.items():
            all_measurements[f'Single_{key}'] = val
        
        store_simulation_data(lab_id, metrics=metrics, measurements=all_measurements, figures=figures)
        