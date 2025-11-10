"""
Certificate generator for completed labs
"""

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime
from lab_config import get_lab

def generate_certificate(lab_name: str, user_name: str = None):
    """Generate a premium certificate for completing a lab including VESIT Logo"""
    from lab_config import get_lab
    lab_config = get_lab(lab_name)

    if not lab_config:
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

    # Canvas size
    width, height = 1600, 1100
    image = Image.new('RGB', (width, height), color="#ffffff")
    draw = ImageDraw.Draw(image)

    # ----------------------------
    # Load VESIT Logo
    # ----------------------------
    import os
    logo_path = os.path.join(os.path.dirname(__file__), "vesit_logo.png")
    try:
        logo = Image.open(logo_path).convert("RGBA")
    except Exception as e:
        st.error(f"Logo file not found: {e}")
        return None

    # Resize logo
    original_w, original_h = logo.size
    logo_width = 240
    scale_factor = logo_width / original_w
    logo_height = int(original_h * scale_factor)
    logo = logo.resize((logo_width, logo_height), Image.LANCZOS)

    # Paste logo at top center
    logo_x = (width - logo_width) // 2
    logo_y = 70
    image.paste(logo, (logo_x, logo_y), logo)

    # ----------------------------
    # Load Fonts
    # ----------------------------
    import platform
    try:
        if platform.system() == "Windows":
            font_path = "C:/Windows/Fonts/arial.ttf"
        elif platform.system() == "Darwin":
            font_path = "/Library/Fonts/Arial.ttf"
        else:
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

        FONT_BOLD = ImageFont.truetype(font_path, 70)
        FONT_NAME = ImageFont.truetype(font_path, 60)
        FONT_TEXT = ImageFont.truetype(font_path, 38)
        FONT_SMALL = ImageFont.truetype(font_path, 30)
    except:
        FONT_BOLD = ImageFont.load_default()
        FONT_NAME = ImageFont.load_default()
        FONT_TEXT = ImageFont.load_default()
        FONT_SMALL = ImageFont.load_default()

    # ----------------------------
    # Gold Border
    # ----------------------------
    gold1 = (212, 175, 55)
    gold2 = (255, 215, 100)

    def gradient_line(x1, y1, x2, y2, col1, col2):
        h = y2 - y1
        for i in range(h):
            r = int(col1[0] + i*(col2[0]-col1[0])/h)
            g = int(col1[1] + i*(col2[1]-col1[1])/h)
            b = int(col1[2] + i*(col2[2]-col1[2])/h)
            draw.line([(x1, y1+i), (x2, y1+i)], fill=(r,g,b))

    # Top, bottom, left, right borders
    gradient_line(30, 30, width-30, 60, gold1, gold2)
    gradient_line(30, height-60, width-30, height-30, gold2, gold1)
    gradient_line(30, 60, 60, height-60, gold1, gold2)
    gradient_line(width-60, 60, width-30, height-60, gold2, gold1)

    # ----------------------------
    # Dynamic Vertical Spacing
    # ----------------------------
    title_y = logo_y + logo_height + 40  # BELOW the logo

    # ----------------------------
    # Certificate Title
    # ----------------------------
    title = "Certificate of Completion"
    tw = draw.textlength(title, font=FONT_BOLD)
    draw.text(((width - tw) // 2, title_y), title, fill="#1a237e", font=FONT_BOLD)

    # Decorative Line
    draw.line(
        (width/2 - 260, title_y + 80, width/2 + 260, title_y + 80),
        fill="#1a237e", width=4
    )

    # Subtitle
    subtitle = "Quantum Virtual Labs"
    sw = draw.textlength(subtitle, font=FONT_TEXT)
    draw.text(((width - sw) // 2, title_y + 130), subtitle, fill="#3949ab", font=FONT_TEXT)

    # Body Text
    text = "This is to certify that"
    tw = draw.textlength(text, font=FONT_TEXT)
    draw.text(((width - tw) // 2, title_y + 210), text, fill="black", font=FONT_TEXT)

    # Student Name
    nw = draw.textlength(user_name, font=FONT_NAME)
    draw.text(((width - nw) // 2, title_y + 270), user_name, fill="#1a237e", font=FONT_NAME)

    # Completion Line
    cl = "has successfully completed the laboratory module:"
    clw = draw.textlength(cl, font=FONT_TEXT)
    draw.text(((width - clw) // 2, title_y + 350), cl, fill="black", font=FONT_TEXT)

    # Lab Name
    lab_text = f"“{lab_config['title']}”"
    lw = draw.textlength(lab_text, font=FONT_TEXT)
    draw.text(((width - lw) // 2, title_y + 410), lab_text, fill="#5e35b1", font=FONT_TEXT)

    # Date
    date_txt = f"Date: {datetime.now().strftime('%B %d, %Y')}"
    dw = draw.textlength(date_txt, font=FONT_SMALL)
    draw.text(((width - dw) // 2, title_y + 490), date_txt, fill="#444", font=FONT_SMALL)

    # Institution
    inst = "Vivekanand Education Society's Institute of Technology, Mumbai"
    iw = draw.textlength(inst, font=FONT_SMALL)
    draw.text(((width - iw) // 2, title_y + 650), inst, fill="#777", font=FONT_SMALL)

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
    
    st.header("Certificate of Completion")
    
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
        st.warning("Please complete and pass the quiz first (score >= 70%)")
        if st.button("Go to Quiz", use_container_width=True):
            st.session_state.current_lab_section = "Test"
            st.rerun()
        return
    
    if not simulation_completed:
        st.info("Complete the simulation to mark this lab as fully completed.")
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
                
                st.success("Certificate generated successfully!")

def has_certificate(lab_id: str):
    """Check if user has generated a certificate for this lab"""
    if "lab_progress" not in st.session_state:
        return False
    progress = st.session_state.lab_progress.get(lab_id, {})
    return progress.get("certificate_generated", False)

