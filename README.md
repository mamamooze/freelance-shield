# 🛡️ Freelance Shield Pro

**An Open-Source Legal Engine for Indian Freelancers**  
*Built with Python & Streamlit.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://freelance-shield.streamlit.app/)

## 🚀 The Mission
Indian freelancers often struggle with delayed payments, "scope creep," and lack of formal contracts. While laws like the **MSME Development Act, 2006** exist to protect them, legal counsel is often too expensive.

**Freelance Shield Pro** democratizes access to legal protection. It is a stateless, automated contract generator that codifies Indian Contract Law into a simple web interface.

## ⚖️ Legal Engineering
This is not a template filler. The app uses **Smart Clause Logic** to adapt contracts to industry risks:

- **MSME Protection:** Embeds Section 16 of the MSME Act (3x bank rate interest for late payments).
- **Anti-Ghosting Protocol:** Sets consequences for client unresponsiveness (>14 days).
- **Industry-Specific Logic:**
    - *Web Dev:* Adds "Bug Fix Warranty" clauses.
    - *Design:* Adds "Source File" IP retention clauses.
    - *Marketing:* Adds "No ROI Guarantee" liability caps.

## 🛠️ Tech Stack
- **Frontend:** Streamlit (Python)
- **Document Engine:** `python-docx` (Word) & `fpdf` (PDF)
- **Deployment:** Streamlit Community Cloud
- **Version Control:** Git & GitHub

## ⚡ How to Run Locally

1. **Clone the repository**
    ```
    git clone https://github.com/mamamooze/freelance-shield.git
    ```
2. **Install dependencies**
    ```
    pip install -r requirements.txt
    ```
3. **Run the app**
    ```
    streamlit run app.py
    ```

## 📄 License
Licensed under the [MIT License](LICENSE).

---

**Disclaimer:** _I am a law student, not a law firm. This tool generates templates for informational purposes and does not constitute legal advice._

---

**Suggestions and pull requests are welcome—let’s make freelance contracts safer together!**
