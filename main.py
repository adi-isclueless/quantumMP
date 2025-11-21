"""
Quantum Virtual Labs - Main Application
Restructured with login, home page, and lab navigation
"""

import streamlit as st
from auth import init_session_state, require_auth, logout
from lab_config import get_all_labs, get_labs_by_category, LABS
from quiz import render_quiz, has_passed_quiz
from certificate import render_certificate_page, has_certificate
import importlib

import streamlit.components.v1 as components

components.html(
    """
    <script>
        window.parent.document.documentElement.scrollTop = 0;
    </script>
    """,
    height=0,
)

# Page configuration
st.set_page_config(
    page_title="Quantum Virtual Labs",
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
    st.session_state.current_lab_section = "Theory"
if "current_lab" not in st.session_state:
    st.session_state.current_lab = None

# Sidebar navigation
with st.sidebar:
    st.title("Quantum Virtual Labs")
    st.markdown("---")
    
    with st.expander("About Quantum Virtual Labs"):
        st.markdown("""
        #### About the Platform  
        The **Quantum Virtual Labs** initiative is a student-developed environment designed to make
        quantum computing concepts **intuitive and visual** through interactive simulations.  

        **Objectives:**
        - Provide an accessible introduction to **quantum principles and measurements**  
        - Demonstrate **entanglement, superposition, and quantum protocols**  
        - Encourage experimentation with **quantum communication and error analysis**

        #### Technical Stack
        - **Frontend:** Streamlit  
        - **Backend:** Qiskit (Aer Simulator)  
        - **Language:** Python  
        - **Visualization:** Matplotlib, Plotly  

        #### Vision
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
        #### Credits  
        **Mentor:**  
        Dr. *Ranjan Bala Jain*, Department of Electronics and Telecommunication (EXTC)

        **Developed by Students:**  
        - *Aditya Upasani* — Computer Engineering (CMPN)  
        - *Abhishek Vishwakarma* — Information Technology (IT)  
        - *Yash Mahajan* — Computer Engineering (CMPN)  
        - *Ryan D'Souza* — Computer Engineering (CMPN)

        ---

        © 2025 Quantum Virtual Labs • Developed at VESIT
        """)
    
    st.markdown("---")
    
    # User info
    st.markdown(f"**Welcome, {st.session_state.user_name or st.session_state.username}!**")
    if st.button("Logout", use_container_width=True):
        logout()
    
    st.markdown("---")
    
    # If in a lab, show lab-specific navigation
    if st.session_state.current_lab:
        st.markdown("### Lab Sections")
        lab_sections = ["Theory", "Test", "Simulation", "Certificate"]
        
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
                if section == "Test" and quiz_passed:
                    label += " (Passed)"
                elif section == "Certificate" and cert_generated:
                    label += " (Generated)"
                
                if st.button(label, use_container_width=True, 
                           type="primary" if st.session_state.current_lab_section == section else "secondary"):
                    st.session_state.current_lab_section = section
                    st.rerun()
            
            st.markdown("---")
            if st.button("← Back to Home", use_container_width=True):
                st.session_state.current_lab = None
                st.session_state.current_lab_section = "Theory"
                st.rerun()

# Main content area
# Show home page if no lab is selected
if not st.session_state.current_lab:
    # Home page with list of experiments
    st.title("Quantum Virtual Labs")
    st.markdown("**Vivekanand Education Society's Institute of Technology, Mumbai**")
    st.markdown("---")
    
    st.markdown("""
    ### Welcome to Quantum Virtual Labs!
    
    Explore quantum computing concepts through interactive simulations. Each lab follows a structured learning path:
    
    1. **Theory** - Learn the concepts and principles
    2. **Test** - Test your knowledge with a quiz
    3. **Simulation** - Hands-on interactive simulation
    4. **Certificate** - Get your certificate of completion
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
                <div style="
                    border: 2px solid #667eea;
                    border-radius: 10px;
                    padding: 1rem;
                    margin: 0.5rem 0;
                    background: var(--secondary-background-color);
                    color: var(--text-color);
                ">
                    <h4 style="color: var(--text-color); margin-top: 0;">{lab_config['title']}</h4>
                    <p style="font-size: 0.9rem; color: var(--text-color-secondary);">
                        {lab_config['description']}
                    </p>
                    <p style="font-size: 0.8rem; color: var(--text-color-secondary);">
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
                    st.session_state.current_lab_section = "Theory"
                    st.rerun()
        
        st.markdown("---")
    
    # About section
    

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
        st.session_state.current_lab_section = "Theory"
        st.rerun()
    
    # Display lab title
    st.title(lab_config["title"])
    st.markdown(f"**Category:** {lab_config['category']} | **Difficulty:** {lab_config['difficulty']}")
    st.markdown("---")
    
    # Render appropriate section
    section = st.session_state.current_lab_section
    
    if section == "Theory":
        st.title("Theory")
        st.markdown(lab_config["theory"])
        
        # Navigation buttons
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Next: Test Your Knowledge →", type="primary", use_container_width=True):
                st.session_state.current_lab_section = "Test"
                st.rerun()
    
    elif section == "Test":
        render_quiz(lab_config["id"])
        
        # Check if quiz passed, then enable simulation
        lab_id = lab_config["id"]
        quiz_passed = has_passed_quiz(lab_id)
        
        if quiz_passed:
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("← Back to Theory", use_container_width=True):
                    st.session_state.current_lab_section = "Theory"
                    st.rerun()
            with col2:
                if st.button("Next: Simulation →", type="primary", use_container_width=True):
                    st.session_state.current_lab_section = "Simulation"
                    st.rerun()
        else:
            if st.button("← Back to Theory", use_container_width=True):
                st.session_state.current_lab_section = "Theory"
                st.rerun()
    
    elif section == "Simulation":
        st.header("Lab Simulation")
        st.markdown("Interactive simulation of the quantum concepts you've learned.")
        
        # Mark simulation as accessed
        if "lab_progress" not in st.session_state:
            st.session_state.lab_progress = {}
        if lab_config["id"] not in st.session_state.lab_progress:
            st.session_state.lab_progress[lab_config["id"]] = {}
        st.session_state.lab_progress[lab_config["id"]]["simulation_accessed"] = True
        
        # Import and run the lab simulation
        try:
            module_name = f"labs.{lab_config['module']}"
            lab_module = importlib.import_module(module_name)
            
            if hasattr(lab_module, 'run'):
                # Run the simulation
                lab_module.run()
                
                # Mark simulation as completed
                st.session_state.lab_progress[lab_config["id"]]["simulation_completed"] = True
            else:
                st.error("Lab simulation module not found or doesn't have a run() function")
        except Exception as e:
            st.error(f"Error loading lab simulation: {str(e)}")
            st.info("The simulation module may need to be updated for the new structure.")
        
        # Navigation buttons
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← Back to Test", use_container_width=True):
                st.session_state.current_lab_section = "Test"
                st.rerun()
        with col2:
            lab_id = lab_config["id"]
            quiz_passed = has_passed_quiz(lab_id)
            if quiz_passed:
                if st.button("Next: Certificate →", type="primary", use_container_width=True):
                    st.session_state.current_lab_section = "Certificate"
                    st.rerun()
            else:
                st.info("Complete and pass the quiz to unlock the certificate")
    
    elif section == "Certificate":
        render_certificate_page(lab_config["id"])
        
        # Navigation button
        if st.button("← Back to Simulation", use_container_width=True):
            st.session_state.current_lab_section = "Simulation"
            st.rerun()