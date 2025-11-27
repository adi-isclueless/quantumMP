# ==================================================
# Quantum Virtual Lab: Superdense Coding (Streamlit + Qiskit)
# ==================================================

import streamlit as st
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram, circuit_drawer
import matplotlib.pyplot as plt
from certificate import store_simulation_data, save_figure_to_data
from lab_utils import display_formulas

# ==================================================
# FUNCTION: Run Superdense Coding Lab
# ==================================================
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

    st.subheader("1. Message Selection")
    bit_choice = st.radio(
        "Select the 2-bit message Alice wishes to send:",
        ("00", "01", "10", "11"),
        horizontal=True
    )

    st.markdown("""
    **Encoding Scheme:**  
    - 00 → Identity (no gate)  
    - 01 → X gate  
    - 10 → Z gate  
    - 11 → X followed by Z
    """)
    display_formulas(title="Formulas", formulas=[
        r"|\Phi^+\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}}"
    ])

    # ------------------------------------------------
    # Quantum Circuit Setup
    # ------------------------------------------------
    qc = QuantumCircuit(2, 2)

    # Step 1: Create a Bell pair (shared entanglement)
    qc.h(0)
    qc.cx(0, 1)
    qc.barrier()

    # Step 2: Alice encodes her 2-bit message
    if bit_choice == "00":
        pass  # No operation
    elif bit_choice == "01":
        qc.x(0)
    elif bit_choice == "10":
        qc.z(0)
    elif bit_choice == "11":
        qc.x(0)
        qc.z(0)

    qc.barrier()

    # Step 3: Bob performs a Bell basis measurement to decode the message
    qc.cx(0, 1)
    qc.h(0)
    qc.barrier()
    qc.measure([0, 1], [0, 1])

    # ------------------------------------------------
    # Simulation
    # ------------------------------------------------
    backend = AerSimulator()
    job = backend.run(qc, shots=1024)
    result = job.result()
    counts = result.get_counts()
    counts = result.get_counts()

    # ------------------------------------------------
    # Visualization
    # ------------------------------------------------
    st.subheader("2. Quantum Circuit Representation")
    fig_circuit = circuit_drawer(qc, output='mpl', style='iqp', scale=1.3)
    st.pyplot(fig_circuit)

    A, B = st.columns(2)
    st.divider()

    with A:
        st.subheader("3. Measurement Results")
        st.markdown("Bob performs a Bell measurement and decodes Alice’s message.")
        fig1 = plot_histogram(counts)
        st.pyplot(fig1)

    with B:
        st.subheader("4. Theoretical Overview")

        st.markdown("""
            **Process Summary:**
            1. **Entanglement Creation:** Alice and Bob share a Bell state before communication.  
            2. **Encoding:** Alice applies a unitary operation based on her 2-bit message.  
            3. **Transmission:** Alice sends her qubit to Bob.  
            4. **Decoding:** Bob performs a joint Bell measurement to extract the original 2-bit message.  

            This demonstrates that **two classical bits** can be transmitted using **only one qubit**,
            exploiting the pre-shared quantum entanglement between Alice and Bob.
            """)

    # ------------------------------------------------
    # Explanation
    # ------------------------------------------------


    st.success(f"Message successfully transmitted and decoded. Expected measurement result: {bit_choice[::-1]}")
    
    # Store simulation data for PDF report
    from lab_config import LABS
    lab_id = None
    for name, config in LABS.items():
        if config.get('module') == 'supcod':
            lab_id = config['id']
            break
    
    if lab_id:
        total = sum(counts.values())
        metrics = {
            'Message Sent': bit_choice,
            'Expected Result': bit_choice[::-1],
            'Number of Shots': '1024',
        }
        for state, count in counts.items():
            prob = (count / total * 100) if total > 0 else 0
            metrics[f'P({state})'] = f"{prob:.2f}%"
        
        figures = [
            save_figure_to_data(fig_circuit, 'Superdense Coding Circuit'),
            save_figure_to_data(fig1, 'Measurement Results')
        ]
        
        store_simulation_data(lab_id, metrics=metrics, measurements=counts, figures=figures)

    st.caption("Developed with Qiskit and Streamlit • Quantum Virtual Labs © 2025")


# ==================================================
# Standalone Execution
# ==================================================
if __name__ == "__main__":
    run()
