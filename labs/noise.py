import matplotlib.pyplot as plt
import streamlit as st
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import state_fidelity, Statevector
from qiskit.visualization import plot_histogram
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, amplitude_damping_error, phase_damping_error


def run():
    # ----------------------------
    # Function to prepare Bell states
    # ----------------------------
    def bell_state_circuit(state_name: str) -> QuantumCircuit:
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)

        if state_name == "Φ-":
            qc.z(0)
        elif state_name == "Ψ+":
            qc.x(1)
        elif state_name == "Ψ-":
            qc.x(1)
            qc.z(0)

        return qc


    # ----------------------------
    # Function to add noise
    # ----------------------------
    def get_noise_model(noise_type, strength):
        noise_model = NoiseModel()
        if noise_type == "Depolarizing":
            noise_model.add_all_qubit_quantum_error(depolarizing_error(strength, 1), ['h', 'x', 'z'])
            noise_model.add_all_qubit_quantum_error(depolarizing_error(2 * strength, 2), ['cx'])
        elif noise_type == "Amplitude Damping":
            noise_model.add_all_qubit_quantum_error(amplitude_damping_error(strength), ['h', 'x', 'z'])
        elif noise_type == "Phase Damping":
            noise_model.add_all_qubit_quantum_error(phase_damping_error(strength), ['h', 'x', 'z'])
        return noise_model


    # ----------------------------
    # Streamlit UI
    # ----------------------------
    st.set_page_config(page_title="Quantum Noise on Bell States", layout="wide")

    st.title("Quantum Noise Effect on Bell States")
    st.markdown(
        """
        Explore how different noise models affect entanglement in Bell states.  
        """
    )    

    colA, colB = st.columns(2)
    with colA:
        state_choice = st.selectbox("Choose Bell State", ["Φ+", "Φ-", "Ψ+", "Ψ-"])
        noise_choice = st.selectbox("Choose Noise Model",
                                    ["None", "Depolarizing", "Amplitude Damping", "Phase Damping"])
    with colB:
        strength = st.slider("Noise Strength", 0.0, 0.3, 0.05)
        shots = st.number_input("Number of Shots", min_value=128, max_value=20000, value=1000, step=128)

    # ----------------------------
    # Build circuit
    # ----------------------------
    qc = bell_state_circuit(state_choice)

    with st.expander("Show Quantum Circuit"):
        st.pyplot(qc.draw('mpl', fold=-1))  # smaller, compact circuit

    # Ideal statevector
    state_ideal = Statevector.from_instruction(qc)
    ideal_probs = state_ideal.probabilities_dict()
    ideal_counts = {k: int(round(v * shots)) for k, v in ideal_probs.items()}

    # Noisy simulation
    if noise_choice != "None":
        noise_model = get_noise_model(noise_choice, strength)
        backend = AerSimulator()
        qc_measure = qc.copy()
        qc_measure.measure_all()

        transpiled = transpile(qc_measure, backend)
        job = backend.run(transpiled, noise_model=noise_model, shots=shots)
        result = job.result()
        counts_noisy = result.get_counts()
    else:
        counts_noisy = ideal_counts

# ----------------------------
# Visualization
# ----------------------------
    st.subheader("Measurement Results")
    col1, col2 = st.columns(2)

# Determine max count for scaling
    max_count = max(max(ideal_counts.values()), max(counts_noisy.values()))
    y_limit = max_count * 1.2  # 10% padding above the tallest bar

    with col1:
        st.markdown("Ideal Probabilities")
        fig1, ax1 = plt.subplots(figsize=(3.5, 2.5))
        plot_histogram(ideal_counts, ax=ax1)
        ax1.set_ylim(0, y_limit)  # set same y-limit
        st.pyplot(fig1)

    with col2:
        st.markdown("Noisy Simulation Results" if noise_choice != "None" else "(No noise: same as ideal)")
        fig2, ax2 = plt.subplots(figsize=(3.5, 2.5))
        plot_histogram(counts_noisy, ax=ax2)
        ax2.set_ylim(0, y_limit)  # same y-limit
        st.pyplot(fig2)


    st.markdown("### Comparison (Ideal vs Noisy)")
    fig3, ax3 = plt.subplots(figsize=(5, 3))  # smaller combined plot
    plot_histogram([ideal_counts, counts_noisy], legend=['Ideal', 'Noisy'], ax=ax3)
    ax3.set_ylim(0, max(max(ideal_counts.values()), max(counts_noisy.values())) * 1.2)
    st.pyplot(fig3)


# ----------------------------
# Fidelity Calculation
# ----------------------------
    st.subheader("Fidelity (Entanglement Quality)")

    if noise_choice != "None":
        try:
            backend_dm = AerSimulator(method='density_matrix')
            qc_dm = qc.copy()
            qc_dm.save_density_matrix(label='rho')
            transpiled_dm = transpile(qc_dm, backend_dm)

            job_dm = backend_dm.run(transpiled_dm, noise_model=noise_model)
            result_dm = job_dm.result()
            data0 = result_dm.data(0)

            rho = None
            for key in ('rho', 'density_matrix', 'density_matrix_0'):
                if key in data0:
                    rho = data0[key]
                    break

            if rho is None:
                st.warning("Couldn't extract density matrix; fidelity unavailable for this Qiskit version.")
            else:
                fid = state_fidelity(state_ideal, rho)
                st.metric("Fidelity (Ideal vs Noisy)", f"{fid:.4f}")
        except Exception as e:
            st.error(f"Density-matrix fidelity calculation failed: {e}")
    else:
        st.metric("Fidelity (Ideal vs Ideal)", "1.0000")
