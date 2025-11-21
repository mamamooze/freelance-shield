import streamlit as st
from fpdf import FPDF
import datetime
import os

# --- 1. SETUP & FAVICON ---
icon_path = "logo.png"
page_icon = icon_path if os.path.exists(icon_path) else "🛡️"

st.set_page_config(
    page_title="Freelance Shield",
    page_icon=page_icon,
    layout="centered",
    initial_sidebar_state="expanded",
)

# --- CUSTOM CSS STYLING ---
st.markdown(
    """
    <style>
        /* Main background with Image and Dimmer */
        .stApp {
            background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
            url("https://raw.githubusercontent.com/mamamooze/freelance-shield/main/background.png");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        
        /* Sidebar transparency */
        [data-testid="stSidebar"] {
            background-color: rgba(255, 255, 255, 0.95);
            border-right: 1px solid #e0e0e0;
        }

        /* Typography */
        h1, h2, h3 {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: #ffffff;
            font-weight: 700;
            text-shadow: 0px 2px 4px rgba(0,0,0,0.5);
        }
        
        .stSubheader, p, label {
            color: #dcdcdc !important;
            font-family: 'Helvetica Neue', sans-serif;
        }

        /* Input field styling */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {
            background-color: rgba(255, 255, 255, 0.9);
            color: #000;
            border-radius: 8px;
        }

        /* Button styling */
        .stButton>button {
            background-color: #3498db;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 10px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
            width: 100%;
        }
        .stButton>button:hover {
            background-color: #2980b9;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- LEGAL DATABASE ---
contract_clauses = {
    "scope_of_work": (
        "1. SCOPE OF WORK & DELIVERABLES\n"
        "The Provider agrees to perform the following services ('Services') for the Client:\n\n"
        "[SCOPE_DETAILS]\n\n"
        "Any request by the Client for alterations or tasks not listed above shall be considered 'Scope Creep' "
        "and will require a written 'Change Order' with additional compensation."
    ),
    "payment_terms": (
        "2. PAYMENT TERMS & STATUTORY INTEREST (MSME ACT)\n"
        "In consideration for the Services, the Client agrees to pay the Provider the Total Project Fee of [PROJECT_COST]. "
        "Execution of this Agreement is contingent upon a mandatory, non-refundable advance payment of [ADVANCE_PERCENT]% of the Total Project Fee. "
        "Services shall commence strictly upon realization of this advance.\n\n"
        "STATUTORY NOTICE: Pursuant to the Micro, Small and Medium Enterprises Development Act, 2006 (MSMED Act), "
        "time is of the essence regarding payments. Any outstanding balance must be cleared within forty-five (45) days.\n\n"
        "In the event of a delay, the Client shall be liable to pay compound interest with monthly rests to the Provider "
        "at three times (3x) the bank rate notified by the Reserve Bank of India (Section 16, MSMED Act, 2006)."
    ),
    "intellectual_property": (
        "3. INTELLECTUAL PROPERTY RIGHTS & LIEN\n"
        "The transfer of Intellectual Property Rights (IPR), copyright, and ownership of all source files, designs, and assets "
        "is strictly conditional upon the full and final realization of the Total Project Fee. "
        "Until the final invoice is cleared, the Provider retains a 'General Lien' and full legal title over all deliverables."
    ),
    "cancellation_policy": (
        "4. TERMINATION & CANCELLATION\n"
        "In the event the Client cancels the project or becomes unresponsive for a period exceeding fourteen (14) days ('Ghosting'), "
        "this Agreement shall be deemed terminated. The Advance Payment shall be forfeited as a cancellation fee, "
        "and all rights to the work shall revert immediately to the Provider."
    )
}

# --- APP LOGIC ---

# Logo Display
if os.path.exists("logo.png"):
    st.image("logo.png", width=150)

st.title("Freelance Shield")
st.subheader("Generate watertight, MSME-protected contracts.")

# Sidebar Inputs
with st.sidebar:
    st.header("📝 Project Details")
    freelancer_name = st.text_input("Provider Name (You)", "Amit Kumar")
    client_name = st.text_input("Client Name", "Tech Solutions Pvt Ltd")
    
    # SCOPE OF WORK (NEW FEATURE)
    st.markdown("---")
    st.caption("👇 Define exactly what you are doing:")
    scope_work = st.text_area(
        "Scope of Work (List items)", 
        "1. Design 5 Social Media Posts\n2. Edit 1 Promotional Video (60s)\n3. Provide Source Files",
        height=150
    )
    
    st.markdown("---")
    project_cost = st.text_input("Total Project Fee", "Rs. 50,000")
    advance_percent = st.slider("Advance Required (%)", 0, 100, 50)
    hourly_rate = st.text_input("Overtime/Hourly Rate", "Rs. 2,000")
    
    st.markdown("---")
    st.caption("🔒 Privacy First: No data is saved.")

# Generate Button
if st.button("Generate Custom Contract", type="primary"):
    
    # 1. SANITIZE INPUTS
    safe_cost = project_cost.replace("₹", "Rs. ").strip()
    safe_rate = hourly_rate.replace("₹", "Rs. ").strip()
    # We sanitize scope input to prevent weird characters breaking PDF
    safe_scope = scope_work.replace("₹", "Rs. ") 
    
    # 2. BUILD THE HEADER
    full_contract_text = "FREELANCE SERVICE AGREEMENT\n"
    full_contract_text += f"Date: {datetime.date.today().strftime('%B %d, %Y')}\n\n"
    full_contract_text += "BETWEEN:\n"
    full_contract_text += f"PROVIDER: {freelancer_name}\n"
    full_contract_text += "AND\n"
    full_contract_text += f"CLIENT: {client_name}\n\n"
    full_contract_text += "-"*60 + "\n\n"
    
    # 3. BUILD THE CLAUSES
    for key, clause in contract_clauses.items():
        filled_clause = clause.replace("[CLIENT_NAME]", client_name)\
                              .replace("[FREELANCER_NAME]", freelancer_name)\
                              .replace("[PROJECT_COST]", safe_cost)\
                              .replace("[ADVANCE_PERCENT]", str(advance_percent))\
                              .replace("[HOURLY_RATE]", safe_rate)\
                              .replace("[SCOPE_DETAILS]", safe_scope) # Injecting the scope
        full_contract_text += filled_clause + "\n\n"

    # 4. BUILD THE SIGNATURE BLOCK
    full_contract_text += "-"*60 + "\n"
    full_contract_text += "IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first above written.\n\n"
    full_contract_text += "SIGNED BY THE PROVIDER:\n\n"
    full_contract_text += "_________________________\n"
    full_contract_text += f"(Signature)\n{freelancer_name}\n\n"
    full_contract_text += "SIGNED BY THE CLIENT:\n\n"
    full_contract_text += "_________________________\n"
    full_contract_text += f"(Signature)\n{client_name}\n"

    # Show Preview
    with st.container():
        st.markdown("### 📄 Contract Preview")
        st.text_area("Copy text below:", full_contract_text, height=450)

    # PDF Generator
    pdf = FPDF()
    pdf.add_page()
    
    # Logo Logic
    if os.path.exists("logo.png"):
        try:
            pdf.image("logo.png", 10, 8, 25)
            pdf.ln(20)
        except:
            pass 
    
    pdf.set_font("Arial", size=11)
    
    try:
        clean_text = full_contract_text.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 6, clean_text)
        pdf_output = pdf.output(dest='S').encode('latin-1')
        
        st.download_button(
            label="⬇️ Download Signed PDF",
            data=pdf_output,
            file_name="Custom_Service_Agreement.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"PDF Generation Error: {e}")

    st.success("✅ Custom Contract Generated.")