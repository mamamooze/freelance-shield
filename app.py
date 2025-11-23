import streamlit as st
from fpdf import FPDF
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import datetime
import os
import time
import io

# --- 1. SETUP & CONFIG ---
icon_path = "logo.png"
page_icon = icon_path if os.path.exists(icon_path) else "🛡️"

st.set_page_config(
    page_title="Freelance Shield Pro",
    page_icon=page_icon,
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 2. CUSTOM CSS ---
st.markdown(
    """
    <style>
        /* BACKGROUND */
        .stApp {
            background-image: linear-gradient(rgba(10, 10, 20, 0.85), rgba(10, 10, 20, 0.90)), 
            url("https://raw.githubusercontent.com/mamamooze/freelance-shield/main/background.png");
            background-size: cover;
            background-attachment: fixed;
        }

        /* HERO TITLE GRADIENT */
        h1 {
            background: -webkit-linear-gradient(45deg, #ffffff, #00d2ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-family: 'Inter', sans-serif;
            font-weight: 900;
            font-size: 3.5rem;
            letter-spacing: -1px;
            text-shadow: 0 2px 10px rgba(0,210,255,0.3);
        }
        h2, h3 { color: #f8f9fa !important; font-family: 'Inter', sans-serif; }
        
        /* TEXT VISIBILITY FIX */
        .stMarkdown p, .stMarkdown li, label {
            color: #e0e0e0 !important;
            font-size: 1.05rem;
            line-height: 1.6;
        }

        /* CARDS (Hover Effect) */
        .stInfo {
            background-color: rgba(30, 41, 59, 0.6);
            border: 1px solid #334155;
            transition: transform 0.2s ease, border-color 0.2s;
        }
        .stInfo:hover {
            transform: translateY(-3px);
            border-color: #00d2ff;
            box-shadow: 0 4px 15px rgba(0, 210, 255, 0.1);
        }

        /* INPUT FIELDS */
        .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
            background-color: #1e293b !important;
            color: #ffffff !important;
            border: 1px solid #475569 !important;
            border-radius: 8px;
        }
        
        /* PREVIEW BOX */
        .stTextArea textarea {
            font-family: 'Courier New', monospace !important;
            background-color: #0f172a !important;
            color: #93c5fd !important; /* Light Blue Text */
            border: 1px solid #3b82f6 !important;
        }

        /* BUTTONS (Neon Glow) */
        .stButton>button {
            background: linear-gradient(90deg, #2563eb, #00d2ff);
            color: white;
            font-weight: bold;
            border: none;
            padding: 0.8rem 1.5rem;
            border-radius: 8px;
            width: 100%;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 4px 15px rgba(0, 210, 255, 0.3);
            transition: all 0.3s;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 210, 255, 0.5);
        }

        /* SIDEBAR */
        [data-testid="stSidebar"] { background-color: #0f172a; border-right: 1px solid #1e293b; }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] p { color: #cbd5e1 !important; }
        
        /* PILL TABS */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: rgba(30, 41, 59, 0.5);
            padding: 10px;
            border-radius: 30px;
            border: 1px solid #334155;
        }
        .stTabs [data-baseweb="tab"] {
            height: auto !important;
            padding: 8px 20px;
            background-color: transparent;
            border-radius: 20px;
            color: #cbd5e1;
            border: none;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            background-color: #3b82f6;
            color: white !important;
            box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3);
        }
        
        /* WARNING BOX */
        .warning-box {
            background-color: rgba(255, 193, 7, 0.15); border-left: 4px solid #ffc107; padding: 10px; margin-bottom: 10px; border-radius: 4px; color: #ffecb3; font-size: 0.9rem;
        }
        
        /* SUCCESS BOX */
        .success-box {
            background-color: rgba(16, 185, 129, 0.15); border-left: 4px solid #10b981; padding: 15px; margin: 15px 0; border-radius: 4px; color: #d1fae5;
        }
        
        /* LEGAL FOOTER */
        .legal-footer {
            font-size: 0.8rem; color: #64748b; text-align: center; margin-top: 50px; padding-top: 20px; border-top: 1px solid #334155;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 3. STATE & LOGIC ---
if 'advance_rate' not in st.session_state: st.session_state.advance_rate = 50
if 'slider_key' not in st.session_state: st.session_state.slider_key = 50
if 'num_key' not in st.session_state: st.session_state.num_key = 50
if 'scope_text' not in st.session_state: st.session_state.scope_text = ""

# --- HELPER FUNCTIONS ---
def clean_text_for_pdf(text):
    """Remove all characters that can't be encoded in latin-1"""
    replacements = {
        '₹': 'Rs. ', '—': '-', '–': '-', '"': '"', '"': '"',
        "‘": "'", "’": "'", '…': '...', '•': '-', '═': '=',
        '\u201c': '"', '\u201d': '"', '\u2018': "'", '\u2019': "'"
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    try:
        text.encode('latin-1')
        return text
    except UnicodeEncodeError:
        return ''.join(char if ord(char) < 256 else '?' for char in text)

def create_professional_pdf(full_text, annexure_text, provider_name, client_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    if os.path.exists("logo.png"):
        try:
            pdf.image("logo.png", 10, 8, 25)
            pdf.ln(25)
        except:
            pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'PROFESSIONAL SERVICE AGREEMENT', 0, 1, 'C')
    pdf.ln(5)
    
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 8, f"Date: {datetime.date.today().strftime('%B %d, %Y')}", 0, 1, 'C')
    pdf.ln(5)
    
    clean_full_text = clean_text_for_pdf(full_text)
    clean_annexure = clean_text_for_pdf(annexure_text)
    clean_provider = clean_text_for_pdf(provider_name)
    clean_client = clean_text_for_pdf(client_name)
    
    lines = clean_full_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line: continue
        if line and len(line) > 2 and line[0].isdigit() and '.' in line[:3]:
            pdf.set_font('Arial', 'B', 12)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(0, 8, line[:80], 0, 1, 'L', 1)
            pdf.ln(2)
        elif 'SIGNED BY' in line or 'SIGNATURE' in line.upper():
            pdf.ln(3)
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 6, line[:150], 0, 1)
        elif line.startswith('===') or line.startswith('---'):
            pdf.ln(2)
        else:
            pdf.set_font('Arial', '', 10)
            if len(line) > 90:
                pdf.multi_cell(0, 5, line)
            else:
                pdf.cell(0, 5, line, 0, 1)
    
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'ANNEXURE A: SCOPE OF WORK', 0, 1, 'L')
    pdf.ln(5)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, clean_annexure)
    
    pdf.ln(10)
    pdf.cell(0, 6, '_________________________________________________________________', 0, 1)
    pdf.ln(5)
    pdf.cell(0, 6, 'Provider Signature: ________________________  Date: __________', 0, 1)
    pdf.cell(0, 6, f'Name: {clean_provider}', 0, 1)
    pdf.ln(5)
    pdf.cell(0, 6, 'Client Signature: ________________________  Date: __________', 0, 1)
    pdf.cell(0, 6, f'Name: {clean_client}', 0, 1)
    
    return pdf.output(dest='S').encode('latin-1', errors='replace')

