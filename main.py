"""
Quantum Playground - Main Application
Interactive quantum computing simulations and experiments
"""

import streamlit as st
from auth import init_session_state, require_auth, logout
from lab_config import get_all_labs, get_labs_by_category, LABS
from quiz import render_quiz, has_passed_quiz
from certificate import render_certificate_page, has_certificate
import importlib
from progress_store import set_lab_progress_flag
from translations import get_text, TRANSLATIONS
from technical_docs import TECHNICAL_DOCUMENTATION
import urllib.parse

import streamlit.components.v1 as components

components.html(
    """
    <script>
        window.parent.document.documentElement.scrollTop = 0;
    </script>
    <style>
        /* Sidebar width to fit 'Quantum Playground' */
        [data-testid="stSidebar"] { width: 320px !important; min-width: 320px !important; }
        @media (min-width: 1200px) {
            [data-testid="stSidebar"] { width: 340px !important; min-width: 340px !important; }
        }

        /* Mobile-specific styles */
        @media (max-width: 768px) {
            .stButton > button {
                font-size: 14px !important;
                padding: 0.5rem 1rem !important;
            }
            .stMarkdown h1 {
                font-size: 1.5rem !important;
            }
            .stMarkdown h2 {
                font-size: 1.25rem !important;
            }
            .stMarkdown h3 {
                font-size: 1.1rem !important;
            }
            /* Reduce padding on mobile */
            .block-container {
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }
        }
        /* Desktop optimization */
        @media (min-width: 769px) {
            .stButton > button {
                min-height: 45px;
            }
            /* Uniform lab cards */
            .qp-card { min-height: 220px; display: flex; flex-direction: column; justify-content: space-between; }
            .qp-card p { margin-bottom: 0.5rem; }
        }
    </style>
    """,
    height=0,
)

