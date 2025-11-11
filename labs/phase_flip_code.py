"""
3-Qubit Phase Flip Code Lab
Extend bit-flip code to detect phase errors in |+⟩/|−⟩ basis
"""

import streamlit as st
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_histogram
from qiskit_aer import AerSimulator
import matplotlib.pyplot as plt

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
        initial_state = st.selectbox("Initial State to Encode", ["|+⟩", "|-⟩", "|0⟩", "|1⟩"], index=0)
        error_qubit = st.selectbox("Apply Phase-Flip Error to Qubit", ["None", "0", "1", "2"], index=0)
    with col2:
        shots = st.slider("Number of Shots", 100, 5000, 1024, 100)
        show_circuit = st.checkbox("Show Circuit Diagram", value=True)
        show_comparison = st.checkbox("Compare with Bit-Flip Code", value=True)
    
    st.divider()
    
    X, Y = st.columns(2)
    with X:
        st.subheader("Phase Flip Code Concept")
        st.markdown("""
        **Phase Flip Code:**
        
        The phase flip code is similar to the bit-flip code, but works in the |+⟩/|−⟩ basis instead of |0⟩/|1⟩ basis.
        
        **Encoding:**
        - Logical |0⟩ is encoded as |+++⟩ = (|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2
        - Logical |1⟩ is encoded as |---⟩ = (|0⟩-|1⟩)/√2 ⊗ (|0⟩-|1⟩)/√2 ⊗ (|0⟩-|1⟩)/√2
        
        **Error Detection:**
        - Phase flip (Z gate) errors can be detected by measuring in X basis
        - Syndrome measurement uses Hadamard basis measurements with ancilla qubits
        """)
        st.subheader("Syndrome Measurement (Error Detection)")
        st.markdown("""
        **Syndrome Measurement in X Basis:**
        - Convert to X basis using Hadamard gates
        - Measure parity using ancilla qubits
        - Syndrome bit 0: parity of qubits 0 and 1 in X basis
        - Syndrome bit 1: parity of qubits 0 and 2 in X basis
        """)

    # Explanation
    
    
    # Encoding circuit
    
    
    # Create encoding circuit with ancilla qubits
    # Qubits 0-2: data qubits, Qubits 3-4: ancilla for syndrome
    qc_encode = QuantumCircuit(5, 2)  # 5 qubits (3 data + 2 ancilla), 2 classical bits
    
    # Prepare initial state in computational basis
    if initial_state == "|+⟩":
        qc_encode.h(0)  # |+⟩ = H|0⟩
    elif initial_state == "|-⟩":
        qc_encode.x(0)
        qc_encode.h(0)  # |-⟩ = HX|0⟩
    elif initial_state == "|0⟩":
        pass  # |0⟩
    elif initial_state == "|1⟩":
        qc_encode.x(0)  # |1⟩
    
    # Encoding to create |ψψψ⟩ in X basis
    # CNOT gates in computational basis
    qc_encode.cx(0, 1)
    qc_encode.cx(0, 2)
    
    # Now convert all to X basis (creates |+++⟩ or |---⟩)
    qc_encode.h(0)
    qc_encode.h(1)
    qc_encode.h(2)
    
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
        qc_error.z(error_idx)  # Phase flip error
        qc_error.barrier()
        st.info(f"Phase-flip error (Z gate) applied to qubit {error_idx}")
    
    # Syndrome measurement (error detection)
    
    
    qc_syndrome = qc_error.copy()
    
    # Convert from X basis to computational basis for syndrome measurement
    qc_syndrome.h(0)
    qc_syndrome.h(1)
    qc_syndrome.h(2)
    qc_syndrome.barrier()
    
    # Syndrome measurement using ancilla qubits (now in computational basis)
    # Ancilla qubit 3: measures parity of qubits 0 and 1 → classical bit 1
    qc_syndrome.cx(0, 3)
    qc_syndrome.cx(1, 3)
    qc_syndrome.measure(3, 1)  # Changed from 0 to 1
    
    # Ancilla qubit 4: measures parity of qubits 0 and 2 → classical bit 0
    qc_syndrome.cx(0, 4)
    qc_syndrome.cx(2, 4)
    qc_syndrome.measure(4, 0)  # Changed from 1 to 0
    
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
        
        # Determine error location
        if error_qubit == "None":
            st.success("**No Error Applied**")
            st.info("""
            **Expected:** Syndrome 00 (no error detected)
            - All qubits should be in the same state in X basis
            - Parity checks should agree
            """)
        else:
            error_idx = int(error_qubit)
            st.warning(f"**Error Applied to Qubit {error_idx}**")
            
            # Syndrome interpretation - CORRECTED MAPPING
            # Note: Qiskit displays bits in little-endian (rightmost is c0)
            # Ancilla 3 measures to c1, Ancilla 4 measures to c0
            if error_idx == 0:
                expected_syndrome = "11"
                st.info("""
                **Expected Syndrome:** 11
                - Qubit 0 has phase error
                - Both parity checks (q0⊕q1 and q0⊕q2) detect the error
                - c1=1, c0=1 → displayed as "11"
                """)
            elif error_idx == 1:
                expected_syndrome = "10"
                st.info("""
                **Expected Syndrome:** 10 (displayed as c1c0)
                - Qubit 1 has phase error
                - First parity check (q0⊕q1) detects it → c1=1
                - Second parity check (q0⊕q2) passes → c0=0
                - c1=1, c0=0 → displayed as "10"
                """)
            else:  # error_idx == 2
                expected_syndrome = "01"
                st.info("""
                **Expected Syndrome:** 01 (displayed as c1c0)
                - Qubit 2 has phase error
                - Second parity check (q0⊕q2) detects it → c0=1
                - First parity check (q0⊕q1) passes → c1=0
                - c1=0, c0=1 → displayed as "01"
                """)
            
            # Check if we got the expected syndrome
            expected_count = counts.get(expected_syndrome, 0)
            if expected_count / total > 0.9:
                st.success(f"Phase error correctly detected! Syndrome {expected_syndrome} observed in {expected_count/total*100:.1f}% of cases.")
            else:
                st.warning(f"Expected syndrome {expected_syndrome}, but got different results.")
    
    # Error correction
    st.divider()
    st.subheader("Error Correction")
    
    st.markdown("""
    **Error Correction Process:**
    
    1. **Detect Error**: Use syndrome measurement to identify which qubit has the phase error
    2. **Correct Error**: Apply Z gate to the corrupted qubit
    3. **Verify**: Measure to confirm correction
    
    **Syndrome to Correction Mapping:**
    - Syndrome 00: No error → No correction needed
    - Syndrome 01: Error on qubit 2 → Apply Z to qubit 2
    - Syndrome 10: Error on qubit 1 → Apply Z to qubit 1
    - Syndrome 11: Error on qubit 0 → Apply Z to qubit 0
    
    Note: Syndromes are displayed as c1c0 (leftmost bit is c1, rightmost is c0)
    """)
    
    if error_qubit != "None":
        st.markdown("### Correction Circuit")
        
        # Create correction circuit
        qc_correct = qc_error.copy()
        
        # Convert from X basis to computational basis
        qc_correct.h(0)
        qc_correct.h(1)
        qc_correct.h(2)
        
        # Syndrome measurement using ancilla qubits
        qc_correct.cx(0, 3)
        qc_correct.cx(1, 3)
        qc_correct.measure(3, 1)  # Changed from 0 to 1
        
        qc_correct.cx(0, 4)
        qc_correct.cx(2, 4)
        qc_correct.measure(4, 0)  # Changed from 1 to 0
        qc_correct.barrier()
        
        # Conditional correction based on measured syndrome
        c0 = qc_correct.clbits[0]
        c1 = qc_correct.clbits[1]
        
        # Syndrome 01 → error on qubit 2 (c0=0, c1=1)
        with qc_correct.if_test((c1, 1)):
            qc_correct.z(2)

        # Syndrome 10 → error on qubit 1 (c0=1, c1=0)
        with qc_correct.if_test((c0, 1)):
            qc_correct.z(1)

        # Syndrome 11 → error on qubit 0
        with qc_correct.if_test((c0, 1)):
            with qc_correct.if_test((c1, 1)):
                qc_correct.z(0)
        
        # Convert back to X basis
        qc_correct.h(0)
        qc_correct.h(1)
        qc_correct.h(2)
        
        if show_circuit:
            fig_correct = qc_correct.draw(output='mpl', fold=-1)
            st.pyplot(fig_correct)
            plt.close()
        
        st.info("""
        **Note:** The correction circuit applies Z gates conditionally based on the syndrome measurement.
        In a real quantum computer, this would require mid-circuit measurement and conditional operations.
        """)
    
    # Comparison with bit-flip code
    if show_comparison:
        st.divider()
        st.subheader("Phase Flip Code vs Bit Flip Code")
        
        comparison_data = {
            "Property": [
                "Basis",
                "Encoded |0⟩",
                "Encoded |1⟩",
                "Error Type Detected",
                "Error Gate",
                "Syndrome Basis",
                "Correction Gate"
            ],
            "Bit-Flip Code": [
                "Computational (Z)",
                "|000⟩",
                "|111⟩",
                "Bit flip (X)",
                "X",
                "Z basis",
                "X"
            ],
            "Phase-Flip Code": [
                "Hadamard (X)",
                "|+++⟩",
                "|---⟩",
                "Phase flip (Z)",
                "Z",
                "X basis",
                "Z"
            ]
        }
        
        st.table(comparison_data)
        
        st.markdown("""
        **Key Differences:**
        
        1. **Basis**: Bit-flip code works in computational basis, phase-flip code works in Hadamard basis
        
        2. **Errors Detected**: 
           - Bit-flip code detects X errors
           - Phase-flip code detects Z errors
        
        3. **Duality**: The codes are dual to each other via Hadamard transformation
        
        4. **Combined**: Shor code combines both to detect both bit and phase errors
        """)
    
    # Analysis
    st.divider()
    st.subheader("Phase Flip Code Analysis")
    
    st.markdown("""
    **Key Properties:**
    
    1. **Error Detection**: Can detect single phase-flip (Z) errors on any of the three qubits
    
    2. **Error Correction**: Can correct single phase-flip errors by applying Z gate to the corrupted qubit
    
    3. **Basis Transformation**: Works by encoding in X basis (|+⟩/|-⟩) instead of Z basis (|0⟩/|1⟩)
    
    4. **Limitations**: 
       - Cannot detect/correct bit-flip errors
       - Cannot correct multiple errors
       - Requires three physical qubits for one logical qubit
    
    5. **Syndrome Table:**
       | Syndrome | Error Location | Correction |
       |----------|----------------|------------|
       | 00       | None           | None       |
       | 01       | Qubit 2        | Z on 2     |
       | 10       | Qubit 1        | Z on 1     |
       | 11       | Qubit 0        | Z on 0     |
       
       Note: Syndromes displayed as c1c0 (little-endian notation)
    
    **Applications:**
    - Quantum error correction for phase errors
    - Protecting quantum information from phase decoherence
    - Building blocks for more complex codes (e.g., Shor code)
    """)
    
    # Mathematical explanation
    st.markdown("### Mathematical Explanation")
    
    st.markdown("""
    **Phase Flip Code in X Basis:**
    
    The phase flip code encodes logical states as:
    
    - |0⟩_L = |+++⟩ = (|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2
    - |1⟩_L = |---⟩ = (|0⟩-|1⟩)/√2 ⊗ (|0⟩-|1⟩)/√2 ⊗ (|0⟩-|1⟩)/√2
    
    **Why it works:**
    - Phase flip (Z) in computational basis becomes bit flip in X basis
    - Z|+⟩ = |-⟩ and Z|-⟩ = |+⟩
    - So detecting phase errors is equivalent to detecting bit errors in X basis
    - The syndrome measurement is done in X basis using Hadamard gates
    - Ancilla qubits are used to measure parity without destroying the data qubits
    """)
