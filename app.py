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

# --- 2. CUSTOM CSS (THE UI OVERHAUL) ---
st.markdown(
    """
    <style>
        /* BACKGROUND */
        .stApp {
            /* Changed opacity from 0.95 to 0.75 so the image shows through */
            background-image: linear-gradient(rgba(10, 10, 20, 0.75), rgba(10, 10, 20, 0.75)), 
            url("https://raw.githubusercontent.com/mamamooze/freelance-shield/main/background.png");
            background-size: cover;
            background-attachment: fixed;
        }

        /* TYPOGRAPHY */
        h1 {
            font-family: 'Inter', sans-serif;
            color: #ffffff !important;
            font-weight: 800;
            font-size: 3.5rem;
            letter-spacing: -1px;
            text-shadow: 0 2px 10px rgba(0,0,0,0.5);
        }
        h2, h3 {
            color: #f8f9fa !important;
            font-family: 'Inter', sans-serif;
        }
        .sub-hero {
            color: #a0a0a0 !important;
            font-size: 1.3rem;
            margin-bottom: 30px;
        }

        /* INPUT FIELDS (Main Area) */
        .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
            background-color: #1e293b !important;
            color: #ffffff !important;
            border: 1px solid #334155 !important;
            border-radius: 8px;
        }
        
        /* PREVIEW BOX STYLING */
        .stTextArea textarea {
            font-family: 'Courier New', monospace !important;
            background-color: #0f172a !important;
            color: #e2e8f0 !important;
            border: 1px solid #3b82f6 !important;
        }
        
        /* TABS STYLING */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            border-bottom: 1px solid #334155;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: transparent;
            border-radius: 5px;
            color: #94a3b8;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            background-color: #3b82f6;
            color: white !important;
        }

        /* BUTTONS */
        .stButton>button {
            background: linear-gradient(90deg, #3b82f6, #2563eb);
            color: white;
            font-weight: bold;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            width: 100%;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(37, 99, 235, 0.3);
        }

        /* SIDEBAR (The Trust Column) */
        [data-testid="stSidebar"] {
            background-color: #0f172a;
            border-right: 1px solid #1e293b;
        }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p {
            color: #cbd5e1 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 3. SESSION STATE & LISTS ---
if 'advance_rate' not in st.session_state:
    st.session_state.advance_rate = 50
if 'scope_text' not in st.session_state:
    st.session_state.scope_text = ""

# City List for Dropdown
indian_cities = [
    "Bengaluru, Karnataka", "New Delhi, Delhi", "Mumbai, Maharashtra", "Chennai, Tamil Nadu", 
    "Hyderabad, Telangana", "Pune, Maharashtra", "Kolkata, West Bengal", "Gurugram, Haryana", 
    "Noida, Uttar Pradesh", "Ahmedabad, Gujarat", "Jaipur, Rajasthan", "Chandigarh", 
    "Lucknow, Uttar Pradesh", "Kochi, Kerala", "Indore, Madhya Pradesh", "Nagpur, Maharashtra", 
    "Coimbatore, Tamil Nadu", "Bhopal, Madhya Pradesh", "Visakhapatnam, Andhra Pradesh", 
    "Surat, Gujarat", "Patna, Bihar", "Bhubaneswar, Odisha", "Guwahati, Assam", "Goa", 
    "Dehradun, Uttarakhand", "Ranchi, Jharkhand", "Other (Type Manually)"
]

scope_templates = {
    "Select a template...": "",
    "Social Media Marketing": "1. DELIVERABLE: 12 Static Posts/month\n   - CRITERIA: PNG Format, Approved by 25th.\n2. DELIVERABLE: 4 Reels/month\n   - CRITERIA: Under 60s, trending audio.",
    "Video Editing": "1. DELIVERABLE: Edit 1 YouTube Video (10 mins)\n   - CRITERIA: 1080p, Color Graded, Audio Mixed.\n2. TIMELINE: Draft delivered within 48 hours.",
    "Web Development": "1. DELIVERABLE: 5-Page WordPress Site\n   - CRITERIA: Mobile responsive, Speed score >80.\n2. EXCLUSION: Domain and Hosting fees."
}

def update_scope():
    selection = st.session_state.template_selector
    if selection != "Select a template...":
        st.session_state.scope_text = scope_templates[selection]

# --- 4. SIDEBAR (TRUST & UPSELL) ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    
    st.markdown("### 🏆 Why Trust Shield?")
    st.info("✅ **Legal Logic:** Based on Indian Contract Act, 1872.")
    st.info("✅ **MSME 3x Interest:** Section 16 Enforceable Clause.")
    st.info("✅ **Zero Data:** We don't store your clients' names.")

    st.markdown("---")
    st.markdown("### ⭐ Testimonials")
    st.caption('*\"Finally a contract that scares bad clients!\"* \n**- Rahul, Graphic Designer**')
    st.caption('*\"Saved me ₹20k in late fees.\"* \n**- Anjali, Content Writer**')

    st.markdown("---")
    st.markdown("### 🆘 Need Custom Help?")
    st.write("Is your project complex? Don't risk it.")
    st.link_button("Hire Me for Review (₹499)", "https://wa.me/YOUR_NUMBER_HERE")

# --- 5. MAIN HERO SECTION ---
col_hero, col_img = st.columns([2, 1])

with col_hero:
    st.markdown("# Stop Chasing Payments.")
    st.markdown('<p class="sub-hero">Generate watertight, MSME-protected contracts for Indian Freelancers in 30 seconds. Free forever.</p>', unsafe_allow_html=True)

    # Trust Badges (Visuals)
    st.markdown("""
    <div style="display: flex; gap: 15px; margin-bottom: 20px;">
        <span style="background: #1e293b; padding: 5px 10px; border-radius: 5px; color: #94a3b8; font-size: 0.9rem;">🏛️ MSME Protected</span>
        <span style="background: #1e293b; padding: 5px 10px; border-radius: 5px; color: #94a3b8; font-size: 0.9rem;">👻 Anti-Ghosting</span>
        <span style="background: #1e293b; padding: 5px 10px; border-radius: 5px; color: #94a3b8; font-size: 0.9rem;">🔒 IP Lock</span>
    </div>
    """, unsafe_allow_html=True)

with col_img:
    pass 

st.markdown("---")

# --- 6. THE FORM (TABS LAYOUT) ---
tab1, tab2, tab3 = st.tabs(["1️⃣ The Parties", "2️⃣ The Work (Scope)", "3️⃣ The Money"])

with tab1:
    st.markdown("### 👤 Who is this contract for?")
    c1, c2 = st.columns(2)
    with c1:
        freelancer_name = st.text_input("Provider Name (You)", "Amit Kumar")
        
        # --- SEARCHABLE CITY DROPDOWN ---
        selected_city = st.selectbox("Your City (For Court Jurisdiction)", options=indian_cities, help="Type to search (e.g. 'Mum' for Mumbai).")
        
        if selected_city == "Other (Type Manually)":
            jurisdiction_city = st.text_input("Type your City & State manually", "Mysuru, Karnataka")
        else:
            jurisdiction_city = selected_city
            
    with c2:
        client_name = st.text_input("Client Name", "Tech Solutions Pvt Ltd")
        gst_registered = st.checkbox("I am GST Registered")

with tab2:
    st.markdown("### 🎯 What are you delivering?")
    st.selectbox("✨ Start with a template:", list(scope_templates.keys()), key="template_selector", on_change=update_scope)
    
    scope_work = st.text_area(
        "Scope of Work (Annexure A)", 
        key="scope_text",
        height=200,
        help="Be specific. Vague contracts lead to unpaid work."
    )
    st.caption("💡 Tip: List 'Exclusions' to prevent Scope Creep.")

with tab3:
    st.markdown("### 💰 Financial Terms")
    c1, c2, c3 = st.columns(3)
    with c1:
        project_fee_num = st.number_input("Total Project Fee (INR)", value=50000, step=1000)
    with c2:
        hourly_rate_num = st.number_input("Overtime Rate (INR/hr)", value=2000, step=500)
    with c3:
        advance_percent = st.slider("Advance Required (%)", 0, 100, 50)
    
    st.info(f"ℹ️ **Calculation:** You will receive **Rs. {int(project_fee_num * (advance_percent/100)):,}** before starting work.")

st.markdown("---")

# --- 7. GENERATE SECTION ---
center_col = st.columns([1, 2, 1])
with center_col[1]:
    generate_btn = st.button("🚀 Generate Legal Contract Now", type="primary")

# --- 8. LOGIC & OUTPUT ---
if generate_btn:
    
    # DATA PREP
    safe_cost = f"Rs. {project_fee_num:,}"
    safe_rate = f"Rs. {hourly_rate_num:,}"
    safe_scope = st.session_state.scope_text.replace("₹", "Rs. ")
    gst_text = "(Exclusive of GST)" if gst_registered else ""
    
    # BUILD TEXT
    full_contract_text = "PROFESSIONAL SERVICE AGREEMENT\n"
    full_contract_text += f"Date: {datetime.date.today().strftime('%B %d, %Y')}\n\n"
    full_contract_text += f"BETWEEN: {freelancer_name} (Provider) AND {client_name} (Client)\n"
    full_contract_text += "-"*60 + "\n\n"
    full_contract_text += f"1. PAYMENT: Total Fee {safe_cost} {gst_text}. Advance: {advance_percent}%. Late payments attract 3x MSME Interest.\n\n"
    full_contract_text += f"2. JURISDICTION: Disputes subject to courts in {jurisdiction_city}.\n\n"
    full_contract_text += "3. IP RIGHTS: Client owns IP only AFTER full payment.\n\n"
    full_contract_text += "4. TERMINATION: 14 days of silence = Ghosting (Contract ends, you keep advance).\n\n"
    
    full_contract_text += "-"*60 + "\n"
    full_contract_text += "IN WITNESS WHEREOF, the parties have executed this Agreement.\n\n"
    full_contract_text += "SIGNED BY PROVIDER:\n"
    full_contract_text += "_________________________\n"
    full_contract_text += f"(Signature)\n{freelancer_name}\n\n"
    full_contract_text += "SIGNED BY CLIENT:\n"
    full_contract_text += "_________________________\n"
    full_contract_text += f"(Signature)\n{client_name}\n"

    # PDF GENERATION
    pdf = FPDF()
    pdf.add_page()
    
    # Logo
    if os.path.exists("logo.png"):
        try:
            pdf.image("logo.png", 10, 8, 25)
            pdf.ln(20)
        except:
            pass
    
    pdf.set_font("Arial", size=10)
    clean_text = full_contract_text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 6, clean_text)
    
    # Annexure Page
    pdf.add_page()
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(0, 10, "ANNEXURE A: SCOPE OF WORK", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", size=10)
    clean_scope = safe_scope.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 6, clean_scope)
    
    pdf_output = pdf.output(dest='S').encode('latin-1')
    
    # SUCCESS PREVIEW
    st.success("✅ Contract Generated Successfully! Review below.")
    
    # Preview Box
    st.markdown("### 📄 Contract Preview")
    st.text_area("Read before downloading:", value=full_contract_text, height=400)
    
    st.write("") # Vertical Spacer
    
    # Download Button Centered
    col_dl_1, col_dl_2, col_dl_3 = st.columns([1, 2, 1])
    with col_dl_2:
        st.download_button(
            label="📥 DOWNLOAD FINAL PDF CONTRACT",
            data=pdf_output,
            file_name="Freelance_Agreement.pdf",
            mime="application/pdf",
            use_container_width=True
        )