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

# --- 2. CUSTOM CSS (HIGH CONTRAST & VISUAL POP) ---
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
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 3. STATE & LOGIC ---
if 'advance_rate' not in st.session_state: st.session_state.advance_rate = 50
if 'slider_key' not in st.session_state: st.session_state.slider_key = 50
if 'num_key' not in st.session_state: st.session_state.num_key = 50
if 'scope_text' not in st.session_state: st.session_state.scope_text = ""

# --- DOCX GENERATOR FUNCTION ---
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

# --- FULL TEMPLATE LIBRARY (12 CATEGORIES) ---
scope_templates = {
    "Select a template...": "",
    
    "Content Writing": """DELIVERABLE: 4 SEO Blog Articles (1000 words each)
- FORMAT: .docx, Grammarly score >90
- TOPICS: Approved by Client in advance
- DELIVERY: 2 articles/week via email
- REVISIONS: 1 round included per article
- EXCLUSIONS: No image sourcing, keyword research, or posting""",

    "Graphic Design": """DELIVERABLE: Logo (PNG/SVG), Business Card (PDF), Banner
- BRIEF: Colors/Fonts provided by Client
- REVISIONS: 3 feedback rounds included (within 2 days)
- DELIVERY: Final files via Google Drive in 7 days
- EXCLUSIONS: No printing costs or stock image purchase""",

    "UI/UX & Web Design": """DELIVERABLE: Wireframe + UI Kit (5 Screens)
- FORMAT: Figma/Sketch/XD files
- TIMELINE: Initial draft in 5 days
- REVISIONS: 2 rounds included
- EXCLUSIONS: No coding/development included""",

    "Web Development": """DELIVERABLE: 5-Page Responsive Website (WordPress)
- SPECS: Speed score >80, Contact Form, About Page
- DELIVERY: Staging link for review, ZIP files after payment
- REVISIONS: 2 rounds included
- EXCLUSIONS: Domain/Hosting fees and content writing not included""",

    "App Development": """DELIVERABLE: Android App MVP (5 Core Features)
- SPECS: Compiles on Android 11+, Source Code included
- TIMELINE: Weekly sprints, 30-day bug fix warranty
- EXCLUSIONS: Google Play Store upload fees not included""",

    "Video Editing": """DELIVERABLE: Edit 2 YouTube Videos (max 8 mins)
- FORMAT: MP4, 1080p, Color Graded
- TIMELINE: Draft within 48 hours of receiving raw files
- REVISIONS: 2 feedback rounds included
- EXCLUSIONS: No captions, thumbnails, or stock footage""",

    "Social Media Marketing": """DELIVERABLE: 12 Static Posts + 4 Reels (Monthly)
- FORMAT: PNG (1080px) and MP4 (<60s)
- SCHEDULE: 3 posts/week, approved by 25th of prev month
- REVISIONS: 2 rounds per month included
- EXCLUSIONS: No paid ad management or community replies""",

    "SEO & Digital Marketing": """DELIVERABLE: SEO Audit (20 pages) + Keyword Plan
- FORMAT: PDF Report, Excel Sheet
- SPECS: 30 priority keywords, competitor analysis
- REVISIONS: 1 round included
- EXCLUSIONS: On-page implementation and backlinks not included""",

    "Virtual Assistance": """DELIVERABLE: Daily Admin Tasks (Email/Calendar)
- REPORTING: Daily Excel report, Inbox cleared
- AVAILABILITY: Mon-Fri, 9am-5pm
- EXCLUSIONS: No calls, travel booking, or personal errands""",

    "Photography": """DELIVERABLE: 50 Product Shots (Edited)
- FORMAT: High-res JPEGs, 3000px, White Background
- TIMELINE: Edits delivered in 3 days
- REVISIONS: 1 re-edit round per batch of 10
- EXCLUSIONS: No props, prints, or location booking fees""",

    "Translation": """DELIVERABLE: Translate 10k words (Eng-Hindi) + 2 Transcripts
- FORMAT: Word/TXT files
- ACCURACY: >98% standard
- REVISIONS: 1 review round included
- EXCLUSIONS: No subtitling or legal localization""",

    "Voice-Over": """DELIVERABLE: 3 Commercial Voice-overs (30s) + 1 Podcast Edit
- FORMAT: WAV/MP3, Commercial rights included
- SCRIPT: Supplied by Client
- REVISIONS: 1 correction round included
- EXCLUSIONS: No music production or mixing"""
}

def update_scope():
    if st.session_state.template_selector != "Select a template...":
        st.session_state.scope_text = scope_templates[st.session_state.template_selector]

def update_from_slider(): st.session_state.num_key = st.session_state.slider_key
def update_from_num(): st.session_state.slider_key = st.session_state.num_key

