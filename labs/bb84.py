"""
BB84 Quantum Key Distribution - Complete Interactive Simulation
Animated step-by-step simulation + comprehensive analysis tools
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
import time
from PIL import Image, ImageDraw
from certificate import store_simulation_data, save_figure_to_data

def run():
    st.divider()
    # Page config
    st.set_page_config(page_title="BB84 Quantum Simulation", layout="wide", initial_sidebar_state="expanded")
    
    # Custom CSS
    st.markdown("""
    <style>
        .main-header {
            font-size: 3rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: bold;
            text-align: center;
            margin-bottom: 1rem;
        }
        .sub-header {
            font-size: 1.5rem;
            color: #764ba2;
            margin-bottom: 2rem;
        }
        .stButton>button {
            border-radius: 10px;
            font-weight: bold;
        }
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
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
    
    # Initialize session state for animation tab
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    if 'transmission_history' not in st.session_state:
        st.session_state.transmission_history = []
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False
    
    # BB84 Protocol Class
    class BB84Protocol:
        """Complete BB84 Quantum Key Distribution implementation"""
        
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
            self.alice_bits = np.random.randint(0, 2, self.n_bits)
            self.alice_bases = np.random.choice(['Z', 'X'], self.n_bits)
            self.bob_bases = np.random.choice(['Z', 'X'], self.n_bits)
            self.bob_results = []
            self.eve_bases = []
            self.eve_results = []
            self.eve_intercepted = []
            
            for i in range(self.n_bits):
                qc = self.alice_prepare_qubit(self.alice_bits[i], self.alice_bases[i])
                
                if eve_intercept and np.random.random() < eve_prob:
                    eve_basis = np.random.choice(['Z', 'X'])
                    self.eve_bases.append(eve_basis)
                    qc_eve = qc.copy()
                    eve_measured = self.bob_measure_qubit(qc_eve, eve_basis)
                    self.eve_results.append(eve_measured)
                    self.eve_intercepted.append(True)
                    qc = self.alice_prepare_qubit(eve_measured, eve_basis)
                else:
                    self.eve_bases.append(None)
                    self.eve_results.append(None)
                    self.eve_intercepted.append(False)
                
                measured = self.bob_measure_qubit(qc, self.bob_bases[i])
                self.bob_results.append(measured)
                
                if progress_callback and i % max(1, self.n_bits // 20) == 0:
                    progress_callback((i + 1) / self.n_bits)
            
            self.bob_results = np.array(self.bob_results)
            self.eve_intercepted = np.array(self.eve_intercepted)
            
            matching_bases = self.alice_bases == self.bob_bases
            self.sifted_key_alice = self.alice_bits[matching_bases]
            self.sifted_key_bob = self.bob_results[matching_bases]
            sifting_efficiency = len(self.sifted_key_alice) / self.n_bits
            
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
    
    # Animation Functions
    def create_animation_frame(step_data, frame=0):
        """Create an animation frame showing qubit transmission"""
        width, height = 700, 280
        img = Image.new('RGB', (width, height), color='#f8f9fa')
        draw = ImageDraw.Draw(img)
        
        alice_x, alice_y = 100, 140
        bob_x, bob_y = 600, 140
        eve_y = 210
        
        # Draw Alice
        draw.ellipse([alice_x-40, alice_y-40, alice_x+40, alice_y+40], 
                     fill='#667eea', outline='#000', width=2)
        draw.text((alice_x, alice_y-55), "ALICE", fill='#667eea', anchor="mm")
        draw.text((alice_x, alice_y), "A", fill='white', anchor="mm")
        
        # Draw Bob
        draw.ellipse([bob_x-40, bob_y-40, bob_x+40, bob_y+40], 
                     fill='#2ecc71', outline='#000', width=2)
        draw.text((bob_x, bob_y-55), "BOB", fill='#2ecc71', anchor="mm")
        draw.text((bob_x, bob_y), "B", fill='white', anchor="mm")
        
        # Draw quantum channel
        draw.line([alice_x+40, alice_y, bob_x-40, bob_y], fill='#3498db', width=3)
        
        # Draw Eve if active
        if step_data.get('eve_active', False):
            eve_x = (alice_x + bob_x) // 2
            draw.ellipse([eve_x-35, eve_y-35, eve_x+35, eve_y+35], 
                         fill='#e74c3c', outline='#000', width=2)
            draw.text((eve_x, eve_y-50), "EVE", fill='#e74c3c', anchor="mm")
            draw.text((eve_x, eve_y), "E", fill='white', anchor="mm")
        
        # Animate qubit
        if frame > 0:
            if step_data.get('eve_active', False) and step_data.get('intercepted', False):
                total_frames = 30
                if frame < total_frames // 2:
                    progress = frame / (total_frames // 2)
                    eve_x = (alice_x + bob_x) // 2
                    qubit_x = alice_x + 40 + progress * (eve_x - 35 - alice_x - 40)
                    qubit_y = alice_y
                else:
                    progress = (frame - total_frames // 2) / (total_frames // 2)
                    eve_x = (alice_x + bob_x) // 2
                    qubit_x = eve_x + 35 + progress * (bob_x - 40 - eve_x - 35)
                    qubit_y = bob_y
            else:
                progress = frame / 30
                qubit_x = alice_x + 40 + progress * (bob_x - 40 - alice_x - 40)
                qubit_y = alice_y
            
            # Draw qubit
            draw.ellipse([qubit_x-15, qubit_y-15, qubit_x+15, qubit_y+15], 
                         fill='#f39c12', outline='#000', width=2)
            bit_text = f"|{step_data['alice_bit']}>{step_data['alice_basis']}"
            draw.text((qubit_x, qubit_y-28), bit_text, fill='#000', anchor="mm")
        
        # Info boxes (smaller)
        draw.rectangle([10, 10, 220, 70], fill='#667eea', outline='#000', width=2)
        draw.text((115, 25), f"Alice's Bit: {step_data['alice_bit']}", fill='white', anchor="mm")
        draw.text((115, 50), f"Alice's Basis: {step_data['alice_basis']}", fill='white', anchor="mm")
        
        draw.rectangle([480, 10, 690, 70], fill='#2ecc71', outline='#000', width=2)
        draw.text((585, 25), f"Bob's Basis: {step_data['bob_basis']}", fill='white', anchor="mm")
        if frame >= 30:
            draw.text((585, 50), f"Bob's Result: {step_data['bob_result']}", fill='white', anchor="mm")
        
        if step_data.get('eve_active', False) and step_data.get('intercepted', False):
            draw.rectangle([260, 230, 440, 275], fill='#e74c3c', outline='#000', width=2)
            draw.text((350, 242), f"Eve's Basis: {step_data['eve_basis']}", fill='white', anchor="mm")
            if frame >= 15:
                draw.text((350, 262), f"Eve Measured: {step_data['eve_result']}", fill='white', anchor="mm")
        
        return img
    
    def generate_transmission():
        """Generate one transmission event"""
        alice_bit = np.random.randint(0, 2)
        alice_basis = np.random.choice(['Z', 'X'])
        bob_basis = np.random.choice(['Z', 'X'])
        
        eve_active = st.session_state.get('eve_enabled', False)
        intercepted = False
        eve_basis = None
        eve_result = None
        
        if alice_basis == bob_basis:
            bob_result = alice_bit
        else:
            bob_result = np.random.randint(0, 2)
        
        eve_rate = st.session_state.get('eve_intercept_rate', 0.35)
        if eve_active and np.random.random() < eve_rate:
            intercepted = True
            eve_basis = np.random.choice(['Z', 'X'])
            if alice_basis == eve_basis:
                eve_result = alice_bit
            else:
                eve_result = np.random.randint(0, 2)
            
            if eve_basis == bob_basis:
                bob_result = eve_result
            else:
                bob_result = np.random.randint(0, 2)
        
        bases_match = alice_basis == bob_basis
        error = alice_bit != bob_result if bases_match else None
        
        return {
            'step': st.session_state.current_step + 1,
            'alice_bit': alice_bit,
            'alice_basis': alice_basis,
            'bob_basis': bob_basis,
            'bob_result': bob_result,
            'bases_match': bases_match,
            'error': error,
            'eve_active': eve_active,
            'intercepted': intercepted,
            'eve_basis': eve_basis,
            'eve_result': eve_result
        }
    
    import io
    import base64

    def run_animation(step_data, placeholder):
        frames = []
        for frame in range(31):
            frames.append(create_animation_frame(step_data, frame))

        # Save frames to in-memory GIF
        buf = io.BytesIO()
        frames[0].save(buf, format='GIF', save_all=True,
                    append_images=frames[1:], duration=30, loop=0)
        buf.seek(0)

        # Convert GIF to base64 and render inline
        b64 = base64.b64encode(buf.read()).decode("utf-8")
        placeholder.markdown(
            f'<img src="data:image/gif;base64,{b64}" alt="animation">',
            unsafe_allow_html=True
        )

    
    # Visualization Functions
    def create_key_comparison_plot(alice_key, bob_key, max_bits=50):
        """Create visual comparison of Alice and Bob's keys"""
        alice_display = alice_key[:max_bits]
        bob_display = bob_key[:max_bits]
        
        fig, ax = plt.subplots(figsize=(16, 4))
        
        for i, bit in enumerate(alice_display):
            color = '#667eea' if bit == 0 else '#764ba2'
            circle = plt.Circle((i, 1), 0.3, color=color, ec='black', linewidth=1.5)
            ax.add_patch(circle)
            ax.text(i, 1, str(bit), ha='center', va='center',
                    color='white', fontsize=12, fontweight='bold', family='monospace')
        
        for i, bit in enumerate(bob_display):
            color = '#667eea' if bit == 0 else '#764ba2'
            circle = plt.Circle((i, 0), 0.3, color=color, ec='black', linewidth=1.5)
            ax.add_patch(circle)
            ax.text(i, 0, str(bit), ha='center', va='center',
                    color='white', fontsize=12, fontweight='bold', family='monospace')
        
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
        
        boxes = [
            {'name': 'Initial Bits', 'value': result['initial_bits'], 'pos': 0, 'color': '#667eea'},
            {'name': 'After Sifting', 'value': result['sifted_bits'], 'pos': 1, 'color': '#764ba2'},
            {'name': 'Test Bits', 'value': result['test_bits'], 'pos': 2, 'color': '#e74c3c'},
            {'name': 'Final Key', 'value': result['final_key_length'], 'pos': 3, 'color': '#2ecc71'}
        ]
        
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
        
        arrow_props = dict(arrowstyle='->', lw=2.5, color='black')
        ax.annotate('', xy=(2.5, 0.75), xytext=(2.0, 0.75), arrowprops=arrow_props)
        ax.annotate('', xy=(5.0, 0.75), xytext=(4.5, 0.75), arrowprops=arrow_props)
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
    
    def create_performance_plots(results_df, varied_param_name):
        """Create performance analysis plots"""
        fig = plt.figure(figsize=(16, 6))
        gs = GridSpec(1, 3, figure=fig, hspace=0.3, wspace=0.35)
        
        # Map parameter names to their column labels
        param_to_col = {
            "Noise": "noise",
            "Number of Bits": "bits",
            "Distance": "distance",
            "Number of Eves": "eves",
            "Fading": "fading"
        }
        
        # Get the correct column name
        x_col = param_to_col.get(varied_param_name, results_df.columns[0])
        
        x_label = varied_param_name
        x_values = results_df[x_col].values
        x_indices = np.arange(len(x_values))
        
        # Format x-axis labels based on parameter type
        if varied_param_name in ["Number of Eves", "Number of Bits"]:
            x_labels = [f'{int(v)}' for v in x_values]
        else:
            x_labels = [f'{v:.1f}' for v in x_values]
        
        # Chart 1: QBER
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.plot(x_indices, results_df['qber'].values,
                 'o-', linewidth=3, markersize=10, color='#e74c3c', label='QBER')
        ax1.axhline(y=11, color='red', linestyle='--', linewidth=2, label='Security Threshold')
        ax1.fill_between(x_indices, 0, 11, alpha=0.2, color='green', label='Secure Zone')
        ax1.set_xlabel(x_label, fontsize=12, fontweight='bold')
        ax1.set_ylabel('QBER (%)', fontsize=12, fontweight='bold')
        ax1.set_title('Quantum Bit Error Rate', fontsize=14, fontweight='bold')
        ax1.set_xticks(x_indices)
        ax1.set_xticklabels(x_labels, rotation=0)
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='best')
        ax1.set_ylim(0, max(30, results_df['qber'].max() + 5))
        
        # Chart 2: Key Length
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.plot(x_indices, results_df['key_length'].values,
                 's-', linewidth=3, markersize=10, color='#3498db', label='Key Length')
        ax2.set_xlabel(x_label, fontsize=12, fontweight='bold')
        ax2.set_ylabel('Final Key Length (bits)', fontsize=12, fontweight='bold')
        ax2.set_title('Final Key Length', fontsize=14, fontweight='bold')
        ax2.set_xticks(x_indices)
        ax2.set_xticklabels(x_labels, rotation=0)
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc='best')
        
        # Chart 3: Security Success Rate
        ax3 = fig.add_subplot(gs[0, 2])
        colors = ['#2ecc71' if x == 100 else '#f39c12' if x > 0 else '#e74c3c'
                  for x in results_df['secure_pct'].values]
        bars = ax3.bar(x_indices, results_df['secure_pct'].values,
                       color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
        ax3.set_xlabel(x_label, fontsize=12, fontweight='bold')
        ax3.set_ylabel('Secure Trials (%)', fontsize=12, fontweight='bold')
        ax3.set_title('Security Success Rate', fontsize=14, fontweight='bold')
        ax3.set_xticks(x_indices)
        ax3.set_xticklabels(x_labels, rotation=0)
        ax3.grid(True, alpha=0.3, axis='y')
        ax3.set_ylim(0, 105)
        
        for i, (bar, val) in enumerate(zip(bars, results_df['secure_pct'].values)):
            height = bar.get_height()
            ax3.text(i, height + 2, f'{height:.0f}%', ha='center', va='bottom', 
                    fontweight='bold', fontsize=9)
        
        fig.suptitle(f'BB84 Performance Analysis - Varying {varied_param_name}',
                     fontsize=16, fontweight='bold', y=0.98)
        
        plt.tight_layout()
        return fig
    
    # Main Application
    
    # Create tabs
    tab1, tab2, tab3= st.tabs(
        ["Animated Simulation", "Protocol Analysis", "Performance Analysis"])
    
    # Tab 1: Animated Simulation
    with tab1:
        st.markdown("### Step-by-Step Animated BB84 Protocol")
        
        # Create placeholders for animation and table (before controls)
        animation_placeholder = st.empty()
        
        # Controls below animation
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            num_steps = st.number_input("Total bits", min_value=20, max_value=100, value=20)
        with col2:
            eve_enabled = st.checkbox("Enable Eve", value=False, 
                                      help="Eve will intercept qubits at specified rate")
            st.session_state.eve_enabled = eve_enabled
            if eve_enabled:
                eve_intercept_rate = st.slider("Eve Intercept Rate (%)", 0, 100, 35, 5, key="eve_rate_tab1")
                st.session_state.eve_intercept_rate = eve_intercept_rate / 100
            else:
                st.session_state.eve_intercept_rate = 0.35
        with col3:
            next_disabled = st.session_state.current_step >= num_steps
            if st.button("Next Step", type="primary", disabled=next_disabled, use_container_width=True, key="next_step_btn"):
                st.session_state.is_running = True
                st.rerun()
        with col4:
            if st.button("Reset", use_container_width=True):
                st.session_state.current_step = 0
                st.session_state.transmission_history = []
                st.session_state.is_running = False
                st.rerun()
        
        # Progress indicator
        if st.session_state.current_step > 0:
            progress = st.session_state.current_step / num_steps
            st.progress(progress, text=f"Progress: {st.session_state.current_step}/{num_steps} transmissions")
        
        # Create placeholders for table and stats
        table_placeholder = st.empty()
        stats_placeholder = st.empty()
        
        # Main animation area
        if st.session_state.is_running and st.session_state.current_step < num_steps:
            step_data = generate_transmission()
            
            # Full animation for single qubit
            for frame in range(31):
                img = create_animation_frame(step_data, frame)
                animation_placeholder.image(img, use_container_width=True)
                time.sleep(0.03)
            
            # Add to history
            st.session_state.transmission_history.append(step_data)
            st.session_state.current_step += 1
            
            # Stop after one transmission
            st.session_state.is_running = False
            st.rerun()
        
        # Display current state (show latest transmission or initial state)
        if len(st.session_state.transmission_history) > 0:
            # Show the most recent transmission
            last_step = st.session_state.transmission_history[-1]
            img = create_animation_frame(last_step, 30)
            animation_placeholder.image(img, use_container_width=True)
            
            # Update table
            df = pd.DataFrame(st.session_state.transmission_history)
            
            # Build columns dynamically based on eve_enabled
            display_data = {
                'Step': df['step'],
                'Alice Bit': df['alice_bit'],
                'Alice Basis': df['alice_basis'],
                'Intercepted': df['intercepted'].map({True: 'YES', False: 'NO'}),
            }
            
            # Add Eve columns only if enabled
            if eve_enabled:
                display_data['Eve Basis'] = df['eve_basis'].fillna('-')
                # Map Eve Result: show the bit if intercepted, otherwise '-'
                eve_result_col = df.apply(
                    lambda row: str(int(row['eve_result'])) if row['intercepted'] and row['eve_result'] is not None else '-',
                    axis=1
                )
                display_data['Eve Result'] = eve_result_col
            
            # Add remaining columns
            display_data.update({
                'Bob Basis': df['bob_basis'],
                'Bob Result': df['bob_result'],
                'Bases Match': df['bases_match'].map({True: 'YES', False: 'NO'}),
                'Error': df['error'].map({True: 'ERROR', False: 'OK', None: 'N/A'}),
            })
            
            display_df = pd.DataFrame(display_data)
            table_placeholder.dataframe(display_df, use_container_width=True, height=300)
            
            # Update stats
            matched = df['bases_match'].sum()
            
            # Calculate QBER - use test bits if complete, otherwise use all matched bits
            qber_display = 0
            qber_for_security = 0
            test_qber_calculated = False
            sifted_df = None
            test_indices = None
            test_indices_set = None
            n_sifted = 0
            
            if matched > 0:
                if st.session_state.current_step >= num_steps:
                    # Simulation complete - calculate QBER from test bits (BB84 protocol)
                    sifted_df = df[df['bases_match'] == True].copy()
                    n_sifted = len(sifted_df)
                    
                    # Use 20% for testing, rest for final key
                    n_test = max(1, int(n_sifted * 0.2))
                    test_indices = np.random.choice(n_sifted, n_test, replace=False)
                    test_indices_set = set(test_indices)
                    
                    # Calculate QBER from test bits
                    test_errors = sum(1 for idx in test_indices
                                    if sifted_df.iloc[idx]['error'] == True)
                    qber_display = (test_errors / n_test * 100) if n_test > 0 else 0
                    qber_for_security = qber_display
                    test_qber_calculated = True
                else:
                    # During simulation - show QBER from all matched bits (approximation)
                    errors = df[df['bases_match'] == True]['error'].sum()
                    qber_display = errors / matched * 100
            
            col1, col2, col3, col4 = stats_placeholder.columns(4)
            with col1:
                st.metric("Total Bits", len(df))
            with col2:
                st.metric("Sifted", f"{matched}")
            with col3:
                if matched > 0:
                    if test_qber_calculated:
                        st.metric("QBER (Test)", f"{qber_display:.1f}%")
                    else:
                        st.metric("QBER", f"{qber_display:.1f}%")
            with col4:
                if eve_enabled:
                    intercepted = df['intercepted'].sum()
                    st.metric("Intercepted", f"{intercepted}")

            # Show formulas used for metrics (LaTeX)
            if matched > 0:
                st.markdown("**Formulas (used for metrics):**")
                st.latex(r"\mathrm{QBER} = \frac{\text{errors}}{n_{\mathrm{test}}} \times 100\%")
                st.latex(r"\text{Sifting Efficiency} = \frac{|\text{sifted key}|}{N_{\text{bits}}} \times 100\%")
                st.latex(r"n_{\mathrm{test}} = \max\left(1,\; \left\lfloor 0.2\times n_{\mathrm{sifted}}\right\rfloor\right)")
            
            # Check if complete
            if st.session_state.current_step >= num_steps:
                if matched > 0 and sifted_df is not None:
                    # QBER already calculated above from test bits
                    qber = qber_for_security
                    
                    # Generate final key from remaining bits
                    final_indices = [i for i in range(n_sifted) if i not in test_indices_set]
                    alice_key = [int(sifted_df.iloc[idx]['alice_bit']) for idx in final_indices]
                    bob_key = [int(sifted_df.iloc[idx]['bob_result']) for idx in final_indices]
                    
                    if qber < 11:
                        st.success("SECURE - QBER below 11%. No eavesdropping detected!")
                        st.markdown("#### Generated Shared Key")
                        # Build the shared (common) final key: keep only positions where Alice and Bob agree
                        shared_key = [a for a, b in zip(alice_key, bob_key) if a == b]
                        if len(shared_key) > 0:
                            key_display_length = min(50, len(shared_key))
                            st.code(f"Shared Key (first {key_display_length} bits): {''.join(map(str, shared_key[:key_display_length]))}")
                            if len(shared_key) > 50:
                                st.caption(f"Showing first 50 of {len(shared_key)} bits")
                            # Warn if there were mismatches in the final keys
                            mismatches = sum(1 for a, b in zip(alice_key, bob_key) if a != b)
                            if mismatches == 0:
                                st.success("✓ Shared key derived with no mismatches")
                            else:
                                st.warning(f"⚠ {mismatches} mismatch(es) were removed when forming the shared key")
                        else:
                            st.warning("No shared key bits available after sifting and testing.")
                    else:
                        st.error("🚨 **Security Alert**: QBER exceeds 11% - Possible eavesdropping detected!")
                        st.info("💡 **What this means**: High error rate suggests communication is compromised. In real quantum cryptography, the key would be discarded and communication restarted.")
                        st.warning("The quantum channel is not secure. Do not use any key generated under these conditions.")
                
        else:
            # Show initial state
            initial_data = {
                'alice_bit': 0, 'alice_basis': 'Z', 'bob_basis': 'Z',
                'bob_result': 0, 'eve_active': eve_enabled, 'intercepted': False
            }
            img = create_animation_frame(initial_data, 0)
            animation_placeholder.image(img, use_container_width=True)
            st.info("Click Next Step to begin transmitting qubits one at a time!")
    
    # Tab 2: Protocol Analysis
    with tab2:
        st.markdown("### Run Complete BB84 Protocol with Qiskit Simulation")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### Parameters")
            n_bits_single = st.slider("Number of Bits", 50, 500, 100, 10)
            noise_single = st.slider("Channel Noise (%)", 0.0, 30.0, 5.0, 0.5)
            
            eve_analysis = st.checkbox("Enable Eve Eavesdropping", value=False, key="eve_analysis")
            eve_prob_analysis = 50
            if eve_analysis:
                eve_prob_analysis = st.slider("Eve Intercept Rate (%)", 0, 100, 50, 5, key="eve_prob_analysis")
            
            run_single = st.button("Run Protocol", type="primary", use_container_width=True)
        
        with col2:
            if run_single:
                with st.spinner("Running BB84 protocol with Qiskit..."):
                    progress_bar = st.progress(0)
                    
                    def update_progress(val):
                        progress_bar.progress(val)
                    
                    bb84 = BB84Protocol(n_bits=int(n_bits_single), noise_prob=noise_single / 100)
                    if eve_analysis:
                        result = bb84.run_protocol(eve_intercept=True, eve_prob=eve_prob_analysis/100, 
                                                   progress_callback=update_progress)
                    else:
                        result = bb84.run_protocol(progress_callback=update_progress)
                    
                    st.markdown("#### Results")
                    metric_cols = st.columns(4)
                    with metric_cols[0]:
                        st.metric("Initial Bits", result['initial_bits'])
                    with metric_cols[1]:
                        st.metric("Sifted Bits", result['sifted_bits'])
                    with metric_cols[2]:
                        st.metric("Final Key", result['final_key_length'])
                    with metric_cols[3]:
                        st.metric("QBER", f"{result['qber'] * 100:.2f}%")
                    
                    if result['secure']:
                        st.success("SECURE - No eavesdropping detected!")
                    else:
                        st.error("⚠️ **Channel Insecure**: High QBER indicates potential eavesdropping")
                        st.info("💡 Consider disabling Eve or using different parameters to see secure key generation.")
                    
                    st.markdown("#### Protocol Flow")
                    flow_fig = create_protocol_flow_viz(result)
                    st.pyplot(flow_fig)
                    
                    st.markdown("#### Key Comparison")
                    if len(bb84.final_key_alice) > 0:
                        key_fig = create_key_comparison_plot(bb84.final_key_alice, bb84.final_key_bob)
                        st.pyplot(key_fig)
                        
                        # Compute shared final key (positions where Alice and Bob agree)
                        shared_key = [a for a, b in zip(bb84.final_key_alice, bb84.final_key_bob) if a == b]
                        st.markdown("#### Shared Key (derived from matching final bits)")
                        if len(shared_key) > 0:
                            st.code(f"Shared Key (first {min(50, len(shared_key))} bits): {''.join(map(str, shared_key[:50]))}")
                        else:
                            st.warning("No shared key bits available after sifting and testing.")
                    else:
                        st.warning("No final key generated. Try with less noise.")
                    
                    with st.expander("Detailed Statistics"):
                        st.write(f"**Sifting Efficiency:** {result['sifting_efficiency'] * 100:.1f}%")
                        st.latex(r"\text{Sifting Efficiency} = \frac{|\text{sifted key}|}{N_{\text{bits}}} \times 100\%")
                        st.write(f"**Errors Found:** {result['errors']} in {result['test_bits']} test bits")
                        st.latex(r"\mathrm{QBER} = \frac{\text{errors}}{n_{\mathrm{test}}} \times 100\%")
                        st.write(f"**Security Threshold:** 11%")
                        st.write(f"**Keys Match:** {'Yes' if result['keys_match'] else 'No'}")
                        if eve_analysis:
                            st.write(f"**Eve Intercepts:** {result['eve_stats']['interceptions']} ({result['eve_stats']['intercept_rate']*100:.1f}%)")
                    
                    # Store simulation data for PDF report
                    from lab_config import LABS
                    lab_id = None
                    for name, config in LABS.items():
                        if config.get('module') == 'bb84':
                            lab_id = config['id']
                            break
                    
                    if lab_id:
                        metrics = {
                            'Initial Bits': str(result['initial_bits']),
                            'Sifted Bits': str(result['sifted_bits']),
                            'Final Key Length': str(result['final_key_length']),
                            'QBER': f"{result['qber'] * 100:.2f}%",
                            'Sifting Efficiency': f"{result['sifting_efficiency'] * 100:.1f}%",
                            'Security Status': 'SECURE' if result['secure'] else 'INSECURE',
                            'Keys Match': 'Yes' if result['keys_match'] else 'No',
                            'Channel Noise': f"{noise_single}%"
                        }
                        if eve_analysis:
                            metrics['Eve Intercept Rate'] = f"{eve_prob_analysis}%"
                            metrics['Eve Interceptions'] = str(result['eve_stats']['interceptions'])
                        
                        # Prepare measurements from final keys
                        measurements = {}
                        if len(bb84.final_key_alice) > 0:
                            # Store measurements from shared key (common bits only)
                            shared_key = [a for a, b in zip(bb84.final_key_alice, bb84.final_key_bob) if a == b]
                            for i in range(min(10, len(shared_key))):
                                measurements[f'Key_Bit_{i}'] = int(shared_key[i])
                        
                        figures = [
                            save_figure_to_data(flow_fig, 'Protocol Flow'),
                            save_figure_to_data(key_fig, 'Key Comparison') if len(bb84.final_key_alice) > 0 else None
                        ]
                        figures = [f for f in figures if f is not None]
                        
                        store_simulation_data(lab_id, metrics=metrics, measurements=measurements, figures=figures)
    
    # Tab 3: Performance Analysis
    with tab3:
        st.markdown("### BB84 Performance Analysis - Vary One Parameter")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### Configuration")
            
            # Parameter to vary
            varied_param = st.selectbox(
                "Parameter to Vary",
                ["Noise", "Number of Bits", "Distance", "Number of Eves", "Fading"],
                key="varied_param"
            )
            
            n_trials_perf = st.slider("Trials per Level", 1, 10, 3, 1, key="perf_trials")
            
            st.markdown("#### Fixed Parameters")
            
            # Fixed parameters
            if varied_param != "Number of Bits":
                fixed_bits = st.slider("Number of Bits", 50, 500, 150, 50, key="fixed_bits")
            else:
                fixed_bits = 150
                st.metric("Number of Bits", f"Variable (50-500)")
            
            if varied_param != "Noise":
                fixed_noise = st.slider("Channel Noise (%)", 0.0, 30.0, 5.0, 0.5, key="fixed_noise")
            else:
                fixed_noise = 5.0
                st.metric("Channel Noise", "Variable (0-30%)")
            
            if varied_param != "Distance":
                fixed_distance = st.slider("Distance (km)", 1, 1000, 100, 100, key="fixed_distance")
            else:
                fixed_distance = 100
                st.metric("Distance", "Variable (1-1000 km)")
            
            if varied_param != "Number of Eves":
                fixed_eves = st.slider("Number of Eves", 0, 5, 0, 1, key="fixed_eves")
            else:
                fixed_eves = 0
                st.metric("Number of Eves", "Variable (0-5)")
            
            if varied_param != "Fading":
                fixed_fading = st.slider("Fading Factor", 0.0, 1.0, 0.1, 0.1, key="fixed_fading")
            else:
                fixed_fading = 0.1
                st.metric("Fading Factor", "Variable (0.0-1.0)")
            
            # Eve Settings (only show if not varying Number of Eves)
            if varied_param != "Number of Eves":
                st.markdown("#### Eve Settings")
                enable_eve_perf = st.checkbox("Enable Eve Eavesdropping", value=False, key="eve_perf")
                eve_rate_perf = 50
                if enable_eve_perf:
                    eve_rate_perf = st.slider("Eve Intercept Rate (%)", 0, 100, 50, 5, key="eve_rate_perf")
            else:
                enable_eve_perf = True
                eve_rate_perf = 50
            
            analyze_btn = st.button("Run Analysis", type="primary", use_container_width=True)
        
        with col2:
            if analyze_btn:
                with st.spinner("Running performance analysis..."):
                    results_data = {
                        'qber': [], 'key_length': [], 'secure_pct': []
                    }
                    
                    # Define varied parameter ranges and values
                    param_configs = {
                        "Noise": {
                            'range': np.linspace(0, 30, 8),
                            'label': 'noise',
                            'unit': '%'
                        },
                        "Number of Bits": {
                            'range': np.array([50, 100, 150, 200, 300, 400, 500]),
                            'label': 'bits',
                            'unit': 'bits'
                        },
                        "Distance": {
                            'range': np.linspace(1, 1000, 8),
                            'label': 'distance',
                            'unit': 'km'
                        },
                        "Number of Eves": {
                            'range': np.array([0, 1, 2, 3, 4, 5]),
                            'label': 'eves',
                            'unit': 'Eves'
                        },
                        "Fading": {
                            'range': np.linspace(0.0, 1.0, 8),
                            'label': 'fading',
                            'unit': 'factor'
                        }
                    }
                    
                    config = param_configs[varied_param]
                    results_data[config['label']] = []
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    total_runs = len(config['range']) * int(n_trials_perf)
                    current_run = 0
                    
                    for param_value in config['range']:
                        qbers, key_lengths = [], []
                        secure_count = 0
                        
                        # Format display value appropriately
                        if varied_param == "Number of Eves" or varied_param == "Number of Bits":
                            display_value = int(param_value)
                        else:
                            display_value = param_value
                        
                        for trial in range(int(n_trials_perf)):
                            status_text.text(f"Testing {varied_param}: {display_value} {config['unit']} - Trial {trial + 1}/{int(n_trials_perf)}")
                            
                            # Determine parameters based on what's being varied
                            if varied_param == "Noise":
                                noise_to_use = param_value / 100
                                bits_to_use = fixed_bits
                            elif varied_param == "Number of Bits":
                                noise_to_use = fixed_noise / 100
                                bits_to_use = int(param_value)
                            else:
                                noise_to_use = fixed_noise / 100
                                bits_to_use = fixed_bits
                            
                            bb84 = BB84Protocol(n_bits=bits_to_use, noise_prob=noise_to_use)
                            if enable_eve_perf:
                                result = bb84.run_protocol(eve_intercept=True, eve_prob=eve_rate_perf/100)
                            else:
                                result = bb84.run_protocol()
                            qbers.append(result['qber'] * 100)
                            key_lengths.append(result['final_key_length'])
                            if result['secure']:
                                secure_count += 1
                            
                            current_run += 1
                            progress_bar.progress(current_run / total_runs)
                        
                        # Store as integer for discrete parameters
                        stored_value = int(param_value) if varied_param in ["Number of Eves", "Number of Bits"] else param_value
                        results_data[config['label']].append(stored_value)
                        results_data['qber'].append(np.mean(qbers))
                        results_data['key_length'].append(np.mean(key_lengths))
                        results_data['secure_pct'].append(secure_count / int(n_trials_perf) * 100)
                    
                    results_df = pd.DataFrame(results_data)
                    
                    # Sort by the varied parameter to ensure correct order
                    results_df = results_df.sort_values(by=config['label']).reset_index(drop=True)
                    
                    status_text.text("Analysis complete!")
                    
                    st.markdown("#### Summary")
                    metric_cols = st.columns(4)
                    with metric_cols[0]:
                        st.metric("Lowest QBER", f"{results_df['qber'].min():.2f}%")
                    with metric_cols[1]:
                        st.metric("Highest QBER", f"{results_df['qber'].max():.2f}%")
                    with metric_cols[2]:
                        st.metric("Avg Key Length", f"{results_df['key_length'].mean():.0f}")
                    with metric_cols[3]:
                        st.metric("Avg Success", f"{results_df['secure_pct'].mean():.1f}%")
                    # Show formulas used in performance analysis
                    st.markdown("**Formulas used:**")
                    st.latex(r"\mathrm{QBER} = \frac{\text{errors}}{n_{\mathrm{test}}} \times 100\%")
                    st.latex(r"\text{Sifting Efficiency} = \frac{|\text{sifted key}|}{N_{\text{bits}}} \times 100\%")
                    st.latex(r"|K_{\mathrm{final}}| = n_{\mathrm{sifted}} - n_{\mathrm{test}}")
                    
                    st.markdown("#### Performance Charts")
                    perf_fig = create_performance_plots(results_df, varied_param)
                    st.pyplot(perf_fig)
                    
                    with st.expander("View & Download Raw Data"):
                        st.dataframe(results_df, use_container_width=True)
                        csv = results_df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name="bb84_performance_analysis.csv",
                            mime="text/csv"
                        )
    
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <p style="text-align: center; color: #666; font-size: 0.9rem;">
    BB84 Quantum Key Distribution Simulator | Built with Qiskit & Streamlit<br>
    Educational tool for understanding quantum cryptography
    </p>
    """, unsafe_allow_html=True)
