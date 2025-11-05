import streamlit as st
from labs import noise, different_states, bb84, random, parity, tomography, tele, supcod

st.set_page_config(page_title="Quantum Virtual Labs", layout="wide")

st.sidebar.title("Quantum Virtual Labs")
choice = st.sidebar.radio(
    "Select a Lab",
    [
        "Home",
        "Measurement in Different Bases",
        "Random Number Generator",
        "Parity Check with Ancilla Qubit",
        "Effect of Noise on Bell States",
        "BB84 Quantum Key Distribution",
        "Superdense Coding",
        "Teleportation of a Quantum State",
        "Tomography of Quantum States"
    ]
)

# -------------------------------
# Home Page
# -------------------------------
if choice == "Home":
    st.title("Quantum Virtual Labs")
    st.markdown("""
    **Vivekanand Education Society's Institute of Technology, Mumbai**

    ---
    #### About the Platform  
    The **Quantum Virtual Labs** initiative is a student-developed environment designed to make
    quantum computing concepts **intuitive and visual** through interactive simulations.  
    Each lab combines **Qiskit** for simulation and **Streamlit** for real-time visualization.

    **Objectives:**
    - Provide an accessible introduction to **quantum principles and measurements**  
    - Demonstrate **entanglement, superposition, and quantum protocols**  
    - Encourage experimentation with **quantum communication and error analysis**

    ---
    #### Logical Lab Flow
    1. **Quantum Foundations**  
       - Measurement in Different Bases  
       - Random Number Generator  

    2. **Quantum Logic & Operations**  
       - Parity Check with Ancilla Qubit  

    3. **Quantum Entanglement & Noise**  
       - Effect of Noise on Bell States  

    4. **Quantum Communication Protocols**  
       - BB84 Quantum Key Distribution  
       - Superdense Coding  
       - Teleportation of a Quantum State  

    5. **Quantum State Characterization**  
       - Tomography of Quantum States  

    ---
    #### Technical Stack
    - **Frontend:** Streamlit  
    - **Backend:** Qiskit (Aer Simulator)  
    - **Language:** Python  
    - **Visualization:** Matplotlib, Plotly  

    ---
    #### Vision
    > “To create a unified, accessible platform that enables students and educators to
    explore quantum phenomena through simulation, experimentation, and visualization.”


    © 2025 Quantum Virtual Labs • Developed at VESIT""")

# -------------------------------
# Lab Routing
# -------------------------------
elif choice == "Measurement in Different Bases":
    different_states.run()
elif choice == "Random Number Generator":
    random.run()
elif choice == "Parity Check with Ancilla Qubit":
    parity.run()
elif choice == "Effect of Noise on Bell States":
    noise.run()
elif choice == "BB84 Quantum Key Distribution":
    bb84.run()
elif choice == "Superdense Coding":
    supcod.run()
elif choice == "Teleportation of a Quantum State":
    tele.run()
elif choice == "Tomography of Quantum States":
    tomography.run()
