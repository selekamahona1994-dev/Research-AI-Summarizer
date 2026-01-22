import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
from groq import Groq
import io

# --- PAGE SETUP ---
st.set_page_config(page_title="Academic Research Architect", layout="wide")
st.title("🔬 10-Paper Research Synthesizer")
st.markdown("### Upload up to 10 Research Papers to generate a Unified Solution")

# --- API SETUP ---
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Groq API Key", type="password")


# --- AI CORE FUNCTIONS ---
def validate_research_paper(text, key):
    """Checks if the document is actually a research paper."""
    client = Groq(api_key=key)
    prompt = f"Is the following text from a formal academic research paper? Answer only 'YES' or 'NO'. \n\nText: {text[:2000]}"
    chat = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return "YES" in chat.choices[0].message.content.upper()


def analyze_paper(text, filename, key):
    """Extracts the specific 10 sections requested."""
    client = Groq(api_key=key)
    prompt = f"""
    Analyze the research paper: {filename}
    You MUST extract and summarize these specific sections:
    1. TITLE PAGE & ABSTRACT
    2. TABLE OF CONTENT (TOC)
    3. INTRODUCTION & LITERATURE REVIEW
    4. DESIGN & METHODOLOGY
    5. IMPLICATION & CONTRIBUTION TO KNOWLEDGE
    6. REFERENCE LIST
    7. RESEARCH SCHEDULE & BUDGET
    8. RESEARCH GAP (What is missing?)

    TEXT: {text[:15000]} 
    """
    chat = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return chat.choices[0].message.content


def create_unified_solution(all_gaps, key):
    """The 'Master Step' - combines 10 gaps into 1 solution."""
    client = Groq(api_key=key)
    prompt = f"""
    You are a Lead Scientist. Below are research gaps from 10 different papers:
    {all_gaps}

    TASK: Propose ONE unified research project/solution that addresses the gaps of all 10 papers.
    Provide:
    - Unified Project Title
    - Combined Methodology
    - Expected Global Impact
    """
    chat = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return chat.choices[0].message.content


# --- USER INTERFACE ---
uploaded_files = st.file_uploader("Upload PDFs (Max 10)", type="pdf", accept_multiple_files=True)

if uploaded_files and api_key:
    if len(uploaded_files) > 10:
        st.error("Please limit your upload to 10 papers.")
    else:
        if st.button("🚀 Analyze & Synthesize"):
            summaries = []
            gaps_list = ""

            progress = st.progress(0)

            for i, file in enumerate(uploaded_files):
                # 1. Read PDF
                pdf_bytes = io.BytesIO(file.read())
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                full_text = "".join([page.get_text() for page in doc[:20]])  # Scan first 20 pages

                # 2. Validate
                if validate_research_paper(full_text, api_key):
                    st.info(f"Validating & Analyzing: {file.name}")
                    summary = analyze_paper(full_text, file.name, api_key)
                    summaries.append({"File": file.name, "Analysis": summary})
                    gaps_list += f"\nGap from {file.name}:\n{summary}\n"
                else:
                    st.warning(f"Skipped: {file.name} (Does not appear to be a research paper)")

                progress.progress((i + 1) / len(uploaded_files))

            # --- OUTPUTS ---
            if summaries:
                st.divider()
                st.header("🏁 Unified Research Solution")
                st.success(create_unified_solution(gaps_list, api_key))

                st.divider()
                st.header("📑 Individual Summaries")
                for item in summaries:
                    with st.expander(f"Analysis for {item['File']}"):
                        st.markdown(item['Analysis'])

                # Downloadable Report
                final_report = "RESEARCH SYNTHESIS REPORT\n\n" + gaps_list
                st.download_button("📥 Download Full Report", final_report, "Final_Research_Analysis.txt")