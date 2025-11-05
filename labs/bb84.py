"""
BB84 Quantum Key Distribution - Interactive Streamlit Dashboard
Beautiful, interactive visualization of quantum cryptography protocol with Eve eavesdropping
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, pauli_error


def run():
    st.markdown("""
    <style>
        .main-header {
            font-size: 3rem;
            color: #667eea;
            text-align: center;
            margin-bottom: 1rem;
        }
        .sub-header {
            font-size: 1.5rem;
            color: #764ba2;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin: 0.5rem 0;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding-left: 20px;
            padding-right: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

    # BB84 Protocol Class
    class BB84Protocol:
        """Complete BB84 Quantum Key Distribution implementation with Eve eavesdropping"""

        def __init__(self, n_bits=100, noise_prob=0.0):
            self.n_bits = n_bits
            self.noise_prob = noise_prob
            self.simulator = AerSimulator()
            self.alice_bits = []
            self.alice_bases = []
            self.bob_bases = []
            self.bob_results = []
            self.sifted_key_alice = []
            self.sifted_key_bob = []
            self.final_key_alice = []
            self.final_key_bob = []
            self.qber = 0
            self.eve_bases = []
            self.eve_results = []
            self.eve_intercepted = []

        def create_noise_model(self):
            if self.noise_prob == 0:
                return None
            noise_model = NoiseModel()
            error = depolarizing_error(self.noise_prob, 1)
            noise_model.add_all_qubit_quantum_error(error, ['h', 'id'])
            prob_meas = self.noise_prob / 2
            error_meas = pauli_error([('X', prob_meas), ('I', 1 - prob_meas)])
            noise_model.add_all_qubit_quantum_error(error_meas, "measure")
            return noise_model

        def alice_prepare_qubit(self, bit, basis):
            qc = QuantumCircuit(1, 1)
            if bit == 1:
                qc.x(0)
            if basis == 'X':
                qc.h(0)
            return qc

        def bob_measure_qubit(self, qc, basis):
            if basis == 'X':
                qc.h(0)
            qc.measure(0, 0)
            noise_model = self.create_noise_model()
            if noise_model:
                job = self.simulator.run(qc, shots=1, noise_model=noise_model)
            else:
                job = self.simulator.run(qc, shots=1)
            result = job.result()
            counts = result.get_counts()
            return int(list(counts.keys())[0])

        def run_protocol(self, eve_intercept=False, eve_prob=1.0, progress_callback=None):
            # Step 1: Alice generates bits and bases
            self.alice_bits = np.random.randint(0, 2, self.n_bits)
            self.alice_bases = np.random.choice(['Z', 'X'], self.n_bits)

            # Step 2: Quantum transmission (with optional Eve interception)
            self.bob_bases = np.random.choice(['Z', 'X'], self.n_bits)
            self.bob_results = []
            self.eve_bases = []
            self.eve_results = []
            self.eve_intercepted = []

            for i in range(self.n_bits):
                qc = self.alice_prepare_qubit(self.alice_bits[i], self.alice_bases[i])

                # Eve's interception
                if eve_intercept and np.random.random() < eve_prob:
                    eve_basis = np.random.choice(['Z', 'X'])
                    self.eve_bases.append(eve_basis)

                    # Eve measures
                    qc_eve = qc.copy()
                    eve_measured = self.bob_measure_qubit(qc_eve, eve_basis)
                    self.eve_results.append(eve_measured)
                    self.eve_intercepted.append(True)

                    # Eve prepares new qubit based on her measurement
                    qc = self.alice_prepare_qubit(eve_measured, eve_basis)
                else:
                    self.eve_bases.append(None)
                    self.eve_results.append(None)
                    self.eve_intercepted.append(False)

                # Bob measures
                measured = self.bob_measure_qubit(qc, self.bob_bases[i])
                self.bob_results.append(measured)

                if progress_callback and i % max(1, self.n_bits // 20) == 0:
                    progress_callback((i + 1) / self.n_bits)

            self.bob_results = np.array(self.bob_results)
            self.eve_intercepted = np.array(self.eve_intercepted)

            # Step 3: Basis reconciliation
            matching_bases = self.alice_bases == self.bob_bases
            self.sifted_key_alice = self.alice_bits[matching_bases]
            self.sifted_key_bob = self.bob_results[matching_bases]
            sifting_efficiency = len(self.sifted_key_alice) / self.n_bits

            # Step 4: Error estimation
            n_sifted = len(self.sifted_key_alice)
            n_test = max(1, int(n_sifted * 0.2))
            test_indices = np.random.choice(n_sifted, n_test, replace=False)
            test_indices_set = set(test_indices)

            errors = sum(1 for idx in test_indices
                         if self.sifted_key_alice[idx] != self.sifted_key_bob[idx])
            self.qber = errors / n_test if n_test > 0 else 0

            final_indices = [i for i in range(n_sifted) if i not in test_indices_set]
            self.final_key_alice = self.sifted_key_alice[final_indices]
            self.final_key_bob = self.sifted_key_bob[final_indices]

            # Eve statistics
            eve_stats = {}
            if hasattr(self, 'eve_intercepted'):
                eve_stats['interceptions'] = np.sum(self.eve_intercepted)
                eve_stats['intercept_rate'] = np.mean(self.eve_intercepted)

            return {
                'initial_bits': self.n_bits,
                'sifted_bits': len(self.sifted_key_alice),
                'final_key_length': len(self.final_key_alice),
                'sifting_efficiency': sifting_efficiency,
                'qber': self.qber,
                'keys_match': np.array_equal(self.final_key_alice, self.final_key_bob),
                'secure': self.qber < 0.11,
                'errors': errors,
                'test_bits': n_test,
                'eve_stats': eve_stats
            }

    def create_key_comparison_plot(alice_key, bob_key, max_bits=50):
        """Create visual comparison of Alice and Bob's keys"""
        alice_display = alice_key[:max_bits]
        bob_display = bob_key[:max_bits]

        fig, ax = plt.subplots(figsize=(16, 4))

        # Plot Alice's key
        for i, bit in enumerate(alice_display):
            color = '#667eea' if bit == 0 else '#764ba2'
            circle = plt.Circle((i, 1), 0.3, color=color, ec='black', linewidth=1.5)
            ax.add_patch(circle)
            ax.text(i, 1, str(bit), ha='center', va='center',
                    color='white', fontsize=12, fontweight='bold', family='monospace')

        # Plot Bob's key
        for i, bit in enumerate(bob_display):
            color = '#667eea' if bit == 0 else '#764ba2'
            circle = plt.Circle((i, 0), 0.3, color=color, ec='black', linewidth=1.5)
            ax.add_patch(circle)
            ax.text(i, 0, str(bit), ha='center', va='center',
                    color='white', fontsize=12, fontweight='bold', family='monospace')

        # Highlight mismatches
        mismatches = [i for i in range(len(alice_display))
                      if alice_display[i] != bob_display[i]]
        for i in mismatches:
            ax.plot([i, i], [0.3, 0.7], 'r-', linewidth=3, marker='x',
                    markersize=15, markeredgewidth=3)

        ax.text(-1.5, 1, "Alice:", ha='right', va='center', fontsize=14, fontweight='bold')
        ax.text(-1.5, 0, "Bob:", ha='right', va='center', fontsize=14, fontweight='bold')

        ax.set_xlim(-2, len(alice_display))
        ax.set_ylim(-0.5, 1.5)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(f'Key Comparison (First {max_bits} bits)',
                     fontsize=16, fontweight='bold', pad=20)

        if mismatches:
            ax.text(len(alice_display) / 2, -0.3,
                    f'{len(mismatches)} mismatch(es) found',
                    ha='center', color='red', fontsize=12, fontweight='bold')

        plt.tight_layout()
        return fig

    def create_protocol_flow_viz(result):
        """Create visualization of protocol flow"""
        fig, ax = plt.subplots(figsize=(12, 6))

        # Define boxes
        boxes = [
            {'name': 'Initial Bits', 'value': result['initial_bits'], 'pos': 0, 'color': '#667eea'},
            {'name': 'After Sifting', 'value': result['sifted_bits'], 'pos': 1, 'color': '#764ba2'},
            {'name': 'Test Bits', 'value': result['test_bits'], 'pos': 2, 'color': '#e74c3c'},
            {'name': 'Final Key', 'value': result['final_key_length'], 'pos': 3, 'color': '#2ecc71'}
        ]

        # Draw boxes
        for box in boxes:
            rect = mpatches.FancyBboxPatch((box['pos'] * 2.5, 0), 2, 1.5,
                                           boxstyle="round,pad=0.1",
                                           facecolor=box['color'],
                                           edgecolor='black', linewidth=2, alpha=0.8)
            ax.add_patch(rect)
            ax.text(box['pos'] * 2.5 + 1, 0.9, box['name'],
                    ha='center', va='center', fontsize=12, fontweight='bold', color='white')
            ax.text(box['pos'] * 2.5 + 1, 0.5, str(box['value']),
                    ha='center', va='center', fontsize=18, fontweight='bold', color='white')
            ax.text(box['pos'] * 2.5 + 1, 0.1, 'bits',
                    ha='center', va='center', fontsize=10, color='white')

        # Draw arrows
        arrow_props = dict(arrowstyle='->', lw=2.5, color='black')
        ax.annotate('', xy=(2.5, 0.75), xytext=(2.0, 0.75), arrowprops=arrow_props)
        ax.annotate('', xy=(5.0, 0.75), xytext=(4.5, 0.75), arrowprops=arrow_props)

        # Split arrow
        ax.annotate('', xy=(7.5, 1.2), xytext=(7.0, 0.75),
                    arrowprops=dict(arrowstyle='->', lw=2.5, color='#e74c3c'))
        ax.annotate('', xy=(7.5, 0.3), xytext=(7.0, 0.75),
                    arrowprops=dict(arrowstyle='->', lw=2.5, color='#2ecc71'))

        ax.set_xlim(-0.5, 9.5)
        ax.set_ylim(-0.5, 2)
        ax.axis('off')
        ax.set_title('BB84 Protocol Flow', fontsize=18, fontweight='bold', pad=20)

        plt.tight_layout()
        return fig

    def create_eve_visualization(bb84, result, max_bits=30):
        """Create visualization showing Eve's interception impact"""
        fig = plt.figure(figsize=(16, 10))
        gs = GridSpec(3, 2, figure=fig, hspace=0.3, wspace=0.3)

        # Plot 1: Interception Pattern
        ax1 = fig.add_subplot(gs[0, :])
        intercepted = bb84.eve_intercepted[:max_bits]
        alice_bits_display = bb84.alice_bits[:max_bits]
        bob_results_display = bb84.bob_results[:max_bits]
        alice_bases_display = bb84.alice_bases[:max_bits]
        bob_bases_display = bb84.bob_bases[:max_bits]

        for i in range(len(intercepted)):
            # Color coding
            if intercepted[i]:
                color = '#e74c3c'  # Red for intercepted
                marker = 'X'
            else:
                color = '#2ecc71'  # Green for not intercepted
                marker = 'o'

            ax1.scatter(i, 0, s=400, c=color, marker=marker, edgecolors='black', linewidth=2)

            # Show bit values
            ax1.text(i, 0.3, f"A:{alice_bits_display[i]}\n{alice_bases_display[i]}",
                     ha='center', va='bottom', fontsize=8, fontweight='bold')
            ax1.text(i, -0.3, f"B:{bob_results_display[i]}\n{bob_bases_display[i]}",
                     ha='center', va='top', fontsize=8, fontweight='bold')

        ax1.set_xlim(-1, len(intercepted))
        ax1.set_ylim(-0.8, 0.8)
        ax1.set_xlabel('Qubit Index', fontsize=12, fontweight='bold')
        ax1.set_title(f'Eve Interception Pattern (First {max_bits} qubits)\n🔴 Intercepted | 🟢 Not Intercepted',
                      fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='x')
        ax1.set_yticks([])

        # Plot 2: Error Distribution
        ax2 = fig.add_subplot(gs[1, 0])
        matching_bases = alice_bases_display == bob_bases_display
        sifted_indices = [i for i in range(len(matching_bases)) if matching_bases[i]]

        if len(sifted_indices) > 0:
            errors_at_index = []
            colors_bars = []
            for idx in sifted_indices:
                has_error = alice_bits_display[idx] != bob_results_display[idx]
                errors_at_index.append(1 if has_error else 0)
                colors_bars.append('#e74c3c' if has_error else '#2ecc71')

            ax2.bar(sifted_indices, errors_at_index, color=colors_bars,
                    edgecolor='black', linewidth=1.5, alpha=0.7)
            ax2.set_xlabel('Qubit Index (Matching Bases Only)', fontsize=11, fontweight='bold')
            ax2.set_ylabel('Error Present', fontsize=11, fontweight='bold')
            ax2.set_title('Errors in Sifted Key', fontsize=13, fontweight='bold')
            ax2.set_ylim(0, 1.2)
            ax2.set_yticks([0, 1])
            ax2.set_yticklabels(['No Error', 'Error'])
            ax2.grid(True, alpha=0.3, axis='y')

        # Plot 3: Statistics Pie Chart
        ax3 = fig.add_subplot(gs[1, 1])
        intercepted_count = np.sum(bb84.eve_intercepted)
        not_intercepted_count = len(bb84.eve_intercepted) - intercepted_count

        sizes = [intercepted_count, not_intercepted_count]
        colors_pie = ['#e74c3c', '#2ecc71']
        labels = [f'Intercepted\n({intercepted_count} bits)',
                  f'Not Intercepted\n({not_intercepted_count} bits)']

        wedges, texts, autotexts = ax3.pie(sizes, labels=labels, colors=colors_pie,
                                           autopct='%1.1f%%', startangle=90,
                                           textprops={'fontsize': 11, 'fontweight': 'bold'},
                                           wedgeprops={'edgecolor': 'black', 'linewidth': 2})
        ax3.set_title('Eve Interception Rate', fontsize=13, fontweight='bold')

        # Plot 4: QBER Comparison
        ax4 = fig.add_subplot(gs[2, 0])
        qber_pct = result['qber'] * 100
        threshold = 11

        bars = ax4.bar(['Measured QBER', 'Security Threshold'],
                       [qber_pct, threshold],
                       color=['#e74c3c' if qber_pct >= threshold else '#f39c12', '#95a5a6'],
                       edgecolor='black', linewidth=2, alpha=0.7)

        ax4.set_ylabel('Error Rate (%)', fontsize=11, fontweight='bold')
        ax4.set_title('QBER vs Security Threshold', fontsize=13, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width() / 2., height,
                     f'{height:.2f}%', ha='center', va='bottom', fontweight='bold', fontsize=11)

        # Add security zone
        if qber_pct < threshold:
            ax4.axhspan(0, threshold, alpha=0.2, color='green')
            ax4.text(0.5, threshold / 2, 'SECURE ZONE', ha='center', va='center',
                     fontsize=10, fontweight='bold', transform=ax4.get_xaxis_transform())

        # Plot 5: Key Statistics
        ax5 = fig.add_subplot(gs[2, 1])
        ax5.axis('off')

        stats_text = f"""📊 DETECTION STATISTICS

    🔴 Eve Intercepted: {result['eve_stats']['interceptions']} qubits 
       ({result['eve_stats']['intercept_rate'] * 100:.1f}%)

    📏 Initial Bits: {result['initial_bits']}
    📐 Sifted Bits: {result['sifted_bits']}
    🔑 Final Key Length: {result['final_key_length']}

    ❌ Errors Detected: {result['errors']} in {result['test_bits']} test bits
    📈 QBER: {result['qber'] * 100:.2f}%

    {'✅ Protocol SECURE' if result['secure'] else '⚠️ Protocol INSECURE'}
    {'No eavesdropping detected' if result['secure'] else 'Eavesdropping detected!'}"""

        ax5.text(0.5, 0.5, stats_text, ha='center', va='center',
                 fontsize=10, family='monospace',
                 bbox=dict(boxstyle='round,pad=1', facecolor='lightgray', alpha=0.8))

        fig.suptitle('🕵️ Eve Eavesdropping Analysis - BB84 Protocol',
                     fontsize=16, fontweight='bold')

        plt.tight_layout()
        return fig

    def create_performance_plots(results_df):
        """Create comprehensive performance analysis plots"""
        fig = plt.figure(figsize=(16, 12))
        gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)

        # QBER vs Noise
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.plot(results_df['noise'], results_df['qber'],
                 'o-', linewidth=3, markersize=10, color='#e74c3c', label='QBER')
        ax1.axhline(y=11, color='red', linestyle='--', linewidth=2, label='Security Threshold')
        ax1.fill_between(results_df['noise'], 0, 11, alpha=0.2, color='green', label='Secure Zone')
        ax1.set_xlabel('Channel Noise (%)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('QBER (%)', fontsize=12, fontweight='bold')
        ax1.set_title('Quantum Bit Error Rate vs Channel Noise', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # Key Length vs Noise
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.plot(results_df['noise'], results_df['key_length'],
                 's-', linewidth=3, markersize=10, color='#3498db', label='Key Length')
        ax2.set_xlabel('Channel Noise (%)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Final Key Length (bits)', fontsize=12, fontweight='bold')
        ax2.set_title('Final Key Length vs Channel Noise', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        # Sifting Efficiency
        ax3 = fig.add_subplot(gs[1, 0])
        ax3.plot(results_df['noise'], results_df['sifting_eff'],
                 '^-', linewidth=3, markersize=10, color='#2ecc71', label='Sifting Efficiency')
        ax3.axhline(y=50, color='gray', linestyle=':', linewidth=2, label='Theoretical (50%)')
        ax3.set_xlabel('Channel Noise (%)', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Sifting Efficiency (%)', fontsize=12, fontweight='bold')
        ax3.set_title('Sifting Efficiency (Basis Matching Rate)', fontsize=14, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        ax3.legend()

        # Security Success Rate
        ax4 = fig.add_subplot(gs[1, 1])
        colors = ['#2ecc71' if x == 100 else '#f39c12' if x > 0 else '#e74c3c'
                  for x in results_df['secure_pct']]
        bars = ax4.bar(results_df['noise'], results_df['secure_pct'],
                       color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
        ax4.set_xlabel('Channel Noise (%)', fontsize=12, fontweight='bold')
        ax4.set_ylabel('Secure Trials (%)', fontsize=12, fontweight='bold')
        ax4.set_title('Security Success Rate', fontsize=14, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')
        ax4.set_ylim(0, 105)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width() / 2., height,
                     f'{height:.0f}%', ha='center', va='bottom', fontweight='bold')

        fig.suptitle('BB84 Quantum Key Distribution - Comprehensive Performance Analysis',
                     fontsize=18, fontweight='bold', y=0.995)

        plt.tight_layout()
        return fig

    # Main Application
    def main():
        st.markdown('<h1 class="main-header">🔐 BB84 Quantum Key Distribution</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Interactive Quantum Cryptography Protocol Simulator</p>',
                    unsafe_allow_html=True)
        st.markdown(
            "**Explore the first quantum key distribution protocol invented by Charles Bennett and Gilles Brassard in 1984**")

        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs(
            ["🎯 Single Protocol Run", "🕵️ Eve Eavesdropping", "📊 Performance Analysis", "📚 Learn BB84"])

        # Tab 1: Single Protocol Run
        with tab1:
            st.markdown("### Run a single instance of the BB84 protocol with custom parameters")
            st.markdown("Adjust the number of bits and channel noise to see how it affects the protocol.")

            col1, col2 = st.columns([1, 2])

            with col1:
                st.markdown("#### Parameters")
                n_bits_single = st.slider("Number of Bits", 50, 500, 100, 10,
                                          help="Total bits Alice wants to send")
                noise_single = st.slider("Channel Noise (%)", 0.0, 30.0, 5.0, 0.5,
                                         help="Probability of errors in quantum channel")

                run_single = st.button("🚀 Run Protocol", type="primary", use_container_width=True)

            with col2:
                if run_single:
                    with st.spinner("Running BB84 protocol..."):
                        progress_bar = st.progress(0)

                        def update_progress(val):
                            progress_bar.progress(val)

                        bb84 = BB84Protocol(n_bits=int(n_bits_single), noise_prob=noise_single / 100)
                        result = bb84.run_protocol(progress_callback=update_progress)

                        # Display metrics
                        st.markdown("#### Results")
                        metric_cols = st.columns(4)
                        with metric_cols[0]:
                            st.metric("Initial Bits", result['initial_bits'])
                        with metric_cols[1]:
                            st.metric("Sifted Bits", result['sifted_bits'])
                        with metric_cols[2]:
                            st.metric("Final Key Length", result['final_key_length'])
                        with metric_cols[3]:
                            qber_color = "🟢" if result['secure'] else "🔴"
                            st.metric("QBER", f"{result['qber'] * 100:.2f}% {qber_color}")

                        # Security status
                        if result['secure']:
                            st.success("✅ **SECURE** - No eavesdropping detected!")
                        else:
                            st.error("⚠️ **INSECURE** - Possible eavesdropping detected!")

                        # Display visualizations
                        st.markdown("#### Protocol Flow")
                        flow_fig = create_protocol_flow_viz(result)
                        st.pyplot(flow_fig)

                        st.markdown("#### Key Comparison")
                        if len(bb84.final_key_alice) > 0:
                            key_fig = create_key_comparison_plot(bb84.final_key_alice, bb84.final_key_bob)
                            st.pyplot(key_fig)

                            # Key samples
                            st.markdown("#### Key Samples (first 50 bits)")
                            st.code(f"Alice's Key: {''.join(map(str, bb84.final_key_alice[:50]))}")
                            st.code(f"Bob's Key:   {''.join(map(str, bb84.final_key_bob[:50]))}")
                        else:
                            st.warning("No final key generated. Try running with less noise.")

                        # Detailed stats
                        with st.expander("📊 Detailed Statistics"):
                            st.write(f"**Sifting Efficiency:** {result['sifting_efficiency'] * 100:.1f}%")
                            st.write(f"**Errors Found:** {result['errors']} in {result['test_bits']} test bits")
                            st.write(f"**Security Threshold:** 11%")
                            st.write(f"**Keys Match:** {'Yes ✅' if result['keys_match'] else 'No ❌'}")

        # Tab 2: Eve Eavesdropping
        with tab2:
            st.markdown("### Simulate an eavesdropper (Eve) intercepting the quantum channel")
            st.markdown("See how Eve's measurements introduce detectable errors and compromise security.")

            col1, col2 = st.columns([1, 2])

            with col1:
                st.markdown("#### Parameters")
                n_bits_eve = st.slider("Number of Bits", 50, 300, 100, 10,
                                       help="Total bits Alice sends", key="eve_bits")
                noise_eve = st.slider("Channel Noise (%)", 0.0, 10.0, 0.0, 0.5,
                                      help="Background quantum channel noise", key="eve_noise")
                eve_prob = st.slider("Eve Interception Rate (%)", 0, 100, 50, 5,
                                     help="Percentage of qubits Eve intercepts", key="eve_prob")

                st.markdown("""
                #### 🎯 What Eve Does:
                1. Intercepts qubits from Alice
                2. Measures them (random basis)
                3. Resends to Bob (disturbed states)

                **Expected:** Higher interception → Higher QBER → Detection!
                """)

                run_eve = st.button("🚀 Run with Eve", type="primary", use_container_width=True, key="run_eve")

            with col2:
                if run_eve:
                    with st.spinner("Running BB84 protocol with Eve eavesdropping..."):
                        progress_bar = st.progress(0)

                        def update_progress(val):
                            progress_bar.progress(val)

                        bb84 = BB84Protocol(n_bits=int(n_bits_eve), noise_prob=noise_eve / 100)
                        result = bb84.run_protocol(eve_intercept=True, eve_prob=eve_prob / 100,
                                                   progress_callback=update_progress)

                        # Display metrics
                        st.markdown("#### Results")
                        metric_cols = st.columns(4)
                        with metric_cols[0]:
                            st.metric("Qubits Intercepted", result['eve_stats']['interceptions'])
                        with metric_cols[1]:
                            st.metric("Interception Rate", f"{result['eve_stats']['intercept_rate'] * 100:.1f}%")
                        with metric_cols[2]:
                            st.metric("Final Key Length", result['final_key_length'])
                        with metric_cols[3]:
                            qber_color = "🟢" if result['secure'] else "🔴"
                            st.metric("QBER", f"{result['qber'] * 100:.2f}% {qber_color}")

                        # Security status
                        if result['secure']:
                            st.warning("⚠️ Eve was NOT detected! (QBER below threshold)")
                            st.info(
                                f"💡 Even though Eve intercepted {result['eve_stats']['intercept_rate'] * 100:.1f}% of qubits, the error rate is still below 11%. This shows that quantum mechanics doesn't guarantee detection of every attack - statistical fluctuations matter!")
                        else:
                            st.error("🚨 Eve was DETECTED! (QBER above threshold)")
                            st.success(
                                f"💡 Eve's {result['eve_stats']['intercept_rate'] * 100:.1f}% interception rate caused enough disturbance to raise the QBER above 11%. This is the quantum advantage - any measurement leaves a detectable trace!")

                        # Display visualizations
                        st.markdown("#### Eve Eavesdropping Analysis")
                        eve_fig = create_eve_visualization(bb84, result)
                        st.pyplot(eve_fig)

                        st.markdown("#### Key Comparison")
                        if len(bb84.final_key_alice) > 0:
                            key_fig = create_key_comparison_plot(bb84.final_key_alice, bb84.final_key_bob)
                            st.pyplot(key_fig)
                        else:
                            st.warning("No final key generated. Too many errors detected.")

                        # Detailed stats
                        with st.expander("📊 Detailed Statistics"):
                            st.write(f"**Initial Bits Sent:** {result['initial_bits']}")
                            st.write(f"**After Sifting:** {result['sifted_bits']} bits")
                            st.write(f"**Final Key Length:** {result['final_key_length']} bits")
                            st.write(f"**Sifting Efficiency:** {result['sifting_efficiency'] * 100:.1f}%")
                            st.write(f"**Errors Found:** {result['errors']} in {result['test_bits']} test bits")
                            st.write(f"**Security Threshold:** 11%")

        # Tab 3: Performance Analysis
        with tab3:
            st.markdown("### Analyze BB84 performance across different noise levels")
            st.markdown("Run multiple trials to see how noise affects QBER, key length, and security.")

            col1, col2 = st.columns([1, 2])

            with col1:
                st.markdown("#### Parameters")
                n_bits_perf = st.slider("Bits per Trial", 100, 500, 200, 50, key="perf_bits")
                n_trials = st.slider("Trials per Noise Level", 1, 20, 5, 1, key="perf_trials")
                noise_min = st.slider("Minimum Noise (%)", 0.0, 15.0, 0.0, 0.5, key="perf_min")
                noise_max = st.slider("Maximum Noise (%)", 5.0, 30.0, 20.0, 0.5, key="perf_max")
                noise_steps = st.slider("Number of Noise Steps", 5, 15, 8, 1, key="perf_steps")

                analyze_btn = st.button("🔬 Analyze Performance", type="primary", use_container_width=True)

            with col2:
                if analyze_btn:
                    with st.spinner("Running performance analysis..."):
                        noise_levels = np.linspace(noise_min / 100, noise_max / 100, int(noise_steps))

                        results_data = {
                            'noise': [],
                            'qber': [],
                            'sifting_eff': [],
                            'key_length': [],
                            'secure_pct': []
                        }

                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        total_runs = len(noise_levels) * int(n_trials)
                        current_run = 0

                        for noise in noise_levels:
                            qbers, sifting_effs, key_lengths = [], [], []
                            secure_count = 0

                            for trial in range(int(n_trials)):
                                status_text.text(
                                    f"Testing {noise * 100:.1f}% noise - Trial {trial + 1}/{int(n_trials)}")

                                bb84 = BB84Protocol(n_bits=int(n_bits_perf), noise_prob=noise)
                                result = bb84.run_protocol()
                                qbers.append(result['qber'] * 100)
                                sifting_effs.append(result['sifting_efficiency'] * 100)
                                key_lengths.append(result['final_key_length'])
                                if result['secure']:
                                    secure_count += 1

                                current_run += 1
                                progress_bar.progress(current_run / total_runs)

                            results_data['noise'].append(noise * 100)
                            results_data['qber'].append(np.mean(qbers))
                            results_data['sifting_eff'].append(np.mean(sifting_effs))
                            results_data['key_length'].append(np.mean(key_lengths))
                            results_data['secure_pct'].append(secure_count / int(n_trials) * 100)

                        results_df = pd.DataFrame(results_data)

                        status_text.text("Analysis complete!")
                        progress_bar.progress(1.0)

                        # Display summary metrics
                        st.markdown("#### Analysis Summary")
                        metric_cols = st.columns(4)
                        with metric_cols[0]:
                            st.metric("Lowest QBER", f"{results_df['qber'].min():.2f}%")
                        with metric_cols[1]:
                            st.metric("Highest QBER", f"{results_df['qber'].max():.2f}%")
                        with metric_cols[2]:
                            st.metric("Avg Key Length", f"{results_df['key_length'].mean():.0f}")
                        with metric_cols[3]:
                            st.metric("Avg Success Rate", f"{results_df['secure_pct'].mean():.1f}%")

                        # Display plots
                        st.markdown("#### Performance Analysis")
                        perf_fig = create_performance_plots(results_df)
                        st.pyplot(perf_fig)

                        # Key findings
                        st.markdown("#### 🔍 Key Findings")
                        st.write(f"✓ Sifting reduces key by ~50% (random basis matching)")
                        st.write(f"✓ QBER increases with channel noise")
                        st.write(f"✓ BB84 detects eavesdropping through elevated QBER")
                        st.write(f"✓ Protocol is secure when QBER < 11%")

                        # Raw data
                        with st.expander("📋 View Raw Data"):
                            st.dataframe(results_df, use_container_width=True)

                            # Download option
                            csv = results_df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Results as CSV",
                                data=csv,
                                file_name="bb84_performance_analysis.csv",
                                mime="text/csv"
                            )

        # Tab 4: Learn BB84
        with tab4:
            st.markdown("## Learn About BB84 Quantum Key Distribution")

            with st.expander("🎯 What is BB84?", expanded=True):
                st.markdown("""
                ### Overview

                BB84 is the first quantum key distribution protocol, invented by Charles Bennett 
                and Gilles Brassard in 1984. It allows two parties (Alice and Bob) to establish 
                a shared secret key using quantum mechanics, with guaranteed detection of eavesdropping.

                **Key Features:**
                - 🔐 **Unconditional Security**: Based on quantum mechanics laws
                - 🕵️ **Eavesdropping Detection**: Any interception disturbs quantum states
                - 🔑 **Shared Key Generation**: Creates identical secret keys for Alice and Bob
                - ⚛️ **Quantum Foundation**: Uses quantum superposition and measurement

                > **Quantum Advantage**: Unlike classical cryptography based on computational complexity, 
                > BB84's security comes from the laws of physics!
                """)

            with st.expander("🔧 How It Works"):
                st.markdown("""
                ### The Protocol Steps

                #### 1️⃣ Alice Prepares Qubits
                Alice randomly chooses:
                - A bit value (0 or 1)
                - A basis (Z: computational or X: Hadamard)

                She encodes the bit in the chosen basis and sends the qubit to Bob.

                #### 2️⃣ Bob Measures
                Bob randomly chooses a measurement basis (Z or X) and measures each received qubit.

                #### 3️⃣ Basis Reconciliation (Sifting)
                Alice and Bob publicly compare their basis choices (not the bit values).
                They keep only the bits where their bases matched (~50% of bits).

                #### 4️⃣ Error Estimation
                They sacrifice some bits to check for errors. If the error rate (QBER) is below 11%,
                the channel is secure. High error rates indicate eavesdropping.

                #### 5️⃣ Privacy Amplification
                They use the remaining bits as their shared secret key.
                """)

                # Add visual diagram
                st.image(
                    "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/BB84_protocol.svg/800px-BB84_protocol.svg.png",
                    caption="BB84 Protocol Flow", use_container_width=True)

            with st.expander("🔒 Security Principles"):
                st.markdown("""
                ### Why is BB84 Secure?

                **The Quantum Advantage:**

                1. **No-Cloning Theorem**: Quantum states cannot be perfectly copied
                2. **Measurement Disturbance**: Measuring a quantum state changes it
                3. **Heisenberg Uncertainty**: Cannot measure in two incompatible bases simultaneously

                **Eavesdropping Detection:**

                If Eve tries to intercept:
                - She must measure qubits (to learn the key)
                - Her measurements disturb the quantum states
                - This introduces errors that Alice and Bob detect through QBER

                **Security Threshold:**
                - QBER < 11%: Channel is secure ✅
                - QBER ≥ 11%: Possible eavesdropping ⚠️

                > ⚠️ **Important**: BB84 doesn't prevent eavesdropping—it detects it!
                > If QBER is high, Alice and Bob abort and try again.
                """)

                # Add interactive demo
                st.markdown("#### Interactive Example")
                col1, col2, col3 = st.columns(3)
                with col1:
                    alice_bit = st.selectbox("Alice's Bit", [0, 1], key="learn_alice_bit")
                    alice_basis = st.selectbox("Alice's Basis", ["Z", "X"], key="learn_alice_basis")
                with col2:
                    bob_basis = st.selectbox("Bob's Basis", ["Z", "X"], key="learn_bob_basis")
                with col3:
                    if alice_basis == bob_basis:
                        st.success(f"✅ Bases Match!\nBob measures: {alice_bit}")
                    else:
                        st.warning(f"❌ Bases Don't Match\nBob measures: Random (50/50)")

            with st.expander("💡 Real-World Applications"):
                st.markdown("""
                ### Current Deployments

                **Industries:**
                - 🏦 **Banking**: Secure inter-bank communications
                - 🏛️ **Government**: Secure government communications
                - 🔬 **Research**: Quantum networks and quantum internet
                - 💼 **Enterprise**: High-security data centers

                **Commercial Systems:**
                - ID Quantique (Switzerland)
                - Toshiba Quantum Key Distribution
                - Chinese quantum satellite "Micius"

                **Limitations:**
                - Distance: ~100 km in fiber, ~1000 km via satellite
                - Speed: Key generation rates (kbps to Mbps)
                - Cost: Specialized hardware required
                - Infrastructure: Needs quantum channels

                **Future Outlook:**
                - Quantum repeaters to extend distance
                - Integration with classical networks
                - Quantum internet infrastructure
                """)

            with st.expander("📖 Additional Resources"):
                st.markdown("""
                ### Learn More

                **Academic Papers:**
                - [Original BB84 Paper (1984)](https://doi.org/10.1016/j.tcs.2014.05.025)
                - [Quantum Cryptography: Public Key Distribution and Coin Tossing](https://arxiv.org/abs/2003.06557)

                **Online Courses:**
                - Quantum Cryptography on Coursera
                - edX: Quantum Cryptography
                - MIT OpenCourseWare: Quantum Information Science

                **Books:**
                - "Quantum Computation and Quantum Information" by Nielsen & Chuang
                - "An Introduction to Quantum Computing" by Kaye, Laflamme, and Mosca

                **Tools & Simulators:**
                - Qiskit (IBM Quantum)
                - Cirq (Google)
                - QuTiP (Quantum Toolbox in Python)
                """)

        # Footer
        st.markdown("---")
        st.markdown("""
        ### 📖 About This Simulator
        This interactive dashboard demonstrates the BB84 quantum key distribution protocol using Qiskit.
        It simulates quantum state preparation, transmission, measurement, and key distribution with realistic noise models.
        The Eve eavesdropping simulation shows how quantum mechanics provides information-theoretic security.

        **Built with**: Qiskit, Streamlit, Matplotlib, NumPy

        **Created by**: Quantum Cryptography Enthusiasts
        """)

    main()
