import streamlit as st
from fpdf import FPDF
import datetime
import os

# --- 1. SETUP & FAVICON (Browser Tab Logo) ---
# We check if logo.png exists. If yes, we use it as the favicon.
# If not, we fallback to the shield emoji.
icon_path = "logo.png"
page_icon = icon_path if os.path.exists(icon_path) else "🛡️"

st.set_page_config(
    page_title="Freelance Shield",
    page_icon=page_icon,  # <--- THIS SETS THE BROWSER TAB LOGO
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

        /* Title text color */
        h1 {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: #ffffff;
            font-weight: 700;
            text-shadow: 0px 2px 4px rgba(0,0,0,0.5);
        }

        /* Subheader text color */
        .stSubheader {
            color: #dcdcdc;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }

        /* Labels for inputs */
        .stTextInput label, .stNumberInput label, .stSlider label {
            color: #ffffff !important;
        }
        
        /* Input field styling */
        .stTextInput>div>div>input {
            background-color: rgba(255, 255, 255, 0.9);
            color: #000;
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
    "payment_terms": (
        "1. PAYMENT TERMS & STATUTORY INTEREST (MSME ACT)\n"
        "In consideration for the Services, the Client agrees to pay the Provider the Total Project Fee of [PROJECT_COST]. "
        "Execution of this Agreement is contingent upon a mandatory, non-refundable advance payment of [ADVANCE_PERCENT]% of the Total Project Fee. "
        "Services shall commence strictly upon realization of this advance.\n\n"
        "STATUTORY NOTICE: Pursuant to the Micro, Small and Medium Enterprises Development Act, 2006 (MSMED Act), "
        "time is of the essence regarding payments. Any outstanding balance must be cleared within the agreed payment cycle, "
        "which shall not exceed forty-five (45) days from the date of acceptance.\n\n"
        "In the event of a delay beyond this period, the Client shall be liable to pay compound interest with monthly rests to the Provider "
        "on the amount due, at three times (3x) the bank rate notified by the Reserve Bank of India (Section 16, MSMED Act, 2006)."
    ),
    "scope_of_work": (
        "2. SCOPE OF WORK & CHANGE ORDERS\n"
        "The Professional Fee covers strictly the deliverables explicitly itemized in the Project Brief. "
        "Any request by the Client for alterations, additions, or modifications that deviate from the agreed Scope ('Scope Creep') "
        "shall requires a written 'Change Order'.\n\n"
        "Additional work shall be billed at the rate of [HOURLY_RATE] per hour. "
        "The Provider reserves the right to suspend work if additional tasks are insisted upon without corresponding financial compensation."
    ),
    "intellectual_property": (
        "3. INTELLECTUAL PROPERTY RIGHTS & LIEN\n"
        "The transfer of Intellectual Property Rights (IPR), copyright, and ownership of all source files, designs, and assets "
        "is strictly conditional upon the full and final realization of the Total Project Fee. "
        "Until the final invoice is cleared, the Provider retains a 'General Lien' and full legal title over all deliverables.\n\n"
        "Usage of the work product prior to full payment constitutes an unauthorized use and infringement of rights under the Copyright Act, 1957."
    ),
    "cancellation_policy": (
        "4. TERMINATION & CANCELLATION\n"
        "In the event the Client cancels the project or becomes unresponsive for a period exceeding fourteen (14) days ('Ghosting'), "
        "this Agreement shall be deemed terminated by the Client's default.\n\n"
        "Upon such termination: (a) The Advance Payment shall be forfeited as a cancellation fee; "
        "(b) The Client shall pay for all work completed beyond the advance coverage; and "
        "(c) All rights to the work shall revert immediately to the Provider."
    )
}

# --- APP LOGIC ---

# Website Logo Display
if os.path.exists("logo.png"):
    st.image("logo.png", width=150)

st.title("Freelance Shield")
st.subheader("Generate watertight, MSME-protected contracts.")

# Sidebar Inputs
with st.sidebar:
    st.header("📝 Agreement Details")
    freelancer_name = st.text_input("Provider Name (You)", "Amit Kumar")
    client_name = st.text_input("Client Name", "Tech Solutions Pvt Ltd")
    project_cost = st.text_input("Total Project Fee", "Rs. 50,000")
    advance_percent = st.slider("Advance Required (%)", 0, 100, 50)
    hourly_rate = st.text_input("Overtime/Hourly Rate", "Rs. 2,000")
    st.markdown("---")
    st.caption("🔒 Privacy First: No data is saved.")

# Generate Button
if st.button("Generate Professional Contract", type="primary"):
    
    # 1. SANITIZE INPUTS
    safe_cost = project_cost.replace("₹", "Rs. ").strip()
    safe_rate = hourly_rate.replace("₹", "Rs. ").strip()
    
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
                              .replace("[HOURLY_RATE]", safe_rate)
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

    # PDF Generator logic
    pdf = FPDF()
    pdf.add_page()
    
    # --- LOGO IN PDF LOGIC ---
    # This puts the logo in the top-left corner of the PDF
    if os.path.exists("logo.png"):
        # Arguments: Name, X position, Y position, Width
        try:
            pdf.image("logo.png", 10, 8, 25)
            pdf.ln(20) # Move cursor down so text doesn't overlap logo
        except:
            pass # If logo fails, just keep generating text
    
    pdf.set_font("Arial", size=11)
    
    # Fix encoding for PDF
    try:
        clean_text = full_contract_text.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 6, clean_text)
        pdf_output = pdf.output(dest='S').encode('latin-1')
        
        st.download_button(
            label="⬇️ Download Signed PDF",
            data=pdf_output,
            file_name="Professional_Service_Agreement.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"PDF Generation Error: {e}")

    st.success("✅ Professional Contract Generated.")