def create_professional_docx(full_text, annexure_text, provider_name, client_name):
    doc = Document()
    
    title = doc.add_heading('PROFESSIONAL SERVICE AGREEMENT', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title.runs[0]
    title_run.font.size = Pt(18)
    title_run.font.color.rgb = RGBColor(37, 99, 235)
    
    date_para = doc.add_paragraph()
    date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    date_run = date_para.add_run(f"Date: {datetime.date.today().strftime('%B %d, %Y')}")
    date_run.font.size = Pt(11)
    
    doc.add_paragraph()
    
    for line in full_text.split('\n'):
        line = line.strip()
        if not line: continue
        
        if line and line[0].isdigit() and '.' in line[:3]:
            heading = doc.add_heading(line, level=2)
            heading_run = heading.runs[0]
            heading_run.font.size = Pt(13)
            heading_run.font.color.rgb = RGBColor(30, 41, 59)
        elif 'SIGNED BY' in line or 'Signature:' in line or 'Date:' in line:
            sig_para = doc.add_paragraph(line)
            sig_para.runs[0].font.size = Pt(11)
            sig_para.runs[0].bold = True
        else:
            para = doc.add_paragraph(line)
            para.runs[0].font.size = Pt(11)
    
    doc.add_page_break()
    annexure_title = doc.add_heading('ANNEXURE A: SCOPE OF WORK', 1)
    annexure_title.runs[0].font.color.rgb = RGBColor(37, 99, 235)
    
    for line in annexure_text.split('\n'):
        if line.strip():
            para = doc.add_paragraph(line.strip())
            para.runs[0].font.size = Pt(11)
    
    doc.add_paragraph()
    doc.add_paragraph('_' * 60)
    
    sig_section = doc.add_paragraph()
    sig_section.add_run(f'\nProvider Signature: _____________________ Date: __________\n')
    sig_section.add_run(f'Name: {provider_name}\n\n')
    sig_section.add_run(f'Client Signature: _____________________ Date: __________\n')
    sig_section.add_run(f'Name: {client_name}')
    
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- TEMPLATES ---
scope_templates = {
    "Select a template...": "",
    "✍️ Content Writing": """DELIVERABLE: 4 SEO Blog Articles (1000 words each)\n- FORMAT: .docx, Grammarly score >90\n- TOPICS: Approved by Client in advance\n- DELIVERY: 2 articles/week via email\n- REVISIONS: 1 round included per article\n- EXCLUSIONS: No image sourcing, keyword research, or posting""",
    "🎨 Graphic Design": """DELIVERABLE: Logo (PNG/SVG), Business Card (PDF), Banner\n- BRIEF: Colors/Fonts provided by Client\n- REVISIONS: 3 feedback rounds included (within 2 days)\n- DELIVERY: Final files via Google Drive in 7 days\n- EXCLUSIONS: No printing costs or stock image purchase""",
    "🖼️ UI/UX & Web Design": """DELIVERABLE: Wireframe + UI Kit (5 Screens)\n- FORMAT: Figma/Sketch/XD files\n- TIMELINE: Initial draft in 5 days\n- REVISIONS: 2 rounds included\n- EXCLUSIONS: No coding/development included""",
    "💻 Web Development": """DELIVERABLE: 5-Page Responsive Website (WordPress)\n- SPECS: Speed score >80, Contact Form, About Page\n- DELIVERY: Staging link for review, ZIP files after payment\n- REVISIONS: 2 rounds included\n- EXCLUSIONS: Domain/Hosting fees and content writing not included""",
    "📱 App Development": """DELIVERABLE: Android App MVP (5 Core Features)\n- SPECS: Compiles on Android 11+, Source Code included\n- TIMELINE: Weekly sprints, 30-day bug fix warranty\n- EXCLUSIONS: Google Play Store upload fees not included""",
    "🎥 Video Editing": """DELIVERABLE: Edit 2 YouTube Videos (max 8 mins)\n- FORMAT: MP4, 1080p, Color Graded\n- TIMELINE: Draft within 48 hours of receiving raw files\n- REVISIONS: 2 feedback rounds included\n- EXCLUSIONS: No captions, thumbnails, or stock footage""",
    "📱 Social Media Marketing": """DELIVERABLE: 12 Static Posts + 4 Reels (Monthly)\n- FORMAT: PNG (1080px) and MP4 (<60s)\n- SCHEDULE: 3 posts/week, approved by 25th of prev month\n- REVISIONS: 2 rounds per month included\n- EXCLUSIONS: No paid ad management or community replies""",
    "📈 SEO & Digital Marketing": """DELIVERABLE: SEO Audit (20 pages) + Keyword Plan\n- FORMAT: PDF Report, Excel Sheet\n- SPECS: 30 priority keywords, competitor analysis\n- REVISIONS: 1 round included\n- EXCLUSIONS: On-page implementation and backlinks not included""",
    "📧 Virtual Assistance": """DELIVERABLE: Daily Admin Tasks (Email/Calendar)\n- REPORTING: Daily Excel report, Inbox cleared\n- AVAILABILITY: Mon-Fri, 9am-5pm\n- EXCLUSIONS: No calls, travel booking, or personal errands""",
    "📸 Photography": """DELIVERABLE: 50 Product Shots (Edited)\n- FORMAT: High-res JPEGs, 3000px, White Background\n- TIMELINE: Edits delivered in 3 days\n- REVISIONS: 1 re-edit round per batch of 10\n- EXCLUSIONS: No props, prints, or location booking fees""",
    "🗣️ Translation": """DELIVERABLE: Translate 10k words (Eng-Hindi) + 2 Transcripts\n- FORMAT: Word/TXT files\n- ACCURACY: >98% standard\n- REVISIONS: 1 review round included\n- EXCLUSIONS: No subtitling or legal localization""",
    "🎙️ Voice-Over": """DELIVERABLE: 3 Commercial Voice-overs (30s) + 1 Podcast Edit\n- FORMAT: WAV/MP3, Commercial rights included\n- SCRIPT: Supplied by Client\n- REVISIONS: 1 correction round included\n- EXCLUSIONS: No music production or mixing"""
}

def update_scope():
    if st.session_state.template_selector != "Select a template...":
        st.session_state.scope_text = scope_templates[st.session_state.template_selector]

def update_from_slider(): st.session_state.num_key = st.session_state.slider_key
def update_from_num(): st.session_state.slider_key = st.session_state.num_key

def get_smart_clauses(category, rate):
    clauses = {
        "acceptance": f"Client review within 5 days. Silence = Acceptance. 2 revisions included. Extra changes billed at {rate}/hr.",
        "warranty": "Provided 'as-is'. No post-delivery support unless specified in Annexure A.",
        "ip_rights": "Client owns IP only AFTER full payment. Use before payment is Copyright Infringement.",
        "cancellation": "Cancellation after work starts incurs forfeiture of the Advance Payment.",
        "termination": "Provider may terminate with 7 days written notice if Client breaches payment terms. Client owes payment for work completed till termination date."
    }
    if category in ["💻 Web Development", "📱 App Development"]:
        clauses["warranty"] = f"BUG FIX WARRANTY: Provider agrees to fix critical bugs reported within 30 days. Feature changes billed at {rate}/hr."
        clauses["ip_rights"] = "CODE OWNERSHIP: Client receives full source code rights upon payment. Provider retains rights to generic libraries."
    elif category in ["🎨 Graphic Design", "🎥 Video Editing", "🖼️ UI/UX & Web Design", "📸 Photography"]:
        clauses["acceptance"] = "CREATIVE APPROVAL: Rejections based on 'personal taste' after initial style approval will be billed as a new Change Order."
        clauses["ip_rights"] = "SOURCE FILES: Final deliverables transfer upon payment. Raw source files remain property of Provider unless purchased."
    elif category in ["📱 Social Media Marketing", "📈 SEO & Digital Marketing"]:
        clauses["warranty"] = "NO ROI GUARANTEE: Provider does NOT guarantee specific results (Likes, Sales, Rankings)."
        clauses["acceptance"] = "APPROVAL WINDOW: Content must be approved 24 hours prior to publishing deadlines."
    elif category in ["✍️ Content Writing", "🗣️ Translation"]:
        clauses["warranty"] = "ORIGINALITY WARRANTY: Provider warrants that work is original."
        clauses["acceptance"] = "EDITORIAL REVIEW: Client has 3 days for factual corrections."
    elif category == "🎙️ Voice-Over":
        clauses["acceptance"] = "CORRECTION POLICY: Includes 1 round for pronunciation errors. Script changes require a new fee."
        clauses["cancellation"] = "KILL FEE: 50% fee if cancelled after start. 100% fee if cancelled after recording."
    elif category == "🗣️ Translation":
        clauses["warranty"] = "ACCURACY WARRANTY: Provider guarantees >98% accuracy. Errors discovered within 7 days will be fixed free."
        clauses["cancellation"] = "KILL FEE: Cancellation after start incurs 50% fee. Cancellation after draft delivery incurs 100% fee."
    return clauses

# --- 4. SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", width=120)
    
    st.markdown("### 🎯 Founder’s Mission")
    st.write("**Hi, I'm a Law Student working to empower Indian freelancers.**")
    st.write("Every year, thousands of independent professionals lose income to late payments, scope creep, and unfair contracts.")
    st.write("**I built this platform so every freelancer—designer, developer, writer—can generate a legally binding, MSME-protected contract in seconds.**")
    
    st.markdown("- 🚀 No more chasing payments")
    st.markdown("- 🛡️ No more ignored clauses")
    st.markdown("- 🏛️ Legal terms trusted by MSMEs")
    
    st.caption("**You deserve to get paid on time, every time.**")
    
    st.markdown("---")
    st.markdown("### 🆘 Need Custom Help?")
    st.write("Complex project? Don't risk it.")
    st.link_button("Hire Me for Review (₹499)", "https://wa.me/YOUR_NUMBER_HERE")
    
    st.markdown("---")
    with st.expander("⚖️ Terms & Privacy Policy"):
        st.markdown("""
        **1. TERMS OF USE**
        - **No Legal Advice:** This tool provides automated templates for informational purposes. It does not constitute an attorney-client relationship.
        - **Prohibited Use:** You may not use this site for unlawful, fraudulent, or commercial scraping purposes.
        - **Limitation of Liability:** We are not liable for disputes arising from the use of these contracts. Consult a qualified lawyer for high-value projects.
        - **Jurisdiction:** Disputes regarding this website are subject to the courts of **Bengaluru, India**.

        **2. PRIVACY POLICY**
        - **Stateless Architecture:** We operate on a "Privacy by Design" model. We **do not store, save, or log** any personal data (names, fees, scope) you enter.
        - **No Database:** All generation happens instantly in your active browser session. Once you close the tab, your data is permanently wiped.
        - **No Third Parties:** We do not sell or trade user data because we do not collect it.
        """)

# --- 5. MAIN UI ---
c1, c2 = st.columns([2, 1])
with c1:
    st.markdown("# Stop Chasing Payments.")
    st.markdown('<p class="sub-hero">Generate watertight, MSME-protected contracts for Indian Freelancers in 30 seconds.</p>', unsafe_allow_html=True)
    
    if 'has_greeted' not in st.session_state:
        hour = datetime.datetime.now().hour
        greeting = "Good Morning" if 5 <= hour < 12 else "Good Afternoon" if 12 <= hour < 18 else "Good Evening"
        st.toast(f"👋 {greeting}, Freelancer! Let's get you protected.")
        st.session_state.has_greeted = True

    st.markdown("""
    <div style="display: flex; gap: 15px; margin-bottom: 20px;">
        <span style="background: #1e293b; padding: 5px 10px; border-radius: 5px; color: #94a3b8; font-size: 0.9rem;">🏛️ MSME Protected</span>
        <span style="background: #1e293b; padding: 5px 10px; border-radius: 5px; color: #94a3b8; font-size: 0.9rem;">👻 Anti-Ghosting</span>
        <span style="background: #1e293b; padding: 5px 10px; border-radius: 5px; color: #94a3b8; font-size: 0.9rem;">🔒 IP Lock</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["👤 The Parties", "🎯 The Work (Scope)", "💰 The Money"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        freelancer_name = st.text_input("Provider Name (You)", "Amit Kumar", help="Name on your Bank Account")
        cities = ["Bengaluru, Karnataka", "New Delhi, Delhi", "Mumbai, Maharashtra", "Chennai, Tamil Nadu", "Hyderabad, Telangana", "Pune, Maharashtra", "Kolkata, West Bengal", "Other (Type Manually)"]
        selected_city = st.selectbox("Your City (Jurisdiction)", cities, help="Where do you want to fight if they don't pay?")
        jurisdiction_city = st.text_input("Type City", "Mysuru") if selected_city == "Other (Type Manually)" else selected_city
    with c2:
        client_name = st.text_input("Client Name", "Tech Solutions Pvt Ltd", help="Company Name or Individual Name")
        gst_registered = st.checkbox("I am GST Registered", help="Check if you have a GSTIN")

with tab2:
    st.markdown('<div class="warning-box">⚠️ <b>NOTE:</b> Selecting a category adjusts the <b>Legal Clauses</b> (IP Rights, Warranty) to match your industry risks.</div>', unsafe_allow_html=True)
    template_choice = st.selectbox("✨ Select Industry (Smart Clauses):", list(scope_templates.keys()), key="template_selector", on_change=update_scope, help="This changes the contract text automatically.")
    scope_work = st.text_area("Scope of Work (Annexure A)", key="scope_text", height=200, help="Be specific. Vague contracts lead to unpaid work.")

with tab3:
    c1, c2, c3 = st.columns(3)
    with c1: project_fee_num = st.number_input("Total Project Fee (INR)", value=50000, step=1000, help="Total contract value")
    with c2: hourly_rate_num = st.number_input("Overtime Rate (INR/hr)", value=2000, step=500, help="Rate for Scope Creep")
    with c3:
        st.write("Advance Required (%)")
        sc1, sc2 = st.columns([3, 1])
        with sc1: st.slider("Slider", 0, 100, key="slider_key", on_change=update_from_slider, label_visibility="collapsed")
        with sc2: st.number_input("Num", 0, 100, key="num_key", on_change=update_from_num, label_visibility="collapsed")
        advance_percent = st.session_state.slider_key
    st.info(f"ℹ️ **Calculation:** You will receive **Rs. {int(project_fee_num * (advance_percent/100)):,}** before starting work.")

st.markdown("---")

# --- CONSENT ---
check_terms = st.checkbox("I agree to the Terms of Use & Privacy Policy. I understand this is a tool, not legal advice.")

c_main = st.columns([1, 2, 1])
with c_main[1]: 
    if check_terms:
        generate_btn = st.button("🚀 Generate Legal Contract Now", type="primary")
    else:
        st.button("🚀 Generate Legal Contract Now", disabled=True, help="Please accept the Terms to proceed.")
        generate_btn = False

if generate_btn:
    if template_choice == "Select a template..." or template_choice == "":
        st.error("⚠️ Please select an Industry Template.")
        st.stop()
    
    if not st.session_state.scope_text.strip():
        st.error("⚠️ Scope of Work is empty!")
        st.stop()

    with st.spinner("Drafting your watertight contract..."):
        time.sleep(1.5)
    
    # CRITICAL FIX: CALCULATE VARIABLES INSIDE GENERATION BLOCK
    advance_amount = int(project_fee_num * (advance_percent/100))
    balance_amount = project_fee_num - advance_amount
    
    safe_cost = f"Rs. {project_fee_num:,}"
    safe_rate = f"Rs. {hourly_rate_num:,}"
    safe_scope = st.session_state.scope_text.replace("₹", "Rs. ")
    gst_clause = "(Exclusive of GST)" if gst_registered else ""
    smart = get_smart_clauses(template_choice, safe_rate)
    cancel_clause = smart.get("cancellation", "Cancellation after work starts incurs a forfeiture of the Advance Payment.")
    
    full_text = f"""PROFESSIONAL SERVICE AGREEMENT

Date: {datetime.date.today().strftime('%B %d, %Y')}

BETWEEN: {freelancer_name} ("Provider")
AND: {client_name} ("Client")

===============================================================

1. PAYMENT TERMS (MSME ACT COMPLIANCE)

Total Fee: {safe_cost} {gst_clause}
Advance: {advance_percent}% (Rs. {advance_amount:,})
Balance: Rs. {balance_amount:,}

Late payments attract compound interest at 3x the Bank Rate (Section 16, MSMED Act, 2006).

===============================================================

2. ACCEPTANCE & REVISIONS

{smart['acceptance']}

===============================================================

3. IP RIGHTS

{smart['ip_rights']}

===============================================================

4. WARRANTY

{smart['warranty']}

===============================================================

5. CONFIDENTIALITY

Strict confidentiality for 2 years post-termination.

===============================================================

6. ANTI-GHOSTING CLAUSE

Provider responds within 1 business day. Client silence >14 days = Termination.

===============================================================

7. CANCELLATION

{smart['cancellation']}

===============================================================

8. TERMINATION BY PROVIDER

{smart['termination']}

===============================================================

9. FORCE MAJEURE

Not liable for acts of God or internet failure.

===============================================================

10. LIMITATION OF LIABILITY

Liability limited to Total Fee paid.

===============================================================

11. JURISDICTION

Disputes subject to Arbitration in {jurisdiction_city}, India under Arbitration Act, 1996.

===============================================================

12. GST COMPLIANCE

Client bears GST liability.

===============================================================

13. STAMP DUTY

Client responsible for stamp duty as per Indian Stamp Act, 1899.

===============================================================

SIGNATURES

PROVIDER:
Signature: _____________________
Name: {freelancer_name}
Date: _____________________

CLIENT:
Signature: _____________________
Name: {client_name}
Date: _____________________
"""
    
    try:
        pdf_data = create_professional_pdf(full_text, safe_scope, freelancer_name, client_name)
        docx_data = create_professional_docx(full_text, safe_scope, freelancer_name, client_name)
        
        st.success("✅ Contract Generated Successfully!")
        
        st.markdown("""
        <div class="success-box">
            <b>📥 Next Steps:</b><br/>
            1. Download PDF for signing<br/>
            2. Send to client<br/>
            3. DO NOT START WORK until advance is received!
        </div>
        """, unsafe_allow_html=True)
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button("📄 Download as PDF", data=pdf_data, file_name="Contract.pdf", mime="application/pdf", use_container_width=True)
        with col_d2:
            st.download_button("📝 Download as Word (Editable)", data=docx_data, file_name="Contract.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
            
        with st.expander("👀 Preview Contract"):
            st.text_area("", value=full_text + "\n\n" + "="*60 + "\nANNEXURE A\n" + "="*60 + "\n\n" + safe_scope, height=300)
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

st.markdown("---")
st.markdown("""
<div class="legal-footer">
    <p><b>© 2025 Freelance Shield Pro.</b> All rights reserved.</p>
    <p><b>Disclaimer:</b> This tool provides templates for informational purposes only.</p>
</div>
""", unsafe_allow_html=True)