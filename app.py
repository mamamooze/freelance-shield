# app.py
import streamlit as st
from fpdf import FPDF
import datetime
import os
import io
import base64
import json
from email.message import EmailMessage
import smtplib

# -------- ASSET: use the uploaded PNG logo (exact path) ----------
# developer requested the uploaded file path be used as the logo url
LOGO_PATH = "/mnt/data/aee8022b-3e6e-40f0-b80b-1bf200509a79.png"
PAGE_ICON = LOGO_PATH if os.path.exists(LOGO_PATH) else "🛡️"

st.set_page_config(page_title="Freelance Shield Pro",
                   page_icon=PAGE_ICON,
                   layout="wide",
                   initial_sidebar_state="auto")

# -------- SIMPLE CSS ----------
st.markdown(
    f"""
    <style>
    .stApp{{background: linear-gradient(rgba(10,10,12,0.95), rgba(10,10,12,0.9));}}
    .hero-title{{font-size:2.2rem; font-weight:800; color:#fff; margin:0;}}
    .hero-sub{{color:#94a3b8; margin-top:6px; font-size:1.05rem}}
    .trust-badge{{background:rgba(255,255,255,0.03); padding:6px 10px; border-radius:6px; color:#94a3b8; font-weight:600}}
    .stButton>button{{background:linear-gradient(90deg,#3b82f6,#2563eb); color:#fff; border-radius:8px; padding:10px 18px;}}
    [data-testid="stSidebar"]{{background:#071024; color:#cbd5e1}}
    .panel{{background:rgba(255,255,255,0.03); padding:16px; border-radius:10px;}}
    </style>
    """,
    unsafe_allow_html=True,
)

# -------- Session defaults ----------
if "step" not in st.session_state:
    st.session_state.step = 1
if "scope_templates" not in st.session_state:
    st.session_state.scope_templates = {
        "None": "",
        "Social Media Marketing": "1. DELIVERABLE: 12 Static Posts/month\n   - CRITERIA: PNG, deliver by 25th.\n2. DELIVERABLE: 4 Reels/month (<60s).",
        "Video Editing": "1. DELIVERABLE: Edit 1 YouTube Video (10 mins)\n   - CRITERIA: 1080p, color grade, audio mix.\n2. TIMELINE: Draft in 48 hours.",
        "Web Development": "1. DELIVERABLE: 5-Page WordPress Site\n   - CRITERIA: Mobile responsive, speed > 80.\n2. EXCLUSION: Domain & hosting fees."
    }

# -------- Helpers ----------
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

def generate_pdf_fpdf(contract_text: str, scope_text: str, logo_path: str = None) -> bytes:
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
    # Prefer reportlab if installed for better UTF-8; fallback to FPDF (kept simple here)
    try:
        # lazy import to avoid requiring reportlab
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        import io
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        y = height - 50
        if os.path.exists(LOGO_PATH):
            try:
                c.drawImage(LOGO_PATH, 40, y - 40, width=120, preserveAspectRatio=True, mask='auto')
                y -= 70
            except Exception:
                pass
        c.setFont("Helvetica", 10)
        for line in contract_text.splitlines():
            c.drawString(40, y, line)
            y -= 14
            if y < 80:
                c.showPage()
                y = height - 50
        c.showPage()
        c.drawString(40, height - 50, "ANNEXURE A: SCOPE OF WORK")
        y = height - 80
        for line in scope_text.splitlines():
            c.drawString(40, y, line)
            y -= 14
            if y < 60:
                c.showPage()
                y = height - 50
        c.save()
        buffer.seek(0)
        return buffer.read()
    except Exception:
        # fallback
        return generate_pdf_fpdf(contract_text, scope_text, LOGO_PATH)

def send_email_with_attachment(smtp_host: str, smtp_port: int, smtp_user: str, smtp_password: str,
                               to_email: str, subject: str, body: str, attachment_bytes: bytes, attachment_name: str):
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

# -------- SIDEBAR ----------
with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=140)
    st.markdown("### Why Freelance Shield")
    st.markdown("- MSME-friendly: includes statutory-interest clause")
    st.markdown("- Anti-ghosting: auto-termination protection")
    st.markdown("- IP lock: you retain rights until payment clears")
    st.markdown("---")

# -------- HERO ----------
hero_col, _ = st.columns([3, 1])
with hero_col:
    st.markdown('<div class="hero-title">Stop chasing payments. Protect your work.</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Generate enforceable freelance contracts in minutes — live preview & single-file app.</div>', unsafe_allow_html=True)
st.markdown("---")

# -------- MAIN: Left form | Right preview ----------
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
            # stop execution so Streamlit re-runs cleanly with updated state
            st.stop()

    elif st.session_state.step == 2:
        st.markdown("#### 🎯 Scope of Work")
        template = st.selectbox("Start with a template (optional)", options=list(st.session_state.scope_templates.keys()))
        scope_default = st.session_state.scope_templates.get(template, "")
        scope_text = st.text_area("Scope (Annexure A)", value=st.session_state.get("scope", scope_default), height=220)
        st.caption("Tip: itemize deliverables and exclusions to avoid disputes.")
        back, nxt = st.columns([1,1])
        if back.button("Back"):
            st.session_state.step = 1
            st.stop()
        if nxt.button("Next: Financials"):
            st.session_state.scope = scope_text
            st.session_state.step = 3
            st.stop()

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
            st.stop()
        if nxt.button("Next: Generate"):
            st.session_state.update({"project_fee": project_fee, "hourly_rate": hourly_rate, "advance_percent": advance_percent})
            st.session_state.step = 4
            st.stop()

    elif st.session_state.step == 4:
        st.markdown("#### ✅ Ready to generate")
        st.write("Review the preview on the right. Generate PDF, email it, or prepare e-sign payload below.")
        back, gen = st.columns([1,1])
        if back.button("Back"):
            st.session_state.step = 3
            st.stop()
        if gen.button("🚀 Generate PDF (creates file in memory)"):
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
    st.text_area("Preview (read-only)", value=preview_text, height=430, key="plain_preview")
    st.markdown("---")

    if st.session_state.get("last_pdf"):
        st.success("✅ PDF in memory")
        col1, col2 = st.columns([1,1])
        with col1:
            st.download_button("📥 Download PDF", st.session_state["last_pdf"], file_name="Freelance_Agreement.pdf", mime="application/pdf", use_container_width=True)
        with col2:
            with st.expander("✉️ Email this PDF to client"):
                st.markdown("Enter SMTP credentials (used only for this send).")
                smtp_host = st.text_input("SMTP Host", value="smtp.gmail.com")
                smtp_port = st.number_input("SMTP Port", value=587)
                smtp_user = st.text_input("SMTP Username (email)", value="")
                smtp_pass = st.text_input("SMTP Password / App Password", type="password")
                to_email = st.text_input("Recipient email", value="client@example.com")
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
    else:
        st.info("Generate a PDF first to enable download, email, and e-sign helpers.")
