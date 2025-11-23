import streamlit as st
from fpdf import FPDF
import datetime
import os
import time

# --- 1. SETUP & CONFIG ---
icon_path = "logo.png"
page_icon = icon_path if os.path.exists(icon_path) else "🛡️"

st.set_page_config(
    page_title="Freelance Shield Pro",
    page_icon=page_icon,
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 2. CUSTOM CSS (FIXED TABS) ---
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

        /* TYPOGRAPHY */
        h1 {
            background: -webkit-linear-gradient(45deg, #ffffff, #3b82f6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-family: 'Inter', sans-serif;
            font-weight: 900;
            font-size: 3.8rem;
            letter-spacing: -2px;
            text-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }
        
        /* INPUT FIELDS */
        .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
            background-color: #1e293b !important;
            color: #ffffff !important;
            border: 1px solid #334155 !important;
            border-radius: 8px;
        }

        /* BUTTONS */
        .stButton>button {
            background: linear-gradient(90deg, #3b82f6, #2563eb);
            color: white;
            font-weight: bold;
            border: none;
            padding: 0.8rem 1.5rem;
            border-radius: 8px;
            width: 100%;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(37, 99, 235, 0.4);
        }

        /* SIDEBAR */
        [data-testid="stSidebar"] {
            background-color: #0f172a;
            border-right: 1px solid #1e293b;
        }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p {
            color: #cbd5e1 !important;
        }
        
        /* --- FIXED TAB STYLING (THE PILL LOOK) --- */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: rgba(30, 41, 59, 0.5);
            padding: 10px;
            border-radius: 30px; /* Makes the container round */
            border: 1px solid #334155;
        }
        .stTabs [data-baseweb="tab"] {
            height: auto !important; /* Removes fixed height issue */
            padding-top: 8px;
            padding-bottom: 8px;
            padding-left: 20px;
            padding-right: 20px;
            background-color: transparent;
            border-radius: 20px;
            color: #cbd5e1;
            border: none;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            background-color: #3b82f6; /* The Blue Box */
            color: white !important;
            box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3);
        }
        
        /* Preview Box Styling */
        .stTextArea textarea {
            font-family: 'Courier New', monospace !important;
            background-color: #0f172a !important;
            color: #e2e8f0 !important;
            border: 1px solid #3b82f6 !important;
        }
        
        /* Warning Box */
        .warning-box {
            background-color: rgba(255, 193, 7, 0.15); border-left: 4px solid #ffc107; padding: 10px; margin-bottom: 10px; border-radius: 4px; color: #ffecb3; font-size: 0.9rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 3. STATE & TEMPLATES ---
if 'advance_rate' not in st.session_state: st.session_state.advance_rate = 50
if 'slider_key' not in st.session_state: st.session_state.slider_key = 50
if 'num_key' not in st.session_state: st.session_state.num_key = 50
if 'scope_text' not in st.session_state: st.session_state.scope_text = ""

# FULL 12 TEMPLATE LIBRARY
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

# --- 4. DYNAMIC LEGAL LOGIC (SMART CLAUSES) ---
def get_smart_clauses(category, rate):
    # Base Clauses
    clauses = {
        "acceptance": f"Client review within 5 days. Silence = Acceptance. 2 revisions included. Extra changes billed at {rate}/hr.",
        "warranty": "Provided 'as-is'. No post-delivery support unless specified in Annexure A.",
        "ip_rights": "Client owns IP only AFTER full payment. Use before payment is Copyright Infringement.",
        "cancellation": "Cancellation after work starts incurs a forfeiture of the Advance Payment."
    }

    # CATEGORY LOGIC
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

    return clauses

# --- 5. SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", width=120)
    st.markdown("### 🏆 Why Trust Shield?")
    st.info("✅ **Legal Logic:** Based on Indian Contract Act, 1872.")
    st.info("✅ **MSME 3x Interest:** Section 16 Enforceable Clause.")
    
    st.markdown("---")
    st.markdown("### 👨‍⚖️ Founder's Mission")
    st.write("**Hi, I'm a Law Student.**")
    st.caption("I built this tool to help Indian freelancers get paid on time, every time.")
    
    st.markdown("---")
    st.markdown("### 🆘 Need Custom Help?")
    st.write("Complex project? Don't risk it.")
    st.link_button("Hire Me for Review (₹499)", "https://wa.me/YOUR_NUMBER_HERE")

# --- 6. MAIN UI ---
c1, c2 = st.columns([2, 1])
with c1:
    st.markdown("# Stop Chasing Payments.")
    st.markdown('<p class="sub-hero">Generate watertight, MSME-protected contracts for Indian Freelancers in 30 seconds.</p>', unsafe_allow_html=True)
    
    # Dynamic Greeting
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

# TABS
tab1, tab2, tab3 = st.tabs(["👤 The Parties", "🎯 The Work (Scope)", "💰 The Money"])

with tab1:
    st.markdown("### 👤 Who is this contract for?")
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
    st.markdown("### 🎯 What are you delivering?")
    st.markdown('<div class="warning-box">⚠️ <b>NOTE:</b> Selecting a category adjusts the <b>Legal Clauses</b> (IP Rights, Warranty) to match your industry risks.</div>', unsafe_allow_html=True)
    template_choice = st.selectbox("✨ Select Industry (Smart Clauses):", list(scope_templates.keys()), key="template_selector", on_change=update_scope)
    scope_work = st.text_area("Scope of Work (Annexure A)", key="scope_text", height=200)

with tab3:
    st.markdown("### 💰 Financial Terms")
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

# --- 7. GENERATION LOGIC ---
if generate_btn:
    with st.spinner("Drafting your watertight contract..."):
        time.sleep(1.5)
    
    safe_cost = f"Rs. {project_fee_num:,}"
    safe_rate = f"Rs. {hourly_rate_num:,}"
    safe_scope = st.session_state.scope_text.replace("₹", "Rs. ")
    gst_clause = "(Exclusive of GST)" if gst_registered else ""

    smart = get_smart_clauses(template_choice, safe_rate)
    
    cancel_clause = smart.get("cancellation", "Cancellation after work starts incurs a forfeiture of the Advance Payment.")

    # CONTRACT TEXT
    full_contract_text = "PROFESSIONAL SERVICE AGREEMENT\n"
    full_contract_text += f"Date: {datetime.date.today().strftime('%B %d, %Y')}\n\n"
    full_contract_text += f"BETWEEN: {freelancer_name} (Provider) AND {client_name} (Client)\n"
    full_contract_text += "-"*60 + "\n\n"
    
    full_contract_text += f"1. PAYMENT & INTEREST (MSME ACT)\n"
    full_contract_text += f"Total Fee: {safe_cost} {gst_clause}. Advance: {advance_percent}%. Late payments attract compound interest at 3x the Bank Rate notified by RBI (Section 16, MSMED Act, 2006).\n\n"
    
    full_contract_text += "2. ACCEPTANCE & REVISIONS\n" + f"{smart['acceptance']}\n\n"
    full_contract_text += "3. CONFIDENTIALITY (NDA)\nBoth parties agree to keep proprietary information confidential during and for two (2) years after termination.\n\n"
    full_contract_text += "4. IP RIGHTS (IP LOCK)\n" + f"{smart['ip_rights']}\n\n"
    full_contract_text += "5. WARRANTY & SUPPORT\n" + f"{smart['warranty']}\n\n"
    full_contract_text += "6. COMMUNICATION POLICY\nProvider will respond within 1 business day. If Client is unresponsive for >14 days, the contract terminates (Ghosting Clause). Standby fee of Rs. 500/day applies for extended delays.\n\n"
    full_contract_text += "7. FORCE MAJEURE\nNeither party is liable for delays caused by natural disasters, pandemics, or internet infrastructure failures.\n\n"
    full_contract_text += "8. LIMITATION OF LIABILITY\nProvider's total liability shall not exceed the Total Project Fee paid. No liability for indirect damages.\n\n"
    full_contract_text += "9. CANCELLATION / KILL FEE\n" + f"{cancel_clause}\n\n"
    full_contract_text += "10. JURISDICTION & AMENDMENT\nAmendments must be in writing. Disputes subject to Arbitration in " + jurisdiction_city + ", India.\n\n"
    full_contract_text += "11. GST COMPLIANCE\nAll fees are exclusive of applicable GST. Client bears GST liability. Provider warrants tax compliance.\n\n"
    
    full_contract_text += "-"*60 + "\n"
    full_contract_text += "IN WITNESS WHEREOF, the parties have executed this Agreement.\n\n"
    full_contract_text += f"SIGNED BY PROVIDER:\n_________________________\n{freelancer_name}\n\n"
    full_contract_text += f"SIGNED BY CLIENT:\n_________________________\n{client_name}\n"

    # PDF GENERATION
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("logo.png"):
        try: pdf.image("logo.png", 10, 8, 25); pdf.ln(20)
        except: pass
    
    pdf.set_font("Arial", size=10)
    clean_text = full_contract_text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 5, clean_text)
    
    # Annexure Page
    pdf.add_page()
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(0, 10, "ANNEXURE A: SCOPE OF WORK", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", size=10)
    clean_scope = safe_scope.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 6, clean_scope)
    
    pdf_output = pdf.output(dest='S').encode('latin-1')
    
    st.success("✅ Contract Generated Successfully! Review below.")
    st.text_area("Read before downloading:", value=full_contract_text, height=400)
    
    col_dl_1, col_dl_2, col_dl_3 = st.columns([1, 2, 1])
    with col_dl_2:
        st.download_button(
            label="📥 DOWNLOAD FINAL PDF CONTRACT",
            data=pdf_output,
            file_name="Freelance_Agreement.pdf",
            mime="application/pdf",
            use_container_width=True
        )