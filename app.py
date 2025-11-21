# app.py
"""
Single-file Streamlit app:
- polished multi-step UI
- live HTML preview
- PDF generation (reportlab preferred; fallback to fpdf)
- SMTP email send with PDF attachment
- ready-made e-sign payload templates and instructions
"""

import streamlit as st
import datetime
import os
import io
import base64
import json
from email.message import EmailMessage
import smtplib

# prefer reportlab for robust UTF-8 handling
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False

# fallback to FPDF if reportlab not available
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except Exception:
    FPDF_AVAILABLE = False

# -------- CONFIG --------
LOGO_PATH = "/mnt/data/2c42bfe0-e688-4517-82b4-c829149f2bae.png"  # uploaded image path
PAGE_ICON = LOGO_PATH if os.path.exists(LOGO_PATH) else "🛡️"

st.set_page_config(page_title="Freelance Shield Pro",
                   page_icon=PAGE_ICON,
                   layout="wide",
                   initial_sidebar_state="auto")

# -------- STYLES --------
st.markdown(
    f"""
    <style>
    :root{{--panel:#0f1724; --muted:#94a3b8; --accent:#2563eb}}
    .stApp {{ background: linear-gradient(rgba(10,10,12,0.95), rgba(10,10,12,0.9)), url('{LOGO_PATH}') no-repeat center; background-size: cover; }}
    .hero-title{{font-size:2.2rem; font-weight:800; color:#fff; margin:0;}}
    .hero-sub{{color:var(--muted); margin-top:6px; font-size:1.05rem}}
    .trust-badge{{background:rgba(255,255,255,0.03); padding:6px 10px; border-radius:6px; color:var(--muted); font-weight:600}}
    .stButton>button{{background:linear-gradient(90deg,#3b82f6,#2563eb); color:#fff; border-radius:8px; padding:10px 18px;}}
    [data-testid="stSidebar"]{{background:#071024; color:#cbd5e1}}
    .panel{{background:rgba(255,255,255,0.03); padding:16px; border-radius:10px;}}
    .muted{{color:var(--muted)}}
    </style>
    """,
    unsafe_allow_html=True,
)

# -------- SESSION STATE defaults --------
if "step" not in st.session_state:
    st.session_state.step = 1
if "scope_templates" not in st.session_state:
    st.session_state.scope_templates = {
        "None": "",
        "Social Media Marketing": "1. DELIVERABLE: 12 Static Posts/month\n   - CRITERIA: PNG, deliver by 25th.\n2. DELIVERABLE: 4 Reels/month (<60s).",
        "Video Editing": "1. DELIVERABLE: Edit 1 YouTube Video (10 mins)\n   - CRITERIA: 1080p, color grade, audio mix.\n2. TIMELINE: Draft in 48 hours.",
        "Web Development": "1. DELIVERABLE: 5-Page WordPress Site\n   - CRITERIA: Mobile responsive, speed > 80.\n2. EXCLUSION: Domain & hosting fees."
    }

# -------- HELPERS --------
def build_contract(values: dict) -> str:
    date = datetime.date.today().strftime("%B %d, %Y")
    gst_note = "(Exclusive of GST)" if values.get("gst_registered") else ""
    total_fee = f"Rs. {int(values['project_fee']):,}"
    advance_amt = int(values['project_fee'] * (values['advance_percent'] / 100))
    advance_text = f"Advance: {values['advance_percent']}% (Rs. {advance_amt:,})"
    scope_text = values.get("scope", "").strip() or "Scope will be attached in Annexure A."

    sections = [
        "PROFESSIONAL SERVICES AGREEMENT",
        f"Date: {date}\n",
        f"BETWEEN: {values['freelancer_name']} (Provider) AND {values['client_name']} (Client)",
        "-" * 60,
        f"1. PAYMENT: Total Fee {total_fee} {gst_note}. {advance_text}. Late payments attract 3x MSME interest (where applicable).",
        f"2. JURISDICTION: Disputes subject to courts in {values['jurisdiction_city']}.",
        "3. IP RIGHTS: Client owns IP only AFTER full payment.",
        "4. TERMINATION: 14 days of client silence = Contract may terminate; provider keeps advance.",
        "\nANNEXURE A: SCOPE OF WORK\n",
        scope_text,
        "\nIN WITNESS WHEREOF, the parties have executed this Agreement.\n",
        "SIGNED BY PROVIDER:\n_________________________\n" + values['freelancer_name'],
        "\nSIGNED BY CLIENT:\n_________________________\n" + values['client_name']
    ]
    return "\n\n".join(sections)

