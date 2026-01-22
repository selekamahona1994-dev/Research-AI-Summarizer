import streamlit as st
import fitz  # PyMuPDF
from groq import Groq
import gspread
from google.oauth2.service_account import Credentials
import io
import pandas as pd
from datetime import datetime


# --- DATABASE CONNECTION (FETCH & SAVE) ---
def get_gspread_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # Fix for private key newline formatting
    secret_info = dict(st.secrets["gcp_service_account"])
    secret_info["private_key"] = secret_info["private_key"].replace("\\n", "\n")

    creds = Credentials.from_service_account_info(secret_info, scopes=scopes)
    return gspread.authorize(creds)


def save_to_database(project_title, solution, count):
    try:
        client = get_gspread_client()
        sheet = client.open_by_key(st.secrets["general"]["spreadsheet_id"]).sheet1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([timestamp, project_title, solution, count])
        return True
    except Exception as e:
        st.error(f"Save Error: {e}")
        return False


def load_dashboard_data():
    try:
        client = get_gspread_client()
        sheet = client.open_by_key(st.secrets["general"]["spreadsheet_id"]).sheet1
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Dashboard Load Error: {e}")
        return pd.DataFrame()


# --- AI CORE LOGIC ---
def is_research_paper(text, key):
    client = Groq(api_key=key)
    prompt = f"Is this a RESEARCH PAPER? (Needs Abstract, Methodology, Refs). Reject CVs. Answer TRUE or FALSE. TEXT: {text[:2000]}"
    chat = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}],
                                          temperature=0)
    return "TRUE" in chat.choices[0].message.content.strip().upper()


def analyze_paper(text, filename, key):
    client = Groq(api_key=key)
    prompt = f"Analyze {filename}. Headers: Abstract, TOC, Intro, Methodology, Contribution, References, Budget, Gap. TEXT: {text[:14000]}"
    return client.chat.completions.create(model="llama-3.1-8b-instant",
                                          messages=[{"role": "user", "content": prompt}]).choices[0].message.content


def synthesize_solution(gaps, key):
    client = Groq(api_key=key)
    prompt = f"Synthesize these research gaps into one unified master solution: {gaps}"
    return client.chat.completions.create(model="llama-3.1-8b-instant",
                                          messages=[{"role": "user", "content": prompt}]).choices[0].message.content


# --- INTERFACE ---
st.set_page_config(page_title="Research Architect Pro", layout="wide")

# Create Tabs
tab1, tab2 = st.tabs(["🚀 New Analysis", "📊 Research Dashboard"])

# --- TAB 1: NEW ANALYSIS ---
with tab1:
    st.title("🔬 Research Synthesis Engine")

    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
    else:
        api_key = st.sidebar.text_input("Groq API Key", type="password")

    uploaded_files = st.file_uploader("Upload up to 10 Academic PDFs", type="pdf", accept_multiple_files=True)

    if uploaded_files and api_key:
        if st.button("🚀 Analyze & Save"):
            all_analyses = ""
            gaps_only = ""
            valid_count = 0

            progress = st.progress(0)
            for i, file in enumerate(uploaded_files):
                pdf_bytes = io.BytesIO(file.read())
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                text = "".join([page.get_text() for page in doc[:10]])

                if is_research_paper(text, api_key):
                    st.info(f"✅ Processing: {file.name}")
                    summary = analyze_paper(text, file.name, api_key)
                    all_analyses += f"\n--- {file.name} ---\n{summary}\n"
                    gaps_only += f"\nGap from {file.name}: {summary}\n"
                    valid_count += 1
                else:
                    st.error(f"❌ Rejected: {file.name} (Non-Research)")
                progress.progress((i + 1) / len(uploaded_files))

            if valid_count > 0:
                master_sol = synthesize_solution(gaps_only, api_key)
                st.success("Analysis Complete!")
                st.subheader("Unified Research Solution")
                st.write(master_sol)

                # Save to Google Sheets
                if save_to_database("Master Synthesis", master_sol, valid_count):
                    st.toast("Saved to Cloud Dashboard!")

# --- TAB 2: DASHBOARD ---
with tab2:
    st.header("📜 Past Research Projects")
    st.write("Data fetched from your permanent Google Sheet.")

    if st.button("🔄 Refresh Dashboard"):
        df = load_dashboard_data()
        if not df.empty:
            # Sort by newest first
            df = df.iloc[::-1]
            st.dataframe(df, use_container_width=True)

            # Allow downloading the whole history
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download History as CSV", csv, "research_history.csv", "text/csv")
        else:
            st.info("No research history found in your Google Sheet yet.")