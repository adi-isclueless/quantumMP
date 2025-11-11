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
        
        if eve_active and np.random.random() > 0.3:
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
    
    def create_performance_plots(results_df):
        """Create comprehensive performance analysis plots"""
        fig = plt.figure(figsize=(16, 12))
        gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)
        
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
        
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.plot(results_df['noise'], results_df['key_length'],
                 's-', linewidth=3, markersize=10, color='#3498db', label='Key Length')
        ax2.set_xlabel('Channel Noise (%)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Final Key Length (bits)', fontsize=12, fontweight='bold')
        ax2.set_title('Final Key Length vs Channel Noise', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        ax3 = fig.add_subplot(gs[1, 0])
        ax3.plot(results_df['noise'], results_df['sifting_eff'],
                 '^-', linewidth=3, markersize=10, color='#2ecc71', label='Sifting Efficiency')
        ax3.axhline(y=50, color='gray', linestyle=':', linewidth=2, label='Theoretical (50%)')
        ax3.set_xlabel('Channel Noise (%)', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Sifting Efficiency (%)', fontsize=12, fontweight='bold')
        ax3.set_title('Sifting Efficiency (Basis Matching Rate)', fontsize=14, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        
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
        
        for bar in bars:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width() / 2., height,
                     f'{height:.0f}%', ha='center', va='bottom', fontweight='bold')
        
        fig.suptitle('BB84 Quantum Key Distribution - Comprehensive Performance Analysis',
                     fontsize=18, fontweight='bold', y=0.995)
        
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
            num_steps = st.number_input("Total Transmissions", min_value=1, max_value=100, value=20)
        with col2:
            eve_enabled = st.checkbox("Enable Eve", value=False, 
                                      help="Eve will intercept ~70% of qubits")
            st.session_state.eve_enabled = eve_enabled
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
            display_df = pd.DataFrame({
                'Step': df['step'],
                'Alice Bit': df['alice_bit'],
                'Alice Basis': df['alice_basis'],
                'Bob Basis': df['bob_basis'],
                'Bob Result': df['bob_result'],
                'Bases Match': df['bases_match'].map({True: 'YES', False: 'NO'}),
                'Error': df['error'].map({True: 'ERROR', False: 'OK', None: 'N/A'}),
            })
            
            if eve_enabled:
                display_df['Intercepted'] = df['intercepted'].map({True: 'YES', False: 'NO'})
                display_df['Eve Basis'] = df['eve_basis'].fillna('-')
            
            table_placeholder.dataframe(display_df, use_container_width=True, height=150)
            
            # Update stats
            matched = df['bases_match'].sum()
            col1, col2, col3, col4 = stats_placeholder.columns(4)
            with col1:
                st.metric("Total Bits", len(df))
            with col2:
                st.metric("Sifted", f"{matched}")
            with col3:
                if matched > 0:
                    errors = df[df['bases_match'] == True]['error'].sum()
                    qber = errors / matched * 100
                    st.metric("QBER", f"{qber:.1f}%")
            with col4:
                if eve_enabled:
                    intercepted = df['intercepted'].sum()
                    st.metric("Intercepted", f"{intercepted}")
            
            # Check if complete
            if st.session_state.current_step >= num_steps:
                if matched > 0:
                    errors = df[df['bases_match'] == True]['error'].sum()
                    qber = errors / matched * 100
                    if qber < 11:
                        st.success("SECURE - QBER below 11%. No eavesdropping detected!")
                    else:
                        st.error("INSECURE - QBER exceeds 11%. Eavesdropping detected!")
                
                st.success("All transmissions complete!")
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
                        st.error("INSECURE - Possible eavesdropping!")
                    
                    st.markdown("#### Protocol Flow")
                    flow_fig = create_protocol_flow_viz(result)
                    st.pyplot(flow_fig)
                    
                    st.markdown("#### Key Comparison")
                    if len(bb84.final_key_alice) > 0:
                        key_fig = create_key_comparison_plot(bb84.final_key_alice, bb84.final_key_bob)
                        st.pyplot(key_fig)
                        
                        st.markdown("#### Key Samples (first 50 bits)")
                        st.code(f"Alice: {''.join(map(str, bb84.final_key_alice[:50]))}")
                        st.code(f"Bob:   {''.join(map(str, bb84.final_key_bob[:50]))}")
                    else:
                        st.warning("No final key generated. Try with less noise.")
                    
                    with st.expander("Detailed Statistics"):
                        st.write(f"**Sifting Efficiency:** {result['sifting_efficiency'] * 100:.1f}%")
                        st.write(f"**Errors Found:** {result['errors']} in {result['test_bits']} test bits")
                        st.write(f"**Security Threshold:** 11%")
                        st.write(f"**Keys Match:** {'Yes' if result['keys_match'] else 'No'}")
                        if eve_analysis:
                            st.write(f"**Eve Intercepts:** {result['eve_stats']['interceptions']} ({result['eve_stats']['intercept_rate']*100:.1f}%)")
    
    # Tab 3: Performance Analysis
    with tab3:
        st.markdown("### Analyze BB84 Performance Across Noise Levels")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### Parameters")
            n_bits_perf = st.slider("Bits per Trial", 100, 500, 200, 50, key="perf_bits")
            n_trials = st.slider("Trials per Level", 1, 20, 5, 1, key="perf_trials")
            noise_min = st.slider("Min Noise (%)", 0.0, 15.0, 0.0, 0.5, key="perf_min")
            noise_max = st.slider("Max Noise (%)", 5.0, 30.0, 20.0, 0.5, key="perf_max")
            noise_steps = st.slider("Noise Steps", 5, 15, 8, 1, key="perf_steps")
            
            analyze_btn = st.button("Analyze Performance", type="primary", use_container_width=True)
        
        with col2:
            if analyze_btn:
                with st.spinner("Running performance analysis..."):
                    noise_levels = np.linspace(noise_min / 100, noise_max / 100, int(noise_steps))
                    
                    results_data = {
                        'noise': [], 'qber': [], 'sifting_eff': [],
                        'key_length': [], 'secure_pct': []
                    }
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    total_runs = len(noise_levels) * int(n_trials)
                    current_run = 0
                    
                    for noise in noise_levels:
                        qbers, sifting_effs, key_lengths = [], [], []
                        secure_count = 0
                        
                        for trial in range(int(n_trials)):
                            status_text.text(f"Testing {noise * 100:.1f}% noise - Trial {trial + 1}/{int(n_trials)}")
                            
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
                    
                    st.markdown("#### Performance Plots")
                    perf_fig = create_performance_plots(results_df)
                    st.pyplot(perf_fig)
                    
                    with st.expander("View & Download Raw Data"):
                        st.dataframe(results_df, use_container_width=True)
                        csv = results_df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name="bb84_performance.csv",
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
