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
from progress_store import set_lab_progress_flag

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
    
    # User info and Progress
    st.markdown(f"**Welcome, {st.session_state.user_name or st.session_state.username}!**")
    if st.button("Logout", use_container_width=True):
        logout()
    
    st.markdown("---")
    
    # Progress section
    st.markdown("### Your Progress")
    total_labs = len(LABS)
    completed = sum(1 for lab_id in [config['id'] for config in LABS.values()] if has_certificate(lab_id))
    quiz_passed_count = sum(1 for lab_id in [config['id'] for config in LABS.values()] if has_passed_quiz(lab_id))
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Labs Completed", f"{completed}/{total_labs}")
    with col2:
        st.metric("Quizzes Passed", f"{quiz_passed_count}/{total_labs}")
    
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
    # ============ WELCOME PAGE ============
    st.markdown("""
    <div style="text-align: center; padding: 40px 0;">
        <h1 style="font-size: 3rem; color: #1a237e; margin-bottom: 10px;">Quantum Virtual Labs</h1>
        <p style="font-size: 1.3rem; color: #667eea; margin-bottom: 20px;">
            Vivekanand Education Society's Institute of Technology, Mumbai
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Welcome section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 15px;
            color: white;
            text-align: center;
        ">
            <h2 style="margin-top: 0; color: white;">Welcome to Quantum Virtual Labs!</h2>
            <p style="font-size: 1.1rem; line-height: 1.8;">
                Explore quantum computing concepts through interactive simulations. 
                Each lab follows a structured learning path to help you master quantum computing.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # Learning path explanation
    st.markdown("### Your Learning Journey")
    
    cols = st.columns(4)
    steps = [
        ("", "Theory", "Learn the concepts and principles"),
        ("", "Test", "Test your knowledge with a quiz"),
        ("", "Simulation", "Hands-on interactive simulation"),
        ("", "Certificate", "Get your certificate of completion")
    ]
    
    for col, (icon, title, desc) in zip(cols, steps):
        with col:
            st.markdown(f"""
            <div style="
                text-align: center;
                padding: 20px;
                background-color: #f0f0f0;
                border-radius: 10px;
                border-left: 5px solid #667eea;
            ">
                <div style="font-size: 2rem; margin-bottom: 10px;">{icon}</div>
                <h4 style="margin: 10px 0; color: #1a237e;">{title}</h4>
                <p style="font-size: 0.9rem; color: #666;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("")
    st.markdown("---")
    
    # Call to action
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <h3 style="color: #1a237e; margin-bottom: 15px;">Ready to Start Learning?</h3>
            <p style="color: #666; font-size: 1.1rem; margin-bottom: 25px;">
                Choose an experiment below and begin your quantum computing journey!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Browse All Experiments", type="primary", use_container_width=True, key="browse_experiments"):
            st.session_state.show_labs = True
            st.rerun()
    
    st.markdown("---")
    
    # Always show all experiments in a table/list format
    st.markdown("## Available Experiments")
    st.markdown(f"**Total: 14 Quantum Computing Labs**")
    st.markdown("")
    
    # Get all labs
    all_labs = []
    for lab_name, lab_config in LABS.items():
        lab_id = lab_config["id"]
        quiz_passed = has_passed_quiz(lab_id)
        cert_generated = has_certificate(lab_id)
        
        # Determine status
        if cert_generated:
            status = "Completed"
        elif quiz_passed:
            status = "Quiz Passed"
        else:
            status = "Not Started"
        
        all_labs.append({
            'title': lab_config['title'],
            'category': lab_config['category'],
            'difficulty': lab_config['difficulty'],
            'status': status,
            'lab_id': lab_id,
            'config': lab_config
        })
    
    # Sort by category
    all_labs.sort(key=lambda x: (x['category'], x['title']))
    
    # Display as a list with buttons
    for idx, lab in enumerate(all_labs):
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            st.markdown(f"**{lab['title']}**")
            st.markdown(f"<small>{lab['category']}</small>", unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"<small>Difficulty: {lab['difficulty']}</small>", unsafe_allow_html=True)
        
        with col3:
            # Status badge
            if lab['status'] == 'Completed':
                st.markdown("<small style='color: #4caf50; font-weight: bold;'>Completed</small>", unsafe_allow_html=True)
            elif lab['status'] == 'Quiz Passed':
                st.markdown("<small style='color: #2196f3; font-weight: bold;'>Quiz Passed</small>", unsafe_allow_html=True)
            else:
                st.markdown("<small style='color: #999;'>Not Started</small>", unsafe_allow_html=True)
        
        with col4:
            if st.button("Start", key=f"start_{lab['lab_id']}", use_container_width=True):
                st.session_state.current_lab = lab['lab_id']
                st.session_state.current_lab_section = "Theory"
                st.rerun()
        
        st.divider()
    

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
        set_lab_progress_flag(lab_config["id"], "simulation_accessed", True)
        
        # Import and run the lab simulation
        try:
            module_name = f"labs.{lab_config['module']}"
            lab_module = importlib.import_module(module_name)
            
            if hasattr(lab_module, 'run'):
                # Run the simulation
                lab_module.run()
                
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