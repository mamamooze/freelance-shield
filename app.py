import streamlit as st
from fpdf import FPDF
import datetime
import os

# --- 1. SETUP & CONFIG ---
icon_path = "logo.png"
page_icon = icon_path if os.path.exists(icon_path) else "🛡️"

st.set_page_config(
    page_title="Freelance Shield Pro",
    page_icon=page_icon,
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 2. CUSTOM CSS (High Contrast) ---
st.markdown(
    """
    <style>
        .stApp {
            background-image: linear-gradient(rgba(10, 10, 20, 0.75), rgba(10, 10, 20, 0.75)), 
            url("https://raw.githubusercontent.com/mamamooze/freelance-shield/main/background.png");
            background-size: cover;
            background-attachment: fixed;
        }
        [data-testid="stSidebar"] { background-color: #0f172a; border-right: 1px solid #1e293b; }
        h1, h2, h3 { color: #ffffff !important; font-family: 'Inter', sans-serif; font-weight: 800; }
        .stMarkdown p, .stMarkdown li { color: #e9ecef !important; font-size: 1.1rem; }
        .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
            background-color: #1e293b !important; color: #ffffff !important; border: 1px solid #334155 !important; border-radius: 8px;
        }
        .stButton>button {
            background: linear-gradient(90deg, #3b82f6, #2563eb); color: white; font-weight: bold; border: none; padding: 0.75rem 1.5rem;
            border-radius: 8px; width: 100%; text-transform: uppercase; letter-spacing: 1px; transition: all 0.3s;
        }
        .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(37, 99, 235, 0.3); }
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: #cbd5e1 !important; }
        
        /* Warning Box Styling */
        .warning-box {
            background-color: rgba(255, 193, 7, 0.15);
            border-left: 4px solid #ffc107;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 4px;
            color: #ffecb3;
            font-size: 0.9rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 3. STATE & TEMPLATES (UPDATED WITH 12 CATEGORIES) ---
if 'advance_rate' not in st.session_state: st.session_state.advance_rate = 50
if 'slider_key' not in st.session_state: st.session_state.slider_key = 50
if 'num_key' not in st.session_state: st.session_state.num_key = 50
if 'scope_text' not in st.session_state: st.session_state.scope_text = ""

scope_templates = {
    "Select a template...": "",
    
    "Video Editing": """DELIVERABLE: Edit 1 YouTube Video (max 10 mins)
- FORMAT: MP4, 1080p HD, 30fps
- COLOR: Professionally color graded to match brand palette
- AUDIO: Normalized and mixed, background music copyright-free
- REVISIONS: 2 feedback rounds included, each within 48 hours
- DELIVERY: First draft sent to Client via Google Drive within 48 hours of raw file receipt
- ACCEPTANCE: Client to provide review/approval within 2 days of delivery. Silence counts as acceptance.
- EXCLUSIONS: No subtitle/captioning, thumbnail, or animation unless specified.""",

    "Social Media Marketing": """DELIVERABLE: 12 Static Social Media Posts per month
- FORMAT: PNG, RGB, 1200x1200px
- BRIEF: Each post includes client-provided text and logo; 3 posts/week, approved by 25th monthly
- DELIVERY: Shared via Google Drive/Dropbox folder, scheduled post calendar
- REVISIONS: 2 rounds of changes/month included; further at agreed hourly rate
- EXCLUSIONS: No paid ad management, audience growth, or influencer outreach

DELIVERABLE: 4 Instagram Reels per month
- FORMAT: MP4, under 60s, trending audio, client review
- CRITERIA: Relevant to monthly theme, on-brand colors and logos
- DELIVERY: Drafts submitted by 15th monthly, feedback window 2 days""",

    "Web Development": """DELIVERABLE: 5-Page WordPress Website
- DESIGN: Mobile responsive; consistent brand colors/fonts
- FUNCTIONALITY: Speed score >80 on Google PageSpeed; Contact form; About page
- TECHNOLOGY: Latest WordPress version, no obsolete plugins
- DELIVERY: Staging link provided for review, final files after approval and payment
- ACCEPTANCE: Client review within 5 days, max 2 revision rounds before final handoff
- EXCLUSIONS: Domain/hosting fees not included; content/copywriting supplied by client""",

    "Content Writing & Copywriting": """DELIVERABLE: Write 4 SEO blog articles (1000 words each)
- FORMAT: .docx, Grammarly score >90, minimum Flesch score 60
- TOPICS: Approved by client before writing; 1 revision per article included
- DELIVERY: 2 articles/week, submitted via email by Friday EOD
- ACCEPTANCE: Client reviews within 3 days; 1 round of changes free
- EXCLUSIONS: No image sourcing, keyword research, or posting""",

    "Graphic Design": """DELIVERABLE: Design logo, business card, and banner
- FORMAT: Logo: PNG+SVG (3000px), Card/Banner: PDF+PNG (A6/A4 size)
- BRIEF: Brand colors and fonts provided by client; 2 initial concepts
- REVISIONS: Up to 3 rounds included, feedback within 2 business days
- DELIVERY: Final files sent via Google Drive within 7 days
- ACCEPTANCE: Written approval or feedback required; further revisions at hourly rate
- EXCLUSIONS: No printing or stock images purchased by designer""",

    "UI/UX & Web Design": """DELIVERABLE: Wireframe and UI kit for fintech app (5 screens)
- FORMAT: Figma, Sketch, or Adobe XD files
- CRITERIA: Mobile responsive, consistent design elements
- DELIVERY: Initial draft within 5 days; prototype link sent to client
- REVISIONS: 2 rounds free, feedback required within 3 days
- ACCEPTANCE: Approval via email or platform chat, silence = acceptance
- EXCLUSIONS: No development/coding, no branding or logo creation""",

    "App Development": """DELIVERABLE: Android app MVP (core 5 features)
- FORMAT: APK + full source code (GitHub repo)
- CRITERIA: Compiles on Android 11+, no critical crashes, UI as per wireframe
- DELIVERY: First build in 14 days, weekly sprints, final build in 30 days
- REVISIONS: 2 cycles per feature, bug-fixing for 30 days post-delivery
- ACCEPTANCE: Client test/approve via feedback form
- EXCLUSIONS: Google Play upload not included, advanced analytics extra""",

    "SEO, SEM & Digital Marketing": """DELIVERABLE: SEO audit + keyword plan for main site (20 pages)
- FORMAT: PDF report, Excel keyword planner
- CRITERIA: 30 priority keywords, competitor analysis summary
- DELIVERY: Draft audit + keyword file in 7 days, feedback in 2 days
- REVISIONS: 1 round included
- EXCLUSIONS: On-page optimizations, backlinks, content rewriting unless stated""",

    "Virtual Assistance/Admin": """DELIVERABLE: Daily email management and meeting scheduling (20 days)
- FORMAT: Report of task completion (Excel), inbox cleared daily
- COMMUNICATION: WhatsApp or email updates each evening
- AVAILABILITY: 9am-5pm, Monday-Friday, 24hr response window
- REVISIONS: 1 round changes per week on task process
- EXCLUSIONS: No calls, travel booking, or personal errands""",

    "Photography & Photo Editing": """DELIVERABLE: Shoot and edit 50 product shots, e-commerce ready
- FORMAT: JPEGs, 3000px, with basic retouching
- TIMELINE: Shoot on location within 2 days, edits delivered in 3 days
- CRITERIA: Clean white background, color balanced, cropped to size
- REVISIONS: 1 re-edit round per batch of 10 photos
- EXCLUSIONS: No video, prints, props, or location booking""",

    "Translation & Transcription": """DELIVERABLE: Translate 10K English words to Hindi + 2 transcriptions (60 mins audio)
- FORMAT: Word or TXT file, time-coded transcription
- ACCURACY: 98% minimum, industry-standard Hindi
- DELIVERY: 3 days for translation, 2 days/audio for transcription
- REVISIONS: 1 review/revision round included per job
- EXCLUSIONS: No subtitling, localization for legal terms extra""",

    "Voice-over/Audio Production": """DELIVERABLE: Record 3 commercial voice-overs (30s each) + edit client podcast episode (1hr)
- FORMAT: WAV and MP3, commercial rights included
- SCRIPT: Provided by client before booking
- DELIVERY: Draft audio within 72 hours, 1 correction round per project
- EXCLUSIONS: No music production, scriptwriting, or mixing unless requested"""
}

def update_scope():
    if st.session_state.template_selector != "Select a template...":
        st.session_state.scope_text = scope_templates[st.session_state.template_selector]

def update_from_slider(): st.session_state.num_key = st.session_state.slider_key
def update_from_num(): st.session_state.slider_key = st.session_state.num_key

# --- 4. SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", width=120)
    st.markdown("### 🏆 Why Trust Shield?")
    st.info("✅ **Legal Logic:** Based on Indian Contract Act, 1872.")
    st.info("✅ **MSME 3x Interest:** Section 16 Enforceable Clause.")
    
    st.markdown("---")
    st.markdown("### 👨‍⚖️ Why I Built This")
    st.write("**Hi, I'm a Law Student.**")
    st.caption("I built this to give every Indian freelancer the legal protection usually reserved for big companies.")
    
    st.markdown("---")
    st.markdown("### 🆘 Need Custom Help?")
    st.write("Complex project? Don't risk it.")
    st.link_button("Hire Me for Review (₹499)", "https://wa.me/YOUR_NUMBER_HERE")

# --- 5. MAIN UI ---
c1, c2 = st.columns([2, 1])
with c1:
    st.markdown("# Stop Chasing Payments.")
    st.markdown('<p class="sub-hero">Generate watertight, MSME-protected contracts for Indian Freelancers in 30 seconds.</p>', unsafe_allow_html=True)
    st.markdown("""
    <div style="display: flex; gap: 15px; margin-bottom: 20px;">
        <span style="background: #1e293b; padding: 5px 10px; border-radius: 5px; color: #94a3b8; font-size: 0.9rem;">🏛️ MSME Protected</span>
        <span style="background: #1e293b; padding: 5px 10px; border-radius: 5px; color: #94a3b8; font-size: 0.9rem;">👻 Anti-Ghosting</span>
        <span style="background: #1e293b; padding: 5px 10px; border-radius: 5px; color: #94a3b8; font-size: 0.9rem;">🔒 IP Lock</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["1️⃣ The Parties", "2️⃣ The Work (Scope)", "3️⃣ The Money"])

with tab1:
    st.markdown("### 👤 Who is this contract for?")
    c1, c2 = st.columns(2)
    with c1:
        freelancer_name = st.text_input("Provider Name (You)", "Amit Kumar")
        selected_city = st.selectbox("Your City (Jurisdiction)", ["Bengaluru, Karnataka", "New Delhi, Delhi", "Mumbai, Maharashtra", "Chennai, Tamil Nadu", "Hyderabad, Telangana", "Other (Type Manually)"])
        jurisdiction_city = st.text_input("Type City", "Mysuru") if selected_city == "Other (Type Manually)" else selected_city
    with c2:
        client_name = st.text_input("Client Name", "Tech Solutions Pvt Ltd")
        gst_registered = st.checkbox("I am GST Registered")

with tab2:
    st.markdown("### 🎯 What are you delivering?")
    
    # WARNING BOX
    st.markdown('<div class="warning-box">⚠️ <b>NOTE:</b> These are just templates. Please edit the text below to match your specific project details (dates, quantities, file formats) before generating.</div>', unsafe_allow_html=True)
    
    st.selectbox("✨ Start with a template:", list(scope_templates.keys()), key="template_selector", on_change=update_scope)
    scope_work = st.text_area("Scope of Work (Annexure A)", key="scope_text", height=300)

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

# --- 6. GENERATION LOGIC ---
if generate_btn:
    safe_cost = f"Rs. {project_fee_num:,}"
    safe_rate = f"Rs. {hourly_rate_num:,}"
    safe_scope = st.session_state.scope_text.replace("₹", "Rs. ")
    gst_clause = "(Exclusive of GST)" if gst_registered else ""

    # CONTRACT TEXT CONSTRUCTION
    full_contract_text = "PROFESSIONAL SERVICE AGREEMENT\n"
    full_contract_text += f"Date: {datetime.date.today().strftime('%B %d, %Y')}\n\n"
    full_contract_text += f"BETWEEN: {freelancer_name} (Provider) AND {client_name} (Client)\n"
    full_contract_text += "-"*60 + "\n\n"
    
    # Clauses (Full set from previous update)
    full_contract_text += f"1. PAYMENT & INTEREST (MSME ACT)\n"
    full_contract_text += f"Total Fee: {safe_cost} {gst_clause}. Advance: {advance_percent}%. Late payments attract compound interest at 3x the Bank Rate (Section 16, MSMED Act, 2006).\n\n"
    full_contract_text += "2. ACCEPTANCE & REVISIONS\nClient review within 5 days. Silence = Acceptance. 2 revisions included. Further changes billed at " + safe_rate + "/hr.\n\n"
    full_contract_text += "3. CONFIDENTIALITY (NDA)\nStrict confidentiality for 2 years post-termination.\n\n"
    full_contract_text += "4. IP RIGHTS (IP LOCK)\nClient owns IP only AFTER full payment. Use before payment is Copyright Infringement.\n\n"
    full_contract_text += "5. WARRANTY & SUPPORT\nProvided 'as-is'. No post-delivery support unless specified in Annexure A.\n\n"
    full_contract_text += "6. COMMUNICATION POLICY\nProvider responds within 1 business day. Client silence >14 days = Termination (Ghosting).\n\n"
    full_contract_text += "7. FORCE MAJEURE\nNot liable for acts of God or internet failure.\n\n"
    full_contract_text += "8. JURISDICTION\nDisputes subject to Arbitration in " + jurisdiction_city + ", India.\n\n"
    
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