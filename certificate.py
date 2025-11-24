"""
Certificate generator for completed labs
"""

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime
from lab_config import get_lab
from progress_store import mark_certificate_generated
import re
import os
import platform
import matplotlib.pyplot as plt

def store_simulation_data(lab_id: str, metrics: dict = None, measurements: dict = None, figures: list = None):
    """
    Store simulation data for inclusion in PDF reports.
    
    Args:
        lab_id: The lab identifier
        metrics: Dictionary of metric names and values (e.g., {'QBER': '5.2%', 'Fidelity': '0.95'})
        measurements: Dictionary of measurement outcomes (e.g., {'00': 512, '11': 512})
        figures: List of figure data - can be:
            - matplotlib Figure objects (will be converted to PNG)
            - BytesIO objects containing image data
            - Bytes containing image data
            - Dicts with 'image' (Figure/bytes/BytesIO) and optional 'caption' (str)
    
    Example usage in a lab:
        from certificate import store_simulation_data, save_figure_to_data
        import matplotlib.pyplot as plt
        
        # After running simulation
        counts = {'00': 512, '11': 512}
        qber = 5.2
        
        # Create a figure
        fig, ax = plt.subplots()
        # ... plot something ...
        
        # Store the data
        store_simulation_data(
            lab_id='bb84',
            metrics={'QBER': f'{qber}%', 'Sifted Bits': '50'},
            measurements=counts,
            figures=[save_figure_to_data(fig, 'Measurement Results')]
        )
    """
    # Ensure global container exists
    if "lab_simulation_data" not in st.session_state:
        st.session_state.lab_simulation_data = {}

    # Ensure entry for this lab
    if lab_id not in st.session_state.lab_simulation_data:
        st.session_state.lab_simulation_data[lab_id] = {
            "metrics": {},
            "measurements": {},
            "figures": []
        }

    # Merge metrics and measurements
    if metrics:
        st.session_state.lab_simulation_data[lab_id]["metrics"].update(metrics)
    if measurements:
        st.session_state.lab_simulation_data[lab_id]["measurements"].update(measurements)

    # Normalize and store figures
    if figures:
        normalized = []
        for item in figures:
            if item is None:
                continue
            caption = ""
            imgobj = item
            if isinstance(item, dict):
                caption = item.get("caption", "") or ""
                imgobj = item.get("image", imgobj)

            # matplotlib Figure -> PNG BytesIO
            try:
                if isinstance(imgobj, plt.Figure):
                    buf = io.BytesIO()
                    imgobj.savefig(buf, format="png", bbox_inches="tight", dpi=150)
                    buf.seek(0)
                    normalized.append({"image": buf, "caption": caption})
                    continue
            except Exception:
                pass

            # bytes / bytearray
            if isinstance(imgobj, (bytes, bytearray)):
                buf = io.BytesIO(imgobj)
                buf.seek(0)
                normalized.append({"image": buf, "caption": caption})
                continue

            # file-like (BytesIO, open file)
            if hasattr(imgobj, "read"):
                try:
                    data = imgobj.read()
                    buf = io.BytesIO(data)
                    buf.seek(0)
                    normalized.append({"image": buf, "caption": caption})
                    continue
                except Exception:
                    pass

            # treat as path-like
            try:
                with open(imgobj, "rb") as fh:
                    buf = io.BytesIO(fh.read())
                    buf.seek(0)
                    normalized.append({"image": buf, "caption": caption})
                    continue
            except Exception:
                # skip objects we can't handle
                continue

        st.session_state.lab_simulation_data[lab_id]["figures"].extend(normalized)

def save_figure_to_data(fig, caption: str = None):
    """
    Helper function to save a matplotlib figure for report inclusion.
    
    Args:
        fig: matplotlib Figure object
        caption: Optional caption for the figure
    
    Returns:
        Dictionary with 'image' and 'caption' keys
    """
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    buf.seek(0)
    return {'image': buf, 'caption': caption or ''}

