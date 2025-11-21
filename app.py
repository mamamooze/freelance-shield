import streamlit as st
from fpdf import FPDF
import datetime
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Freelance Shield",
    page_icon="🛡️",
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

        /* Title text color (White to stand out on dark background) */
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

        /* Labels for inputs (Make them white) */
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
        "1. PAYMENT TERMS & STATUTORY INTEREST UNDER MSME ACT\n"
        "In consideration for the Services, [CLIENT_NAME] agrees to pay the Total Project Cost of [PROJECT_COST]. "
        "Execution of this Agreement requires a mandatory, non-refundable advance payment of [ADVANCE_PERCENT]% of the Total Project Cost. "
        "Work shall strictly commence only upon realization of this advance.\n\n"
        "Pursuant to the Micro, Small and Medium Enterprises Development Act, 2006 (MSMED Act), "
        "[CLIENT_NAME] acknowledges that time is of the essence regarding payments. "
        "Any outstanding balance must be cleared within the payment cycle agreed herein, which shall in no case exceed forty-five (45) days "
        "from the date of acceptance of the deliverable or deemed acceptance.\n\n"
        "NOTICE OF STATUTORY LIABILITY: In the event of a delay in payment beyond the stipulated 45-day period, [CLIENT_NAME] shall be "
        "liable to pay compound interest with monthly rests to [FREELANCER_NAME] on the amount due, at three times (3x) the bank rate notified by the Reserve Bank of India, "
        "as mandated by Section 16 of the MSMED Act, 2006. This statutory interest is mandatory and cannot be waived by contract."
    ),
    "scope_of_work": (
        "2. SCOPE OF WORK & CHANGE ORDERS\n"
        "The Professional Fee agreed upon covers strictly and exclusively the deliverables explicitly itemized in the 'Scope of Services' Annexure. "
        "Any request by [CLIENT_NAME] for alterations, additions, or modifications that deviate from the agreed Scope ("
        "'Scope Creep') shall not be performed unless a written 'Change Order' is executed.\n\n"
        "All work performed under a Change Order shall be billed additionally at the rate of [HOURLY_RATE] per hour. "
        "[FREELANCER_NAME] reserves the absolute right to suspend work if [CLIENT_NAME] insists on additional tasks without approving the corresponding financial compensation. "
        "Silence or acquiescence by [FREELANCER_NAME] regarding minor changes shall not constitute a waiver of this clause for future deviations."
    ),
    "intellectual_property": (
        "3. INTELLECTUAL PROPERTY RIGHTS & GENERAL LIEN\n"
        "Notwithstanding anything to the contrary, the transfer of Intellectual Property Rights (IPR), copyright, and ownership of all source files, "
        "designs, code, and assets created by [FREELANCER_NAME] is strictly conditional upon the full and final realization of the Total Project Cost. "
        "Until the final invoice is cleared in full, [FREELANCER_NAME] retains a 'General Lien' and full legal title over all deliverables.\n\n"
        "WARNING: Any use, reproduction, modification, or deployment of the work product by [CLIENT_NAME] prior to full payment constitutes "
        "an unauthorized use and a direct infringement of [FREELANCER_NAME]'s rights under the Copyright Act, 1957. "
        "[FREELANCER_NAME] reserves the right to issue a DMCA takedown notice or pursue injunctive relief for such unauthorized use without further notice."
    ),
    "cancellation_policy": (
        "4. CANCELLATION & TERMINATION FOR INACTION ('GHOSTING')\n"
        "In the event [CLIENT_NAME] unilaterally cancels the project for any reason, or renders the project impossible to complete due to lack of feedback, "
        "provision of assets, or unresponsiveness for a continuous period exceeding fourteen (14) days ('Ghosting'), this Agreement shall be deemed terminated by [CLIENT_NAME]'s default.\n\n"
        "Upon such termination:\n"
        "(a) The [ADVANCE_PERCENT]% advance payment shall be forfeited in its entirety as a cancellation fee to cover booking costs and opportunity cost;\n"
        "(b) [CLIENT_NAME] shall immediately pay for all additional work completed beyond the advance coverage up to the date of termination; and\n"
        "(c) All rights to the work done shall revert immediately to [FREELANCER_NAME]. [CLIENT_NAME] shall have no right to use any preliminary drafts or incomplete work."
    )
}

# --- APP LAYOUT ---

# Logo Check & Display
logo_path = "logo.png"
if os.path.exists(logo_path):
    st.image(logo_path, width=150) # Adjust width as needed

st.title("Freelance Shield")
st.subheader("Generate watertight, MSME-protected contracts in seconds.")

# Sidebar Inputs
with st.sidebar:
    st.header("📝 Project Details")
    freelancer_name = st.text_input("Your Name (Freelancer)", "Amit Kumar")
    client_name = st.text_input("Client Name/Company", "Tech Solutions Pvt Ltd")
    project_cost = st.text_input("Total Project Fee (INR)", "₹50,000")
    advance_percent = st.slider("Advance Required (%)", min_value=0, max_value=100, value=50)
    hourly_rate = st.text_input("Hourly Rate for Extra Work", "₹2,000")
    st.markdown("---")
    st.write("🔒 *Your data is not stored.*")

# Generate Button
if st.button("Generate Contract Now", type="primary"):
    # Assemble the text
    full_contract_text = f"FREELANCE SERVICE AGREEMENT\nDate: {datetime.date.today()}\n\n"
    full_contract_text += f"BETWEEN: {freelancer_name} (The Provider) AND {client_name} (The Client)\n\n"
    
    for key, clause in contract_clauses.items():
        # Replace placeholders with user inputs
        filled_clause = clause.replace("[CLIENT_NAME]", client_name)\
                              .replace("[FREELANCER_NAME]", freelancer_name)\
                              .replace("[PROJECT_COST]", project_cost)\
                              .replace("[ADVANCE_PERCENT]", str(advance_percent))\
                              .replace("[HOURLY_RATE]", hourly_rate)
        full_contract_text += filled_clause + "\n\n"

    # Show on screen with a nice container
    with st.container():
        st.markdown("### 📄 Contract Preview")
        st.text_area("Preview", full_contract_text, height=400, label_visibility="collapsed")

    # PDF Generator
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Clean text for PDF
    clean_text = full_contract_text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, clean_text)
    
    pdf_output = pdf.output(dest='S').encode('latin-1')
    
    st.download_button(
        label="⬇️ Download PDF Contract",
        data=pdf_output,
        file_name="Freelance_Shield_Contract.pdf",
        mime="application/pdf"
    )
    
    st.success("✅ Contract generated! You are now protected by the MSME Act.")