# --- SMART LEGAL LOGIC ---
def get_smart_clauses(category, rate):
    # Base Clauses
    clauses = {
        "acceptance": f"Client review within 5 days. Silence = Acceptance. 2 revisions included. Extra changes billed at {rate}/hr.",
        "warranty": "Provided 'as-is'. No post-delivery support unless specified in Annexure A.",
        "ip_rights": "Client owns IP only AFTER full payment. Use before payment is Copyright Infringement.",
        "cancellation": "Cancellation after work starts incurs a forfeiture of the Advance Payment."
    }

    # Category Overrides
    if category in ["Web Development", "App Development"]:
        clauses["warranty"] = f"BUG FIX WARRANTY: Provider agrees to fix critical bugs reported within 30 days. Feature changes billed at {rate}/hr."
        clauses["ip_rights"] = "CODE OWNERSHIP: Client receives full source code rights upon payment. Provider retains rights to generic libraries."
    
    elif category in ["Graphic Design", "Video Editing", "UI/UX & Web Design", "Photography"]:
        clauses["acceptance"] = "CREATIVE APPROVAL: Rejections based on 'personal taste' after initial style approval will be billed as a new Change Order."
        clauses["ip_rights"] = "SOURCE FILES: Final deliverables transfer upon payment. Raw source files (PSD/PrProj) remain property of Provider unless purchased."

    elif category in ["Social Media Marketing", "SEO & Digital Marketing"]:
        clauses["warranty"] = "NO ROI GUARANTEE: Provider does NOT guarantee specific results (Likes, Sales, Rankings) as platform algorithms are external."
        clauses["acceptance"] = "APPROVAL WINDOW: Content must be approved 24 hours prior to publishing deadlines."

    elif category in ["Content Writing", "Translation"]:
        clauses["warranty"] = "ORIGINALITY WARRANTY: Provider warrants that work is original and passes standard plagiarism checks."
        clauses["acceptance"] = "EDITORIAL REVIEW: Client has 3 days for factual corrections. Stylistic rewrites count as a revision."

    elif category == "Voice-Over":
        clauses["acceptance"] = "CORRECTION POLICY: Includes 1 round for pronunciation/pacing errors. Script changes require a new fee."
        clauses["cancellation"] = "KILL FEE: 50% fee if cancelled after start. 100% fee if cancelled after recording session."
        
    elif category == "Translation":
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

# --- 5. MAIN UI ---
c1, c2 = st.columns([2, 1])
with c1:
    st.markdown("# Stop Chasing Payments.")
    st.markdown('<p class="sub-hero">Generate watertight, MSME-protected contracts for Indian Freelancers in 30 seconds.</p>', unsafe_allow_html=True)
    
    hour = datetime.datetime.now().hour
    greeting = "Good Morning" if 5 <= hour < 12 else "Good Afternoon" if 12 <= hour < 18 else "Good Evening"
    st.toast(f"👋 {greeting}, Freelancer! Let's get you protected.")

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
        freelancer_name = st.text_input("Provider Name (You)", "Amit Kumar")
        cities = ["Bengaluru, Karnataka", "New Delhi, Delhi", "Mumbai, Maharashtra", "Chennai, Tamil Nadu", "Hyderabad, Telangana", "Pune, Maharashtra", "Kolkata, West Bengal", "Gurugram, Haryana", "Noida, Uttar Pradesh", "Other (Type Manually)"]
        selected_city = st.selectbox("Your City (Jurisdiction)", cities)
        jurisdiction_city = st.text_input("Type City", "Mysuru") if selected_city == "Other (Type Manually)" else selected_city
    with c2:
        client_name = st.text_input("Client Name", "Tech Solutions Pvt Ltd")
        gst_registered = st.checkbox("I am GST Registered")

with tab2:
    st.markdown('<div class="warning-box">⚠️ <b>NOTE:</b> Selecting a category adjusts the <b>Legal Clauses</b> (IP Rights, Warranty) to match your industry risks.</div>', unsafe_allow_html=True)
    template_choice = st.selectbox("✨ Select Industry (Smart Clauses):", list(scope_templates.keys()), key="template_selector", on_change=update_scope)
    scope_work = st.text_area("Scope of Work (Annexure A)", key="scope_text", height=200, help="Be specific!")

with tab3:
    c1, c2, c3 = st.columns(3)
    with c1: project_fee_num = st.number_input("Total Project Fee (INR)", value=50000, step=1000)
    with c2: hourly_rate_num = st.number_input("Overtime Rate (INR/hr)", value=2000, step=500)
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
    # UX: Progress Bar
    progress_text = "Drafting legal clauses..."
    my_bar = st.progress(0, text=progress_text)
    for percent_complete in range(100):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1, text=progress_text)
    time.sleep(0.5)
    my_bar.empty()

    # LOGIC
    safe_cost = f"Rs. {project_fee_num:,}"
    safe_rate = f"Rs. {hourly_rate_num:,}"
    safe_scope = st.session_state.scope_text.replace("₹", "Rs. ")
    gst_clause = "(Exclusive of GST)" if gst_registered else ""
    smart = get_smart_clauses(template_choice, safe_rate)
    cancel_clause = smart.get("cancellation", "Cancellation after work starts incurs a forfeiture of the Advance Payment.")

    # TEXT CONSTRUCTION
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

    # PDF GENERATION
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

    # WORD GENERATION
    docx_data = create_docx(full_text, safe_scope)

   # UI OUTPUT (Corrected Ending)
    st.balloons()
    st.success("✅ Contract Ready! Choose your format below.")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button(
            label="📄 Download as PDF",
            data=pdf_data,
            file_name="Contract.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    with col_d2:
        st.download_button(
            label="📝 Download as Word (Editable)",
            data=docx_data,
            file_name="Contract.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
        
    with st.expander("👀 View Preview"):
        st.text_area("Contract Text:", value=full_text + "\n\n" + safe_scope, height=300)