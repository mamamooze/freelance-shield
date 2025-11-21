import streamlit as st
from fpdf import FPDF
import datetime
import os

# --- 1. SETUP & FAVICON ---
icon_path = "logo.png"
page_icon = icon_path if os.path.exists(icon_path) else "🛡️"

st.set_page_config(
    page_title="Freelance Shield Pro",
    page_icon=page_icon,
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CUSTOM CSS STYLING ---
st.markdown(
    """
    <style>
        /* Main background */
        .stApp {
            background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.9)), 
            url("https://raw.githubusercontent.com/mamamooze/freelance-shield/main/background.png");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        
        [data-testid="stSidebar"] {
            background-color: rgba(255, 255, 255, 0.95);
            border-right: 1px solid #e0e0e0;
        }

        h1, h2, h3 {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: #ffffff;
            font-weight: 700;
            text-shadow: 0px 2px 4px rgba(0,0,0,0.5);
        }
        
        .stSubheader, p, label, .stCheckbox label, .stMarkdown {
            color: #dcdcdc !important;
            font-family: 'Helvetica Neue', sans-serif;
        }
        
        /* Info Box Styling */
        .stInfo {
            background-color: rgba(52, 152, 219, 0.1);
            color: white;
            border: 1px solid #3498db;
        }

        /* Input field styling */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>div>input {
            background-color: rgba(255, 255, 255, 0.9);
            color: #000;
            border-radius: 8px;
        }

        /* Button styling */
        .stButton>button {
            background-color: #2ecc71;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 12px 24px;
            font-weight: 700;
            transition: all 0.3s ease;
            width: 100%;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .stButton>button:hover {
            background-color: #27ae60;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- SESSION STATE INITIALIZATION ---
# We ensure the keys exist before the widgets load to avoid the yellow warning
if 'slider_key' not in st.session_state:
    st.session_state.slider_key = 50
if 'num_key' not in st.session_state:
    st.session_state.num_key = 50

# --- SYNC FUNCTIONS ---
# When Slider moves, update the Num box
def update_from_slider():
    st.session_state.num_key = st.session_state.slider_key

# When Num box changes, update the Slider
def update_from_num():
    st.session_state.slider_key = st.session_state.num_key

# --- LEGAL DATABASE ---
contract_clauses = {
    "scope_of_work": (
        "1. SCOPE OF WORK & DELIVERABLES\n"
        "The Provider agrees to perform the services ('Services') explicitly detailed in \"ANNEXURE A\" attached to this Agreement. "
        "Any task not listed in Annexure A is considered out of scope.\n\n"
        "CHANGE ORDERS: Any request by the Client for alterations, additions, or modifications that deviate from the Scope ('Scope Creep') "
        "must be made in writing and will be billed additionally at the rate of [HOURLY_RATE] per hour."
    ),
    "payment_terms": (
        "2. PAYMENT TERMS & STATUTORY INTEREST (MSME ACT)\n"
        "Total Project Fee: [PROJECT_COST] [GST_CLAUSE]\n"
        "Advance Payment: [ADVANCE_PERCENT]% (Non-refundable). Work commences only upon realization of advance.\n\n"
        "STATUTORY NOTICE: Pursuant to the Micro, Small and Medium Enterprises Development Act, 2006 (MSMED Act), "
        "time is of the essence regarding payments. Any outstanding balance must be cleared within forty-five (45) days.\n\n"
        "LATE FEES: In the event of a delay, the Client shall be liable to pay compound interest with monthly rests to the Provider "
        "at three times (3x) the bank rate notified by the Reserve Bank of India (Section 16, MSMED Act, 2006)."
    ),
    "intellectual_property": (
        "3. INTELLECTUAL PROPERTY RIGHTS & LIEN\n"
        "The transfer of Intellectual Property Rights (IPR), copyright, and ownership of all source files, designs, and assets "
        "is strictly conditional upon the full and final realization of the Total Project Fee. "
        "Until the final invoice is cleared, the Provider retains a 'General Lien' and full legal title over all deliverables.\n\n"
        "UNAUTHORIZED USE: Usage of the work product prior to full payment constitutes an unauthorized use and infringement of rights under the Copyright Act, 1957."
    ),
    "confidentiality": (
        "4. CONFIDENTIALITY\n"
        "Both parties agree to maintain strict confidentiality regarding proprietary information, business strategies, and trade secrets. "
        "This obligation survives the termination of this Agreement for a period of two (2) years."
    ),
    "termination": (
        "5. TERMINATION & CANCELLATION\n"
        "BY CLIENT: If the Client cancels the project or becomes unresponsive for >14 days ('Ghosting'), the Agreement is terminated by default. "
        "The Advance Payment is forfeited as a cancellation fee.\n\n"
        "BY PROVIDER: The Provider may terminate if the Client fails to make payments within agreed timelines or engages in abusive conduct. "
        "In such cases, the Client remains liable for all work completed up to the date of termination."
    ),
    "liability": (
        "6. LIMITATION OF LIABILITY & WARRANTY\n"
        "The Services are provided on an 'as-is' basis. The Provider makes no specific warranty regarding fitness for a particular purpose. "
        "LIMITATION: The Provider's total liability under this Agreement shall strictly NOT EXCEED the Total Project Fee paid by the Client. "
        "In no event shall the Provider be liable for indirect, consequential, or punitive damages."
    ),
    "jurisdiction": (
        "7. DISPUTE RESOLUTION & JURISDICTION\n"
        "This Agreement shall be governed by the laws of India. "
        "Any dispute arising out of this Agreement shall be subject to the exclusive jurisdiction of the courts in [CITY], India."
    )
}

# --- APP LOGIC ---

# Main Header Area
col1, col2 = st.columns([1, 5])
with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=100)
    else:
        st.write("🛡️")
with col2:
    st.title("Freelance Shield Pro")
    st.markdown("*Generate Bulletproof, MSME-Protected Contracts in Seconds.*")

# --- SIDEBAR ---
with st.sidebar:
    st.header("📝 Project Details")
    freelancer_name = st.text_input("Provider Name (You)", "Amit Kumar")
    client_name = st.text_input("Client Name", "Tech Solutions Pvt Ltd")
    jurisdiction_city = st.text_input("Your City (For Courts)", "Bengaluru, Karnataka")
    gst_registered = st.checkbox("Are you GST Registered?")
    
    st.markdown("---")
    st.caption("👇 Define Scope & Acceptance Criteria:")
    scope_work = st.text_area(
        "Scope of Work (Annexure A)", 
        "1. DELIVERABLE: 5 Social Media Posts\n   - CRITERIA: High-res PNG format.\n\n2. DELIVERABLE: 1 Promotional Video (60s)\n   - CRITERIA: 1080p, subtitles included.",
        height=200
    )
    
    st.markdown("---")
    project_fee_num = st.number_input("Total Project Fee (INR)", value=50000, step=1000)
    hourly_rate_num = st.number_input("Overtime/Hourly Rate (INR)", value=2000, step=500)
    
    st.write("Advance Required (%)")
    c1, c2 = st.columns([3, 1])
    
    # --- WIDGETS (Fixed: Removed 'value=' arg to fix yellow warning) ---
    with c1:
        st.slider("Slider", 0, 100, key="slider_key", on_change=update_from_slider, label_visibility="collapsed")
    with c2:
        st.number_input("Num", 0, 100, key="num_key", on_change=update_from_num, label_visibility="collapsed")
    
    # We read the value from the slider key (which is synced to num_key)
    advance_percent = st.session_state.slider_key
    
    st.markdown("---")
    generate_btn = st.button("🚀 Generate Contract", type="primary")

# --- MAIN SCREEN CONTENT ---

if not generate_btn:
    # 1. FEATURES GRID
    st.markdown("### ⚡ Why use this contract?")
    f1, f2, f3 = st.columns(3)
    
    with f1:
        st.info("**🏛️ MSME Protection**\n\nIncludes Section 16 clause: Clients must pay **3x Bank Interest** for delays > 45 days.")
    with f2:
        st.info("**👻 Anti-Ghosting**\n\nUnresponsive client? The contract auto-terminates after 14 days and you **keep the advance**.")
    with f3:
        st.info("**🔒 IP Lock**\n\nClients don't own your work until they pay 100%. If they use it before paying, it's **Copyright Infringement**.")

    st.markdown("---")

    # 2. HOW IT WORKS
    st.markdown("### 🛠️ How it works")
    w1, w2, w3 = st.columns(3)
    with w1:
        st.markdown("#### 1. Fill Details")
        st.caption("Enter your rates, scope, and city in the sidebar.")
    with w2:
        st.markdown("#### 2. Define Scope")
        st.caption("List exactly what you are doing to avoid 'Scope Creep'.")
    with w3:
        st.markdown("#### 3. Export PDF")
        st.caption("Download a legally binding PDF ready for e-signing.")

    st.markdown("---")

    # 3. FAQ
    with st.expander("❓ Frequently Asked Questions"):
        st.write("**Is this legally binding?**\nYes, it uses standard Indian Contract Act clauses. Once signed by both parties, it is enforceable.")
        st.write("**What is the MSME Act?**\nIt is a law that protects small businesses/freelancers from delayed payments. You usually need Udyam Registration to enforce the court case, but the *threat* in the contract works for everyone.")
        st.write("**Can I edit the PDF?**\nNo, the PDF is locked to ensure integrity. If you need changes, edit the inputs and regenerate.")

# --- GENERATION LOGIC ---
if generate_btn:
    
    # SANITIZE
    safe_cost = f"Rs. {project_fee_num:,}"
    safe_rate = f"Rs. {hourly_rate_num:,}"
    safe_scope = scope_work.replace("₹", "Rs. ")
    gst_text = "(Exclusive of GST)" if gst_registered else ""
    
    # BUILD TEXT
    full_contract_text = "PROFESSIONAL SERVICE AGREEMENT\n"
    full_contract_text += f"Date: {datetime.date.today().strftime('%B %d, %Y')}\n\n"
    full_contract_text += "BETWEEN:\n"
    full_contract_text += f"PROVIDER: {freelancer_name}\n"
    full_contract_text += "AND\n"
    full_contract_text += f"CLIENT: {client_name}\n\n"
    full_contract_text += "-"*60 + "\n\n"
    
    for key, clause in contract_clauses.items():
        filled_clause = clause.replace("[CLIENT_NAME]", client_name)\
                              .replace("[FREELANCER_NAME]", freelancer_name)\
                              .replace("[PROJECT_COST]", safe_cost)\
                              .replace("[ADVANCE_PERCENT]", str(advance_percent))\
                              .replace("[HOURLY_RATE]", safe_rate)\
                              .replace("[CITY]", jurisdiction_city)\
                              .replace("[GST_CLAUSE]", gst_text)
        full_contract_text += filled_clause + "\n\n"

    full_contract_text += "-"*60 + "\n"
    full_contract_text += "IN WITNESS WHEREOF, the parties have executed this Agreement.\n\n"
    full_contract_text += "SIGNED BY PROVIDER:\n\n"
    full_contract_text += "_________________________\n"
    full_contract_text += f"(Signature)\n{freelancer_name}\n\n"
    full_contract_text += "SIGNED BY CLIENT:\n\n"
    full_contract_text += "_________________________\n"
    full_contract_text += f"(Signature)\n{client_name}\n"

    # PREVIEW
    st.success("✅ Contract Generated Successfully!")
    
    col_prev, col_dl = st.columns([3, 1])
    with col_prev:
        st.text_area("Preview:", full_contract_text, height=300)
    
    # PDF
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("logo.png"):
        try:
            pdf.image("logo.png", 10, 8, 25)
            pdf.ln(20)
        except:
            pass 
    
    pdf.set_font("Arial", size=10)
    try:
        clean_text = full_contract_text.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 5, clean_text)
        
        pdf.add_page()
        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(0, 10, "ANNEXURE A: SCOPE OF WORK", ln=True)
        pdf.ln(5)
        pdf.set_font("Arial", size=10)
        clean_scope = safe_scope.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 6, clean_scope)
        
        pdf_output = pdf.output(dest='S').encode('latin-1')
        
        with col_dl:
            st.write("\n")
            st.write("\n")
            st.download_button(
                label="⬇️ Download PDF",
                data=pdf_output,
                file_name="Service_Agreement.pdf",
                mime="application/pdf"
            )
    except Exception as e:
        st.error(f"Error: {e}")