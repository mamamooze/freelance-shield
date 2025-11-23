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
        
        /* TEXT VISIBILITY */
        .stMarkdown p, .stMarkdown li, label {
            color: #e0e0e0 !important;
            font-size: 1.05rem;
            line-height: 1.6;
        }

        /* CARDS */
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
            color: #93c5fd !important;
            border: 1px solid #3b82f6 !important;
        }

        /* BUTTONS */
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

# --- FULL TEMPLATE LIBRARY ---
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
    # DEFAULT / BASE CLAUSES
    clauses = {
        "revisions": f"2 rounds of revisions included. Revisions must be requested within 2 business days. Extra changes billed at {rate}/hr.",
        "ip": "Client shall receive full ownership ONLY upon receipt of full payment. Until then, Provider retains exclusive property rights.",
        "warranty": "Deliverables are provided 'as-is'. No guarantees regarding third-party compatibility or market performance.",
        "cancellation": "If Client cancels after work commences, Client forfeits the advance payment in full."
    }

    # 1. TECHNOLOGY (WEB/APP)
    if category in ["💻 Web Development", "📱 App Development"]:
        clauses["ip"] = "Client receives full source code rights upon final payment. Provider retains rights to generic libraries/frameworks."
        clauses["warranty"] = "BUG FIX WARRANTY: Provider agrees to fix critical bugs reported within 30 days of delivery. No third-party modifications allowed."
        clauses["cancellation"] = "Client owes payment for all completed milestones plus 50% of current milestone in progress."

    # 2. CREATIVE (DESIGN/PHOTO/VIDEO/UI)
    elif category in ["🎨 Graphic Design", "🎥 Video Editing", "🖼️ UI/UX & Web Design", "📸 Photography"]:
        clauses["ip"] = "Final deliverables (PNG/JPG/MP4) transfer to Client. Raw source files (PSD/AI/PrProj) remain property of Provider unless purchased."
        clauses["revisions"] = "Rejections based solely on 'personal taste' after initial style approval will constitute a new project fee."
        
    # 3. MARKETING (SOCIAL/SEO)
    elif category in ["📱 Social Media Marketing", "📈 SEO & Digital Marketing"]:
        clauses["warranty"] = "NO ROI GUARANTEE: Provider does NOT guarantee specific business outcomes (sales, followers, rankings)."
        clauses["revisions"] = "Content must be approved 24 hours prior to scheduled publishing deadlines."
        clauses["cancellation"] = "30 days written notice required for termination. Payment due for current month."

    # 4. WRITING/TRANSLATION
    elif category in ["✍️ Content Writing", "🗣️ Translation"]:
        clauses["warranty"] = "ORIGINALITY WARRANTY: Provider warrants that work is original (not plagiarized). Translation accuracy >98%."
        clauses["revisions"] = "1 review round covers accuracy/grammar. Style changes or re-translation requests are billed separately."
        clauses["cancellation"] = "50% fee due if cancelled after work begins. 100% fee due if cancelled after draft delivery."

    # 5. VOICE OVER
    elif category == "🎙️ Voice-Over":
        clauses["revisions"] = "One revision round covers pronunciation errors only. Script changes or creative redirection require a new fee."
        clauses["cancellation"] = "50% kill fee if cancelled after start. 100% fee if cancelled after recording session."

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

# --- 6. GENERATION & EXPORT ---
if generate_btn:
    with st.spinner("Drafting your watertight contract..."):
        time.sleep(1.5)
    
    safe_cost = f"Rs. {project_fee_num:,}"
    safe_rate = f"Rs. {hourly_rate_num:,}"
    safe_scope = st.session_state.scope_text.replace("₹", "Rs. ")
    gst_clause = "(Exclusive of GST)" if gst_registered else ""
    smart = get_smart_clauses(template_choice, safe_rate)

    full_text = f"""
FREELANCE SHIELD - PROFESSIONAL SERVICE AGREEMENT
Date: {datetime.date.today().strftime('%B %d, %Y')}

BETWEEN: {freelancer_name} (Provider)
AND {client_name} (Client)

1. SERVICES & SCOPE
Provider agrees to perform services as described in Annexure A (Scope of Work).

2. PAYMENT & INTEREST (MSME ACT COMPLIANT)
Total Fee: {safe_cost} {gst_clause}
Advance Payment: {advance_percent}% due upon signing. Work commences only upon realization.
Late Payment Interest: Any payment delayed beyond 45 days will attract compound interest at 3x the Bank Rate notified by the RBI (Section 16, MSMED Act, 2006).

3. ACCEPTANCE & REVISIONS
Review Period: {smart['acceptance']}

4. INTELLECTUAL PROPERTY RIGHTS
{smart['ip_rights']}

5. WARRANTY & LIABILITY
{smart['warranty']}
Limitation of Liability: Provider's total liability is strictly limited to the Total Fee paid.

6. CONFIDENTIALITY (NON-DISCLOSURE)
Both parties agree to maintain strict confidentiality regarding proprietary information for 2 years post-termination.

7. CANCELLATION & KILL FEE
{smart['cancellation']}

8. COMMUNICATION & GHOSTING
Response Time: Provider responds within 1 business day.
Ghosting Protection: If Client is unresponsive for 14 consecutive days, the project is deemed terminated and advance is forfeited.

9. FORCE MAJEURE
Neither party shall be liable for delays due to acts of God, internet failure, or government action.

10. DISPUTE RESOLUTION & JURISDICTION
Governing Law: Laws of India.
Arbitration: Disputes unresolved after 15 days of negotiation shall be referred to binding arbitration in {jurisdiction_city}, India.

11. ENTIRE AGREEMENT
This Agreement supersedes all prior discussions. Modifications must be in writing.

---------------------------------------------------
SIGNED BY PROVIDER: 
Name: {freelancer_name}
Date: ________________

SIGNED BY CLIENT: 
Name: {client_name}
Date: ________________
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

# --- LEGAL FOOTER ---
st.markdown("---")
st.markdown("""
<div class="legal-footer">
    <p>© 2025 Freelance Shield Pro. All rights reserved.</p>
    <p><b>Disclaimer:</b> This tool provides templates for informational purposes only and does not constitute legal advice. 
    We are not a law firm. Please consult a qualified attorney for your specific business needs.</p>
</div>
""", unsafe_allow_html=True)