"""
3-Qubit Bit Flip Code Lab
Encode a qubit into 3 qubits to detect single bit-flip errors
"""

import streamlit as st
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_histogram
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
        initial_state = st.selectbox("Initial State to Encode", ["|0⟩", "|1⟩", "|+⟩", "Custom"], index=0)
        if initial_state == "Custom":
            theta = st.slider("Theta (rotation angle)", 0.0, np.pi, np.pi/4, 0.1)
        else:
            theta = 0.0
    with col2:
        error_qubit = st.selectbox("Apply Bit-Flip Error to Qubit", ["None", "0", "1", "2"], index=0)
        shots = st.slider("Number of Shots", 100, 5000, 1024, 100)
        show_circuit = st.checkbox("Show Circuit Diagram", value=True)
    
    st.divider()
    
    X, Y = st.columns(2)
    with X:
        st.subheader("Encoding Circuit")
        st.markdown("""
        **Bit-Flip Code Encoding:**
        1. Encode |ψ⟩ into 3 qubits: |ψ⟩ → |ψ⟩|0⟩|0⟩
        2. Apply CNOT gates to create redundancy
        3. Result: |ψ⟩|ψ⟩|ψ⟩ (three copies of the logical qubit)
        """)
        # Syndrome measurement (error detection)
        st.subheader("Syndrome Measurement (Error Detection)")
        st.markdown("""
        **Syndrome Measurement:**
        - Measure parity of qubits 0 and 1 → syndrome bit 0
        - Measure parity of qubits 0 and 2 → syndrome bit 1
        - Syndrome tells us which qubit has the error (if any)
        """)

    # Encoding circuit
    
    
    # Create encoding circuit with ancilla qubits for syndrome measurement
    # Qubits 0-2: data qubits, Qubits 3-4: ancilla for syndrome
    qc_encode = QuantumCircuit(5, 2)  # 5 qubits (3 data + 2 ancilla), 2 classical bits
    
    # Prepare initial state
    if initial_state == "|0⟩":
        pass  # Already in |0⟩
    elif initial_state == "|1⟩":
        qc_encode.x(0)
    elif initial_state == "|+⟩":
        qc_encode.h(0)
    elif initial_state == "Custom":
        qc_encode.ry(theta, 0)
    
    # Encoding: CNOT from qubit 0 to qubits 1 and 2
    qc_encode.cx(0, 1)
    qc_encode.cx(0, 2)
    qc_encode.barrier()
    
    with Y:
        if show_circuit:
            st.markdown("### Encoding Circuit")
            fig_encode = qc_encode.draw(output='mpl', fold=-1)
            st.pyplot(fig_encode)
            plt.close()
    
    # Apply error (if any)
    qc_error = qc_encode.copy()
    if error_qubit != "None":
        error_idx = int(error_qubit)
        qc_error.x(error_idx)
        qc_error.barrier()
        st.info(f"Bit-flip error (X gate) applied to qubit {error_idx}")
    
    
    
    qc_syndrome = qc_error.copy()
    
    # Syndrome measurement using ancilla qubits
    # Ancilla qubit 3: measures parity of qubits 0 and 1
    qc_syndrome.cx(0, 3)
    qc_syndrome.cx(1, 3)
    qc_syndrome.measure(3, 0)
    
    # Ancilla qubit 4: measures parity of qubits 0 and 2
    qc_syndrome.cx(0, 4)
    qc_syndrome.cx(2, 4)
    qc_syndrome.measure(4, 1)
    
    if show_circuit:
        st.markdown("### Complete Circuit (Encoding + Error + Syndrome)")
        fig_syndrome = qc_syndrome.draw(output='mpl', fold=-1)
        st.pyplot(fig_syndrome)
        plt.close()
    
    # Run simulation
    backend = AerSimulator()
    job = backend.run(qc_syndrome, shots=shots)
    result = job.result()
    counts = result.get_counts()
    
    # Display results
    st.subheader("Syndrome Measurement Results")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Syndrome Outcomes")
        fig_hist = plot_histogram(counts)
        st.pyplot(fig_hist)
        plt.close()
    
    with col2:
        st.markdown("### Syndrome Interpretation")
        
        # Analyze syndromes
        syndrome_00 = counts.get('00', 0)
        syndrome_01 = counts.get('01', 0)
        syndrome_10 = counts.get('10', 0)
        syndrome_11 = counts.get('11', 0)
        
        total = sum(counts.values())
        
        st.metric("Syndrome 00", syndrome_00, f"{syndrome_00/total*100:.1f}%")
        st.metric("Syndrome 01", syndrome_01, f"{syndrome_01/total*100:.1f}%")
        st.metric("Syndrome 10", syndrome_10, f"{syndrome_10/total*100:.1f}%")
        st.metric("Syndrome 11", syndrome_11, f"{syndrome_11/total*100:.1f}%")
        display_formulas(title="Formulas", formulas=[
            r"s_1 = q_0 \oplus q_1",
            r"s_0 = q_0 \oplus q_2"
        ])
        
        # Determine error location
        if error_qubit == "None":
            st.success("**No Error Applied**")
            st.info("""
            **Expected:** Syndrome 00 (no error detected)
            - All qubits should have the same value
            - Parity checks should agree
            """)
        else:
            error_idx = int(error_qubit)
            st.warning(f"**Error Applied to Qubit {error_idx}**")
            
            # Syndrome interpretation
            if error_idx == 0:
                expected_syndrome = "11"
                st.info("""
                **Expected Syndrome:** 11
                - Qubit 0 has error
                - Both parity checks detect the error
                """)
            elif error_idx == 1:
                expected_syndrome = "01"
                st.info("""
                **Expected Syndrome:** 01
                - Qubit 1 has error
                - First parity check (q0⊕q1) detects it
                """)
            else:  # error_idx == 2
                expected_syndrome = "10"
                st.info("""
                **Expected Syndrome:** 10
                - Qubit 2 has error
                - Second parity check (q0⊕q2) detects it
                """)
            
            # Check if we got the expected syndrome
            expected_count = counts.get(expected_syndrome, 0)
            if expected_count / total > 0.9:
                st.success(f"Error correctly detected! Syndrome {expected_syndrome} observed in {expected_count/total*100:.1f}% of cases.")
            else:
                st.warning(f"Expected syndrome {expected_syndrome}, but got different results.")
    
    # Error correction (if error detected)
    st.divider()
    st.subheader("Error Correction")
    
    st.markdown("""
    **Error Correction Process:**
    
    1. **Detect Error**: Use syndrome measurement to identify which qubit has the error
    2. **Correct Error**: Apply X gate to the corrupted qubit
    3. **Verify**: Measure to confirm correction
    
    **Syndrome to Correction Mapping:**
    - Syndrome 00: No error → No correction needed
    - Syndrome 01: Error on qubit 1 → Apply X to qubit 1
    - Syndrome 10: Error on qubit 2 → Apply X to qubit 2
    - Syndrome 11: Error on qubit 0 → Apply X to qubit 0
    """)
    
    if error_qubit != "None":
        st.markdown("### Correction Circuit")
        
        # Create correction circuit
        qc_correct = qc_error.copy()
        
        # Syndrome measurement using ancilla qubits
        # Ancilla qubit 3: measures parity of qubits 0 and 1
        qc_correct.cx(0, 3)
        qc_correct.cx(1, 3)
        qc_correct.measure(3, 0)
        
        # Ancilla qubit 4: measures parity of qubits 0 and 2
        qc_correct.cx(0, 4)
        qc_correct.cx(2, 4)
        qc_correct.measure(4, 1)
        qc_correct.barrier()
        
        # Conditional correction based on measured syndrome
        # We need to reference classical bits by index
        c0 = qc_correct.clbits[0]
        c1 = qc_correct.clbits[1]

        # Syndrome 01 → error on qubit 1 (c0=1, c1=0)
        with qc_correct.if_test((c0, 1)):
            qc_correct.x(1)

        # Syndrome 10 → error on qubit 2 (c0=0, c1=1)
        with qc_correct.if_test((c1, 1)):
            qc_correct.x(2)

        # Syndrome 11 → error on qubit 0 (c0=1, c1=1)
        with qc_correct.if_test((c0, 1)):
            with qc_correct.if_test((c1, 1)):
                qc_correct.x(0)
        
        if show_circuit:
            fig_correct = qc_correct.draw(output='mpl', fold=-1)
            st.pyplot(fig_correct)
            plt.close()
        
        st.info("""
        **Note:** The correction circuit applies X gates conditionally based on the syndrome measurement.
        In a real quantum computer, this would require mid-circuit measurement and conditional operations.
        """)
    
    # Analysis
    st.divider()
    st.subheader("Bit-Flip Code Analysis")
    
    st.markdown("""
    **Key Properties:**
    
    1. **Error Detection**: Can detect single bit-flip errors on any of the three qubits
    
    2. **Error Correction**: Can correct single bit-flip errors by applying X gate to the corrupted qubit
    
    3. **Limitations**: 
       - Cannot detect/correct phase errors
       - Cannot correct multiple errors
       - Requires three physical qubits for one logical qubit
    
    4. **Syndrome Table:**
       | Syndrome | Error Location | Correction |
       |----------|----------------|------------|
       | 00       | None           | None       |
       | 01       | Qubit 1        | X on 1     |
       | 10       | Qubit 2        | X on 2     |
       | 11       | Qubit 0        | X on 0     |
    
    **Applications:**
    - Quantum error correction
    - Fault-tolerant quantum computing
    - Protecting quantum information from decoherence
    """)
    
    # Verify encoding
    if initial_state in ["|0⟩", "|1⟩"]:
        st.markdown("### Encoding Verification")
        
        # Check encoded state
        qc_check = QuantumCircuit(3)
        if initial_state == "|1⟩":
            qc_check.x(0)
        qc_check.cx(0, 1)
        qc_check.cx(0, 2)
        
        state = Statevector.from_instruction(qc_check)
        
        if initial_state == "|0⟩":
            expected_state = "|000⟩"
        else:
            expected_state = "|111⟩"
        
        st.info(f"**Encoded state:** {expected_state}")
        st.write("The logical |0⟩ is encoded as |000⟩ and logical |1⟩ is encoded as |111⟩")
    
    # Store simulation data for PDF report
    from lab_config import LABS
    lab_id = None
    for name, config in LABS.items():
        if config.get('module') == 'bit_flip_code':
            lab_id = config['id']
            break
    
    if lab_id:
        total = sum(counts.values())
        metrics = {
            'Initial State': initial_state,
            'Error Qubit': error_qubit,
            'Number of Shots': str(shots),
        }
        for syndrome, count in counts.items():
            prob = (count / total * 100) if total > 0 else 0
            metrics[f'Syndrome {syndrome}'] = f"{prob:.1f}%"
        
        figures = []
        if show_circuit:
            figures.append(save_figure_to_data(fig_encode, 'Encoding Circuit'))
            figures.append(save_figure_to_data(fig_syndrome, 'Complete Circuit'))
            if error_qubit != "None":
                figures.append(save_figure_to_data(fig_correct, 'Correction Circuit'))
        figures.append(save_figure_to_data(fig_hist, 'Syndrome Measurement Results'))
        
        store_simulation_data(lab_id, metrics=metrics, measurements=counts, figures=figures)