def generate_certificate(lab_id_or_name: str, user_name: str = None, lab_config: dict = None):
    """Generate a premium certificate for completing a lab including VESIT Logo"""
    # If lab_config is provided, use it directly
    if lab_config is None:
        from lab_config import get_lab, LABS
        lab_config = get_lab(lab_id_or_name)

        # Fallback: try to find by ID or name
        if not lab_config:
            for name, config in LABS.items():
                if config["id"] == lab_id_or_name or name == lab_id_or_name:
                    lab_config = config
                    break

        if not lab_config:
            st.error(f"Lab not found: {lab_id_or_name}")
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
            cert_image = generate_certificate(lab_id, user_name, lab_config)
            
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
                mark_certificate_generated(lab_id)
                
                st.success("Certificate generated successfully!")
    
    # Generate Report button
    st.markdown("---")
    st.markdown("### Generate Lab Report")
    st.markdown("Create a comprehensive PDF report containing the experiment details, theory, and conclusions.")
    
    if st.button("Generate Report", type="primary", use_container_width=True):
        with st.spinner("Generating PDF report..."):
            pdf_buffer = generate_lab_report(lab_config, user_name)
            
            if pdf_buffer:
                st.success("Report generated successfully!")
                st.download_button(
                    label="Download Report (PDF)",
                    data=pdf_buffer.getvalue(),
                    file_name=f"report_{lab_config['id']}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

def generate_lab_report(lab_config: dict, user_name: str = None):
    """Generate a PDF report for the lab experiment"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
    except ImportError:
        st.error("reportlab library is required. Please install it using: pip install reportlab")
        return None
    
    if user_name is None:
        user_name = st.session_state.get("user_name", "Student")
    
    # Register a Unicode-capable font so Greek symbols render correctly
    body_font_name = "Helvetica"
    bold_font_name = "Helvetica-Bold"
    font_candidates = []
    system_name = platform.system()
    if system_name == "Windows":
        font_candidates = [
            ("ArialUnicodeMS", r"C:\Windows\Fonts\arialuni.ttf", r"C:\Windows\Fonts\arialuni.ttf"),
            ("Arial", r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\arialbd.ttf"),
        ]
    elif system_name == "Darwin":
        font_candidates = [
            ("ArialUnicodeMS", "/Library/Fonts/Arial Unicode.ttf", "/Library/Fonts/Arial Unicode.ttf"),
            ("Arial", "/Library/Fonts/Arial.ttf", "/Library/Fonts/Arial Bold.ttf"),
        ]
    else:  # Linux and others
        font_candidates = [
            ("DejaVuSans", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            ("FreeSans", "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
             "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"),
        ]

    for candidate_name, regular_path, bold_path in font_candidates:
        if os.path.exists(regular_path) and os.path.exists(bold_path):
            try:
                pdfmetrics.registerFont(TTFont(candidate_name, regular_path))
                pdfmetrics.registerFont(TTFont(f"{candidate_name}-Bold", bold_path))
                body_font_name = candidate_name
                bold_font_name = f"{candidate_name}-Bold"
                break
            except Exception:
                continue

    # Create PDF buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=36, leftMargin=32,
                            topMargin=32, bottomMargin=32)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName=bold_font_name
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#3949ab'),
        spaceAfter=12,
        spaceBefore=20,
        fontName=bold_font_name
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#5e35b1'),
        spaceAfter=10,
        spaceBefore=15,
        fontName=bold_font_name
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.black,
        spaceAfter=12,
        alignment=TA_JUSTIFY,
        leading=14,
        fontName=body_font_name
    )
    
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=5,
        alignment=TA_LEFT,
        fontName=body_font_name
    )
    
    # Helper function to sanitize plain text (used in tables)
    def sanitize_plain_text(text):
        if text is None:
            return ""
        if not isinstance(text, str):
            text = str(text)
        replacement_map = {
            '\u27E8': '<', '\u27E9': '>',
            '\u3008': '<', '\u3009': '>',
            '\u2329': '<', '\u232A': '>',
        }
        if any(ch in text for ch in replacement_map):
            text = ''.join(replacement_map.get(ch, ch) for ch in text)
        return text

    # Helper function to clean markdown and convert to Paragraph
    def markdown_to_paragraph(text, style):
        # Remove markdown headers
        text = re.sub(r'^###+\s+(.+)$', r'<b>\1</b>', text, flags=re.MULTILINE)
        # Convert bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        # Convert italic
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        # Convert code blocks (simple)
        text = re.sub(r'`(.+?)`', r'<font name="Courier">\1</font>', text)
        # Convert Unicode superscript and subscript characters to <super> or <sub>
        superscript_map = {
            '\u2070': '0', '\u00b9': '1', '\u00b2': '2', '\u00b3': '3',
            '\u2074': '4', '\u2075': '5', '\u2076': '6', '\u2077': '7', '\u2078': '8', '\u2079': '9',
            '\u207a': '+', '\u207b': '-', '\u207c': '=', '\u207d': '(', '\u207e': ')', '\u207f': 'n',
            '\u02b0': 'h', '\u02b2': 'j', '\u1d2c': 'L'
        }

        subscript_map = {
            '\u2080': '0', '\u2081': '1', '\u2082': '2', '\u2083': '3',
            '\u2084': '4', '\u2085': '5', '\u2086': '6', '\u2087': '7', '\u2088': '8', '\u2089': '9',
            '\u208a': '+', '\u208b': '-', '\u208c': '=', '\u208d': '(', '\u208e': ')',
            '\u2090': 'a', '\u2091': 'e', '\u2092': 'o', '\u2093': 'x', '\u2095': 'h',
            '\u2096': 'k', '\u2097': 'l', '\u2098': 'm', '\u2099': 'n', '\u209a': 'p', '\u209b': 's', '\u209c': 't'
        }

        def replace_super_sub_runs(s: str) -> str:
            out = []
            i = 0
            L = len(s)
            while i < L:
                ch = s[i]
                if ch in superscript_map:
                    run = []
                    while i < L and s[i] in superscript_map:
                        run.append(superscript_map.get(s[i], ''))
                        i += 1
                    out.append(f"<super>{''.join(run)}</super>")
                elif ch in subscript_map:
                    run = []
                    while i < L and s[i] in subscript_map:
                        run.append(subscript_map.get(s[i], ''))
                        i += 1
                    out.append(f"<sub>{''.join(run)}</sub>")
                else:
                    out.append(ch)
                    i += 1
            return ''.join(out)

        text = replace_super_sub_runs(text)

        # Convert common bra-ket angle characters to safe HTML entities so they
        # render correctly in ReportLab paragraphs (avoid raw '<' / '>' which
        # are interpreted as markup).
        angle_map = {
            '\u27E8': '&lt;',  # ⟨
            '\u27E9': '&gt;',  # ⟩
            '\u3008': '&lt;',  # 〈
            '\u3009': '&gt;',  # 〉
            '\u2329': '&lt;',  # 〈 (fallback)
            '\u232A': '&gt;'   # 〉 (fallback)
        }
        if any(ch in text for ch in angle_map):
            out_chars = []
            for ch in text:
                out_chars.append(angle_map.get(ch, ch))
            text = ''.join(out_chars)

        # Convert line breaks
        text = text.replace('\n', '<br/>')
        return Paragraph(text, style)
    
    # Helper function to add image to PDF
        # Helper function to add image to PDF
    def add_image_to_pdf(image_path_or_buffer, width=None, height=None):
        """Add an image to the PDF, preserving aspect ratio while fitting to page"""
        try:
            from reportlab.platypus import Image as RLImage
            
            # Maximum page dimensions available for images
            max_width = 5.5 * inch
            max_height = 8.5 * inch

            # Prepare a file-like buffer for the image
            if isinstance(image_path_or_buffer, bytes):
                img_buffer = io.BytesIO(image_path_or_buffer)
            elif isinstance(image_path_or_buffer, io.BytesIO):
                img_buffer = image_path_or_buffer
            else:
                # Path-like object
                img_buffer = None

            # Try to determine intrinsic image size using PIL to preserve aspect ratio
            if img_buffer is not None:
                img_buffer.seek(0)
                pil_img = Image.open(img_buffer)
                orig_w_px, orig_h_px = pil_img.size
                
                # Get DPI if available, default to 72
                dpi = pil_img.info.get('dpi', (72, 72))
                dpi_x = dpi[0] if isinstance(dpi, tuple) else dpi
                dpi_y = dpi[1] if isinstance(dpi, tuple) else dpi
                
                # Convert pixels to points (1 point = 1/72 inch)
                try:
                    orig_w_pts = (orig_w_px / dpi_x) * 72
                    orig_h_pts = (orig_h_px / dpi_y) * 72
                except Exception:
                    # Fallback: assume ~96 DPI
                    orig_w_pts = orig_w_px * 0.75
                    orig_h_pts = orig_h_px * 0.75

                # Calculate aspect ratio
                aspect_ratio = orig_w_pts / orig_h_pts if orig_h_pts > 0 else 1

                # Calculate scale to fit within max dimensions while preserving aspect ratio
                scale_w = max_width / orig_w_pts if orig_w_pts > 0 else 1
                scale_h = max_height / orig_h_pts if orig_h_pts > 0 else 1
                
                # Use the smallest scale to ensure it fits in both dimensions
                scale = min(scale_w, scale_h, 1.0)  # Never upscale, only shrink if needed

                # Calculate final dimensions
                final_w = orig_w_pts * scale
                final_h = orig_h_pts * scale

                # Rewind buffer for reportlab
                img_buffer.seek(0)
                img = RLImage(img_buffer, width=final_w, height=final_h)
            else:
                # Path-like handling
                img = RLImage(image_path_or_buffer, width=max_width, height=max_height)

            return img
        except Exception as e:
            st.warning(f"Could not add image to PDF: {e}")
            return None
    
    # Title
    elements.append(Paragraph("Quantum Virtual Laboratory Experiment Report", title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Report Information Table
    info_data = [
        ['Experiment Title:', lab_config.get('title', 'N/A')],
        ['Student Name:', user_name],
        ['Date:', datetime.now().strftime('%B %d, %Y')],
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), bold_font_name),
        ('FONTNAME', (1, 0), (1, -1), body_font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.4*inch))
    
    # 1. Aim/Objective
    elements.append(Paragraph("1. Aim", heading_style))
    aim_text = lab_config.get('description', 'No aim specified.')
    elements.append(markdown_to_paragraph(aim_text, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # 2. Theory
    elements.append(Paragraph("2. Theory", heading_style))
    theory_text = lab_config.get('theory', 'No theory content available.')
    # Split theory into paragraphs for better formatting
    theory_paragraphs = theory_text.split('\n\n')
    for para in theory_paragraphs:
        if para.strip():
            # Check if it's a heading
            if para.strip().startswith('#'):
                # Extract heading text
                heading_match = re.match(r'^#+\s+(.+)$', para.strip())
                if heading_match:
                    elements.append(Paragraph(heading_match.group(1), subheading_style))
            else:
                elements.append(markdown_to_paragraph(para, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # 3. Implementation
    elements.append(Paragraph("3. Implementation", heading_style))
    implementation_text = f"""
    This experiment was implemented using Qiskit, a quantum computing framework, and executed through the Quantum Virtual Labs platform.
    
    <b>Tools and Technologies Used:</b>
    <br/>• Qiskit: Quantum circuit design and simulation
    <br/>• Qiskit Aer: Quantum circuit execution and simulation
    <br/>• Python: Programming language for implementation
    <br/>• Streamlit: Interactive web interface
    
    <b>Methodology:</b>
    <br/>The experiment was conducted through an interactive simulation interface that allows users to:
    <br/>• Design and visualize quantum circuits
    <br/>• Execute quantum operations and measurements
    <br/>• Analyze results and observe quantum phenomena
    <br/>• Understand the theoretical concepts through hands-on experimentation
    
    The implementation follows the theoretical framework described in the Theory section, providing a practical demonstration of quantum computing principles.
    """
    elements.append(markdown_to_paragraph(implementation_text, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # 4. Observations/Results
    elements.append(Paragraph("4. Observations and Results", heading_style))
    
    # Check for stored simulation results
    lab_id = lab_config.get('id', '')
    simulation_data = None
    if "lab_simulation_data" in st.session_state:
        simulation_data = st.session_state.lab_simulation_data.get(lab_id)
    
    # If no simulation data exists, create default figures for the report
    if simulation_data is None:
        from lab_figures import get_lab_figures
        default_figures = get_lab_figures(lab_id)
        if default_figures:
            simulation_data = {
                "metrics": {},
                "measurements": {},
                "figures": default_figures
            }
    
    if simulation_data:
        # Include actual simulation results
        observations_text = f"""
        Through the interactive simulation, the following key observations and results were obtained:
        """
        elements.append(markdown_to_paragraph(observations_text, normal_style))
        elements.append(Spacer(1, 0.15*inch))
        
        # Add simulation metrics/values as a table
        if 'metrics' in simulation_data and simulation_data['metrics']:
            elements.append(Paragraph("Simulation Metrics:", subheading_style))
            metrics_data = [['Metric', 'Value']]
            for key, value in simulation_data['metrics'].items():
                metrics_data.append([
                    sanitize_plain_text(key),
                    sanitize_plain_text(value)
                ])
            
            metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e3f2fd')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), bold_font_name),
                ('FONTNAME', (0, 1), (-1, -1), body_font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            elements.append(metrics_table)
            elements.append(Spacer(1, 0.2*inch))
        
        # Add measurement results/statistics
        if 'measurements' in simulation_data and simulation_data['measurements']:
            elements.append(Paragraph("Measurement Results:", subheading_style))
            meas_data = [['State', 'Count', 'Probability']]
            total = sum(simulation_data['measurements'].values()) if isinstance(simulation_data['measurements'], dict) else 0
            for state, count in simulation_data['measurements'].items():
                prob = (count / total * 100) if total > 0 else 0
                meas_data.append([
                    sanitize_plain_text(state),
                    sanitize_plain_text(count),
                    sanitize_plain_text(f"{prob:.2f}%")
                ])
            
            if len(meas_data) > 1:  # More than just header
                meas_table = Table(meas_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
                meas_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e3f2fd')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), bold_font_name),
                        ('FONTNAME', (0, 1), (-1, -1), body_font_name),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ]))
                elements.append(meas_table)
                elements.append(Spacer(1, 0.2*inch))
        
        # Add figures/images if available
        if 'figures' in simulation_data and simulation_data['figures']:
            elements.append(Paragraph("Simulation Figures:", subheading_style))
            for idx, fig_data in enumerate(simulation_data['figures']):
                if isinstance(fig_data, (bytes, io.BytesIO)):
                    img = add_image_to_pdf(fig_data, width=5*inch)
                    if img:
                        elements.append(img)
                        elements.append(Spacer(1, 0.15*inch))
                elif isinstance(fig_data, dict) and 'image' in fig_data:
                    img = add_image_to_pdf(fig_data['image'], width=5*inch)
                    if img:
                        if 'caption' in fig_data:
                            elements.append(Paragraph(f"<i>Figure {idx+1}: {fig_data['caption']}</i>", info_style))
                        elements.append(img)
                        elements.append(Spacer(1, 0.15*inch))
    else:
        # Generic observations if no simulation data
        observations_text = f"""
        Through the interactive simulation, the following key observations were made:
        
        <b>Key Findings:</b>
        <br/>• The experiment successfully demonstrated the quantum concepts related to {lab_config.get('title', 'the experiment')}
        <br/>• The simulation results align with the theoretical predictions
        <br/>• The interactive nature of the platform facilitated better understanding of quantum phenomena
        
        <b>Experimental Data:</b>
        <br/>The simulation was executed with various parameters, and the results were observed in real-time through the interactive interface. The measurements and outcomes were consistent with quantum mechanical principles.
        
        <i>Note: For detailed simulation results and figures, please run the simulation before generating the report.</i>
        """
        elements.append(markdown_to_paragraph(observations_text, normal_style))
    
    elements.append(Spacer(1, 0.2*inch))
    
    # 5. Conclusion
    elements.append(Paragraph("5. Conclusion", heading_style))
    conclusion_text = f"""
    This laboratory experiment on <b>{lab_config.get('title', 'Quantum Computing')}</b> provided valuable insights into quantum computing principles and their practical applications.
    
    <b>Summary:</b>
    <br/>The experiment successfully demonstrated the theoretical concepts through interactive simulation. The hands-on approach facilitated a deeper understanding of quantum mechanics and its applications in computing.
    
    <b>Key Learnings:</b>
    <br/>• Understanding of fundamental quantum computing concepts
    <br/>• Practical experience with quantum circuit design and simulation
    <br/>• Insight into the behavior of quantum systems
    <br/>• Appreciation for the potential applications of quantum computing
    
    <b>Future Scope:</b>
    <br/>This experiment serves as a foundation for exploring more advanced quantum computing topics, including quantum algorithms, error correction, and quantum communication protocols.
    """
    elements.append(markdown_to_paragraph(conclusion_text, normal_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    elements.append(Spacer(1, 0.2*inch))
    footer_text = f"""
    <i>This report was generated automatically by the Quantum Virtual Labs platform.</i>
    <br/><i>Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i>
    """
    elements.append(markdown_to_paragraph(footer_text, info_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def has_certificate(lab_id: str):
    """Check if user has generated a certificate for this lab"""
    if "lab_progress" not in st.session_state:
        return False
    progress = st.session_state.lab_progress.get(lab_id, {})
    return progress.get("certificate_generated", False)

