import streamlit as st
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector, DensityMatrix
from qiskit.visualization import plot_bloch_multivector
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from io import BytesIO
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


    # Initialize session state
    if 'measurements_done' not in st.session_state:
        st.session_state.measurements_done = False
        st.session_state.results = None

    # State preparation section
    st.header("1. State Preparation")
    col1, col2 = st.columns(2)

    with col1:
        state_type = st.selectbox(
            "Select quantum state",
            ["|0⟩", "|1⟩", "|+⟩", "|-⟩", "|i⟩", "|-i⟩", "Custom angles"]
        )

    with col2:
        shots = st.slider("Number of measurement shots", 100, 10000, 1000, 100)

    if state_type == "Custom angles":
        col1, col2 = st.columns(2)
        with col1:
            theta = st.slider("Theta (angle)", 0.0, np.pi, np.pi / 4, 0.1)
        with col2:
            phi = st.slider("Phi (phase)", 0.0, 2 * np.pi, 0.0, 0.1)
    else:
        theta = 0.0
        phi = 0.0

    def create_state_circuit(state_type, theta=0, phi=0):
        """Create a quantum circuit for the desired state"""
        qc = QuantumCircuit(1)

        if state_type == "|0⟩":
            # Ground state, no operation needed
            pass
        elif state_type == "|1⟩":
            qc.x(0)
        elif state_type == "|+⟩":
            # |+⟩ = (|0⟩ + |1⟩)/√2
            qc.h(0)
        elif state_type == "|-⟩":
            # |-⟩ = (|0⟩ - |1⟩)/√2
            qc.x(0)
            qc.h(0)
        elif state_type == "|i⟩":
            # |i⟩ = (|0⟩ + i|1⟩)/√2
            qc.h(0)
            qc.s(0)
        elif state_type == "|-i⟩":
            # |-i⟩ = (|0⟩ - i|1⟩)/√2
            qc.h(0)
            qc.sdg(0)
        elif state_type == "Custom angles":
            qc.ry(theta)(0)
            qc.rz(phi)(0)

        return qc

    def measure_in_basis(state_circuit, basis, shots):
        """Measure the state in a specific basis"""
        qc = state_circuit.copy()
        qc.add_register(ClassicalRegister(1))

        if basis == 'X':
            qc.h(0)
        elif basis == 'Y':
            qc.sdg(0)
            qc.h(0)

        qc.measure(0, 0)

        simulator = AerSimulator()
        job = simulator.run(qc, shots=shots)
        result = job.result()
        counts = result.get_counts()

        return counts

    def perform_tomography(state_circuit, shots):
        """Perform quantum state tomography"""
        bases = ['Z', 'X', 'Y']
        measurements = {}

        for basis in bases:
            counts = measure_in_basis(state_circuit, basis, shots)
            measurements[basis] = counts

        return measurements

    def reconstruct_state(measurements, shots):
        """Reconstruct density matrix from measurements"""
        # Get expectation values
        exp_z = (measurements['Z'].get('0', 0) - measurements['Z'].get('1', 0)) / shots
        exp_x = (measurements['X'].get('0', 0) - measurements['X'].get('1', 0)) / shots
        exp_y = (measurements['Y'].get('0', 0) - measurements['Y'].get('1', 0)) / shots

        # Reconstruct density matrix: rho = (I + r·σ) / 2
        rho = np.array([
            [0.5 + 0.5 * exp_z, 0.5 * (exp_x - 1j * exp_y)],
            [0.5 * (exp_x + 1j * exp_y), 0.5 - 0.5 * exp_z]
        ])

        return rho, (exp_x, exp_y, exp_z)

    def create_city_tower_plot(measurements, shots, basis_name):
        """Create 3D city tower visualization for measurement outcomes"""
        outcomes = ['0', '1']
        counts = [measurements.get('0', 0), measurements.get('1', 0)]
        probs = [c / shots for c in counts]

        x_pos = [0, 1]
        y_pos = [0, 0]
        z_pos = [0, 0]

        dx = [0.6, 0.6]
        dy = [0.6, 0.6]
        dz = probs

        colors = ['rgba(0, 100, 200, 0.8)', 'rgba(200, 50, 50, 0.8)']

        fig = go.Figure()

        for i in range(len(outcomes)):
            fig.add_trace(go.Mesh3d(
                x=[x_pos[i], x_pos[i], x_pos[i] + dx[i], x_pos[i] + dx[i],
                   x_pos[i], x_pos[i], x_pos[i] + dx[i], x_pos[i] + dx[i]],
                y=[y_pos[i], y_pos[i] + dy[i], y_pos[i] + dy[i], y_pos[i],
                   y_pos[i], y_pos[i] + dy[i], y_pos[i] + dy[i], y_pos[i]],
                z=[z_pos[i], z_pos[i], z_pos[i], z_pos[i],
                   z_pos[i] + dz[i], z_pos[i] + dz[i], z_pos[i] + dz[i], z_pos[i] + dz[i]],
                i=[0, 0, 0, 0, 1, 1, 2, 2, 4, 4],
                j=[1, 2, 4, 1, 2, 5, 3, 6, 5, 6],
                k=[2, 3, 5, 5, 6, 6, 7, 7, 6, 7],
                color=colors[i],
                opacity=0.8,
                name=f'|{outcomes[i]}⟩'
            ))

        fig.update_layout(
            title=f"{basis_name}-basis Measurements",
            scene=dict(
                xaxis=dict(title='Outcome', tickvals=[0.3, 1.3], ticktext=['|0⟩', '|1⟩']),
                yaxis=dict(title='', showticklabels=False, range=[-0.5, 1]),
                zaxis=dict(title='Probability', range=[0, 1]),
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
            ),
            height=400,
            showlegend=True
        )

        return fig

    def matrix_sqrt(matrix):
        """Compute matrix square root using eigendecomposition"""
        eigenvalues, eigenvectors = np.linalg.eigh(matrix)
        sqrt_eigenvalues = np.sqrt(eigenvalues.astype(complex))
        return eigenvectors @ np.diag(sqrt_eigenvalues) @ eigenvectors.conj().T

    def bloch_vector_to_statevector(bloch_vector):
        """Convert Bloch vector to statevector for visualization"""
        x, y, z = bloch_vector

        # Calculate theta and phi from Bloch vector
        r = np.sqrt(x ** 2 + y ** 2 + z ** 2)
        if r < 1e-10:
            theta = 0
            phi = 0
        else:
            theta = np.arccos(z / r) if r > 1e-10 else 0
            phi = np.arctan2(y, x)

        # Create statevector: |ψ⟩ = cos(θ/2)|0⟩ + e^(iφ)sin(θ/2)|1⟩
        alpha = np.cos(theta / 2)
        beta = np.exp(1j * phi) * np.sin(theta / 2)

        return Statevector([alpha, beta])

    # Run tomography button
    if st.button("Run Quantum State Tomography", type="primary"):
        state_circuit = create_state_circuit(state_type, theta, phi)

        with st.spinner("Performing measurements in X, Y, and Z bases..."):
            measurements = perform_tomography(state_circuit, shots)
            rho_reconstructed, bloch_vec = reconstruct_state(measurements, shots)

            # Get theoretical state
            theoretical_state = Statevector(state_circuit)
            theoretical_rho = DensityMatrix(theoretical_state)

            st.session_state.measurements_done = True
            st.session_state.results = {
                'measurements': measurements,
                'rho_reconstructed': rho_reconstructed,
                'bloch_vec': bloch_vec,
                'theoretical_state': theoretical_state,
                'theoretical_rho': theoretical_rho,
                'state_circuit': state_circuit
            }

    # Display results
    if st.session_state.measurements_done:
        results = st.session_state.results

        st.header("2. Measurement Results")

        # City tower visualizations
        col1, col2, col3 = st.columns(3)

        with col1:
            fig_z = create_city_tower_plot(results['measurements']['Z'], shots, 'Z')
            st.plotly_chart(fig_z, use_container_width=True)

        with col2:
            fig_x = create_city_tower_plot(results['measurements']['X'], shots, 'X')
            st.plotly_chart(fig_x, use_container_width=True)

        with col3:
            fig_y = create_city_tower_plot(results['measurements']['Y'], shots, 'Y')
            st.plotly_chart(fig_y, use_container_width=True)

        st.header("3. State Reconstruction")

        # Bloch spheres comparison
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Theoretical State")
            fig_theo = plot_bloch_multivector(results['theoretical_state'])
            buf = BytesIO()
            fig_theo.savefig(buf, format='png', bbox_inches='tight', dpi=150)
            buf.seek(0)
            st.image(buf, use_container_width=True)
            plt.close(fig_theo)

            theo_sv = results['theoretical_state'].data
            st.write("Theoretical amplitudes:")
            st.write(f"α (|0⟩): {theo_sv[0]:.4f}")
            st.write(f"β (|1⟩): {theo_sv[1]:.4f}")

        with col2:
            st.subheader("Reconstructed State")
            bloch_x, bloch_y, bloch_z = results['bloch_vec']

            # Convert Bloch vector to statevector for consistent visualization
            reconstructed_statevector = bloch_vector_to_statevector((bloch_x, bloch_y, bloch_z))
            fig_reco = plot_bloch_multivector(reconstructed_statevector)
            buf = BytesIO()
            fig_reco.savefig(buf, format='png', bbox_inches='tight', dpi=150)
            buf.seek(0)
            st.image(buf, use_container_width=True)
            plt.close(fig_reco)

            # Calculate amplitudes from density matrix
            rho = results['rho_reconstructed']
            st.write("Reconstructed amplitudes (from density matrix):")
            st.write(f"ρ₀₀ (|0⟩): {rho[0, 0]:.4f}")
            st.write(f"ρ₁₁ (|1⟩): {rho[1, 1]:.4f}")

        st.header("4. Fidelity Analysis")

        # Calculate fidelity using eigendecomposition
        theo_rho = results['theoretical_rho'].data
        reco_rho = results['rho_reconstructed']

        # Fidelity: F = Tr(sqrt(sqrt(rho1) * rho2 * sqrt(rho1)))
        sqrt_theo = matrix_sqrt(theo_rho)
        product = sqrt_theo @ reco_rho @ sqrt_theo
        sqrt_product = matrix_sqrt(product)
        fidelity = np.trace(sqrt_product).real

        col1, col2 = st.columns(2)

        with col1:
            st.metric("State Fidelity", f"{fidelity:.4f}")
            st.write("Fidelity of 1.0 indicates perfect reconstruction")

        with col2:
            st.write("Bloch vector components:")
            st.write(f"⟨X⟩: {bloch_x:.4f}")
            st.write(f"⟨Y⟩: {bloch_y:.4f}")
            st.write(f"⟨Z⟩: {bloch_z:.4f}")

        # Density matrices
        st.subheader("Density Matrix Comparison")
        col1, col2 = st.columns(2)

        with col1:
            st.write("Theoretical:")
            st.write(theo_rho)

        with col2:
            st.write("Reconstructed:")
            st.write(reco_rho)
        
        # Store simulation data for PDF report
        from lab_config import LABS
        lab_id = None
        for name, config in LABS.items():
            if config.get('module') == 'tomography':
                lab_id = config['id']
                break
        
        if lab_id:
            metrics = {
                'State Type': state_type,
                'Number of Shots': str(shots),
                'Fidelity': f"{fidelity:.4f}",
                'Bloch X': f"{bloch_x:.4f}",
                'Bloch Y': f"{bloch_y:.4f}",
                'Bloch Z': f"{bloch_z:.4f}",
            }
            theo_sv = results['theoretical_state'].data
            metrics['Theoretical α(|0⟩)'] = f"{theo_sv[0]:.4f}"
            metrics['Theoretical β(|1⟩)'] = f"{theo_sv[1]:.4f}"
            metrics['Reconstructed ρ₀₀'] = f"{rho[0, 0]:.4f}"
            metrics['Reconstructed ρ₁₁'] = f"{rho[1, 1]:.4f}"
            
            # Aggregate measurements from all bases
            all_measurements = {}
            for basis in ['Z', 'X', 'Y']:
                for state, count in results['measurements'][basis].items():
                    all_measurements[f'{basis}_{state}'] = count
            
            figures = [
                save_figure_to_data(fig_theo, 'Theoretical State (Bloch Sphere)'),
                save_figure_to_data(fig_reco, 'Reconstructed State (Bloch Sphere)')
            ]
            
            store_simulation_data(lab_id, metrics=metrics, measurements=all_measurements, figures=figures)

    st.markdown("---")
    st.write(
        "This virtual lab demonstrates quantum state tomography by measuring a single qubit in three complementary bases and reconstructing the density matrix.")


if __name__ == "__main__":
    run()