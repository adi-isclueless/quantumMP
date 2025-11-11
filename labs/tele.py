# ===============================================
# Quantum Teleportation Virtual Lab (Streamlit + Qiskit)
# Modular version — ready for multi-lab dashboard integration
# ===============================================

import streamlit as st
from qiskit_aer import AerSimulator
from qiskit import QuantumCircuit
from qiskit.visualization import plot_bloch_multivector, plot_histogram, circuit_drawer
import matplotlib.pyplot as plt
import numpy as np

# ==================================================
# FUNCTION: Run Quantum Teleportation Lab
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

    # -----------------------
    # User Controls
    # -----------------------
    col1, col2 = st.columns([1, 1])
    with col1:
        theta = st.slider("Rotation angle θ (in radians)", 0.0, np.pi, np.pi/3, 0.1)
        phi = st.slider("Phase angle ϕ (in radians)", 0.0, 2*np.pi, np.pi/4, 0.1)
        st.markdown("The initial state prepared by Alice is:")
        st.latex(r"|ψ⟩ = cos(\frac{θ}{2})|0⟩ + e^{iϕ}sin(\frac{θ}{2})|1⟩")

    with col2:
        st.info(" Tip: Use θ and ϕ to change Alice's qubit on the Bloch sphere. "
                "This is the state that will be teleported!")

    # -----------------------
    # Step 1: Initialize Circuit
    # -----------------------
    qc = QuantumCircuit(3, 3)
    qc.ry(theta, 0)
    qc.rz(phi, 0)

    # Step 2: Create entanglement between qubits 1 and 2
    qc.h(1)
    qc.cx(1, 2)

    # Step 3: Bell measurement on qubits 0 and 1
    qc.cx(0, 1)
    qc.h(0)
    qc.barrier()
    qc.measure([0, 1], [0, 1])

    # Step 4: Conditional operations on Bob's qubit (fixed for newer Qiskit)
    qc.barrier()
    with qc.if_test((qc.clbits[1], 1)):
        qc.x(2)
    with qc.if_test((qc.clbits[0], 1)):
        qc.z(2)

    # Step 5: Visualize circuit
    st.subheader(" Quantum Circuit for Teleportation")
    fig_circuit = circuit_drawer(qc, output='mpl', style='iqp', scale=1.3)
    st.pyplot(fig_circuit)
    plt.close()

    # -----------------------
    # Step 6: Simulation
    # -----------------------
    backend = AerSimulator()
    qc.save_statevector()
    shots = 1024
    job = backend.run(qc, shots=shots)
    result = job.result()
    counts = result.get_counts()
    statevector = result.data(0)['statevector']

    # -----------------------
    # Step 7: Visualization
    # -----------------------
    st.divider()
    st.subheader(" Simulation Results")

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("###  Measurement Outcomes (Alice & Bob)")
        fig1 = plot_histogram(counts)
        st.pyplot(fig1)
        plt.close()

    with col4:
        st.markdown("###  Final State (Bloch Sphere of Bob's Qubit)")
        bloch_fig = plot_bloch_multivector(statevector)
        st.pyplot(bloch_fig)
        plt.close()

    # -----------------------
    # Step 8: Explanation
    # -----------------------
    st.divider()
    st.subheader("Step-by-Step Explanation")

    st.markdown("""
    1️⃣ **Alice** prepares a random quantum state |ψ⟩ on qubit 0.  
    2️⃣ **Alice & Bob** share an **entangled pair** (qubits 1 & 2).  
    3️⃣ Alice performs a **Bell measurement** on her two qubits.  
    4️⃣ Alice sends the **classical bits** (measurement results) to Bob.  
    5️⃣ **Bob** applies **conditional gates (X/Z)** based on those bits.  
    6️⃣ Bob's qubit now exactly matches Alice's original state |ψ⟩ —  
    without any physical transmission of the qubit itself!
    """)

    st.success("Quantum teleportation complete — Bob's qubit successfully receives Alice's state!")

    st.caption("Powered by Qiskit • Developed with Streamlit • © Quantum Virtual Labs 2025")