def generate_pdf_reportlab(contract_text: str, scope_text: str, logo_path: str = None) -> bytes:
    """Generate a PDF using reportlab (supports UTF-8). Returns bytes."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Register a TTF font if available for proper UTF-8 rendering
    # Try to register a common font; if not found, fallback to default
    try:
        # Attempt to register DejaVu if available in system fonts
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont("DejaVu", font_path))
            font_name = "DejaVu"
        else:
            font_name = "Helvetica"
    except Exception:
        font_name = "Helvetica"

    y = height - 50
    if logo_path and os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, 40, y - 40, width=120, preserveAspectRatio=True, mask='auto')
            y -= 70
        except Exception:
            pass

    c.setFont(font_name, 12)
    lines = contract_text.splitlines()
    left_margin = 40
    max_width = width - 2 * left_margin
    for line in lines:
        # wrap long lines simply
        if c.stringWidth(line, font_name, 12) < max_width:
            c.drawString(left_margin, y, line)
            y -= 16
        else:
            # naive wrap
            words = line.split()
            cur_line = ""
            for w in words:
                test = (cur_line + " " + w).strip()
                if c.stringWidth(test, font_name, 12) < max_width:
                    cur_line = test
                else:
                    c.drawString(left_margin, y, cur_line)
                    y -= 16
                    cur_line = w
            if cur_line:
                c.drawString(left_margin, y, cur_line)
                y -= 16
        if y < 80:
            c.showPage()
            y = height - 50
            c.setFont(font_name, 12)

    # Annexure page
    c.showPage()
    c.setFont(font_name, 12)
    c.drawString(left_margin, height - 50, "ANNEXURE A: SCOPE OF WORK")
    y = height - 80
    for line in scope_text.splitlines():
        if c.stringWidth(line, font_name, 12) < max_width:
            c.drawString(left_margin, y, line)
            y -= 16
        else:
            words = line.split()
            cur_line = ""
            for w in words:
                test = (cur_line + " " + w).strip()
                if c.stringWidth(test, font_name, 12) < max_width:
                    cur_line = test
                else:
                    c.drawString(left_margin, y, cur_line)
                    y -= 16
                    cur_line = w
            if cur_line:
                c.drawString(left_margin, y, cur_line)
                y -= 16
        if y < 60:
            c.showPage()
            y = height - 50
            c.setFont(font_name, 12)

    c.save()
    buffer.seek(0)
    return buffer.read()

def generate_pdf_fpdf(contract_text: str, scope_text: str, logo_path: str = None) -> bytes:
    """Fallback PDF generation using FPDF (latin-1 fallback)."""
    pdf = FPDF()
    pdf.add_page()
    if logo_path and os.path.exists(logo_path):
        try:
            pdf.image(logo_path, 10, 8, 30)
            pdf.ln(22)
        except Exception:
            pass
    pdf.set_font("Arial", size=10)
    safe = contract_text.encode("latin-1", "replace").decode("latin-1")
    for line in safe.splitlines():
        pdf.multi_cell(0, 6, line)
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "ANNEXURE A: SCOPE OF WORK", ln=True)
    pdf.ln(4)
    pdf.set_font("Arial", size=10)
    scope_safe = scope_text.encode("latin-1", "replace").decode("latin-1")
    pdf.multi_cell(0, 6, scope_safe or "(empty)")
    return pdf.output(dest="S").encode("latin-1")

def pdf_bytes(contract_text: str, scope_text: str) -> bytes:
    if REPORTLAB_AVAILABLE:
        return generate_pdf_reportlab(contract_text, scope_text, LOGO_PATH)
    elif FPDF_AVAILABLE:
        return generate_pdf_fpdf(contract_text, scope_text, LOGO_PATH)
    else:
        raise RuntimeError("No PDF library available. Install reportlab or fpdf.")

def send_email_with_attachment(smtp_host: str, smtp_port: int, smtp_user: str, smtp_password: str,
                               to_email: str, subject: str, body: str, attachment_bytes: bytes, attachment_name: str):
    """
    Send a simple email via SMTP with PDF attachment. Credentials are used only for this call.
    """
    msg = EmailMessage()
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)
    msg.add_attachment(attachment_bytes, maintype="application", subtype="pdf", filename=attachment_name)

    with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as s:
        s.starttls()
        s.login(smtp_user, smtp_password)
        s.send_message(msg)

# E-SIGN payload templates (no calls, just templates & instructions)
def example_esign_payload_docu_sign(contract_bytes_b64: str, recipient_name: str, recipient_email: str):
    """
    Returns an example JSON payload for DocuSign-like APIs.
    You will still need to follow provider docs and attach authentication.
    """
    payload = {
        "documents": [
            {
                "documentBase64": contract_bytes_b64,
                "name": "Freelance_Agreement.pdf",
                "fileExtension": "pdf",
                "documentId": "1"
            }
        ],
        "recipients": {
            "signers": [
                {
                    "email": recipient_email,
                    "name": recipient_name,
                    "recipientId": "1",
                    "routingOrder": "1"
                }
            ]
        },
        "status": "sent"
    }
    return payload

# -------- SIDEBAR --------
with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=140)
    st.markdown("### Why Freelance Shield")
    st.markdown("- MSME-friendly: includes statutory-interest clause")
    st.markdown("- Anti-ghosting: auto-termination protection")
    st.markdown("- IP lock: you retain rights until payment clears")
    st.markdown("---")
    st.markdown("### Tools")
    st.write("Use the steps to the left. Nothing is stored permanently.")
    st.markdown("---")
    st.markdown("### Quick help")
    st.caption("Need help integrating DocuSign/HelloSign? Export PDF and use the provider's developer dashboard. If you want, I can prepare the exact API call for your account.")

st.markdown("")

# -------- HERO / SUMMARY --------
hero_col, _ = st.columns([3, 1])
with hero_col:
    st.markdown('<div class="hero-title">Stop chasing payments. Protect your work.</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Generate enforceable, MSME-aware freelance contracts in minutes — live preview & single-file app.</div>', unsafe_allow_html=True)
    st.markdown('<div style="display:flex; gap:8px; margin-top:10px;">'
                '<div class="trust-badge">🏛️ MSME Protected</div>'
                '<div class="trust-badge">👻 Anti-Ghosting</div>'
                '<div class="trust-badge">🔒 IP Lock</div></div>', unsafe_allow_html=True)
st.markdown("---")

# -------- MAIN: Multi-step form on left, preview on right --------
left, right = st.columns([2, 3], gap="large")

with left:
    st.markdown("### 1 — Fill details (guided)")
    step_cols = st.columns([1,1,1,1])
    labels = ["Parties", "Scope", "Money", "Generate"]
    for i, c in enumerate(step_cols):
        marker = "✅" if st.session_state.step > i+1 else f"{i+1}"
        c.markdown(f"**{marker}**\n{labels[i]}")

    if st.session_state.step == 1:
        st.markdown("#### 👤 Parties")
        c1, c2 = st.columns(2)
        with c1:
            freelancer_name = st.text_input("Your name (Provider)", value=st.session_state.get("freelancer_name", "Amit Kumar"))
            jurisdiction_city = st.text_input("Your City (for Court Jurisdiction)", value=st.session_state.get("jurisdiction_city", "Bengaluru, Karnataka"))
        with c2:
            client_name = st.text_input("Client / Company name", value=st.session_state.get("client_name", "Tech Solutions Pvt Ltd"))
            gst_registered = st.checkbox("I am GST Registered", value=st.session_state.get("gst_registered", False))

        if st.button("Next: Define Scope"):
            st.session_state.update({
                "freelancer_name": freelancer_name,
                "jurisdiction_city": jurisdiction_city,
                "client_name": client_name,
                "gst_registered": gst_registered,
                "step": 2
            })
            st.experimental_rerun()

    elif st.session_state.step == 2:
        st.markdown("#### 🎯 Scope of Work")
        template = st.selectbox("Start with a template (optional)", options=list(st.session_state.scope_templates.keys()))
        scope_default = st.session_state.scope_templates.get(template, "")
        scope_text = st.text_area("Scope (Annexure A)", value=st.session_state.get("scope", scope_default), height=220)
        st.caption("Tip: itemize deliverables and exclusions to avoid disputes.")
        back, nxt = st.columns([1,1])
        if back.button("Back"):
            st.session_state.step = 1
            st.experimental_rerun()
        if nxt.button("Next: Financials"):
            st.session_state.scope = scope_text
            st.session_state.step = 3
            st.experimental_rerun()

    elif st.session_state.step == 3:
        st.markdown("#### 💰 Financials")
        c1, c2, c3 = st.columns(3)
        with c1:
            project_fee = st.number_input("Total Project Fee (INR)", value=int(st.session_state.get("project_fee", 50000)), step=1000, min_value=0)
        with c2:
            hourly_rate = st.number_input("Overtime Rate (INR/hr)", value=int(st.session_state.get("hourly_rate", 2000)), step=500, min_value=0)
        with c3:
            advance_percent = st.slider("Advance Required (%)", 0, 100, value=int(st.session_state.get("advance_percent", 50)))

        st.info(f"You will receive Rs. {int(project_fee * (advance_percent / 100)):,} as advance.")
        back, nxt = st.columns([1,1])
        if back.button("Back"):
            st.session_state.step = 2
            st.experimental_rerun()
        if nxt.button("Next: Generate"):
            st.session_state.update({"project_fee": project_fee, "hourly_rate": hourly_rate, "advance_percent": advance_percent})
            st.session_state.step = 4
            st.experimental_rerun()

    elif st.session_state.step == 4:
        st.markdown("#### ✅ Ready to generate")
        st.write("Review the preview on the right. Generate PDF, email it, or prepare the e-sign payload below.")
        back, gen = st.columns([1,1])
        if back.button("Back"):
            st.session_state.step = 3
            st.experimental_rerun()
        if gen.button("🚀 Generate PDF (creates file in memory)"):
            # prepare contract and generate PDF bytes
            values = {
                "freelancer_name": st.session_state.get("freelancer_name", ""),
                "client_name": st.session_state.get("client_name", ""),
                "jurisdiction_city": st.session_state.get("jurisdiction_city", ""),
                "project_fee": st.session_state.get("project_fee", 0),
                "advance_percent": st.session_state.get("advance_percent", 0),
                "hourly_rate": st.session_state.get("hourly_rate", 0),
                "scope": st.session_state.get("scope", ""),
                "gst_registered": st.session_state.get("gst_registered", False)
            }
            contract_text = build_contract(values)
            try:
                pdf_data = pdf_bytes(contract_text, values["scope"])
            except Exception as e:
                st.error("PDF generation failed: " + str(e))
                pdf_data = None

            if pdf_data:
                st.session_state["last_pdf"] = pdf_data
                st.success("PDF generated in memory. You can download, email, or prepare e-sign payload.")
            else:
                st.error("No PDF produced.")

# RIGHT: Live preview + actions
with right:
    st.markdown("### Live preview & actions")
    preview_values = {
        "freelancer_name": st.session_state.get("freelancer_name", "Amit Kumar"),
        "client_name": st.session_state.get("client_name", "Tech Solutions Pvt Ltd"),
        "jurisdiction_city": st.session_state.get("jurisdiction_city", "Bengaluru, Karnataka"),
        "project_fee": st.session_state.get("project_fee", 50000),
        "advance_percent": st.session_state.get("advance_percent", 50),
        "hourly_rate": st.session_state.get("hourly_rate", 2000),
        "scope": st.session_state.get("scope", st.session_state.scope_templates.get("None", "")),
        "gst_registered": st.session_state.get("gst_registered", False)
    }
    preview_text = build_contract(preview_values)

    # Nicely render the preview inside an HTML component (simple lightweight renderer)
    preview_html = f"""
    <div style="background:#051027; padding:18px; border-radius:8px; color:#dbeafe; font-family: Inter, sans-serif;">
      <h3 style="margin-top:0;color:#fff">Contract preview</h3>
      <div style="font-family: 'Courier New', monospace; white-space:pre-wrap; background:rgba(255,255,255,0.02); padding:12px; border-radius:6px; max-height:540px; overflow:auto;">
        {st.markdown(preview_text.replace('\n', '<br>'), unsafe_allow_html=True)}
      </div>
    </div>
    """

    # fallback — we already rendered above; keep a direct textarea as well
    st.text_area("Plain preview (read-only)", value=preview_text, height=430, key="plain_preview")
    st.markdown("---")

    # If a PDF exists in session, show actions
    if st.session_state.get("last_pdf"):
        st.success("✅ PDF in memory")
        col1, col2 = st.columns([1,1])
        with col1:
            st.download_button("📥 Download PDF", st.session_state["last_pdf"], file_name="Freelance_Agreement.pdf", mime="application/pdf", use_container_width=True)
        with col2:
            with st.expander("✉️ Email this PDF to client"):
                st.markdown("Enter SMTP credentials to send this file. Credentials are used for this call only; nothing is stored.")
                smtp_host = st.text_input("SMTP Host", value="smtp.gmail.com")
                smtp_port = st.number_input("SMTP Port", value=587)
                smtp_user = st.text_input("SMTP Username (email)", value="")
                smtp_pass = st.text_input("SMTP Password / App Password", type="password")
                to_email = st.text_input("Recipient email", value=st.session_state.get("client_email", "client@example.com"))
                subj = st.text_input("Email subject", value="Freelance Agreement")
                body = st.text_area("Email body", value="Please find attached the agreement. Sign and return.", height=120)
                if st.button("Send email now"):
                    try:
                        send_email_with_attachment(smtp_host, smtp_port, smtp_user, smtp_pass,
                                                   to_email, subj, body,
                                                   st.session_state["last_pdf"], "Freelance_Agreement.pdf")
                        st.success("Email sent successfully.")
                    except Exception as e:
                        st.error("Email send failed: " + str(e))

        # E-sign helper
        with st.expander("🖋️ Prepare e-sign payloads (example)"):
            st.markdown("Below are example payloads you can use with providers like DocuSign or HelloSign. They require API keys and endpoints from your account.")
            b64 = base64.b64encode(st.session_state["last_pdf"]).decode("utf-8")
            st.code(json.dumps(example_esign_payload_docu_sign(b64, preview_values["client_name"], "client@example.com"), indent=2))
            st.markdown("**Notes:**")
            st.markdown("- Replace `recipient` details and add authentication header (Bearer token).")
            st.markdown("- Provider-specific fields (tabs, signHere locations) must be configured per provider docs.")
            st.markdown("- I can generate a provider-specific API call if you give me the provider and API credentials (or demo keys).")
    else:
        st.info("Generate a PDF first to enable download, email, and e-sign helpers.")

# -------- END --------
