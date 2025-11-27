import matplotlib.pyplot as plt
import streamlit as st
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.visualization import plot_histogram
from qiskit_aer import AerSimulator
from scipy import stats
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
    # ----------------------------
    # Function to create QRNG circuit
    # ----------------------------
    def create_qrng_circuit(num_qubits: int) -> QuantumCircuit:
        """
        Create a quantum circuit for random number generation.
        Uses Hadamard gates to create superposition, then measures.
        """
        qc = QuantumCircuit(num_qubits, num_qubits)

        # Apply Hadamard gate to all qubits (creates superposition)
        for qubit in range(num_qubits):
            qc.h(qubit)

        # Measure all qubits
        qc.measure(range(num_qubits), range(num_qubits))
        # print(x)
        return qc

    # ----------------------------
    # Function to generate random numbers
    # ----------------------------
    def generate_random_numbers(num_qubits: int, num_samples: int) -> list:
        qc = create_qrng_circuit(num_qubits)

        # Use AerSimulator
        backend = AerSimulator()
        transpiled = transpile(qc, backend)

        random_numbers = []
        for _ in range(num_samples):
            job = backend.run(transpiled, shots=1)
            result = job.result()
            counts = result.get_counts()

            binary_string = list(counts.keys())[0]
            decimal_value = int(binary_string, 2)
            random_numbers.append(decimal_value)

        return random_numbers

    # ----------------------------
    # Statistical Analysis Functions
    # ----------------------------
    def calculate_statistics(data: list, num_qubits: int) -> dict:
        max_value = 2 ** num_qubits - 1

        stats_dict = {
            'mean': np.mean(data),
            'theoretical_mean': max_value / 2,
            'std_dev': np.std(data),
            'min': np.min(data),
            'max': np.max(data),
            'unique_values': len(set(data)),
            'total_samples': len(data)
        }

        return stats_dict

    def chi_square_test(data: list, num_qubits: int) -> tuple:
        """
        Perform chi-square test for uniformity.
        Returns (chi_square_statistic, p_value)
        """
        max_value = 2 ** num_qubits
        expected_freq = len(data) / max_value

        # Count occurrences of each value
        observed_freq = np.bincount(data, minlength=max_value)
        expected_freq_array = np.full(max_value, expected_freq)

        # Chi-square test
        chi_square_stat = np.sum((observed_freq - expected_freq_array) ** 2 / expected_freq_array)
        degrees_of_freedom = max_value - 1
        p_value = 1 - stats.chi2.cdf(chi_square_stat, degrees_of_freedom)

        return chi_square_stat, p_value

    # ----------------------------
    # Entropy Assessment Functions
    # ----------------------------
    def calculate_min_entropy(data: list, num_qubits: int) -> dict:
        max_value = 2 ** num_qubits

        # Count occurrences and calculate probabilities
        observed_freq = np.bincount(data, minlength=max_value)
        probabilities = observed_freq / len(data)

        # Find maximum probability (worst-case for adversary)
        max_prob = np.max(probabilities)

        # Calculate min-entropy
        if max_prob > 0:
            min_entropy_total = -np.log2(max_prob)
            min_entropy_per_bit = min_entropy_total / num_qubits
        else:
            min_entropy_total = 0
            min_entropy_per_bit = 0

        # Theoretical maximum is num_qubits (for uniform distribution)
        theoretical_max = num_qubits

        return {
            'min_entropy_total': min_entropy_total,
            'min_entropy_per_bit': min_entropy_per_bit,
            'theoretical_max': theoretical_max,
            'max_probability': max_prob,
            'quality_percentage': (min_entropy_total / theoretical_max) * 100 if theoretical_max > 0 else 0
        }

    def calculate_collision_entropy(data: list, num_qubits: int) -> dict:
        max_value = 2 ** num_qubits

        # Count occurrences and calculate probabilities
        observed_freq = np.bincount(data, minlength=max_value)
        probabilities = observed_freq / len(data)

        # Calculate sum of squared probabilities
        sum_squared_prob = np.sum(probabilities ** 2)

        # Calculate collision entropy
        if sum_squared_prob > 0:
            collision_entropy = -np.log2(sum_squared_prob)
        else:
            collision_entropy = 0

        # Theoretical maximum
        theoretical_max = num_qubits

        return {
            'collision_entropy': collision_entropy,
            'theoretical_max': theoretical_max,
            'sum_squared_probabilities': sum_squared_prob,
            'quality_percentage': (collision_entropy / theoretical_max) * 100 if theoretical_max > 0 else 0
        }

    def calculate_shannon_entropy(data: list, num_qubits: int) -> dict:
        max_value = 2 ** num_qubits

        # Count occurrences and calculate probabilities
        observed_freq = np.bincount(data, minlength=max_value)
        probabilities = observed_freq / len(data)

        # Remove zero probabilities to avoid log(0)
        probabilities = probabilities[probabilities > 0]

        # Calculate Shannon entropy
        shannon_entropy = -np.sum(probabilities * np.log2(probabilities))

        # Theoretical maximum
        theoretical_max = num_qubits

        return {
            'shannon_entropy': shannon_entropy,
            'theoretical_max': theoretical_max,
            'quality_percentage': (shannon_entropy / theoretical_max) * 100 if theoretical_max > 0 else 0
        }

    def real_time_entropy_monitor(data: list, num_qubits: int, block_size: int = 100) -> dict:
        if len(data) < block_size:
            block_size = len(data) // 2 if len(data) >= 2 else len(data)

        num_blocks = len(data) // block_size
        block_entropies = []

        for i in range(num_blocks):
            block_data = data[i * block_size:(i + 1) * block_size]
            block_min_entropy = calculate_min_entropy(block_data, num_qubits)
            block_entropies.append(block_min_entropy['min_entropy_per_bit'])

        if len(block_entropies) > 0:
            mean_entropy = np.mean(block_entropies)
            std_entropy = np.std(block_entropies)
            min_block_entropy = np.min(block_entropies)
            max_block_entropy = np.max(block_entropies)

            # Quality check: standard deviation should be low for consistent randomness
            consistency_score = 100 - (std_entropy * 100) if std_entropy < 1 else 0
        else:
            mean_entropy = 0
            std_entropy = 0
            min_block_entropy = 0
            max_block_entropy = 0
            consistency_score = 0

        return {
            'num_blocks': num_blocks,
            'block_size': block_size,
            'mean_entropy': mean_entropy,
            'std_entropy': std_entropy,
            'min_block_entropy': min_block_entropy,
            'max_block_entropy': max_block_entropy,
            'consistency_score': consistency_score,
            'block_entropies': block_entropies
        }

    # ----------------------------
    # Streamlit UI - COMPLETELY REDESIGNED
    # ----------------------------
    st.set_page_config(
        page_title="QRNG Lab",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Custom CSS for modern styling
    st.markdown("""
        <style>
        .main-header {
            text-align: center;
            padding: 2rem 0;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        .main-header h1 {
            color: white;
            font-size: 3rem;
            margin: 0;
        }
        .main-header p {
            color: #e0e0e0;
            font-size: 1.2rem;
        }
        .stat-card {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 5px solid #667eea;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .big-number {
            font-size: 2.5rem;
            font-weight: bold;
            color: #667eea;
            margin: 0;
        }
        .label-text {
            color: #6c757d;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        </style>
    """, unsafe_allow_html=True)


    # ----------------------------
    # Main Control Panel (Top Section)
    # ----------------------------

    # Three columns for controls
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 2, 1])

    with ctrl_col1:
        st.markdown("<p style='font-size: 1.3rem; font-weight: bold;'>Qubit Configuration</p>", unsafe_allow_html=True)
        num_qubits = st.select_slider(
            "Select Number of Qubits",
            options=[2, 3, 4, 5, 6, 7, 8],
            value=4,
            help="More qubits = larger range of random numbers"
        )
        max_possible_value = 2 ** num_qubits - 1
        st.info(f"**Output Range:** 0 to {max_possible_value} ({2 ** num_qubits} possible values)")

    with ctrl_col2:
        st.markdown("<p style='font-size: 1.3rem; font-weight: bold;'>Sample Size</p>", unsafe_allow_html=True)
        num_samples = st.slider(
            "Choose Sample Size",
            min_value=500,
            max_value=5000,
            value=1000,
            step=50,
            help="Number of random numbers to generate"
        )
        st.info(f"**Generating:** {num_samples:,} random numbers")

    with ctrl_col3:
        st.markdown("<p style='font-size: 1.3rem; font-weight: bold;'>Action</p>", unsafe_allow_html=True)
        st.write("")  # Spacing
        st.write("")  # Spacing
        generate_button = st.button("🚀 Generate", type="primary", use_container_width=True)

        if st.button("Reset", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    st.divider()

    # ----------------------------
    # Quantum Circuit Preview (Tabs)
    # ----------------------------
    tab1, tab2, tab3, tab4 = st.tabs(["Results", "Entropy Assessment", "Circuit Design", "Documentation"])

    with tab2:
        st.markdown("### Entropy Assessment")
        st.markdown("""
        Entropy assessment measures the level of inherent unpredictability in the raw, unconditioned output of a QRNG.
        This is a fundamental metric that distinguishes QRNGs from classical systems.
        """)

        if 'random_numbers' in st.session_state:
            random_numbers = st.session_state['random_numbers']
            num_qubits_used = st.session_state['num_qubits']

            # Calculate all entropy metrics
            min_entropy = calculate_min_entropy(random_numbers, num_qubits_used)
            collision_entropy = calculate_collision_entropy(random_numbers, num_qubits_used)
            shannon_entropy = calculate_shannon_entropy(random_numbers, num_qubits_used)
            rt_monitor = real_time_entropy_monitor(random_numbers, num_qubits_used, block_size=100)

            # Display entropy metrics
            st.markdown("#### Core Entropy Metrics")

            ent_col1, ent_col2, ent_col3 = st.columns(3)

            with ent_col1:
                quality_color = "#27ae60" if min_entropy['quality_percentage'] >= 90 else "#f39c12" if min_entropy[
                                                                                                           'quality_percentage'] >= 75 else "#e74c3c"
                st.markdown(f"""
                <div class="stat-card" style="border-left-color: {quality_color};">
                    <p class="label-text">Min-Entropy (H∞)</p>
                    <p class="big-number" style="color: {quality_color}; font-size: 2rem;">{min_entropy['min_entropy_total']:.4f}</p>
                    <small>Per bit: {min_entropy['min_entropy_per_bit']:.4f}</small><br>
                    <small>Max possible: {min_entropy['theoretical_max']}</small><br>
                    <small><strong>Quality: {min_entropy['quality_percentage']:.1f}%</strong></small>
                </div>
                """, unsafe_allow_html=True)

                with st.expander("About Min-Entropy"):
                    st.markdown(f"""
                    **Min-Entropy (H∞)** is the most crucial metric for cryptographic applications.

                    **Formula:** $H_{{\\infty}}(X) = -\\log_2(\\max_{{x \\in X}} p(x))$

                    - Quantifies the **worst-case** unpredictability
                    - Assumes adversary knows which value is most likely
                    - Higher values (closer to {num_qubits_used}) = more secure
                    - Essential for cryptographic key generation

                    **Your result:** The maximum probability of any value is {min_entropy['max_probability']:.6f}, 
                    giving a min-entropy of {min_entropy['min_entropy_total']:.4f} bits.
                    """)

            with ent_col2:
                quality_color = "#27ae60" if collision_entropy['quality_percentage'] >= 90 else "#f39c12" if \
                    collision_entropy['quality_percentage'] >= 75 else "#e74c3c"
                st.markdown(f"""
                <div class="stat-card" style="border-left-color: {quality_color};">
                    <p class="label-text">Collision Entropy (Hc)</p>
                    <p class="big-number" style="color: {quality_color}; font-size: 2rem;">{collision_entropy['collision_entropy']:.4f}</p>
                    <small>Max possible: {collision_entropy['theoretical_max']}</small><br>
                    <small><strong>Quality: {collision_entropy['quality_percentage']:.1f}%</strong></small>
                </div>
                """, unsafe_allow_html=True)

                with st.expander("About Collision Entropy"):
                    st.markdown(f"""
                    **Collision Entropy (Hc)** measures the probability of getting the same value twice.

                    **Formula:** $H_c(X) = -\\log_2(\\sum_x p(x)^2)$

                    - Considers probability of **collisions**
                    - Provides different perspective on randomness
                    - Important for hash functions and protocols

                    **Your result:** Sum of squared probabilities is {collision_entropy['sum_squared_probabilities']:.6f}, 
                    giving collision entropy of {collision_entropy['collision_entropy']:.4f} bits.
                    """)

            with ent_col3:
                quality_color = "#27ae60" if shannon_entropy['quality_percentage'] >= 90 else "#f39c12" if \
                shannon_entropy[
                    'quality_percentage'] >= 75 else "#e74c3c"
                st.markdown(f"""
                <div class="stat-card" style="border-left-color: {quality_color};">
                    <p class="label-text">Shannon Entropy (H)</p>
                    <p class="big-number" style="color: {quality_color}; font-size: 2rem;">{shannon_entropy['shannon_entropy']:.4f}</p>
                    <small>Max possible: {shannon_entropy['theoretical_max']}</small><br>
                    <small><strong>Quality: {shannon_entropy['quality_percentage']:.1f}%</strong></small>
                </div>
                """, unsafe_allow_html=True)

                with st.expander("About Shannon Entropy"):
                    st.markdown(f"""
                    **Shannon Entropy (H)** is the classical measure of information content.

                    **Formula:** $H(X) = -\\sum_x p(x) \\log_2(p(x))$

                    - Average information per symbol
                    - Classical measure of unpredictability
                    - Higher values indicate more uniform distribution

                    **Your result:** Shannon entropy of {shannon_entropy['shannon_entropy']:.4f} bits indicates 
                    {shannon_entropy['quality_percentage']:.1f}% of maximum possible randomness.
                    """)

            st.divider()

            # Real-time monitoring section
            st.markdown("####Real-Time Entropy Monitoring")
            st.markdown("""
            Advanced QRNGs continuously monitor entropy to detect deviations in the quantum process,
            ensuring high-quality randomness without external noise or manipulation.
            """)

            monitor_col1, monitor_col2 = st.columns([2, 1])

            with monitor_col1:
                # Plot entropy over blocks
                if len(rt_monitor['block_entropies']) > 0:
                    fig_entropy, ax_entropy = plt.subplots(figsize=(10, 5))

                    block_indices = range(1, rt_monitor['num_blocks'] + 1)
                    ax_entropy.plot(block_indices, rt_monitor['block_entropies'],
                                    marker='o', linewidth=2, markersize=6, color='#667eea', label='Block Min-Entropy')
                    ax_entropy.axhline(y=rt_monitor['mean_entropy'], color='#27ae60',
                                       linestyle='--', linewidth=2, label=f'Mean: {rt_monitor["mean_entropy"]:.4f}')
                    ax_entropy.axhline(y=1.0, color='#e74c3c',
                                       linestyle=':', linewidth=2, label='Ideal: 1.0')
                    ax_entropy.fill_between(block_indices,
                                            rt_monitor['mean_entropy'] - rt_monitor['std_entropy'],
                                            rt_monitor['mean_entropy'] + rt_monitor['std_entropy'],
                                            alpha=0.2, color='#667eea', label=f'±1 Std Dev')

                    ax_entropy.set_xlabel('Block Number', fontsize=12, fontweight='bold')
                    ax_entropy.set_ylabel('Min-Entropy per Bit', fontsize=12, fontweight='bold')
                    ax_entropy.set_title('Entropy Consistency Across Data Blocks', fontsize=14, fontweight='bold',
                                         pad=15)
                    ax_entropy.legend(fontsize=10, loc='best')
                    ax_entropy.grid(True, alpha=0.3, linestyle='--')
                    ax_entropy.spines['top'].set_visible(False)
                    ax_entropy.spines['right'].set_visible(False)
                    ax_entropy.set_ylim([0, 1.1])

                    st.pyplot(fig_entropy)

            with monitor_col2:
                st.markdown("**Monitoring Statistics:**")
                st.metric("Number of Blocks", rt_monitor['num_blocks'])
                st.metric("Block Size", rt_monitor['block_size'])
                st.metric("Mean Entropy", f"{rt_monitor['mean_entropy']:.4f}")
                st.metric("Std Deviation", f"{rt_monitor['std_entropy']:.4f}")
                st.metric("Min Block Entropy", f"{rt_monitor['min_block_entropy']:.4f}")
                st.metric("Max Block Entropy", f"{rt_monitor['max_block_entropy']:.4f}")

                # Display entropy formulas
                display_formulas(title="Formulas", formulas=[
                    r"H_{\min} = -\log_2(\max_i p_i)",
                    r"H_{\mathrm{collision}} = -\log_2\left(\sum_i p_i^2\right)",
                    r"H_{\mathrm{Shannon}} = -\sum_i p_i \log_2 p_i"
                ])

                consistency_color = "#27ae60" if rt_monitor['consistency_score'] >= 90 else "#f39c12" if rt_monitor[
                                                                                                             'consistency_score'] >= 75 else "#e74c3c"
                st.markdown(f"""
                <div style="background: {consistency_color}; color: white; padding: 1rem; border-radius: 8px; text-align: center; margin-top: 1rem;">
                    <h3 style="margin: 0;">Consistency Score</h3>
                    <h1 style="margin: 0.5rem 0;">{rt_monitor['consistency_score']:.1f}%</h1>
                    <p style="margin: 0; font-size: 0.9rem;">
                        {"Excellent" if rt_monitor['consistency_score'] >= 90 else "⚠Good" if rt_monitor['consistency_score'] >= 75 else "Needs Attention"}
                    </p>
                </div>
                """, unsafe_allow_html=True)

            st.divider()

            # Security Assessment
            st.markdown("#### Cryptographic Security Assessment")

            # Determine overall security level
            min_quality = min_entropy['quality_percentage']
            if min_quality >= 95:
                security_level = "EXCELLENT - Suitable for cryptographic key generation"
                security_color = "#27ae60"
            elif min_quality >= 85:
                security_level = "GOOD - Suitable for most applications with conditioning"
                security_color = "#f39c12"
            elif min_quality >= 70:
                security_level = "FAIR - Requires post-processing before cryptographic use"
                security_color = "#e67e22"
            else:
                security_level = "LOW - Not recommended for cryptographic applications"
                security_color = "#e74c3c"

            st.markdown(f"""
            <div style="background: {security_color}; color: white; padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
                <h3 style="margin: 0 0 0.5rem 0;">Overall Security Level</h3>
                <h2 style="margin: 0;">{security_level}</h2>
            </div>
            """, unsafe_allow_html=True)

            # Recommendations
            st.markdown("#### Recommendations")

            if min_quality >= 95:
                st.success("""
                Your QRNG output has excellent entropy properties:
                - Min-entropy is very high, indicating strong unpredictability
                - Consistency across blocks is good
                - Suitable for direct use in cryptographic applications
                """)
            elif min_quality >= 85:
                st.info("""
                Your QRNG output has good entropy properties:
                - Consider using randomness extraction (e.g., hash functions) for critical applications
                - Monitor entropy continuously in production environments
                - Suitable for most non-critical cryptographic uses
                """)
            else:
                st.warning("""
                Your QRNG output could be improved:
                - Use randomness extractors or post-processing algorithms
                - Increase sample size for better statistical properties
                - Consider checking quantum circuit noise and decoherence
                - Not recommended for direct cryptographic use without conditioning
                """)

        else:
            st.info("Generate random numbers first to see entropy analysis!")

    with tab3:
        st.markdown("### Quantum Circuit Architecture")
        circuit_preview = create_qrng_circuit(num_qubits)

        col1, col2 = st.columns([3, 1])
        with col1:
            fig_circuit = circuit_preview.draw('mpl', fold=-1)
            st.pyplot(fig_circuit)
        with col2:
            st.markdown(f"""
            **Circuit Details:**
            - **Qubits:** {num_qubits}
            - **Gates:** {num_qubits} Hadamard
            - **Measurements:** {num_qubits}

            **Process:**
            1. Initialize qubits in |0⟩
            2. Apply H gate (superposition)
            3. Measure each qubit
            4. Convert binary → decimal
            """)

    with tab4:
        st.markdown("""
        ### About Quantum Random Number Generation

        **Quantum Advantage:**
        - Classical RNGs use algorithms (pseudo-random)
        - QRNGs use quantum measurement (truly random)
        - Based on fundamental quantum uncertainty

        **How This Works:**
        1. **Superposition:** Hadamard gates create equal probability states
        2. **Measurement:** Quantum state collapses to 0 or 1 randomly
        3. **Aggregation:** Multiple measurements create random bit strings
        4. **Conversion:** Binary strings become decimal numbers

        **Statistical Tests:**
        - **Chi-Square Test:** Validates uniform distribution
        - **P-value > 0.05:** Indicates true randomness
        """)

    # ----------------------------
    # Results Section (Tab 1)
    # ----------------------------
    with tab1:
        if generate_button:
            with st.spinner("⚛️ Quantum computation in progress..."):
                random_numbers = generate_random_numbers(num_qubits, num_samples)
                st.session_state['random_numbers'] = random_numbers
                st.session_state['num_qubits'] = num_qubits
                st.session_state['num_samples'] = num_samples

        if 'random_numbers' in st.session_state:
            random_numbers = st.session_state['random_numbers']
            num_qubits_used = st.session_state['num_qubits']
            num_samples_used = st.session_state['num_samples']

            st.success(f" Successfully generated {len(random_numbers):,} quantum random numbers!")

            # ----------------------------
            # Key Metrics Dashboard
            # ----------------------------
            st.markdown("## Statistical Dashboard")

            stats_dict = calculate_statistics(random_numbers, num_qubits_used)
            chi_stat, p_value = chi_square_test(random_numbers, num_qubits_used)

            # 5 columns for key metrics
            m1, m2, m3, m4, m5 = st.columns(5)

            with m1:
                st.markdown(f"""
                <div class="stat-card">
                    <p class="label-text">Mean Value</p>
                    <p class="big-number">{stats_dict['mean']:.2f}</p>
                    <small>Expected: {stats_dict['theoretical_mean']:.2f}</small>
                </div>
                """, unsafe_allow_html=True)

            with m2:
                st.markdown(f"""
                <div class="stat-card">
                    <p class="label-text">Std Deviation</p>
                    <p class="big-number">{stats_dict['std_dev']:.2f}</p>
                    <small>Spread measure</small>
                </div>
                """, unsafe_allow_html=True)

            with m3:
                st.markdown(f"""
                <div class="stat-card">
                    <p class="label-text">Range</p>
                    <p class="big-number">{stats_dict['min']}-{stats_dict['max']}</p>
                    <small>Min to Max</small>
                </div>
                """, unsafe_allow_html=True)

            with m4:
                st.markdown(f"""
                <div class="stat-card">
                    <p class="label-text">Unique Values</p>
                    <p class="big-number">{stats_dict['unique_values']}</p>
                    <small>Of {2 ** num_qubits_used} possible</small>
                </div>
                """, unsafe_allow_html=True)

            with m5:
                uniformity_status = "Uniform" if p_value > 0.05 else "Non-uniform"
                color = "#667eea" if p_value > 0.05 else "#f39c12"
                st.markdown(f"""
                <div class="stat-card">
                    <p class="label-text">Chi-Square Test</p>
                    <p class="big-number" style="color: {color}; font-size: 1.5rem;">{uniformity_status}</p>
                    <small>p-value: {p_value:.4f}</small>
                </div>
                """, unsafe_allow_html=True)

            st.divider()

            # ----------------------------
            # Visualization Section
            # ----------------------------
            st.markdown("## Distribution Visualizations")

            viz_col1, viz_col2 = st.columns(2)

            with viz_col1:
                st.markdown("### Frequency Distribution")
                fig1, ax1 = plt.subplots(figsize=(10, 6))

                counts = np.bincount(random_numbers, minlength=2 ** num_qubits_used)
                x_values = range(2 ** num_qubits_used)

                ax1.bar(x_values, counts, color='#667eea', alpha=0.8, edgecolor='#764ba2', linewidth=1.5)
                ax1.axhline(y=num_samples_used / (2 ** num_qubits_used), color='#e74c3c',
                            linestyle='--', label='Expected Uniform', linewidth=2.5)
                ax1.set_xlabel('Decimal Value', fontsize=13, fontweight='bold')
                ax1.set_ylabel('Frequency', fontsize=13, fontweight='bold')
                ax1.set_title('Distribution of Generated Numbers', fontsize=15, fontweight='bold', pad=20)
                ax1.legend(fontsize=11)
                ax1.grid(True, alpha=0.3, linestyle='--')
                ax1.spines['top'].set_visible(False)
                ax1.spines['right'].set_visible(False)

                st.pyplot(fig1)
                
                # (Moved storing/export logic to after CDF figure is created)

                # Additional stats below chart
                deviation = abs(stats_dict['mean'] - stats_dict['theoretical_mean'])
                st.metric("Mean Deviation from Expected", f"{deviation:.3f}",
                          delta=f"{(deviation / stats_dict['theoretical_mean'] * 100):.2f}%",
                          delta_color="inverse")

            with viz_col2:
                st.markdown("### Cumulative Distribution Function")
                fig2, ax2 = plt.subplots(figsize=(10, 6))

                sorted_data = np.sort(random_numbers)
                cumulative = np.arange(1, len(sorted_data) + 1) / len(sorted_data)

                ax2.plot(sorted_data, cumulative, linewidth=3, color='#27ae60', alpha=0.8)
                ax2.fill_between(sorted_data, cumulative, alpha=0.2, color='#27ae60')
                ax2.set_xlabel('Decimal Value', fontsize=13, fontweight='bold')
                ax2.set_ylabel('Cumulative Probability', fontsize=13, fontweight='bold')
                ax2.set_title('Cumulative Distribution', fontsize=15, fontweight='bold', pad=20)
                ax2.grid(True, alpha=0.3, linestyle='--')
                ax2.spines['top'].set_visible(False)
                ax2.spines['right'].set_visible(False)
                ax2.set_ylim([0, 1])

                st.pyplot(fig2)

                # Chi-square details
                st.metric("Chi-Square Statistic", f"{chi_stat:.4f}")

                # Store simulation data for PDF/report now that both figures exist
                try:
                    from lab_config import LABS

                    lab_id = None
                    for name, config in LABS.items():
                        if config.get('module') == 'random':
                            lab_id = config['id']
                            break

                    if lab_id:
                        # Prepare metrics
                        metrics = {
                            'Mean Value': f"{stats_dict['mean']:.2f}",
                            'Expected Mean': f"{stats_dict['theoretical_mean']:.2f}",
                            'Std Deviation': f"{stats_dict['std_dev']:.2f}",
                            'Range': f"{stats_dict['min']}-{stats_dict['max']}",
                            'Unique Values': f"{stats_dict['unique_values']}/{2**num_qubits_used}",
                            'Chi-Square p-value': f"{p_value:.4f}",
                            'Uniformity': "Uniform" if p_value > 0.05 else "Non-uniform"
                        }

                        # Prepare measurements (convert to counts format)
                        measurements = {}
                        counts_array = np.bincount(random_numbers, minlength=2**num_qubits_used)
                        for val, count in enumerate(counts_array):
                            if count > 0:
                                measurements[str(val)] = int(count)

                        # Prepare figures (save copies of both figures)
                        figures = [
                            save_figure_to_data(fig1, 'Frequency Distribution'),
                            save_figure_to_data(fig2, 'Cumulative Distribution Function')
                        ]

                        # Add entropy plot if available
                        try:
                            rt_monitor = real_time_entropy_monitor(random_numbers, num_qubits_used, block_size=100)
                            if len(rt_monitor['block_entropies']) > 0:
                                fig_entropy, ax_entropy = plt.subplots(figsize=(10, 5))
                                block_indices = range(1, rt_monitor['num_blocks'] + 1)
                                ax_entropy.plot(block_indices, rt_monitor['block_entropies'],
                                                marker='o', linewidth=2, markersize=6, color='#667eea')
                                ax_entropy.axhline(y=rt_monitor['mean_entropy'], color='#27ae60',
                                                   linestyle='--', linewidth=2)
                                ax_entropy.set_xlabel('Block Number', fontsize=12, fontweight='bold')
                                ax_entropy.set_ylabel('Min-Entropy per Bit', fontsize=12, fontweight='bold')
                                ax_entropy.set_title('Entropy Consistency Across Data Blocks', fontsize=14, fontweight='bold')
                                ax_entropy.grid(True, alpha=0.3, linestyle='--')
                                figures.append(save_figure_to_data(fig_entropy, 'Entropy Consistency'))
                                plt.close(fig_entropy)
                        except Exception:
                            # non-fatal: don't block UI if entropy plot generation fails
                            pass

                        # Add entropy metrics
                        try:
                            min_entropy = calculate_min_entropy(random_numbers, num_qubits_used)
                            metrics['Min-Entropy'] = f"{min_entropy['min_entropy_total']:.4f}"
                            metrics['Min-Entropy Quality'] = f"{min_entropy['quality_percentage']:.1f}%"
                        except Exception:
                            pass

                        store_simulation_data(lab_id, metrics=metrics, measurements=measurements, figures=figures)
                except Exception:
                    # Swallow exceptions here to avoid breaking the UI
                    pass

            st.divider()

            # ----------------------------
            # Data Export Section
            # ----------------------------
            st.markdown("## Export & Data Preview")

            export_col1, export_col2, export_col3 = st.columns([2, 2, 3])

            with export_col1:
                data_string = "\n".join(map(str, random_numbers))
                st.download_button(
                    label="Download TXT",
                    data=data_string,
                    file_name=f"qrng_{num_qubits_used}qubits_{num_samples_used}samples.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            with export_col2:
                csv_data = "index,value\n" + "\n".join([f"{i},{val}" for i, val in enumerate(random_numbers)])
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"qrng_{num_qubits_used}qubits_{num_samples_used}samples.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            with export_col3:
                # Sample preview with selection
                preview_size = st.slider("Preview sample size:", 10, 200, 50, 10)
                with st.expander(f"Preview first {preview_size} values", expanded=False):
                    preview_data = random_numbers[:preview_size]
                    # Display as columns for better readability
                    cols_per_row = 10
                    for i in range(0, len(preview_data), cols_per_row):
                        st.text(" ".join(f"{val:3d}" for val in preview_data[i:i + cols_per_row]))

        else:
            # Empty state with call-to-action
            st.markdown("""
            <div style='text-align: center; padding: 4rem 2rem; background: #f8f9fa; border-radius: 10px;'>
                <h2>Ready to Generate Quantum Random Numbers?</h2>
                <p style='font-size: 1.2rem; color: #6c757d;'>
                    Configure your parameters above and click the <strong>Generate</strong> button to start!
                </p>
            </div>
            """, unsafe_allow_html=True)

    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #6c757d; padding: 1rem;'>
        <small>Powered by Qiskit & Quantum Mechanics | Built with Streamlit</small>
    </div>
    """, unsafe_allow_html=True)
