"""
Quantum Circuit Identity Verification Lab
Verify equivalence of circuits (e.g., HZH = X, consecutive CNOT swaps)
"""

import streamlit as st
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector
from qiskit.visualization import plot_histogram
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
    
    st.divider()
    
    # Select identity to verify
    identity_type = st.selectbox(
        "Select Circuit Identity to Verify",
        [
            "HZH = X",
            "HXH = Z",
            "CNOT Swap (two CNOTs)",
            "H^2 = I (Hadamard self-inverse)",
            "X^2 = I (Pauli X self-inverse)",
            "Y^2 = I (Pauli Y self-inverse)",
            "Z^2 = I (Pauli Z self-inverse)"        
        ]
    )
    
    st.divider()
    
    # Create circuits based on selection
    if identity_type == "HZH = X":
        st.markdown("### Verifying: HZH = X")
        st.markdown("**Theory:** Applying H, then Z, then H is equivalent to applying X")
        
        # Circuit 1: HZH
        qc1 = QuantumCircuit(1)
        qc1.h(0)
        qc1.z(0)
        qc1.h(0)
        qc1.name = "HZH"
        
        # Circuit 2: X
        qc2 = QuantumCircuit(1)
        qc2.x(0)
        qc2.name = "X"
        
        description = "HZH should be equivalent to X gate"
        
    elif identity_type == "HXH = Z":
        st.markdown("### Verifying: HXH = Z")
        st.markdown("**Theory:** Applying H, then X, then H is equivalent to applying Z")
        
        qc1 = QuantumCircuit(1)
        qc1.h(0)
        qc1.x(0)
        qc1.h(0)
        qc1.name = "HXH"
        
        qc2 = QuantumCircuit(1)
        qc2.z(0)
        qc2.name = "Z"
        
        description = "HXH should be equivalent to Z gate"
        
    elif identity_type == "CNOT Swap (two CNOTs)":
        st.markdown("### Verifying: CNOT(a,b) CNOT(b,a) CNOT(a,b) = SWAP")
        st.markdown("**Theory:** Three CNOT gates in specific order implement a SWAP")
        
        qc1 = QuantumCircuit(2)
        qc1.cx(0, 1)
        qc1.cx(1, 0)
        qc1.cx(0, 1)
        qc1.name = "CNOT SWAP"
        
        qc2 = QuantumCircuit(2)
        qc2.swap(0, 1)
        qc2.name = "SWAP"
        
        description = "Three CNOT gates should be equivalent to SWAP gate"
        
    elif identity_type == "H^2 = I (Hadamard self-inverse)":
        st.markdown("### Verifying: H^2 = I")
        st.markdown("**Theory:** Hadamard gate is self-inverse")
        
        qc1 = QuantumCircuit(1)
        qc1.h(0)
        qc1.h(0)
        qc1.name = "H^2"
        
        qc2 = QuantumCircuit(1)
        # Identity is implicit - no gates
        qc2.name = "I"
        
        description = "Two Hadamard gates should be equivalent to identity"
        
    elif identity_type == "X^2 = I (Pauli X self-inverse)":
        st.markdown("### Verifying: X^2 = I")
        
        qc1 = QuantumCircuit(1)
        qc1.x(0)
        qc1.x(0)
        qc1.name = "X^2"
        
        qc2 = QuantumCircuit(1)
        qc2.name = "I"
        
        description = "Two X gates should be equivalent to identity"
        
    elif identity_type == "Y^2 = I (Pauli Y self-inverse)":
        st.markdown("### Verifying: Y^2 = I")
        
        qc1 = QuantumCircuit(1)
        qc1.y(0)
        qc1.y(0)
        qc1.name = "Y^2"
        
        qc2 = QuantumCircuit(1)
        qc2.name = "I"
        
        description = "Two Y gates should be equivalent to identity"
        
    elif identity_type == "Z^2 = I (Pauli Z self-inverse)":
        st.markdown("### Verifying: Z^2 = I")
        
        qc1 = QuantumCircuit(1)
        qc1.z(0)
        qc1.z(0)
        qc1.name = "Z^2"
        
        qc2 = QuantumCircuit(1)
        qc2.name = "I"
        
        description = "Two Z gates should be equivalent to identity"
        
    else:  # Custom Circuit
        st.markdown("### Custom Circuit Identity")
        st.info("Custom circuit verification not yet implemented. Please select a predefined identity.")
        return
    
    # Display circuits
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### Circuit 1: {qc1.name}")
        fig1 = qc1.draw(output='mpl', fold=-1)
        st.pyplot(fig1)
        plt.close()
    
    with col2:
        st.markdown(f"### Circuit 2: {qc2.name}")
        fig2 = qc2.draw(output='mpl', fold=-1)
        st.pyplot(fig2)
        plt.close()
    
    st.divider()
    
    # Method 1: Operator comparison
    st.subheader("Method 1: Operator Comparison")
    
    try:
        op1 = Operator(qc1)
        op2 = Operator(qc2)
        
        # Check if operators are equal
        if op1.equiv(op2):
            st.success("Circuits are equivalent! Operators match.")
            equivalence = True
        else:
            st.error("Circuits are NOT equivalent. Operators differ.")
            equivalence = False
            
        # Show operator matrices
        with st.expander("View Operator Matrices"):
            st.markdown("**Circuit 1 Operator:**")
            st.write(op1.data)
            st.markdown("**Circuit 2 Operator:**")
            st.write(op2.data)
            st.markdown("**Difference:**")
            st.write(np.abs(op1.data - op2.data))
            
    except Exception as e:
        st.warning(f"Operator comparison failed: {str(e)}")
        equivalence = None
    
    st.divider()
    
    # Method 2: Measurement comparison
    st.subheader("Method 2: Measurement Comparison")
    
    # Test on different input states
    input_states = st.multiselect(
        "Test Input States",
        ["|0⟩", "|1⟩", "|+⟩", "|-⟩", "|i⟩", "|-i⟩"],
        default=["|0⟩", "|1⟩", "|+⟩"]
    )
    
    shots = st.slider("Number of Shots", 100, 5000, 1024, 100)
    
    backend = AerSimulator()
    results_match = True
    
    for input_state in input_states:
        st.markdown(f"### Testing on {input_state}")
        
        # Prepare input state
        qc_input = QuantumCircuit(qc1.num_qubits)
        if input_state == "|0⟩":
            # Already in |0⟩
            pass
        elif input_state == "|1⟩":
            qc_input.x(0)
        elif input_state == "|+⟩":
            qc_input.h(0)
        elif input_state == "|-⟩":
            qc_input.h(0)
            qc_input.z(0)
        elif input_state == "|i⟩":
            qc_input.h(0)
            qc_input.s(0)
        elif input_state == "|-i⟩":
            qc_input.h(0)
            qc_input.sdg(0)
        
        # Apply circuit 1
        qc1_test = qc_input.copy()
        qc1_test.compose(qc1, inplace=True)
        qc1_test.measure_all()
        
        # Apply circuit 2
        qc2_test = qc_input.copy()
        qc2_test.compose(qc2, inplace=True)
        qc2_test.measure_all()
        
        # Run simulations
        job1 = backend.run(qc1_test, shots=shots)
        counts1 = job1.result().get_counts()
        
        job2 = backend.run(qc2_test, shots=shots)
        counts2 = job2.result().get_counts()
        
        # Compare results
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Circuit 1 ({qc1.name}) Results:**")
            fig1 = plot_histogram(counts1)
            st.pyplot(fig1)
            plt.close()
        
        with col2:
            st.markdown(f"**Circuit 2 ({qc2.name}) Results:**")
            fig2 = plot_histogram(counts2)
            st.pyplot(fig2)
            plt.close()
        
        # Check if results match
        if counts1 == counts2:
            st.success(f"Results match for {input_state}!")
        else:
            # Calculate similarity
            all_states = set(counts1.keys()) | set(counts2.keys())
            total1 = sum(counts1.values())
            total2 = sum(counts2.values())
            
            differences = []
            for state in all_states:
                prob1 = counts1.get(state, 0) / total1
                prob2 = counts2.get(state, 0) / total2
                diff = abs(prob1 - prob2)
                differences.append(diff)
            
            max_diff = max(differences)
            if max_diff < 0.05:  # 5% tolerance
                st.success(f"Results very similar for {input_state} (max diff: {max_diff:.4f})")
            else:
                st.warning(f"Results differ for {input_state} (max diff: {max_diff:.4f})")
                results_match = False
    
    st.divider()
    
    # Final verdict
    st.subheader("Verification Result")
    
    if equivalence is True and results_match:
        st.success("""
        **IDENTITY VERIFIED**
        
        Both operator comparison and measurement comparison confirm that the circuits are equivalent!
        """)
    elif equivalence is True:
        st.warning("""
        **PARTIALLY VERIFIED**
        
        Operator comparison shows equivalence, but measurement results show some differences.
        This may be due to statistical fluctuations or implementation details.
        """)
    elif equivalence is False:
        st.error("""
        **IDENTITY NOT VERIFIED**
        
        The circuits are not equivalent according to operator comparison.
        """)
    else:
        if results_match:
            st.info("""
            **MEASUREMENT VERIFIED**
            
            Measurement results match, but operator comparison was not available.
            """)
    
    # Explanation
    st.divider()
    st.subheader("Understanding Circuit Identities")
    
    st.markdown("""
    **Why Circuit Identities Matter:**
    
    1. **Circuit Optimization**: Equivalent circuits can be simplified
    2. **Gate Decomposition**: Complex gates can be decomposed into simpler ones
    3. **Error Correction**: Understanding identities helps in error correction
    4. **Algorithm Design**: Identities are used in quantum algorithm design
    
    **Common Identities:**
    - HZH = X: Hadamard conjugates Z to X
    - HXH = Z: Hadamard conjugates X to Z
    - CNOT sequences can implement SWAP
    - All Pauli gates are self-inverse (X² = Y² = Z² = I)
    - Hadamard is self-inverse (H² = I)
    """)
    
    # Store simulation data for PDF report
    from lab_config import LABS
    lab_id = None
    for name, config in LABS.items():
        if config.get('module') == 'circuit_identity':
            lab_id = config['id']
            break
    
    if lab_id and 'input_states' in locals() and len(input_states) > 0:
        metrics = {
            'Identity Type': identity_type,
            'Number of Shots': str(shots),
            'Operator Equivalence': 'Yes' if equivalence else 'No' if equivalence is False else 'Unknown',
            'Measurement Equivalence': 'Yes' if results_match else 'No',
        }
        
        # Aggregate measurements from all input states
        all_measurements = {}
        for input_state in input_states:
            # Get counts from the last tested state (they're overwritten in loop)
            # We'll use a simplified approach
            pass
        
        figures = [
            save_figure_to_data(fig1, f'Circuit 1: {qc1.name}'),
            save_figure_to_data(fig2, f'Circuit 2: {qc2.name}')
        ]
        
        # Add measurement histograms if available
        if 'counts1' in locals() and 'counts2' in locals():
            fig_hist1 = plot_histogram(counts1)
            fig_hist2 = plot_histogram(counts2)
            figures.append(save_figure_to_data(fig_hist1, f'Circuit 1 Results'))
            figures.append(save_figure_to_data(fig_hist2, f'Circuit 2 Results'))
            plt.close(fig_hist1)
            plt.close(fig_hist2)
        
        # Use counts from last tested state as measurements
        if 'counts1' in locals():
            store_simulation_data(lab_id, metrics=metrics, measurements=counts1, figures=figures)

