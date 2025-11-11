import streamlit as st
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_histogram, plot_bloch_multivector
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
    A, B = st.columns(2)
    with A:
        st.markdown("""
        **States:**  
        - |+⟩ = (|0⟩ + |1⟩) / √2  
        - |i⟩ = (|0⟩ + i|1⟩) / √2 
        """)
    with B:
        st.markdown(""" 
        **Measurement Bases:**  
        - Z → |0⟩, |1⟩  
        - X → |+⟩, |−⟩  
        - Y → |+i⟩, |−i⟩
        """)


    # --- user controls ---
    col1, col2, col3 = st.columns(3)
    with col1:
        state_choice = st.selectbox("Select State", ["|+>", "|i>"])
    with col2:
        basis_choice = st.selectbox("Select Measurement Basis", ["Z", "X", "Y"])
    with col3:
        shots = st.slider("Number of Shots", 100, 5000, 1024, step=100)

    # --- create the quantum circuit based on chosen state ---
    qc = QuantumCircuit(1)
    if state_choice == "|+>":
        qc.h(0)
    elif state_choice == "|i>":
        qc.h(0)
        qc.s(0)

    # --- Apply transformations for chosen measurement basis ---
    meas_circ = qc.copy()
    if basis_choice == "X":
        meas_circ.h(0)
    elif basis_choice == "Y":
        meas_circ.sdg(0)
        meas_circ.h(0)
    meas_circ.measure_all()

    # --- run simulation ---
    backend = AerSimulator(method='density_matrix')
    job = backend.run(meas_circ, shots=shots)
    counts = job.result().get_counts()

    # --- layout: Bloch sphere + results side by side ---
    st.markdown("### Visualization")
    colA, colB = st.columns([1,1])

    with colA:
        st.markdown(" ")
        st.markdown(" ")
        st.markdown(" ")
        st.subheader("Initial State (Bloch Sphere)")
        state = Statevector.from_instruction(qc)
        bloch_fig = plot_bloch_multivector(state)
        bloch_fig.set_size_inches(3, 3)
        st.pyplot(bloch_fig)

    with colB:
        st.subheader(f"Measurement Results in {basis_choice}-basis ({shots} shots)")
        hist_fig = plot_histogram(counts)
        st.pyplot(hist_fig)
        st.subheader("Quantum Circuit Used for Measurement")
        circ_fig = meas_circ.draw(output="mpl")
        st.pyplot(circ_fig)
    # --- display circuit below ---
  
