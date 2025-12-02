import streamlit as st
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_histogram, plot_bloch_multivector
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
    A, B = st.columns(2)
    with A:
        st.markdown("""
        **States:**  
        - |+⟩ = (|0⟩ + |1⟩) / √2  
        - |i⟩ = (|0⟩ + i|1⟩) / √2 
        """)
        display_formulas(title="Formulas", formulas=[
            r"|+\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}}",
            r"|i\rangle = \frac{|0\rangle + i|1\rangle}{\sqrt{2}}"
        ])
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
    
    # Store simulation data for PDF report
    from lab_config import LABS
    lab_id = None
    for name, config in LABS.items():
        if config.get('module') == 'different_states':
            lab_id = config['id']
            break
    
    if lab_id:
        # Clear any existing simulation data for this lab to prevent stale figures
        if "lab_simulation_data" in st.session_state and lab_id in st.session_state.lab_simulation_data:
            st.session_state.lab_simulation_data[lab_id] = {
                "metrics": {},
                "measurements": {},
                "figures": []
            }
        
        # Calculate probabilities
        total = sum(counts.values())
        metrics = {
            'State': state_choice,
            'Measurement Basis': basis_choice,
            'Number of Shots': str(shots),
        }
        for state, count in counts.items():
            prob = (count / total * 100) if total > 0 else 0
            metrics[f'P(|{state}⟩)'] = f"{prob:.2f}%"
        
        # Generate comprehensive measurement data for both states in all bases
        all_figures = [
            save_figure_to_data(bloch_fig, f'Bloch Sphere - {state_choice} State'),
            save_figure_to_data(hist_fig, f'Measurement Results in {basis_choice}-basis'),
            save_figure_to_data(circ_fig, 'Quantum Circuit')
        ]
        
        # Add measurements for |+> state in all three bases
        for basis in ['Z', 'X', 'Y']:
            qc_plus = QuantumCircuit(1)
            qc_plus.h(0)
            meas_plus = qc_plus.copy()
            if basis == 'X':
                meas_plus.h(0)
            elif basis == 'Y':
                meas_plus.sdg(0)
                meas_plus.h(0)
            meas_plus.measure_all()
            
            job_plus = backend.run(meas_plus, shots=shots)
            counts_plus = job_plus.result().get_counts()
            
            # Create a new figure explicitly for each plot
            fig_plus = plt.figure(figsize=(8, 6))
            hist_plus = plot_histogram(counts_plus, figsize=(8, 6))
            all_figures.append(save_figure_to_data(hist_plus, f'|+⟩ State measured in {basis}-basis'))
            plt.close(hist_plus)
            plt.close(fig_plus)
        
        # Add measurements for |i> state in all three bases
        for basis in ['Z', 'X', 'Y']:
            qc_i = QuantumCircuit(1)
            qc_i.h(0)
            qc_i.s(0)
            meas_i = qc_i.copy()
            if basis == 'X':
                meas_i.h(0)
            elif basis == 'Y':
                meas_i.sdg(0)
                meas_i.h(0)
            meas_i.measure_all()
            
            job_i = backend.run(meas_i, shots=shots)
            counts_i = job_i.result().get_counts()
            
            # Create a new figure explicitly for each plot
            fig_i = plt.figure(figsize=(8, 6))
            hist_i = plot_histogram(counts_i, figsize=(8, 6))
            all_figures.append(save_figure_to_data(hist_i, f'|i⟩ State measured in {basis}-basis'))
            plt.close(hist_i)
            plt.close(fig_i)
        
        # Store all the simulation data
        store_simulation_data(lab_id, metrics=metrics, measurements=counts, figures=all_figures)
        
        # Debug: Confirm data was stored
        st.success(f"✅ Stored {len(all_figures)} figures for report generation")
        
        # Close figures to free memory and prevent duplicates
        plt.close(bloch_fig)
        plt.close(hist_fig)
        plt.close(circ_fig)
  
