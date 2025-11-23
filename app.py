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

# --- 2. CUSTOM CSS ---
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
        .warning-box {
            background-color: rgba(255, 193, 7, 0.15); border-left: 4px solid #ffc107; padding: 10px; margin-bottom: 10px; border-radius: 4px; color: #ffecb3; font-size: 0.9rem;
        }
        /* Preview Box Styling */
        .stTextArea textarea {
            font-family: 'Courier New', monospace !important;
            background-color: #0f172a !important;
            color: #e2e8f0 !important;
            border: 1px solid #3b82f6 !important;
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

# FULL 12 TEMPLATE LIBRARY (ANNEXURE A CONTENT)
scope_templates = {
    "Select a template...": "",
    
    "Content Writing & Copywriting": """- 4 SEO blog articles, each 1000 words, in .docx format (Grammarly >90), delivered 2/week.
- Topics approved in advance by Client.
- 1 revision per article included.
- No image sourcing, keyword research, or posting.""",

    "Graphic Design": """- Logo (PNG/SVG, 3000px), Business Card/Banner (PDF/PNG, A6/A4 size), colors/fonts per Client.
- 3 feedback rounds, 7 day timeline, excludes printing/stock.""",

    "UI/UX & Web Design": """- Wireframe + UI kit for 5 screens, Figma/Sketch/XD format, mobile responsive.
- Delivery in 5 days, 2 revisions, acceptance by email.""",

    "Web Development": """- 5-page responsive website (WordPress/HTML/CSS/JS), speed score >80.
- ZIP files after client sign-off.
- No hosting/domain fees; Client provides content.""",

    "App Development": """- Android app with 5 features, APK + full source code, compiles on Android 11+.
- Weekly sprints, bug fix for 30 days, client testing via builds.""",

    "Video Editing & Animation": """- Edit 2 YouTube videos, up to 8 min, MP4 1080p, color/audio edited.
- Excludes captions/thumbnails/stock, 2 revisions max.""",

    "Social Media Marketing": """- 20 posts/month (PNG, 1080x1080px), 5/week, as briefed.
- 4 reels/month (MP4 <60s, trending audio).""",

    "SEO, SEM & Digital Marketing": """- Site audit (20 pages), 30 priority keywords, competitor analysis.
- Excludes on-page, backlink, content rewriting.""",

    "Virtual Assistance/Admin": """- Email and calendar tasks managed Mon-Fri.
- Daily Excel report.
- No calls or travel booking.""",

    "Photography & Photo Editing": """- 50 product JPEGs, 3000px, color balanced, white background.
- One re-edit per batch of 10.
- No props, prints, location booking.""",

    "Translation & Transcription": """- Translate 10,000 English words to Hindi, Word/TXT format, accuracy >98%.
- Transcribe 2 audio files (60 min), time-coded, .txt format.
- 1 revision per job, 7-day warranty for corrections.
- No subtitling, legal certification, or localization unless specified.""",

    "Voice-over & Audio Production": """- 3 commercial voiceovers, each 30 sec, delivered in WAV & MP3, edited, royalty-free.
- 1 podcast episode edit (1 hr), with noise cancellation and levels adjustment.
- One retake per project, deadline [date]. Scripts provided by Client.
- No music production/composition unless stated."""
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

    # 1. Content Writing & Copywriting
    if category == "Content Writing & Copywriting":
        clauses["warranty"] = "PLAGIARISM & EDITORIAL WARRANTY: All work must be original and plagiarism-free. Must meet stated readability (eg: Grammarly score >90)."
        clauses["acceptance"] = "Client has 3 days for review; 1 revision per article included."

    # 2. Graphic Design
    elif category == "Graphic Design":
        clauses["ip_rights"] = "IP transfers to Client upon final payment; source drafts (AI/PSD) NOT included unless specified. No physical print or stock image purchase included."
        clauses["acceptance"] = "2 initial concepts per item. 3 feedback rounds included, feedback within 2 days per round."

    # 3. UI/UX & Web Design
    elif category == "UI/UX & Web Design":
        clauses["warranty"] = "DESIGN ONLY: Provider delivers designs only, no coding/build/development included."
        clauses["confidentiality"] = "No sharing of wireframes, prototypes, or concepts to third parties."

    # 4. Web Development
    elif category == "Web Development":
        clauses["warranty"] = "Demo link delivered in 10 days. No hosting/domain/content writing included unless specified."
        clauses["acceptance"] = "Client has 5 days for review. After approval and payment, files and code are released."

    # 5. App Development
    elif category == "App Development":
        clauses["warranty"] = "30-day bug-fix included post-acceptance; extras billed. Provider not responsible for app store upload unless stated."
        clauses["ip_rights"] = "Source code and rights transferred post payment. Use terms as described."

    # 6. Video Editing & Animation
    elif category == "Video Editing & Animation":
        clauses["acceptance"] = "2 feedback rounds included; draft within 48 hours of receiving files. Client has 2 days for acceptance; no response = accepted."
        
    # 7. Social Media Marketing
    elif category == "Social Media Marketing":
        clauses["acceptance"] = "Posts delivered weekly. 2 feedback rounds per post/month."
        
    # 8. SEO, SEM & Digital Marketing
    elif category == "SEO, SEM & Digital Marketing":
        clauses["acceptance"] = "PDF/Excel delivered in 7 days. Client has 2 days for review."
    
    # 9. Virtual Assistance/Admin
    elif category == "Virtual Assistance/Admin":
        clauses["acceptance"] = "Daily email summary, WhatsApp for urgent requests."
    
    # 10. Photography & Photo Editing
    elif category == "Photography & Photo Editing":
        clauses["ip_rights"] = "Commercial rights transfer after payment. No props, prints, or location booking fees included."
    
    # 11. Translation & Transcription
    elif category == "Translation & Transcription":
        clauses["warranty"] = "ACCURACY WARRANTY: Translation >98% accuracy. Provider warrants correction of errors discovered within 7 days."
        clauses["cancellation"] = "Cancellation after work has started incurs a 50% kill fee; after draft delivery, full fee due."
    
    # 12. Voice-over & Audio Production
    elif category == "Voice-over & Audio Production":
        clauses["acceptance"] = "1 correction/re-take per voiceover project included if notified within 5 days. Additional retakes billed at agreed rate."
        clauses["cancellation"] = "KILL FEE: If cancelled after project start, 50% kill fee applies. If after recording session, full session rate due."

    return clauses

# --- 5. SIDEBAR ---
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

# --- 6. MAIN UI ---
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
        # Searchable City Dropdown
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
    safe_cost = f"Rs. {project_fee_num:,}"
    safe_rate = f"Rs. {hourly_rate_num:,}"
    safe_scope = st.session_state.scope_text.replace("₹", "Rs. ")
    gst_clause = "(Exclusive of GST)" if gst_registered else ""

    # FETCH SMART CLAUSES
    smart = get_smart_clauses(template_choice, safe_rate)
    
    # Ensure cancellation key exists (fallback for generic templates)
    cancel_clause = smart.get("cancellation", "Cancellation after work starts incurs a forfeiture of the Advance Payment.")

    # CONTRACT TEXT
    full_contract_text = "PROFESSIONAL SERVICE AGREEMENT\n"
    full_contract_text += f"Date: {datetime.date.today().strftime('%B %d, %Y')}\n\n"
    full_contract_text += f"BETWEEN: {freelancer_name} (Provider) AND {client_name} (Client)\n"
    full_contract_text += "-"*60 + "\n\n"
    
    # Clauses
    full_contract_text += f"1. PAYMENT & INTEREST (MSME ACT)\n"
    # HERE IS THE FIX: Replaced hardcoded percentage with variable {advance_percent}
    full_contract_text += f"Total Fee: {safe_cost} {gst_clause}. Advance: {advance_percent}% (Non-refundable). Work commences only upon realization of advance.\n"
    full_contract_text += "Late payments attract compound interest at 3x the Bank Rate notified by RBI (Section 16, MSMED Act, 2006).\n\n"
    
    full_contract_text += "2. ACCEPTANCE & REVISIONS\n"
    full_contract_text += f"{smart['acceptance']}\n\n"
    
    full_contract_text += "3. CONFIDENTIALITY (NDA)\n"
    full_contract_text += "Both parties agree to keep proprietary information confidential during and for two (2) years after termination.\n\n"
    
    full_contract_text += "4. IP RIGHTS (IP LOCK)\n"
    full_contract_text += f"{smart['ip_rights']}\n\n"
    
    full_contract_text += "5. WARRANTY & SUPPORT\n"
    full_contract_text += f"{smart['warranty']}\n\n"
    
    full_contract_text += "6. COMMUNICATION POLICY\n"
    full_contract_text += "Provider will respond within 1 business day. If Client is unresponsive for >14 days, the contract terminates (Ghosting Clause). Standby fee of Rs. 500/day applies for extended delays.\n\n"
    
    full_contract_text += "7. FORCE MAJEURE\n"
    full_contract_text += "Neither party is liable for delays caused by natural disasters, pandemics, or internet infrastructure failures.\n\n"
    
    full_contract_text += "8. LIMITATION OF LIABILITY\n"
    if "liability" in smart:
        full_contract_text += f"{smart['liability']} "
    full_contract_text += "Provider's total liability shall not exceed the Total Project Fee paid. No liability for indirect damages.\n\n"

    full_contract_text += "9. CANCELLATION / KILL FEE\n"
    full_contract_text += f"{cancel_clause}\n\n"

    full_contract_text += "10. JURISDICTION & AMENDMENT\n"
    full_contract_text += "Amendments must be in writing. Disputes subject to Arbitration in " + jurisdiction_city + ", India.\n\n"
    
    full_contract_text += "11. GST COMPLIANCE\n"
    full_contract_text += "All fees are exclusive of applicable GST. Client bears GST liability. Provider warrants tax compliance.\n\n"
    
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