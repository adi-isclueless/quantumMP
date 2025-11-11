import matplotlib.pyplot as plt
import streamlit as st
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import state_fidelity, Statevector
from qiskit.visualization import plot_histogram
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, amplitude_damping_error, phase_damping_error


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
    st.set_page_config(page_title="Bell States and Noise Analysis", layout="wide")
    st.divider()
    
    # Create tabs for different analyses
    tab1, tab2 = st.tabs(["**Bell State Analysis**", "**Noise Effects**"])
    
    # Tab 1: Bell State Analysis
    with tab1:
        st.subheader("Bell State Analysis")
        st.markdown("""
        **Objective:** Prepare all 4 Bell states and show differences in measurement outcomes and correlations.
        """)
        
        colA, colB = st.columns(2)
        with colA:
            state_choice = st.selectbox("Choose Bell State", ["Φ+", "Φ-", "Ψ+", "Ψ-"], key="bell_analysis")
            analyze_all = st.checkbox("Analyze All Bell States", value=False)
        with colB:
            shots = st.number_input("Number of Shots", min_value=128, max_value=20000, value=1000, step=128, key="bell_shots")
            show_correlations = st.checkbox("Show Correlations", value=True)
        
        if analyze_all:
            # Analyze all Bell states
            st.markdown("### All Four Bell States Analysis")
            
            bell_states = ["Φ+", "Φ-", "Ψ+", "Ψ-"]
            all_results = {}
            
            for bell_state in bell_states:
                qc = bell_state_circuit(bell_state)
                qc_measure = qc.copy()
                qc_measure.measure_all()
                
                backend = AerSimulator()
                job = backend.run(qc_measure, shots=shots)
                result = job.result()
                counts = result.get_counts()
                all_results[bell_state] = counts
            
            # Display comparison
            cols = st.columns(4)
            for idx, (bell_state, counts) in enumerate(all_results.items()):
                with cols[idx]:
                    st.markdown(f"### |{bell_state}⟩")
                    fig, ax = plt.subplots(figsize=(3, 2))
                    plot_histogram(counts, ax=ax)
                    st.pyplot(fig)
                    plt.close()
                    
                    # Show expected states
                    if bell_state == "Φ+":
                        expected = ["00", "11"]
                        st.info("Expected: |00⟩, |11⟩")
                    elif bell_state == "Φ-":
                        expected = ["00", "11"]
                        st.info("Expected: |00⟩, |11⟩")
                    elif bell_state == "Ψ+":
                        expected = ["01", "10"]
                        st.info("Expected: |01⟩, |10⟩")
                    else:  # Ψ-
                        expected = ["01", "10"]
                        st.info("Expected: |01⟩, |10⟩")
            
            # Correlation analysis
            if show_correlations:
                st.markdown("### Correlation Analysis")
                st.markdown("""
                **Bell State Correlations:**
                
                | Bell State | Correlation | Measurement Outcomes |
                |------------|-------------|---------------------|
                | |Φ⁺⟩ | Perfect positive | |00⟩ or |11⟩ (same bits) |
                | |Φ⁻⟩ | Perfect positive | |00⟩ or |11⟩ (same bits, different phase) |
                | |Ψ⁺⟩ | Perfect negative | |01⟩ or |10⟩ (opposite bits) |
                | |Ψ⁻⟩ | Perfect negative | |01⟩ or |10⟩ (opposite bits, different phase) |
                
                **Key Property:** Measuring one qubit immediately determines the other qubit's state.
                """)
        else:
            # Single Bell state analysis
            qc = bell_state_circuit(state_choice)
            
            st.markdown(f"### Bell State |{state_choice}⟩ Analysis")
            
            # Show circuit
            with st.expander("Show Quantum Circuit"):
                fig_circuit = qc.draw('mpl', fold=-1)
                st.pyplot(fig_circuit)
                plt.close()
            
            # Ideal statevector
            state_ideal = Statevector.from_instruction(qc)
            ideal_probs = state_ideal.probabilities_dict()
            ideal_counts = {k: int(round(v * shots)) for k, v in ideal_probs.items()}
            
            # Run simulation
            qc_measure = qc.copy()
            qc_measure.measure_all()
            backend = AerSimulator()
            job = backend.run(qc_measure, shots=shots)
            result = job.result()
            counts = result.get_counts()
            
            # Display results
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Measurement Results")
                fig, ax = plt.subplots(figsize=(4, 3))
                plot_histogram(counts, ax=ax)
                st.pyplot(fig)
                plt.close()
                
                # Show probabilities
                total = sum(counts.values())
                for state, count in sorted(counts.items()):
                    prob = count / total
                    st.write(f"P(|{state}⟩) = {prob:.4f}")
            
            with col2:
                st.markdown("### Bell State Properties")
                
                if state_choice == "Φ+":
                    st.markdown("""
                    **|Φ⁺⟩ = (|00⟩ + |11⟩)/√2**
                    
                    - Perfect correlation: both qubits same
                    - Measuring |0⟩ on first → second is |0⟩
                    - Measuring |1⟩ on first → second is |1⟩
                    """)
                elif state_choice == "Φ-":
                    st.markdown("""
                    **|Φ⁻⟩ = (|00⟩ - |11⟩)/√2**
                    
                    - Perfect correlation: both qubits same
                    - Phase difference from |Φ⁺⟩
                    - Same measurement outcomes as |Φ⁺⟩
                    """)
                elif state_choice == "Ψ+":
                    st.markdown("""
                    **|Ψ⁺⟩ = (|01⟩ + |10⟩)/√2**
                    
                    - Perfect anti-correlation: qubits opposite
                    - Measuring |0⟩ on first → second is |1⟩
                    - Measuring |1⟩ on first → second is |0⟩
                    """)
                else:  # Ψ-
                    st.markdown("""
                    **|Ψ⁻⟩ = (|01⟩ - |10⟩)/√2**
                    
                    - Perfect anti-correlation: qubits opposite
                    - Phase difference from |Ψ⁺⟩
                    - Same measurement outcomes as |Ψ⁺⟩
                    """)
                
                # Verify correlations
                if show_correlations:
                    st.markdown("### Correlation Verification")
                    if state_choice in ["Φ+", "Φ-"]:
                        # Should see only 00 and 11
                        expected = {"00", "11"}
                        observed = set(counts.keys())
                        if observed == expected:
                            st.success("Perfect correlation confirmed! Only |00⟩ and |11⟩ observed.")
                        else:
                            st.warning(f"Expected {{00, 11}}, got {observed}")
                    else:  # Ψ+ or Ψ-
                        # Should see only 01 and 10
                        expected = {"01", "10"}
                        observed = set(counts.keys())
                        if observed == expected:
                            st.success("Perfect anti-correlation confirmed! Only |01⟩ and |10⟩ observed.")
                        else:
                            st.warning(f"Expected {{01, 10}}, got {observed}")
    
    # Tab 2: Noise Effects (existing functionality)
    with tab2:
        st.subheader("Noise Effects on Bell States")
        st.markdown("Explore how different noise models affect entanglement in Bell states.")
        
        colA, colB = st.columns(2)
        with colA:
            state_choice_noise = st.selectbox("Choose Bell State", ["Φ+", "Φ-", "Ψ+", "Ψ-"], key="noise_state")
            noise_choice = st.selectbox("Choose Noise Model",
                                        ["None", "Depolarizing", "Amplitude Damping", "Phase Damping"], key="noise_type")
        with colB:
            strength = st.slider("Noise Strength", 0.0, 0.3, 0.05, key="noise_strength")
            shots_noise = st.number_input("Number of Shots", min_value=128, max_value=20000, value=1000, step=128, key="noise_shots")
        
        # Build circuit
        qc = bell_state_circuit(state_choice_noise)

        with st.expander("Show Quantum Circuit"):
            st.pyplot(qc.draw('mpl', fold=-1))
            plt.close()

        # Ideal statevector
        state_ideal = Statevector.from_instruction(qc)
        ideal_probs = state_ideal.probabilities_dict()
        ideal_counts = {k: int(round(v * shots_noise)) for k, v in ideal_probs.items()}

        # Noisy simulation
        if noise_choice != "None":
            noise_model = get_noise_model(noise_choice, strength)
            backend = AerSimulator()
            qc_measure = qc.copy()
            qc_measure.measure_all()

            transpiled = transpile(qc_measure, backend)
            job = backend.run(transpiled, noise_model=noise_model, shots=shots_noise)
            result = job.result()
            counts_noisy = result.get_counts()
        else:
            counts_noisy = ideal_counts

        # Visualization
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
            plt.close()

        with col2:
            st.markdown("Noisy Simulation Results" if noise_choice != "None" else "(No noise: same as ideal)")
            fig2, ax2 = plt.subplots(figsize=(3.5, 2.5))
            plot_histogram(counts_noisy, ax=ax2)
            ax2.set_ylim(0, y_limit)  # same y-limit
            st.pyplot(fig2)
            plt.close()

        st.markdown("### Comparison (Ideal vs Noisy)")
        fig3, ax3 = plt.subplots(figsize=(5, 3))  # smaller combined plot
        plot_histogram([ideal_counts, counts_noisy], legend=['Ideal', 'Noisy'], ax=ax3)
        ax3.set_ylim(0, max(max(ideal_counts.values()), max(counts_noisy.values())) * 1.2)
        st.pyplot(fig3)
        plt.close()

        # Fidelity Calculation
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