# Page configuration
st.set_page_config(
    page_title="Quantum Playground",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Initialize session state
init_session_state()

# Check authentication
if not st.session_state.authenticated:
    from auth import login_page
    login_page()
    st.stop()

# Initialize current lab section if not set
if "current_lab_section" not in st.session_state:
    st.session_state.current_lab_section = "Learning Path"
if "current_lab" not in st.session_state:
    st.session_state.current_lab = None
# Initialize view mode (welcome, home, or profile)
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "welcome"  # Start with welcome page
# Initialize language
if "language" not in st.session_state:
    st.session_state.language = "en"  # Default to English
# Detect device type for mobile optimization
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = False  # Will be set via user agent or screen width

# Sidebar navigation - ONLY show if NOT on welcome page
if st.session_state.view_mode != "welcome":
    with st.sidebar:
        # Title at top
        st.title(get_text("title", st.session_state.language))
        st.markdown("---")
        
        # Language selector
        lang_options = {"English": "en", "हिंदी (Hindi)": "hi", "Español (Spanish)": "es", "Français (French)": "fr", "Română (Romanian)": "ro"}
        selected_lang = st.selectbox(
            get_text("", st.session_state.language),
            options=list(lang_options.keys()),
            index=list(lang_options.values()).index(st.session_state.language),
            key="lang_selector"
        )
        st.session_state.language = lang_options[selected_lang]
        lang = st.session_state.language
        
        # Help & FAQ Section
        with st.expander(get_text("help", lang)):
            st.markdown("""
            ### Frequently Asked Questions
            
            **Q: How do I start an experiment?**
            A: Click "Start Experiment" on any lab card from the home page.
            
            **Q: Why is the quiz locked?**
            A: You must complete the simulation first. The quiz tests hands-on understanding.
            
            **Q: How do I get a certificate?**
            A: Pass the quiz with 70% or higher, then generate your certificate.
            
            **Q: Can I retake the quiz?**
            A: Yes! Click "Retake Quiz" if you want to improve your score.
            
            **Q: What are the system requirements?**
            A: Any modern browser (Chrome, Firefox, Safari, Edge). No installation needed!
            
            **Q: Is my progress saved?**
            A: Yes, all progress is saved automatically to your account.
            
            **Q: How long does each lab take?**
            A: Most labs take 15-30 minutes to complete (theory + simulation + quiz).
            
            **Q: Can I use this on mobile?**
            A: Yes! The platform is optimized for mobile devices.
            
            **Need more help?** Contact your instructor or check the Technical Documentation.
            """)
        
        # About the Platform
        with st.expander(get_text("about_platform", lang)):
            st.markdown("""
            #### About the Platform  
            **Quantum Playground** is a student-developed interactive platform designed to make
            quantum computing concepts **intuitive and visual** through interactive simulations.  

            **""" + get_text("objectives", lang) + """**
            - Provide an accessible introduction to **quantum principles and measurements**  
            - Demonstrate **entanglement, superposition, and quantum protocols**  
            - Encourage experimentation with **quantum communication and error analysis**

            #### """ + get_text("technical_stack", lang) + """
            - **Frontend:** Streamlit  
            - **Backend:** Qiskit (Aer Simulator)  
            - **Language:** Python  
            - **Visualization:** Matplotlib, Plotly  

            #### """ + get_text("vision", lang) + """
            > "To create a unified, accessible platform that enables students and educators to
            explore quantum phenomena through simulation, experimentation, and visualization."

            ---
            """)
            col1, col2, col3 = st.columns([2, 3, 2])
            with col2:
                try:
                    st.image("vesit_logo.png", width=200)
                except:
                    st.info("VESIT Logo")
            st.markdown("""
            #### """ + get_text("credits", lang) + """  
            **""" + get_text("mentor", lang) + """**  
            Dr. *Ranjan Bala Jain*, Department of Electronics and Telecommunication (EXTC)

            **""" + get_text("developed_by", lang) + """**  
            - *Aditya Upasani* — Computer Engineering (CMPN)  
            - *Abhishek Vishwakarma* — Information Technology (IT)  
            - *Yash Mahajan* — Computer Engineering (CMPN)  
            - *Ryan D'Souza* — Computer Engineering (CMPN)

            ---

            © 2025 Quantum Playground • Developed at VESIT
            """)
        
        # Technical Documentation Button
        if st.button(get_text("technical_docs", lang), use_container_width=True):
            st.session_state.view_mode = "documentation"
            st.session_state.current_lab = None
            st.rerun()
        
        st.markdown("---")
        
        # User info and Progress
        st.markdown(f"**{get_text('welcome', st.session_state.language)} {st.session_state.user_name or st.session_state.username}!**")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(get_text("profile", st.session_state.language), use_container_width=True):
                st.session_state.view_mode = "profile"
                st.session_state.current_lab = None
                st.rerun()
        with col2:
            if st.button(get_text("logout", st.session_state.language), use_container_width=True):
                logout()
        
        st.markdown("---")
        
        # If in a lab, show lab-specific navigation
        if st.session_state.current_lab:
            st.markdown(f"### {get_text('lab_sections', st.session_state.language)}")
            lab_sections = [
                get_text("learning_path", st.session_state.language),
                get_text("theory", st.session_state.language),
                get_text("simulation", st.session_state.language),
                get_text("quiz", st.session_state.language),
                get_text("certificate", st.session_state.language)
            ]
            
            # Get lab config
            lab_config = None
            for lab_name, config in LABS.items():
                if config["id"] == st.session_state.current_lab:
                    lab_config = config
                    break
            
            if lab_config:
                # Show progress indicators
                lab_id = lab_config["id"]
                quiz_passed = has_passed_quiz(lab_id)
                cert_generated = has_certificate(lab_id)
                
                
                for section in lab_sections:
                    label = f"{section}"
                    
                    # Add checkmarks for completed sections
                    if section == "Quiz" and quiz_passed:
                        label += " ✓ Passed"
                    elif section == "Certificate" and cert_generated:
                        label += " ✓ Generated"
                    elif section == "Simulation":
                        sim_completed = st.session_state.lab_progress.get(lab_id, {}).get("simulation_completed", False)
                        if sim_completed:
                            label += " ✓ Completed"
                    
                    if st.button(label, use_container_width=True, 
                               type="primary" if st.session_state.current_lab_section == section else "secondary"):
                        st.session_state.current_lab_section = section
                        st.rerun()
                
                st.markdown("---")
                if st.button("← " + get_text("back_to_experiments", st.session_state.language), use_container_width=True):
                    st.session_state.current_lab = None
                    st.session_state.current_lab_section = "Learning Path"
                    st.session_state.view_mode = "home"
                    st.rerun()

# Main content area
# Show welcome page first after login
if st.session_state.view_mode == "welcome" and not st.session_state.current_lab:
    # Welcome Page
    st.title(get_text("title", st.session_state.language))
    st.markdown("**Vivekanand Education Society's Institute of Technology, Mumbai**")
    st.markdown("---")
    
    # About the Platform
    st.markdown("## " + get_text("about_platform", st.session_state.language))
    st.markdown("""
    **Quantum Playground** is a student-developed interactive platform designed to make 
    quantum computing concepts **intuitive and visual** through interactive simulations.
    """)
    
    # Objectives
    st.markdown("### " + get_text("objectives", st.session_state.language))
    st.markdown("""
    - Provide an accessible introduction to **quantum principles and measurements**
    - Demonstrate **entanglement, superposition, and quantum protocols**
    - Encourage experimentation with **quantum communication and error analysis**
    """)
    
    # Technical Stack
    st.markdown("### " + get_text("technical_stack", st.session_state.language))
    st.markdown("""
    - **Frontend:** Streamlit
    - **Backend:** Qiskit (Aer Simulator)
    - **Language:** Python
    - **Visualization:** Matplotlib, Plotly
    """)
    
    # Vision
    st.markdown("### " + get_text("vision", st.session_state.language))
    st.info("""
    *"To create a unified, accessible platform that enables students and educators to 
    explore quantum phenomena through simulation, experimentation, and visualization."*
    """)
    
    st.markdown("---")
    
    # Credits
    col1, col2 = st.columns([1, 2])
    
    with col1:
        try:
            st.image("vesit_logo.png", width=250)
        except:
            st.info("VESIT Logo")
    
    with col2:
        st.markdown("### Credits")
        st.markdown("""
        **Mentor:**  
        Dr. Ranjan Bala Jain, Department of Electronics and Telecommunication (EXTC)

        **Developed by Students:**
        - Aditya Upasani — Computer Engineering (CMPN)
        - Abhishek Vishwakarma — Information Technology (IT)
        - Yash Mahajan — Computer Engineering (CMPN)
        - Ryan D'Souza — Computer Engineering (CMPN)
        """)
    
    st.markdown("---")
    
    # Welcome Section
    st.markdown("## Welcome to Quantum Playground!")
    st.markdown("""
    Explore quantum computing concepts through interactive simulations. Each experiment follows a structured learning path:
    
    1. **Learning Path** - Overview of your learning journey
    2. **Theory** - Learn the concepts and principles
    3. **Simulation** - Hands-on interactive simulation
    4. **Quiz** - Test your knowledge (unlocked after simulation)
    5. **Certificate** - Get your certificate of completion
    """)
    
    st.markdown("---")
    
    # List of Experiments
    st.markdown("## Available Experiments")
    st.markdown("### 14 Interactive Quantum Experiments:")
    
    experiments = [
        "Measurement in Different Bases",
        "Q-Random Number Generator",
        "Multi-Qubit Superposition",
        "Parity Check with Ancilla Qubit",
        "Q-Circuit Identity Verification",
        "Bell State Analysis and Noise Effects",
        "Entanglement in 3 Qubits (GHZ State)",
        "Entanglement in 3 Qubits (W State)",
        "BB84 Quantum Key Distribution",
        "Superdense Coding",
        "Quantum Teleportation",
        "Tomography of Quantum States",
        "Error Detection with 3-Qubit Phase Flip Code",
        "Error Detection with 3 Qubit Bit Flip Code"
    ]
    
    # Display in two columns
    col1, col2 = st.columns(2)
    mid_point = len(experiments) // 2
    
    with col1:
        for i, exp in enumerate(experiments[:mid_point], 1):
            st.markdown(f"**{i}.** {exp}")
    
    with col2:
        for i, exp in enumerate(experiments[mid_point:], mid_point + 1):
            st.markdown(f"**{i}.** {exp}")
    
    st.markdown("---")
    
    # Call to Action Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Exploring Experiments", use_container_width=True, type="primary"):
            st.session_state.view_mode = "home"
            st.rerun()
    
    st.markdown("---")
    st.markdown("© 2025 Quantum Playground • Developed at VESIT")

# Show home page (experiment listing) if view_mode is "home"
elif st.session_state.view_mode == "home" and not st.session_state.current_lab:
    # Home page with list of experiments
    st.title(get_text("title", st.session_state.language))
    st.markdown("**Vivekanand Education Society's Institute of Technology, Mumbai**")
    st.markdown("---")
    
    st.markdown("""
    ### """ + get_text("welcome", st.session_state.language) + """
    
    Explore quantum computing concepts through interactive simulations. Each lab follows a structured learning path:
    
    1. **Learning Path** - Overview of your learning journey
    2. **Theory** - Learn the concepts and principles
    3. **Simulation** - Hands-on interactive simulation
    4. **Quiz** - Test your knowledge (unlocked after simulation)
    5. **Certificate** - Get your certificate of completion
    """)
    
    st.markdown("---")
    
    # Display labs by category
    labs_by_category = get_labs_by_category()
    
    for category, labs in labs_by_category.items():
        st.markdown(f"### {category}")
        
        # Create columns for lab cards
        cols = st.columns(3)
        for idx, (lab_name, lab_config) in enumerate(labs):
            col = cols[idx % 3]
            
            with col:
                # Check progress
                lab_id = lab_config["id"]
                quiz_passed = has_passed_quiz(lab_id)
                cert_generated = has_certificate(lab_id)
                
                card_html = f"""
                <div class=\"qp-card\" style="
                    border: 2px solid #667eea;
                    border-radius: 10px;
                    padding: 1rem;
                    margin: 0.5rem 0;
                    background: var(--secondary-background-color);
                    color: var(--text-color);
                ">
                    <h4 style=\"color: var(--text-color); margin-top: 0; margin-bottom: 0.5rem;\">{lab_config['title']}</h4>
                    <p style=\"font-size: 0.9rem; color: var(--text-color-secondary);\">
                        {lab_config['description']}
                    </p>
                    <p style=\"font-size: 0.8rem; color: var(--text-color-secondary); margin-top: auto;\">
                        Difficulty: {lab_config['difficulty']} • {
                            'Completed' if cert_generated else
                            'Quiz Passed' if quiz_passed else 'Not Started'
                        }
                    </p>
                </div>
                """

                st.markdown(card_html, unsafe_allow_html=True)
                
                if st.button(f"Start Experiment", key=f"start_{lab_id}", use_container_width=True):
                    st.session_state.current_lab = lab_id
                    st.session_state.current_lab_section = "Learning Path"
                    st.rerun()
        
        st.markdown("---")

elif st.session_state.view_mode == "documentation" and not st.session_state.current_lab:
    # Technical Documentation Page
    st.title("Technical Documentation")
    st.markdown("---")
    st.markdown(TECHNICAL_DOCUMENTATION)
    
    st.markdown("---")
    if st.button("← Back to Home", use_container_width=False):
        st.session_state.view_mode = "home"
        st.rerun()

elif st.session_state.view_mode == "profile" and not st.session_state.current_lab:
    # Profile Page
    st.title("Your Profile")
    st.markdown("---")
    
    # User Information Card
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 15px;
            color: white;
            text-align: center;
        ">
            <h2 style="margin-top: 0; color: white;">{st.session_state.user_name or st.session_state.username}</h2>
            <p style="font-size: 1rem; margin: 10px 0;">@{st.session_state.username}</p>
            <p style="font-size: 0.95rem; margin: 10px 0;">{st.session_state.email}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # Statistics Section
    st.markdown("## Your Statistics")
    
    total_labs = len(LABS)
    completed = sum(1 for lab_id in [config['id'] for config in LABS.values()] if has_certificate(lab_id))
    quiz_passed_count = sum(1 for lab_id in [config['id'] for config in LABS.values()] if has_passed_quiz(lab_id))
    not_started = total_labs - completed - (quiz_passed_count - completed)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Labs", total_labs)
    with col2:
        st.metric("Completed", completed)
    with col3:
        st.metric("In Progress", quiz_passed_count - completed)
    with col4:
        st.metric("Not Started", not_started)
    
    st.markdown("---")
    
    # Completed Experiments Section
    st.markdown("## Completed Experiments")
    
    completed_labs = []
    in_progress_labs = []
    not_started_labs = []
    
    for lab_name, lab_config in LABS.items():
        lab_id = lab_config["id"]
        cert_generated = has_certificate(lab_id)
        quiz_passed = has_passed_quiz(lab_id)
        
        lab_info = {
            'title': lab_config['title'],
            'category': lab_config['category'],
            'difficulty': lab_config['difficulty'],
            'lab_id': lab_id
        }
        
        if cert_generated:
            completed_labs.append(lab_info)
        elif quiz_passed:
            in_progress_labs.append(lab_info)
        else:
            not_started_labs.append(lab_info)
    
    # Display Completed Labs
    if completed_labs:
        for lab in completed_labs:
            col1, col2, col3, col4 = st.columns([2.5, 0.8, 0.8, 0.9])
            with col1:
                st.markdown(f"**{lab['title']}**")
                st.markdown(f"<small>{lab['category']}</small>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<small>{lab['difficulty']}</small>", unsafe_allow_html=True)
            with col3:
                st.markdown("<small style='color: #4caf50; font-weight: bold;'>Completed</small>", unsafe_allow_html=True)
            with col4:
                if st.button("View", key=f"view_{lab['lab_id']}", use_container_width=True):
                    st.session_state.current_lab = lab['lab_id']
                    st.session_state.current_lab_section = "Certificate"
                    st.rerun()
            st.divider()
    else:
        st.info("No completed labs yet. Start an experiment to get started!")
    
    st.markdown("")
    st.markdown("## In Progress")
    
    if in_progress_labs:
        for lab in in_progress_labs:
            col1, col2, col3, col4 = st.columns([2.5, 0.8, 0.8, 0.9])
            with col1:
                st.markdown(f"**{lab['title']}**")
                st.markdown(f"<small>{lab['category']}</small>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<small>{lab['difficulty']}</small>", unsafe_allow_html=True)
            with col3:
                st.markdown("<small style='color: #2196f3; font-weight: bold;'>Quiz Passed</small>", unsafe_allow_html=True)
            with col4:
                if st.button("Continue", key=f"continue_{lab['lab_id']}", use_container_width=True):
                    st.session_state.current_lab = lab['lab_id']
                    st.session_state.current_lab_section = "Simulation"
                    st.rerun()
            st.divider()
    else:
        st.info("No labs in progress.")
    
    st.markdown("")
    
    # Back to Home Button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("← Back to Experiments", use_container_width=True):
            st.session_state.view_mode = "home"
            st.rerun()

else:
    # Lab page
    lab_config = None
    for lab_name, config in LABS.items():
        if config["id"] == st.session_state.current_lab:
            lab_config = config
            break
    
    if not lab_config:
        st.error("Lab not found. Returning to home.")
        st.session_state.current_lab = None
        st.session_state.current_lab_section = "Learning Path"
        st.session_state.view_mode = "home"
        st.rerun()
    
    # Display lab title
    st.title(lab_config["title"])
    st.markdown(f"**Category:** {lab_config['category']} | **Difficulty:** {lab_config['difficulty']}")
    st.markdown("---")
    
    # Render appropriate section
    section = st.session_state.current_lab_section
    
    # Get progress status
    lab_id = lab_config["id"]
    sim_completed = st.session_state.lab_progress.get(lab_id, {}).get("simulation_completed", False)
    quiz_passed = has_passed_quiz(lab_id)
    cert_generated = has_certificate(lab_id)
    
    if section == "Learning Path":
        st.title("Learning Path")
        st.markdown("Follow this structured path to master the quantum concept:")
        st.markdown("---")
        
        # Step 1: Learning Path (current)
        st.markdown("### Step 1: Learning Path (Current Tab)")
        st.info("You are here! Review the complete learning journey.")
        st.markdown("")
        
        # Step 2: Theory
        st.markdown("### Step 2: Theory")
        st.markdown("Learn the fundamental concepts, principles, and mathematics behind this quantum phenomenon.")
        st.markdown("**Status:** Always accessible")
        if st.button("Go to Theory", key="nav_theory", use_container_width=True):
            st.session_state.current_lab_section = "Theory"
            st.rerun()
        st.markdown("")
        
        # Step 3: Simulation
        st.markdown("### Step 3: Simulation")
        st.markdown("Hands-on interactive simulation where you experiment with quantum circuits and observe results.")
        status_sim = "Completed" if sim_completed else "Not started"
        st.markdown(f"**Status:** {status_sim}")
        if st.button("Go to Simulation", key="nav_sim", use_container_width=True):
            st.session_state.current_lab_section = "Simulation"
            st.rerun()
        st.markdown("")
        
        # Step 4: Quiz
        st.markdown("### Step 4: Quiz")
        st.markdown("Test your understanding with a comprehensive quiz. Score 70% or higher to pass.")
        if not sim_completed:
            st.warning("**Locked:** Complete the simulation first to unlock the quiz.")
            st.markdown("**Status:** Locked")
        elif quiz_passed:
            st.markdown("**Status:** Passed")
            if st.button("Go to Quiz", key="nav_quiz", use_container_width=True):
                st.session_state.current_lab_section = "Quiz"
                st.rerun()
        else:
            st.markdown("**Status:** Unlocked - Ready to attempt")
            if st.button("Go to Quiz", key="nav_quiz", use_container_width=True):
                st.session_state.current_lab_section = "Quiz"
                st.rerun()
        st.markdown("")
        
        # Step 5: Certificate
        st.markdown("### Step 5: Certificate & Report")
        st.markdown("Generate your certificate of completion and comprehensive lab report.")
        if not quiz_passed:
            st.warning("**Locked:** Pass the quiz first to unlock certificate generation.")
            st.markdown("**Status:** Locked")
        elif cert_generated:
            st.markdown("**Status:** Generated")
            if st.button("Go to Certificate", key="nav_cert", use_container_width=True):
                st.session_state.current_lab_section = "Certificate"
                st.rerun()
        else:
            st.markdown("**Status:** Unlocked - Ready to generate")
            if st.button("Go to Certificate", key="nav_cert", use_container_width=True):
                st.session_state.current_lab_section = "Certificate"
                st.rerun()
        
        st.markdown("---")
        st.success("**Tip:** Follow the steps in order for the best learning experience!")
        
        # Next button
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Next: Start Learning →", type="primary", use_container_width=True):
                st.session_state.current_lab_section = "Theory"
                st.rerun()
    
    elif section == "Theory":
        st.title("Theory")
        st.markdown(lab_config["theory"])
        
        # Navigation buttons
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← Back to Learning Path", use_container_width=True):
                st.session_state.current_lab_section = "Learning Path"
                st.rerun()
        with col2:
            if st.button("Next: Simulation →", type="primary", use_container_width=True):
                st.session_state.current_lab_section = "Simulation"
                st.rerun()
    
    elif section == "Quiz":
        # Check if simulation is completed
        lab_id = lab_config["id"]
        sim_completed = st.session_state.lab_progress.get(lab_id, {}).get("simulation_completed", False)
        
        if not sim_completed:
            st.warning("⚠️ **Please complete the simulation first before taking the quiz.**")
            st.info("The quiz is designed to test your understanding after hands-on experience with the simulation.")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("← Back to Simulation", type="primary", use_container_width=True):
                    st.session_state.current_lab_section = "Simulation"
                    st.rerun()
            with col2:
                if st.button("← Back to Theory", use_container_width=True):
                    st.session_state.current_lab_section = "Theory"
                    st.rerun()
        else:
            render_quiz(lab_config["id"])
            
            # Check if quiz passed
            quiz_passed = has_passed_quiz(lab_id)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("← " + get_text("back_to_simulation", st.session_state.language), use_container_width=True):
                    st.session_state.current_lab_section = "Simulation"
                    st.rerun()
            with col2:
                if quiz_passed:
                    if st.button(get_text("next_certificate", st.session_state.language), type="primary", use_container_width=True):
                        st.session_state.current_lab_section = "Certificate"
                        st.rerun()
                else:
                    st.info(get_text("pass_quiz_unlock", st.session_state.language))
    
    elif section == "Simulation":
        st.header(get_text("lab_simulation", st.session_state.language))
        st.markdown(get_text("simulation_intro", st.session_state.language))
        
        # Mark simulation as accessed
        set_lab_progress_flag(lab_config["id"], "simulation_accessed", True)
        
        # Import and run the lab simulation
        try:
            module_name = f"labs.{lab_config['module']}"
            lab_module = importlib.import_module(module_name)
            
            if hasattr(lab_module, 'run'):
                # Run the simulation
                try:
                    lab_module.run()
                except TypeError:
                    # If labs later accept a lang param, try passing it
                    try:
                        lab_module.run(st.session_state.language)
                    except Exception:
                        pass
                
                # Mark simulation as completed
                set_lab_progress_flag(lab_config["id"], "simulation_completed", True)
            else:
                st.error("Lab simulation module not found or doesn't have a run() function")
        except Exception as e:
            st.error(f"Error loading lab simulation: {str(e)}")
            st.info("The simulation module may need to be updated for the new structure.")
        
        # Navigation buttons
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← " + get_text("back_to_theory", st.session_state.language), use_container_width=True):
                st.session_state.current_lab_section = "Theory"
                st.rerun()
        with col2:
            if st.button(get_text("next_quiz", st.session_state.language), type="primary", use_container_width=True):
                st.session_state.current_lab_section = "Quiz"
                st.rerun()
    
    elif section == "Certificate":
        render_certificate_page(lab_config["id"])
        
        # Navigation button
        if st.button("← " + get_text("quiz", st.session_state.language), use_container_width=True):
            st.session_state.current_lab_section = "Quiz"
            st.rerun()