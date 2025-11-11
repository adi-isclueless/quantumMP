import streamlit as st
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
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
    st.title("Quantum Walk Simulation")
    st.markdown("### Discrete-Time Quantum Walk on a Line")

    # Configuration
    col1, col2, col3 = st.columns(3)
    with col1:
        num_steps = st.slider("Number of Steps", 1, 10, 5)
    with col2:
        num_positions = st.slider("Number of Positions", 3, 11, 7, step=2)
    with col3:
        shots = st.selectbox("Number of Shots", [100, 500, 1000, 5000], index=2)

    coin_type = st.radio("Coin Operator Type", ["Hadamard", "Grover"])

    if st.button("Run Simulation", type="primary"):
        with st.spinner("Running quantum walk simulation..."):
            # Number of qubits needed for positions
            position_qubits = int(np.ceil(np.log2(num_positions)))

            # Create quantum circuit
            coin = QuantumRegister(1, 'coin')
            position = QuantumRegister(position_qubits, 'position')
            c = ClassicalRegister(position_qubits + 1, 'measurement')

            qc = QuantumCircuit(coin, position, c)

            # Initialize at center position
            center = num_positions // 2
            for i, bit in enumerate(format(center, f'0{position_qubits}b')):
                if bit == '1':
                    qc.x(position[position_qubits - 1 - i])

            # Initialize coin in superposition
            qc.h(coin[0])

            qc.barrier()

            # Quantum walk steps
            for step in range(num_steps):
                # Apply coin operator
                if coin_type == "Hadamard":
                    qc.h(coin[0])
                else:  # Grover
                    qc.h(coin[0])
                    qc.z(coin[0])
                    qc.h(coin[0])

                # Conditional shift operations
                # Move right if coin is |0>
                for i in range(position_qubits):
                    qc.x(coin[0])
                    qc.mcx([coin[0]] + [position[j] for j in range(i)], position[i])
                    qc.x(coin[0])

                # Move left if coin is |1>
                for i in range(position_qubits):
                    qc.mcx([coin[0]] + [position[j] for j in range(i)], position[i],
                           ctrl_state='1' + '1' * i)

                qc.barrier()

            # Measure all qubits
            qc.measure(coin[0], c[0])
            for i in range(position_qubits):
                qc.measure(position[i], c[i + 1])

            # Execute
            simulator = AerSimulator()
            job = simulator.run(qc, shots=shots)
            result = job.result()
            counts = result.get_counts()

            # Display results
            st.markdown("### Circuit Diagram")
            fig_circuit = qc.draw(output='mpl', style='iqp', fold=-1)
            st.pyplot(fig_circuit)
            plt.close()

            st.markdown("### Position Distribution")

            # Convert bitstrings to positions
            position_counts = {}
            for bitstring, count in counts.items():
                position_bits = bitstring.split()[0][1:]
                pos = int(position_bits[::-1], 2) if position_bits else 0
                if pos < num_positions:
                    position_counts[pos] = position_counts.get(pos, 0) + count

            # Create position histogram
            fig, ax = plt.subplots(figsize=(10, 6))
            positions = sorted(position_counts.keys())
            probs = [position_counts[p] / shots for p in positions]

            ax.bar(positions, probs, color='#1f77b4', alpha=0.7, edgecolor='black')
            ax.set_xlabel('Position', fontsize=12)
            ax.set_ylabel('Probability', fontsize=12)
            ax.set_title(f'Quantum Walk Distribution after {num_steps} Steps', fontsize=14)
            ax.grid(True, alpha=0.3)
            ax.set_xticks(range(num_positions))
            ax.set_xlim(-0.5, num_positions - 0.5)

            st.pyplot(fig)
            plt.close()

            # Statistics
            st.markdown("### Statistics")
            col1, col2, col3 = st.columns(3)

            mean_position = sum(p * position_counts[p] for p in position_counts) / shots
            variance = sum((p - mean_position) ** 2 * position_counts[p] for p in position_counts) / shots
            std_dev = np.sqrt(variance)

            with col1:
                st.metric("Mean Position", f"{mean_position:.2f}")
            with col2:
                st.metric("Standard Deviation", f"{std_dev:.2f}")
            with col3:
                st.metric("Initial Position", center)

            # Classical comparison
            st.markdown("### Classical vs Quantum Comparison")
            st.markdown(f"""
            **Classical Random Walk Spread:** Proportional to √n (√{num_steps} ≈ {np.sqrt(num_steps):.2f})

            **Quantum Walk Spread:** Proportional to n ({num_steps})

            The quantum walk spreads quadratically faster than classical random walks.
            """)

            # Raw data
            with st.expander("View Raw Measurement Data"):
                st.json(counts)


if __name__ == "__main__":
    run()