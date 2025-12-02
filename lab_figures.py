"""
Default figures, charts, and circuit diagrams for each lab.
These are generated automatically for reports even if user doesn't simulate.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from qiskit import QuantumCircuit
from qiskit.visualization import circuit_drawer
from certificate import save_figure_to_data
import io


def create_bb84_figures():
    """BB84 Quantum Key Distribution figures"""
    figures = []
    
    # Figure 1: BB84 Protocol Flow Diagram
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    ax.text(0.5, 0.95, 'BB84 Quantum Key Distribution Protocol', 
            ha='center', fontsize=14, fontweight='bold', transform=ax.transAxes)
    
    # Protocol steps
    steps = [
        "1. Alice sends random qubits\n   in random bases (X or Z)",
        "2. Bob receives qubits and\n   measures in random bases",
        "3. Bob announces his bases\n   (publicly)",
        "4. Alice confirms which\n   bases match (publicly)",
        "5. Matching bases produce\n   the shared key"
    ]
    
    y_pos = 0.8
    for i, step in enumerate(steps):
        color = '#667eea' if i % 2 == 0 else '#764ba2'
        ax.add_patch(mpatches.FancyBboxPatch((0.05, y_pos - 0.12), 0.9, 0.1,
                     boxstyle="round,pad=0.01", facecolor=color, alpha=0.3, 
                     edgecolor=color, transform=ax.transAxes))
        ax.text(0.5, y_pos - 0.07, step, ha='center', va='center', 
               fontsize=10, transform=ax.transAxes)
        y_pos -= 0.15
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    figures.append(save_figure_to_data(fig, 'BB84 Protocol Overview'))
    plt.close(fig)
    
    # Figure 2: Quantum Bases Representation
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Rectilinear basis (Z)
    ax = axes[0]
    ax.set_title('Rectilinear Basis (Z)', fontsize=12, fontweight='bold')
    ax.quiver(0, 0, 1, 0, angles='xy', scale_units='xy', scale=1, color='red', width=0.01, label='|0⟩')
    ax.quiver(0, 0, 0, 1, angles='xy', scale_units='xy', scale=1, color='blue', width=0.01, label='|1⟩')
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Diagonal basis (X)
    ax = axes[1]
    ax.set_title('Diagonal Basis (X)', fontsize=12, fontweight='bold')
    ax.quiver(0, 0, 1/np.sqrt(2), 1/np.sqrt(2), angles='xy', scale_units='xy', scale=1, 
             color='green', width=0.01, label='|+⟩')
    ax.quiver(0, 0, -1/np.sqrt(2), 1/np.sqrt(2), angles='xy', scale_units='xy', scale=1, 
             color='orange', width=0.01, label='|−⟩')
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    plt.tight_layout()
    figures.append(save_figure_to_data(fig, 'Quantum Measurement Bases'))
    plt.close(fig)
    
    return figures


def create_different_states_figures():
    """Measurement in Different Bases figures"""
    figures = []
    
    # Figure 1: Quantum State Vectors
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.text(0.5, 0.95, 'Quantum States and Their Representations', 
            ha='center', fontsize=14, fontweight='bold', transform=ax.transAxes)
    
    states = [
        ('|0⟩', '(1, 0)', '#FF6B6B'),
        ('|1⟩', '(0, 1)', '#4ECDC4'),
        ('|+⟩ = (|0⟩ + |1⟩)/√2', '(1/√2, 1/√2)', '#45B7D1'),
        ('|−⟩ = (|0⟩ − |1⟩)/√2', '(1/√2, −1/√2)', '#FFA07A'),
    ]
    
    y_pos = 0.8
    for state, vec, color in states:
        ax.add_patch(mpatches.FancyBboxPatch((0.05, y_pos - 0.1), 0.9, 0.08,
                     boxstyle="round,pad=0.01", facecolor=color, alpha=0.2,
                     edgecolor=color, transform=ax.transAxes))
        ax.text(0.15, y_pos - 0.06, state, fontsize=11, fontweight='bold', 
               transform=ax.transAxes, va='center')
        ax.text(0.7, y_pos - 0.06, vec, fontsize=10, 
               transform=ax.transAxes, va='center', family='monospace')
        y_pos -= 0.15
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    figures.append(save_figure_to_data(fig, 'Quantum States Reference'))
    plt.close(fig)
    
    # Figure 2: Measurement Bases
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    bases = [
        ('Z Basis', ['|0⟩', '|1⟩']),
        ('X Basis', ['|+⟩', '|−⟩']),
        ('Y Basis', ['|+i⟩', '|−i⟩']),
    ]
    
    for idx, (basis_name, outcomes) in enumerate(bases):
        ax = axes[idx]
        ax.set_title(basis_name, fontsize=12, fontweight='bold')
        colors = ['#FF6B6B', '#4ECDC4']
        for i, outcome in enumerate(outcomes):
            ax.add_patch(mpatches.Rectangle((0.2, 0.5 - i*0.3), 0.6, 0.2, 
                         facecolor=colors[i], alpha=0.3, edgecolor=colors[i], linewidth=2))
            ax.text(0.5, 0.6 - i*0.3, outcome, ha='center', va='center', fontsize=12, fontweight='bold')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
    
    plt.tight_layout()
    figures.append(save_figure_to_data(fig, 'Measurement Bases Overview'))
    plt.close(fig)
    
    return figures


def create_multi_qubit_superposition_figures():
    """Multi-Qubit Superposition figures"""
    figures = []
    
    # Figure 1: Circuit Diagram for 3-qubit superposition
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.h(1)
    qc.h(2)
    qc.measure_all()
    
    circuit_img = circuit_drawer(qc, output='mpl', scale=0.7)
    figures.append(save_figure_to_data(circuit_img, 'Three-Qubit Equal Superposition Circuit'))
    plt.close(circuit_img)
    
    # Figure 2: Superposition States Visualization
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.text(0.5, 0.95, 'N-Qubit Equal Superposition States', 
            ha='center', fontsize=14, fontweight='bold', transform=ax.transAxes)
    
    num_states = [2, 3, 4, 5]
    y_pos = 0.8
    
    for n in num_states:
        num_outcomes = 2**n
        state_str = f'({"|0⟩" + " + " + "|1⟩" * (n-1)}) / √{num_outcomes}'
        outcomes_str = f'{num_outcomes} equally probable outcomes'
        
        ax.add_patch(mpatches.FancyBboxPatch((0.05, y_pos - 0.12), 0.9, 0.1,
                     boxstyle="round,pad=0.01", facecolor='#667eea', alpha=0.2,
                     edgecolor='#667eea', transform=ax.transAxes))
        ax.text(0.15, y_pos - 0.07, f'{n} Qubits:', fontsize=11, fontweight='bold', 
               transform=ax.transAxes, va='center')
        ax.text(0.7, y_pos - 0.07, outcomes_str, fontsize=10, 
               transform=ax.transAxes, va='center')
        y_pos -= 0.15
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    figures.append(save_figure_to_data(fig, 'N-Qubit Superposition States'))
    plt.close(fig)
    
    return figures


def create_ghz_state_figures():
    """GHZ State figures"""
    figures = []
    
    # Figure 1: GHZ Circuit
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(0, 2)
    qc.measure_all()
    
    circuit_img = circuit_drawer(qc, output='mpl', scale=0.7)
    figures.append(save_figure_to_data(circuit_img, 'GHZ State Circuit: (|000⟩ + |111⟩)/√2'))
    plt.close(circuit_img)
    
    # Figure 2: GHZ State Properties
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.text(0.5, 0.95, 'GHZ State: Perfect Entanglement', 
            ha='center', fontsize=14, fontweight='bold', transform=ax.transAxes)
    
    properties = [
        ('State', '|000⟩ + |111⟩) / √2'),
        ('Entanglement', 'Maximally entangled (3-qubit GHZ state)'),
        ('Measurement', 'All qubits always agree (correlated)'),
        ('Applications', 'Quantum cryptography, teleportation, error correction'),
    ]
    
    y_pos = 0.8
    for prop, value in properties:
        ax.add_patch(mpatches.FancyBboxPatch((0.05, y_pos - 0.1), 0.9, 0.08,
                     boxstyle="round,pad=0.01", facecolor='#764ba2', alpha=0.2,
                     edgecolor='#764ba2', transform=ax.transAxes))
        ax.text(0.15, y_pos - 0.06, f'{prop}:', fontsize=11, fontweight='bold', 
               transform=ax.transAxes, va='center')
        ax.text(0.4, y_pos - 0.06, value, fontsize=10, 
               transform=ax.transAxes, va='center')
        y_pos -= 0.15
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    figures.append(save_figure_to_data(fig, 'GHZ State Properties'))
    plt.close(fig)
    
    return figures


def create_bell_state_figures():
    """Bell State / W State / Entanglement figures"""
    figures = []
    
    # Figure 1: All Four Bell State Circuits (as separate images in one composite)
    bell_state_configs = [
        ('|Φ⁺⟩ = (|00⟩ + |11⟩)/√2', 0),
        ('|Φ⁻⟩ = (|00⟩ − |11⟩)/√2', 1),
        ('|Ψ⁺⟩ = (|01⟩ + |10⟩)/√2', 2),
        ('|Ψ⁻⟩ = (|01⟩ − |10⟩)/√2', 3),
    ]
    
    # Create individual circuit figures
    for state_name, gate_config in bell_state_configs:
        qc = QuantumCircuit(2)
        
        # Build circuit based on configuration
        if gate_config == 0:  # |Φ⁺⟩
            qc.h(0)
            qc.cx(0, 1)
        elif gate_config == 1:  # |Φ⁻⟩
            qc.h(0)
            qc.cx(0, 1)
            qc.z(0)
        elif gate_config == 2:  # |Ψ⁺⟩
            qc.h(0)
            qc.cx(0, 1)
            qc.x(1)
        elif gate_config == 3:  # |Ψ⁻⟩
            qc.h(0)
            qc.cx(0, 1)
            qc.x(1)
            qc.z(0)
        
        circuit_img = circuit_drawer(qc, output='mpl', scale=0.7)
        figures.append(save_figure_to_data(circuit_img, f'{state_name} Circuit'))
        plt.close(circuit_img)
    
    # Figure 2: Bell States Overview
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.text(0.5, 0.95, 'Bell Entangled States (2-Qubit)', 
            ha='center', fontsize=14, fontweight='bold', transform=ax.transAxes)
    
    bell_states = [
        '|Φ⁺⟩ = (|00⟩ + |11⟩)/√2',
        '|Φ⁻⟩ = (|00⟩ − |11⟩)/√2',
        '|Ψ⁺⟩ = (|01⟩ + |10⟩)/√2',
        '|Ψ⁻⟩ = (|01⟩ − |10⟩)/√2',
    ]
    
    y_pos = 0.8
    for state in bell_states:
        ax.add_patch(mpatches.FancyBboxPatch((0.1, y_pos - 0.1), 0.8, 0.08,
                     boxstyle="round,pad=0.01", facecolor='#45B7D1', alpha=0.3,
                     edgecolor='#45B7D1', transform=ax.transAxes))
        ax.text(0.5, y_pos - 0.06, state, fontsize=12, ha='center',
               transform=ax.transAxes, va='center', family='monospace')
        y_pos -= 0.15
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    figures.append(save_figure_to_data(fig, 'Four Bell Entangled States'))
    plt.close(fig)
    
    return figures


def create_w_state_figures():
    """W State figures"""
    figures = []
    
    # Figure 1: W State Circuit
    qc = QuantumCircuit(3)
    qc.x(0)
    qc.cx(0, 1)
    qc.h(1)
    qc.cx(1, 2)
    qc.measure_all()
    
    circuit_img = circuit_drawer(qc, output='mpl', scale=0.7)
    figures.append(save_figure_to_data(circuit_img, 'W State Circuit: (|001⟩ + |010⟩ + |100⟩)/√3'))
    plt.close(circuit_img)
    
    # Figure 2: W vs GHZ Comparison
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.text(0.5, 0.95, 'W State vs GHZ State Comparison', 
            ha='center', fontsize=14, fontweight='bold', transform=ax.transAxes)
    
    comparisons = [
        ('Definition', 'W: (|001⟩ + |010⟩ + |100⟩)/√3', 'GHZ: (|000⟩ + |111⟩)/√2'),
        ('Nonzero Terms', 'W has 3 terms with weight 1', 'GHZ has 2 terms with weight 1'),
        ('Robustness', 'W more robust to qubit loss', 'GHZ sensitive to qubit loss'),
        ('Applications', 'Better for error correction', 'Better for cryptography'),
    ]
    
    y_pos = 0.8
    for label, w_prop, ghz_prop in comparisons:
        # Label
        ax.text(0.05, y_pos - 0.06, label, fontsize=10, fontweight='bold', 
               transform=ax.transAxes, va='center')
        # W property
        ax.add_patch(mpatches.Rectangle((0.25, y_pos - 0.09), 0.35, 0.06,
                     facecolor='#4ECDC4', alpha=0.2, edgecolor='#4ECDC4', transform=ax.transAxes))
        ax.text(0.425, y_pos - 0.06, w_prop, fontsize=9, 
               transform=ax.transAxes, va='center', ha='center')
        # GHZ property
        ax.add_patch(mpatches.Rectangle((0.62, y_pos - 0.09), 0.33, 0.06,
                     facecolor='#FF6B6B', alpha=0.2, edgecolor='#FF6B6B', transform=ax.transAxes))
        ax.text(0.785, y_pos - 0.06, ghz_prop, fontsize=9, 
               transform=ax.transAxes, va='center', ha='center')
        y_pos -= 0.15
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    figures.append(save_figure_to_data(fig, 'W vs GHZ State Comparison'))
    plt.close(fig)
    
    return figures


def create_bit_flip_code_figures():
    """3-Qubit Bit Flip Error Correction figures"""
    figures = []
    
    # Figure 1: Bit Flip Code Circuit
    qc = QuantumCircuit(3)
    qc.cx(0, 1)
    qc.cx(0, 2)
    qc.measure_all()
    
    circuit_img = circuit_drawer(qc, output='mpl', scale=0.7)
    figures.append(save_figure_to_data(circuit_img, '3-Qubit Bit Flip Code: Encoding'))
    plt.close(circuit_img)
    
    # Figure 2: Error Detection Process
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.text(0.5, 0.95, '3-Qubit Bit Flip Error Correction', 
            ha='center', fontsize=14, fontweight='bold', transform=ax.transAxes)
    
    steps = [
        ('Step 1', 'Encoding: |ψ⟩ → |ψψψ⟩ (copy logical qubit)'),
        ('Step 2', 'Transmit: Send through noisy channel'),
        ('Step 3', 'Error Detection: Measure parity checks'),
        ('Step 4', 'Decode: Majority vote to identify error'),
        ('Step 5', 'Correction: Apply X gate if needed'),
    ]
    
    y_pos = 0.82
    for step_num, description in steps:
        color = '#667eea' if steps.index((step_num, description)) % 2 == 0 else '#764ba2'
        ax.add_patch(mpatches.FancyBboxPatch((0.05, y_pos - 0.08), 0.9, 0.07,
                     boxstyle="round,pad=0.01", facecolor=color, alpha=0.2,
                     edgecolor=color, transform=ax.transAxes))
        ax.text(0.08, y_pos - 0.045, step_num, fontsize=11, fontweight='bold', 
               transform=ax.transAxes, va='center')
        ax.text(0.25, y_pos - 0.045, description, fontsize=10, 
               transform=ax.transAxes, va='center')
        y_pos -= 0.12
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    figures.append(save_figure_to_data(fig, 'Bit Flip Error Correction Process'))
    plt.close(fig)
    
    return figures


def create_phase_flip_code_figures():
    """3-Qubit Phase Flip Error Correction figures"""
    figures = []
    
    # Figure 1: Phase Flip Code Circuit
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.h(1)
    qc.h(2)
    qc.cx(0, 1)
    qc.cx(0, 2)
    qc.measure_all()
    
    circuit_img = circuit_drawer(qc, output='mpl', scale=0.7)
    figures.append(save_figure_to_data(circuit_img, '3-Qubit Phase Flip Code: Encoding'))
    plt.close(circuit_img)
    
    # Figure 2: Phase Flip vs Bit Flip
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.text(0.5, 0.95, 'Phase Flip vs Bit Flip Error Correction', 
            ha='center', fontsize=14, fontweight='bold', transform=ax.transAxes)
    
    comparisons = [
        ('Error Type', 'Bit Flip: X error', 'Phase Flip: Z error'),
        ('Detection', 'Parity checks in Z basis', 'Parity checks in X basis'),
        ('Correction', 'Apply X gate to affected qubit', 'Apply Z gate to affected qubit'),
        ('Circuit', 'CNOT-based encoding', 'Hadamard before/after CNOT'),
    ]
    
    y_pos = 0.8
    for label, bit_flip, phase_flip in comparisons:
        ax.text(0.03, y_pos - 0.06, label, fontsize=10, fontweight='bold', 
               transform=ax.transAxes, va='center')
        ax.add_patch(mpatches.Rectangle((0.22, y_pos - 0.085), 0.26, 0.055,
                     facecolor='#FF6B6B', alpha=0.2, edgecolor='#FF6B6B', transform=ax.transAxes))
        ax.text(0.35, y_pos - 0.06, bit_flip, fontsize=8, 
               transform=ax.transAxes, va='center', ha='center')
        ax.add_patch(mpatches.Rectangle((0.52, y_pos - 0.085), 0.45, 0.055,
                     facecolor='#4ECDC4', alpha=0.2, edgecolor='#4ECDC4', transform=ax.transAxes))
        ax.text(0.745, y_pos - 0.06, phase_flip, fontsize=8, 
               transform=ax.transAxes, va='center', ha='center')
        y_pos -= 0.15
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    figures.append(save_figure_to_data(fig, 'Error Correction Comparison'))
    plt.close(fig)
    
    return figures


def create_superdense_coding_figures():
    """Superdense Coding figures"""
    figures = []
    
    # Figure 1: Superdense Coding Circuit
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.x(0)  # Example: send 11
    qc.cx(0, 1)
    qc.h(0)
    qc.measure_all()
    
    circuit_img = circuit_drawer(qc, output='mpl', scale=0.7)
    figures.append(save_figure_to_data(circuit_img, 'Superdense Coding Circuit'))
    plt.close(circuit_img)
    
    # Figure 2: Encoding Guide
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.text(0.5, 0.95, 'Superdense Coding: Encode 2 Bits in 1 Qubit', 
            ha='center', fontsize=14, fontweight='bold', transform=ax.transAxes)
    
    encodings = [
        ('00', 'Do nothing (I)'),
        ('01', 'Apply X gate'),
        ('10', 'Apply Z gate'),
        ('11', 'Apply Y gate (Z·X)'),
    ]
    
    y_pos = 0.8
    for bits, operation in encodings:
        ax.add_patch(mpatches.FancyBboxPatch((0.1, y_pos - 0.1), 0.8, 0.08,
                     boxstyle="round,pad=0.01", facecolor='#667eea', alpha=0.2,
                     edgecolor='#667eea', transform=ax.transAxes))
        ax.text(0.25, y_pos - 0.06, f'Send "{bits}":', fontsize=11, fontweight='bold',
               transform=ax.transAxes, va='center')
        ax.text(0.65, y_pos - 0.06, operation, fontsize=11,
               transform=ax.transAxes, va='center')
        y_pos -= 0.15
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    figures.append(save_figure_to_data(fig, 'Superdense Coding Encoding Guide'))
    plt.close(fig)
    
    return figures


def create_teleportation_figures():
    """Quantum Teleportation figures"""
    figures = []
    
    # Figure 1: Teleportation Circuit
    qc = QuantumCircuit(3, 2)
    qc.cx(0, 1)
    qc.h(0)
    qc.measure(0, 0)
    qc.measure(1, 1)
    qc.cx(1, 2)
    qc.cx(0, 2)
    
    circuit_img = circuit_drawer(qc, output='mpl', scale=0.7)
    figures.append(save_figure_to_data(circuit_img, 'Quantum Teleportation Circuit'))
    plt.close(circuit_img)
    
    # Figure 2: Teleportation Process
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.text(0.5, 0.95, 'Quantum Teleportation Protocol', 
            ha='center', fontsize=14, fontweight='bold', transform=ax.transAxes)
    
    steps = [
        ('Preparation', 'Alice prepares unknown qubit |ψ⟩'),
        ('Entanglement', 'Alice & Bob share maximally entangled state'),
        ('Bell Measurement', 'Alice measures her 2 qubits → 2 classical bits'),
        ('Communication', 'Alice sends 2 classical bits to Bob'),
        ('Correction', 'Bob applies gate based on measurement result'),
        ('Result', 'Bob\'s qubit now in state |ψ⟩'),
    ]
    
    y_pos = 0.85
    for step_num, description in steps:
        color = '#45B7D1' if steps.index((step_num, description)) % 2 == 0 else '#FFA07A'
        ax.add_patch(mpatches.FancyBboxPatch((0.05, y_pos - 0.08), 0.9, 0.07,
                     boxstyle="round,pad=0.01", facecolor=color, alpha=0.2,
                     edgecolor=color, transform=ax.transAxes))
        ax.text(0.08, y_pos - 0.045, step_num, fontsize=10, fontweight='bold', 
               transform=ax.transAxes, va='center')
        ax.text(0.3, y_pos - 0.045, description, fontsize=9, 
               transform=ax.transAxes, va='center')
        y_pos -= 0.12
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    figures.append(save_figure_to_data(fig, 'Teleportation Protocol Steps'))
    plt.close(fig)
    
    return figures


def create_tomography_figures():
    """Quantum State Tomography figures"""
    figures = []
    
    # Figure 1: Tomography Overview
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.text(0.5, 0.95, 'Quantum State Tomography: Full State Reconstruction', 
            ha='center', fontsize=14, fontweight='bold', transform=ax.transAxes)
    
    steps = [
        ('Preparation', 'Prepare unknown quantum state |ψ⟩'),
        ('Measurements', 'Measure in multiple bases (X, Y, Z)'),
        ('Data Collection', 'Collect statistics for each basis'),
        ('Reconstruction', 'Use linear inversion to recover density matrix'),
        ('Verification', 'Compare theoretical vs measured state fidelity'),
    ]
    
    y_pos = 0.8
    for step, desc in steps:
        ax.add_patch(mpatches.FancyBboxPatch((0.05, y_pos - 0.1), 0.9, 0.08,
                     boxstyle="round,pad=0.01", facecolor='#667eea', alpha=0.2,
                     edgecolor='#667eea', transform=ax.transAxes))
        ax.text(0.15, y_pos - 0.06, f'{step}:', fontsize=11, fontweight='bold',
               transform=ax.transAxes, va='center')
        ax.text(0.35, y_pos - 0.06, desc, fontsize=10,
               transform=ax.transAxes, va='center')
        y_pos -= 0.14
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    figures.append(save_figure_to_data(fig, 'Quantum State Tomography Overview'))
    plt.close(fig)
    
    # Figure 2: Measurement Bases for Tomography
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    bases_info = [
        ('Z-Basis Measurement', '|0⟩ and |1⟩', 'Z'),
        ('X-Basis Measurement', '|+⟩ and |−⟩', 'X'),
        ('Y-Basis Measurement', '|+i⟩ and |−i⟩', 'Y'),
    ]
    
    for idx, (name, outcomes, basis) in enumerate(bases_info):
        ax = axes[idx]
        ax.text(0.5, 0.95, f'{basis}-Basis', fontsize=12, fontweight='bold',
               ha='center', transform=ax.transAxes)
        ax.text(0.5, 0.8, name, fontsize=10, ha='center', transform=ax.transAxes)
        ax.text(0.5, 0.5, outcomes, fontsize=10, ha='center', transform=ax.transAxes,
               bbox=dict(boxstyle='round', facecolor='#667eea', alpha=0.2))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
    
    plt.tight_layout()
    figures.append(save_figure_to_data(fig, 'Tomography Measurement Bases'))
    plt.close(fig)
    
    return figures


def create_quantum_walk_figures():
    """Quantum Walk figures"""
    figures = []
    
    # Figure 1: Classical vs Quantum Walk
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.text(0.5, 0.95, 'Classical Walk vs Quantum Walk', 
            ha='center', fontsize=14, fontweight='bold', transform=ax.transAxes)
    
    comparisons = [
        ('Probability', 'Classical: Random distribution', 'Quantum: Interference patterns'),
        ('Speed', 'Classical: Polynomial time', 'Quantum: Quadratic speedup'),
        ('Superposition', 'Classical: Single position', 'Quantum: Superposition of paths'),
        ('Applications', 'Classical: Limited', 'Quantum: Search, optimization, simulation'),
    ]
    
    y_pos = 0.8
    for property_name, classical, quantum in comparisons:
        ax.text(0.02, y_pos - 0.06, property_name, fontsize=10, fontweight='bold',
               transform=ax.transAxes, va='center')
        ax.add_patch(mpatches.Rectangle((0.18, y_pos - 0.085), 0.3, 0.055,
                     facecolor='#FF6B6B', alpha=0.2, edgecolor='#FF6B6B', transform=ax.transAxes))
        ax.text(0.33, y_pos - 0.06, classical, fontsize=9, ha='center',
               transform=ax.transAxes, va='center')
        ax.add_patch(mpatches.Rectangle((0.52, y_pos - 0.085), 0.46, 0.055,
                     facecolor='#4ECDC4', alpha=0.2, edgecolor='#4ECDC4', transform=ax.transAxes))
        ax.text(0.75, y_pos - 0.06, quantum, fontsize=9, ha='center',
               transform=ax.transAxes, va='center')
        y_pos -= 0.15
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    figures.append(save_figure_to_data(fig, 'Classical vs Quantum Walk Comparison'))
    plt.close(fig)
    
    return figures


def create_parity_figures():
    """Parity Check with Ancilla Qubit figures"""
    figures = []
    
    # Figure 1: Parity Check Circuit
    qc = QuantumCircuit(3)
    qc.cx(0, 2)  # Data qubit to ancilla
    qc.cx(1, 2)  # Data qubit to ancilla
    qc.measure_all()
    
    circuit_img = circuit_drawer(qc, output='mpl', scale=0.7)
    figures.append(save_figure_to_data(circuit_img, 'Parity Check Circuit'))
    plt.close(circuit_img)
    
    # Figure 2: Parity Check Truth Table
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.text(0.5, 0.95, 'Parity Check with Ancilla Qubit (2 Data + 1 Ancilla)', 
            ha='center', fontsize=14, fontweight='bold', transform=ax.transAxes)
    
    truth_table = [
        ('Input Q0', 'Input Q1', 'Ancilla (out)', 'Parity'),
        ('0', '0', '0', 'Even'),
        ('0', '1', '1', 'Odd'),
        ('1', '0', '1', 'Odd'),
        ('1', '1', '0', 'Even'),
    ]
    
    y_pos = 0.8
    for row_idx, row in enumerate(truth_table):
        is_header = row_idx == 0
        y_pos -= 0.12
        
        # Draw row background
        color = '#667eea' if is_header else '#764ba2'
        ax.add_patch(mpatches.Rectangle((0.1, y_pos - 0.05), 0.8, 0.08,
                     facecolor=color, alpha=0.2 if not is_header else 0.3,
                     edgecolor=color, transform=ax.transAxes))
        
        # Draw columns
        col_width = 0.2
        for col_idx, cell in enumerate(row):
            x_pos = 0.15 + col_idx * col_width
            weight = 'bold' if is_header else 'normal'
            ax.text(x_pos, y_pos, cell, fontsize=11, fontweight=weight,
                   transform=ax.transAxes, va='center', ha='center', family='monospace')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    figures.append(save_figure_to_data(fig, 'Parity Check Truth Table'))
    plt.close(fig)
    
    return figures


def create_circuit_identity_figures():
    """Circuit Identity Verification figures"""
    figures = []
    
    # Figure 1: Common Quantum Gate Identities
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.text(0.5, 0.97, 'Fundamental Quantum Gate Identities', 
            ha='center', fontsize=14, fontweight='bold', transform=ax.transAxes)
    
    identities = [
        ('H² = I', 'Hadamard is self-inverse'),
        ('X² = I', 'Pauli-X is self-inverse'),
        ('(CX)² = I', 'CNOT is self-inverse'),
        ('H·X·H = Z', 'Conjugation relation'),
        ('(XZ)³ = iI', 'Braid relation'),
        ('X·Y·Z = iI', 'Pauli product identity'),
    ]
    
    y_pos = 0.85
    for identity, description in identities:
        ax.add_patch(mpatches.FancyBboxPatch((0.05, y_pos - 0.09), 0.9, 0.07,
                     boxstyle="round,pad=0.01", facecolor='#667eea', alpha=0.2,
                     edgecolor='#667eea', transform=ax.transAxes))
        ax.text(0.15, y_pos - 0.055, identity, fontsize=11, fontweight='bold',
               transform=ax.transAxes, va='center', family='monospace')
        ax.text(0.65, y_pos - 0.055, description, fontsize=10,
               transform=ax.transAxes, va='center')
        y_pos -= 0.12
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    figures.append(save_figure_to_data(fig, 'Quantum Gate Identities'))
    plt.close(fig)
    
    return figures


def create_noise_figures():
    """Quantum Noise and Error Models figures"""
    figures = []
    
    # Figure 1: All Four Bell State Circuits
    bell_state_configs = [
        ('|Φ⁺⟩ = (|00⟩ + |11⟩)/√2', 'phi_plus'),
        ('|Φ⁻⟩ = (|00⟩ − |11⟩)/√2', 'phi_minus'),
        ('|Ψ⁺⟩ = (|01⟩ + |10⟩)/√2', 'psi_plus'),
        ('|Ψ⁻⟩ = (|01⟩ − |10⟩)/√2', 'psi_minus'),
    ]
    
    for state_name, state_type in bell_state_configs:
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        
        if state_type == 'phi_minus':
            qc.z(0)
        elif state_type == 'psi_plus':
            qc.x(1)
        elif state_type == 'psi_minus':
            qc.x(1)
            qc.z(0)
        
        circuit_img = circuit_drawer(qc, output='mpl', scale=0.7)
        figures.append(save_figure_to_data(circuit_img, f'{state_name} Circuit'))
        plt.close(circuit_img)
    
    # Figure 2: Common Error Types
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.text(0.5, 0.97, 'Common Quantum Noise Models', 
            ha='center', fontsize=14, fontweight='bold', transform=ax.transAxes)
    
    noise_types = [
        ('Bit Flip', 'X error with probability p'),
        ('Phase Flip', 'Z error with probability p'),
        ('Depolarizing', 'Random Pauli error with probability p'),
        ('Amplitude Damping', 'Energy loss (non-unitary)'),
        ('Phase Damping', 'Pure dephasing, coherence loss'),
        ('Thermal Noise', 'Temperature-dependent decoherence'),
    ]
    
    y_pos = 0.85
    for noise_name, description in noise_types:
        ax.add_patch(mpatches.FancyBboxPatch((0.05, y_pos - 0.08), 0.9, 0.06,
                     boxstyle="round,pad=0.01", facecolor='#FF6B6B', alpha=0.2,
                     edgecolor='#FF6B6B', transform=ax.transAxes))
        ax.text(0.1, y_pos - 0.05, noise_name, fontsize=11, fontweight='bold',
               transform=ax.transAxes, va='center')
        ax.text(0.6, y_pos - 0.05, description, fontsize=10,
               transform=ax.transAxes, va='center')
        y_pos -= 0.12
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    figures.append(save_figure_to_data(fig, 'Quantum Noise Models'))
    plt.close(fig)
    
    return figures


def create_randomng_figures():
    """Quantum Random Number Generator figures"""
    figures = []
    
    # Figure 1: QRNG vs Classical RNG
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.text(0.5, 0.95, 'Quantum vs Classical Random Number Generation', 
            ha='center', fontsize=14, fontweight='bold', transform=ax.transAxes)
    
    comparisons = [
        ('Source', 'Classical: Deterministic algorithm', 'Quantum: Quantum uncertainty'),
        ('Predictability', 'Classical: Pseudo-random, predictable', 'Quantum: True random, unpredictable'),
        ('Periodicity', 'Classical: Repeating cycle', 'Quantum: Non-repeating'),
        ('Quality', 'Classical: Passes statistical tests', 'Quantum: Perfect randomness'),
    ]
    
    y_pos = 0.8
    for label, classical, quantum in comparisons:
        ax.text(0.02, y_pos - 0.06, label, fontsize=10, fontweight='bold',
               transform=ax.transAxes, va='center')
        ax.add_patch(mpatches.Rectangle((0.18, y_pos - 0.085), 0.3, 0.055,
                     facecolor='#FF6B6B', alpha=0.2, edgecolor='#FF6B6B', transform=ax.transAxes))
        ax.text(0.33, y_pos - 0.06, classical, fontsize=8.5, ha='center',
               transform=ax.transAxes, va='center')
        ax.add_patch(mpatches.Rectangle((0.52, y_pos - 0.085), 0.46, 0.055,
                     facecolor='#4ECDC4', alpha=0.2, edgecolor='#4ECDC4', transform=ax.transAxes))
        ax.text(0.75, y_pos - 0.06, quantum, fontsize=8.5, ha='center',
               transform=ax.transAxes, va='center')
        y_pos -= 0.15
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    figures.append(save_figure_to_data(fig, 'QRNG vs Classical RNG'))
    plt.close(fig)
    
    # Figure 2: QRNG Circuit
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.h(1)
    qc.h(2)
    qc.measure_all()
    
    circuit_img = circuit_drawer(qc, output='mpl', scale=0.7)
    figures.append(save_figure_to_data(circuit_img, '3-Qubit Random Number Generator Circuit'))
    plt.close(circuit_img)
    
    return figures


# Map of lab IDs to their figure generation functions
LAB_FIGURES = {
    'bb84': create_bb84_figures,
    'different_states': create_different_states_figures,
    'multi_qubit_superposition': create_multi_qubit_superposition_figures,
    'ghz_state': create_ghz_state_figures,
    'w_state': create_w_state_figures,
    'bit_flip_code': create_bit_flip_code_figures,
    'phase_flip_code': create_phase_flip_code_figures,
    'supcod': create_superdense_coding_figures,
    'tele': create_teleportation_figures,
    'tomography': create_tomography_figures,
    'walk': create_quantum_walk_figures,
    'parity': create_parity_figures,
    'circuit_identity': create_circuit_identity_figures,
    'noise': create_noise_figures,
    'random': create_randomng_figures,
}


def get_lab_figures(lab_id: str):
    """
    Get the default figures for a lab.
    
    Args:
        lab_id: The ID of the lab
        
    Returns:
        List of figure objects or empty list if lab not found
    """
    if lab_id in LAB_FIGURES:
        return LAB_FIGURES[lab_id]()
    return []
