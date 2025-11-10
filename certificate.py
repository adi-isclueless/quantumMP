"""
Certificate generator for completed labs
"""

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime
from lab_config import get_lab

def generate_certificate(lab_name: str, user_name: str = None):
    """Generate a certificate for completing a lab"""
    lab_config = get_lab(lab_name)
    if not lab_config:
        # Try to find by name
        from lab_config import LABS
        for name, config in LABS.items():
            if config["id"] == lab_name or name == lab_name:
                lab_config = config
                break
    
    if not lab_config:
        st.error("Lab not found")
        return None
    
    if user_name is None:
        user_name = st.session_state.get("user_name", "Student")
    
    # Create certificate image
    width, height = 1200, 800
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Try to load fonts, fallback to default if not available
    import platform
    try:
        if platform.system() == "Windows":
            font_paths = [
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/ARIAL.TTF",
                "arial.ttf"
            ]
        elif platform.system() == "Darwin":  # macOS
            font_paths = [
                "/Library/Fonts/Arial.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
                "arial.ttf"
            ]
        else:  # Linux
            font_paths = [
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "arial.ttf"
            ]
        
        font_file = None
        for path in font_paths:
            try:
                font_file = path
                ImageFont.truetype(path, 10)  # Test if font exists
                break
            except:
                continue
        
        if font_file:
            title_font = ImageFont.truetype(font_file, 60)
            name_font = ImageFont.truetype(font_file, 48)
            text_font = ImageFont.truetype(font_file, 32)
            date_font = ImageFont.truetype(font_file, 24)
        else:
            raise Exception("No font found")
    except:
        # Use default font if system fonts not available
        title_font = ImageFont.load_default()
        name_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        date_font = ImageFont.load_default()
    
    # Draw border
    border_width = 10
    draw.rectangle([border_width, border_width, width-border_width, height-border_width], 
                   outline='#667eea', width=border_width)
    
    # Draw decorative elements
    # Top decoration
    draw.rectangle([width//2 - 200, 50, width//2 + 200, 70], fill='#667eea')
    
    # Title
    title = "Certificate of Completion"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(((width - title_width) // 2, 120), title, fill='#667eea', font=title_font)
    
    # Subtitle
    subtitle = "Quantum Virtual Labs"
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=text_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    draw.text(((width - subtitle_width) // 2, 200), subtitle, fill='#764ba2', font=text_font)
    
    # Certificate text
    cert_text = f"This is to certify that"
    text_bbox = draw.textbbox((0, 0), cert_text, font=text_font)
    text_width = text_bbox[2] - text_bbox[0]
    draw.text(((width - text_width) // 2, 280), cert_text, fill='black', font=text_font)
    
    # User name
    name_text = user_name
    name_bbox = draw.textbbox((0, 0), name_text, font=name_font)
    name_width = name_bbox[2] - name_bbox[0]
    draw.text(((width - name_width) // 2, 340), name_text, fill='#667eea', font=name_font)
    
    # Lab completion text
    completion_text = f"has successfully completed the lab on"
    comp_bbox = draw.textbbox((0, 0), completion_text, font=text_font)
    comp_width = comp_bbox[2] - comp_bbox[0]
    draw.text(((width - comp_width) // 2, 420), completion_text, fill='black', font=text_font)
    
    # Lab name
    lab_text = f'"{lab_config["title"]}"'
    lab_bbox = draw.textbbox((0, 0), lab_text, font=text_font)
    lab_width = lab_bbox[2] - lab_bbox[0]
    draw.text(((width - lab_width) // 2, 480), lab_text, fill='#764ba2', font=text_font)
    
    # Date
    date_text = f"Date: {datetime.now().strftime('%B %d, %Y')}"
    date_bbox = draw.textbbox((0, 0), date_text, font=date_font)
    date_width = date_bbox[2] - date_bbox[0]
    draw.text(((width - date_width) // 2, 580), date_text, fill='gray', font=date_font)
    
    # Institution
    institution_text = "Vivekanand Education Society's Institute of Technology, Mumbai"
    inst_bbox = draw.textbbox((0, 0), institution_text, font=date_font)
    inst_width = inst_bbox[2] - inst_bbox[0]
    draw.text(((width - inst_width) // 2, 650), institution_text, fill='gray', font=date_font)
    
    # Signature line
    draw.line([width//2 - 150, 720, width//2 + 150, 720], fill='black', width=2)
    draw.text((width//2 - 50, 730), "Signature", fill='gray', font=date_font)
    
    # Bottom decoration
    draw.rectangle([width//2 - 200, height-70, width//2 + 200, height-50], fill='#667eea')
    
    return image

def render_certificate_page(lab_name: str):
    """Render certificate page for a lab"""
    from lab_config import LABS
    lab_config = None
    for name, config in LABS.items():
        if config["id"] == lab_name or name == lab_name:
            lab_config = config
            break
    
    if not lab_config:
        st.error("Lab not found")
        return
    
    st.header("🏆 Certificate of Completion")
    
    # Check if user has completed all requirements
    lab_id = lab_config["id"]
    quiz_passed = False
    simulation_completed = False
    
    if "lab_progress" in st.session_state:
        progress = st.session_state.lab_progress.get(lab_id, {})
        quiz_passed = progress.get("quiz_passed", False)
        simulation_completed = progress.get("simulation_completed", False)
    
    # Check quiz score
    from quiz import has_passed_quiz
    quiz_passed = has_passed_quiz(lab_id) or quiz_passed
    
    if not quiz_passed:
        st.warning("⚠️ Please complete and pass the quiz first (score >= 70%)")
        if st.button("Go to Quiz", use_container_width=True):
            st.session_state.current_lab_section = "Test"
            st.rerun()
        return
    
    if not simulation_completed:
        st.info("💡 Complete the simulation to mark this lab as fully completed.")
        # Allow certificate generation even if simulation not completed, but warn
        st.warning("Note: Certificate can be generated after passing the quiz.")
    
    # Generate certificate
    user_name = st.session_state.get("user_name", "Student")
    
    st.markdown(f"### Congratulations, {user_name}!")
    st.markdown(f"You have successfully completed the **{lab_config['title']}** lab.")
    
    # Generate and display certificate
    if st.button("Generate Certificate", type="primary", use_container_width=True):
        with st.spinner("Generating certificate..."):
            cert_image = generate_certificate(lab_config["title"], user_name)
            
            if cert_image:
                # Convert to bytes
                img_buffer = io.BytesIO()
                cert_image.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                
                # Display certificate
                st.image(cert_image, use_container_width=True)
                
                # Download button
                st.download_button(
                    label="Download Certificate",
                    data=img_buffer.getvalue(),
                    file_name=f"certificate_{lab_config['id']}_{datetime.now().strftime('%Y%m%d')}.png",
                    mime="image/png",
                    use_container_width=True
                )
                
                # Mark certificate as generated
                if "lab_progress" not in st.session_state:
                    st.session_state.lab_progress = {}
                if lab_id not in st.session_state.lab_progress:
                    st.session_state.lab_progress[lab_id] = {}
                st.session_state.lab_progress[lab_id]["certificate_generated"] = True
                st.session_state.lab_progress[lab_id]["certificate_date"] = datetime.now().strftime('%Y-%m-%d')
                
                st.success("✅ Certificate generated successfully!")

def has_certificate(lab_id: str):
    """Check if user has generated a certificate for this lab"""
    if "lab_progress" not in st.session_state:
        return False
    progress = st.session_state.lab_progress.get(lab_id, {})
    return progress.get("certificate_generated", False)

