import streamlit as st
from fpdf import FPDF
from docx import Document
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

# --- 2. CUSTOM CSS (ACCESSIBILITY & UX UPGRADE) ---
st.markdown(
    """
    <style>
        /* BACKGROUND */
        .stApp {
            background-image: linear-gradient(rgba(15, 23, 42, 0.95), rgba(15, 23, 42, 0.95)), 
            url("https://raw.githubusercontent.com/mamamooze/freelance-shield/main/background.png");
            background-size: cover;
            background-attachment: fixed;
        }

        /* ACCESSIBILITY: TYPOGRAPHY */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            font-size: 18px; /* Larger font for readability */
        }
        
        h1 {
            background: -webkit-linear-gradient(45deg, #ffffff, #0ea5e9); /* High contrast Blue */
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 900;
            font-size: 3.5rem;
            letter-spacing: -1px;
            padding-bottom: 10px;
        }
        h2, h3 { color: #f8fafc !important; font-weight: 700; }
        
        /* TEXT CONTRAST FIX */
        .stMarkdown p, .stMarkdown li, label, .stCaption {
            color: #e2e8f0 !important; /* High contrast grey-white */
            line-height: 1.6;
        }

        /* MICRO-INTERACTIONS: CARDS */
        .stInfo {
            background-color: rgba(30, 41, 59, 0.8);
            border: 1px solid #475569;
            border-radius: 12px;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        }
        .stInfo:hover {
            transform: translateY(-5px) scale(1.01);
            border-color: #0ea5e9;
            box-shadow: 0 10px 25px rgba(14, 165, 233, 0.25);
        }

        /* MOBILE FRIENDLY INPUTS (Large Touch Targets) */
        .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
            background-color: #1e293b !important;
            color: #ffffff !important;
            border: 1px solid #64748b !important;
            border-radius: 8px;
            min-height: 45px; /* Tappable on mobile */
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #0ea5e9 !important;
            box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.3) !important;
        }

        /* BUTTONS (Interactive & Accessible) */
        .stButton>button {
            background: linear-gradient(90deg, #0284c7, #0ea5e9); /* Solid Blue Gradient */
            color: white;
            font-weight: 800;
            border: none;
            padding: 1rem 2rem;
            border-radius: 10px;
            width: 100%;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: all 0.2s ease;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px rgba(14, 165, 233, 0.4);
            background: linear-gradient(90deg, #0369a1, #0284c7);
        }
        .stButton>button:active {
            transform: scale(0.98);
        }

        /* SIDEBAR VISIBILITY */
        [data-testid="stSidebar"] { background-color: #0f172a; border-right: 1px solid #334155; }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] p { color: #f1f5f9 !important; }
        
        /* PROGRESS STEPPER VISUAL */
        .step-container {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
            background: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 50px;
        }
        .step {
            color: #94a3b8;
            font-weight: bold;
            font-size: 0.9rem;
        }
        .step.active {
            color: #38bdf8; /* Cyan for active */
            text-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
        }
        
        /* WARNING BOX */
        .warning-box {
            background-color: rgba(234, 179, 8, 0.1); 
            border-left: 4px solid #eab308; 
            padding: 15px; 
            margin-bottom: 15px; 
            border-radius: 4px; 
            color: #fde047; 
            font-weight: 500;
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

# --- DOCX GENERATOR ---
def create_docx(full_text, annexure_text):
    doc = Document()
    doc.add_heading('PROFESSIONAL SERVICE AGREEMENT', 0)
    doc.add_paragraph(full_text)
    doc.add_page_break()
    doc.add_heading('ANNEXURE A: SCOPE OF WORK', 1)
    doc.add_paragraph(annexure_text)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- FULL TEMPLATE LIBRARY (WITH ICONS) ---
scope_templates = {
    "Select a template...": "",
    "✍️ Content Writing": """DELIVERABLE: 4 SEO Blog Articles (1000 words each)\n- FORMAT: .docx, Grammarly score >90\n- TOPICS: Approved by Client\n- DELIVERY: 2 articles/week\n- REVISIONS: 1 round included\n- EXCLUSIONS: No image sourcing.""",
    "🎨 Graphic Design": """DELIVERABLE: Logo (PNG/SVG), Business Card (PDF)\n- BRIEF: Colors provided by Client\n- REVISIONS: 3 rounds included\n- DELIVERY: 7 days\n- EXCLUSIONS: No printing costs.""",
    "🖼️ UI/UX & Web Design": """DELIVERABLE: Wireframe + UI Kit (5 Screens)\n- FORMAT: Figma/Sketch\n- TIMELINE: 5 days draft\n- REVISIONS: 2 rounds\n- EXCLUSIONS: No coding.""",
    "💻 Web Development": """DELIVERABLE: 5-Page WordPress Site\n- SPECS: Speed score >80\n- DELIVERY: Staging link review\n- REVISIONS: 2 rounds\n- EXCLUSIONS: Domain/Hosting fees.""",
    "📱 App Development": """DELIVERABLE: Android App MVP\n- SPECS: Compiles Android 11+\n- TIMELINE: Weekly sprints\n- EXCLUSIONS: Play Store fees.""",
    "🎥 Video Editing": """DELIVERABLE: Edit 2 YouTube Videos (8 mins)\n- FORMAT: MP4, 1080p\n- TIMELINE: 48hr draft\n- REVISIONS: 2 rounds\n- EXCLUSIONS: No stock footage.""",
    "📱 Social Media Marketing": """DELIVERABLE: 12 Posts + 4 Reels\n- FORMAT: PNG/MP4\n- SCHEDULE: 3 posts/week\n- REVISIONS: 2 rounds\n- EXCLUSIONS: No paid ads.""",
    "📈 SEO & Digital Marketing": """DELIVERABLE: SEO Audit (20 pages)\n- FORMAT: PDF Report\n- SPECS: 30 keywords\n- REVISIONS: 1 round\n- EXCLUSIONS: No backlinks.""",
    "📧 Virtual Assistance": """DELIVERABLE: Daily Admin Tasks\n- REPORTING: Daily Excel\n- AVAILABILITY: Mon-Fri 9-5\n- EXCLUSIONS: No personal errands.""",
    "📸 Photography": """DELIVERABLE: 50 Product Shots\n- FORMAT: High-res JPEG\n- TIMELINE: 3 days\n- REVISIONS: 1 round\n- EXCLUSIONS: No prop fees.""",
    "🗣️ Translation": """DELIVERABLE: Translate 10k words\n- FORMAT: Word/TXT\n- ACCURACY: >98%\n- REVISIONS: 1 round\n- EXCLUSIONS: No legal localization.""",
    "🎙️ Voice-Over": """DELIVERABLE: 3 Commercial Scripts\n- FORMAT: WAV/MP3\n- REVISIONS: 1 correction round\n- EXCLUSIONS: No music mixing."""
}

def update_scope():
    if st.session_state.template_selector != "Select a template...":
        st.session_state.scope_text = scope_templates[st.session_state.template_selector]

def update_from_slider(): st.session_state.num_key = st.session_state.slider_key
def update_from_num(): st.session_state.slider_key = st.session_state.num_key

# --- SMART LEGAL LOGIC (UPDATED WITH ICONS) ---
def get_smart_clauses(category, rate):
    clauses = {
        "acceptance": f"Client review within 5 days. Silence = Acceptance. 2 revisions included. Extra changes billed at {rate}/hr.",
        "warranty": "Provided 'as-is'. No post-delivery support unless specified in Annexure A.",
        "ip_rights": "Client owns IP only AFTER full payment. Use before payment is Copyright Infringement.",
        "cancellation": "Cancellation after work starts incurs a forfeiture of the Advance Payment."
    }

    if category in ["💻 Web Development", "📱 App Development"]:
        clauses["warranty"] = f"BUG FIX WARRANTY: Provider agrees to fix critical bugs reported within 30 days. Feature changes billed at {rate}/hr."
        clauses["ip_rights"] = "CODE OWNERSHIP: Client receives full source code rights upon payment. Provider retains rights to generic libraries."
    elif category in ["🎨 Graphic Design", "🎥 Video Editing", "🖼️ UI/UX & Web Design", "📸 Photography"]:
        clauses["acceptance"] = "CREATIVE APPROVAL: Rejections based on 'personal taste' after initial approval billed as Change Order."
        clauses["ip_rights"] = "SOURCE FILES: Final deliverables transfer upon payment. Raw source files remain property of Provider unless purchased."
    elif category in ["📱 Social Media Marketing", "📈 SEO & Digital Marketing"]:
        clauses["warranty"] = "NO ROI GUARANTEE: Provider does NOT guarantee specific results (Likes, Sales) as platform algorithms are external."
        clauses["acceptance"] = "APPROVAL WINDOW: Content must be approved 24 hours prior to publishing."
    elif category in ["✍️ Content Writing", "🗣️ Translation"]:
        clauses["warranty"] = "ORIGINALITY WARRANTY: Provider warrants work is original and passes plagiarism checks."
        clauses["acceptance"] = "EDITORIAL REVIEW: Client has 3 days for corrections. Stylistic rewrites count as revision."
    elif category == "🎙️ Voice-Over":
        clauses["acceptance"] = "CORRECTION POLICY: Includes 1 round for pronunciation errors. Script changes require new fee."
        clauses["cancellation"] = "KILL FEE: 50% fee if cancelled after start. 100% fee after recording."
    elif category == "🗣️ Translation":
        clauses["warranty"] = "ACCURACY WARRANTY: >98% accuracy guaranteed."
        clauses["cancellation"] = "KILL FEE: 50% fee if cancelled after start. 100% fee after delivery."

    return clauses

# --- 4. SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", width=120)
    
    st.markdown("### 🎯 Founder’s Mission")
    st.info("**Hi, I'm a Law Student.**\nI built this tool to help Indian freelancers get paid on time, every time.")
    
    st.markdown("---")
    st.markdown("### 🆘 Need Custom Help?")
    st.write("Complex project? Don't risk it.")
    st.link_button("Hire Me for Review (₹499)", "https://wa.me/YOUR_NUMBER_HERE")

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

st.markdown("---")

# VISUAL PROGRESS TRACKER
st.markdown("""
<div class="step-container">
    <span class="step active">1. THE PARTIES</span>
    <span class="step active">2. THE WORK</span>
    <span class="step active">3. THE MONEY</span>
    <span class="step">4. GENERATE</span>
</div>
""", unsafe_allow_html=True)

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
c_main = st.columns([1, 2, 1])
with c_main[1]: generate_btn = st.button("🚀 Generate Legal Contract Now", type="primary")

# --- 6. GENERATION & EXPORT ---
if generate_btn:
    with st.spinner("Drafting your watertight contract..."):
        time.sleep(1.5)
    
    safe_cost = f"Rs. {project_fee_num:,}"
    safe_rate = f"Rs. {hourly_rate_num:,}"
    safe_scope = st.session_state.scope_text.replace("₹", "Rs. ")
    gst_clause = "(Exclusive of GST)" if gst_registered else ""
    smart = get_smart_clauses(template_choice, safe_rate)
    cancel_clause = smart.get("cancellation", "Cancellation after work starts incurs a forfeiture of the Advance Payment.")

    full_text = f"""
    PROFESSIONAL SERVICE AGREEMENT
    Date: {datetime.date.today().strftime('%B %d, %Y')}
    BETWEEN: {freelancer_name} (Provider) AND {client_name} (Client)
    
    1. PAYMENT & INTEREST (MSME ACT)
    Total Fee: {safe_cost} {gst_clause}. Advance: {advance_percent}%.
    Late payments attract compound interest at 3x the Bank Rate (Section 16, MSMED Act, 2006).
    
    2. ACCEPTANCE & REVISIONS
    {smart['acceptance']}
    
    3. CONFIDENTIALITY (NDA)
    Strict confidentiality for 2 years post-termination.
    
    4. IP RIGHTS (IP LOCK)
    {smart['ip_rights']}
    
    5. WARRANTY & SUPPORT
    {smart['warranty']}
    
    6. COMMUNICATION POLICY
    Provider responds within 1 business day. Client silence >14 days = Termination (Ghosting).
    
    7. FORCE MAJEURE
    Not liable for acts of God or internet failure.
    
    8. LIMITATION OF LIABILITY
    Liability limited to Total Fee paid. No indirect damages.
    
    9. CANCELLATION / KILL FEE
    {cancel_clause}
    
    10. JURISDICTION
    Disputes subject to Arbitration in {jurisdiction_city}, India.
    
    11. GST COMPLIANCE
    Client bears GST liability.
    
    ---------------------------------------------------
    SIGNED BY PROVIDER: {freelancer_name}
    SIGNED BY CLIENT: {client_name}
    """

    # PDF
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("logo.png"):
        try: pdf.image("logo.png", 10, 8, 25); pdf.ln(20)
        except: pass
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 5, full_text.encode('latin-1', 'replace').decode('latin-1'))
    pdf.add_page()
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(0, 10, "ANNEXURE A: SCOPE OF WORK", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 5, safe_scope.encode('latin-1', 'replace').decode('latin-1'))
    pdf_data = pdf.output(dest='S').encode('latin-1')

    # WORD
    docx_data = create_docx(full_text, safe_scope)

    # UI OUTPUT
    st.success("✅ Contract Generated Successfully! Choose your format below.")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button("📄 Download as PDF", data=pdf_data, file_name="Contract.pdf", mime="application/pdf", use_container_width=True)
    with col_d2:
        st.download_button("📝 Download as Word (Editable)", data=docx_data, file_name="Contract.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
        
    with st.expander("👀 View Preview"):
        st.text_area("", value=full_text + "\n\n" + safe_scope, height=300)