import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
from groq import Groq
import io

# --- PAGE SETUP ---
st.set_page_config(page_title="Multi-Paper Research Architect", layout="wide")
st.title("🔬 10-Paper AI Research Summarizer & Synthesizer")
st.write("Upload up to 10 papers. The AI will analyze each and create a unified solution.")

# --- API SETUP ---
# This looks for the key in your Streamlit Cloud Secrets (or local .streamlit/secrets.toml)
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Groq API Key", type="password")


# --- AI LOGIC ---
def analyze_paper(text, filename, key):
    """Processes a single paper using the current Llama 3.1 model."""
    client = Groq(api_key=key)
    prompt = f"""
    Analyze the research paper: {filename}
    Extract and summarize the following sections clearly:
    - TITLE PAGE & ABSTRACT
    - TABLE OF CONTENT (TOC)
    - INTRODUCTION & LITERATURE REVIEW
    - RESEARCH DESIGN & METHODOLOGY
    - IMPLICATION & CONTRIBUTION TO KNOWLEDGE
    - REFERENCE LIST
    - RESEARCH SCHEDULE & BUDGET
    - RESEARCH GAP (Identify exactly what is missing or needed)

    PAPER TEXT: {text[:15000]} 
    """
    chat = client.chat.completions.create(
        model="llama-3.1-8b-instant",  # FIXED MODEL NAME
        messages=[{"role": "user", "content": prompt}]
    )
    return chat.choices[0].message.content


def synthesize_solution(all_gaps, key):
    """Combines all gaps into one unified solution."""
    client = Groq(api_key=key)
    prompt = f"""
    Below are the research gaps found in multiple papers:
    {all_gaps}

    TASK: Combine all these gaps and propose ONE unified research solution 
    that solves these problems at once. Provide a Title, Methodology, and Impact.
    """
    chat = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return chat.choices[0].message.content


# --- USER INTERFACE ---
uploaded_files = st.file_uploader("Upload up to 10 Research PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files and api_key:
    if len(uploaded_files) > 10:
        st.warning("Only the first 10 papers will be processed.")
        uploaded_files = uploaded_files[:10]

    if st.button("🚀 Analyze All & Synthesize Solution"):
        individual_summaries = []
        combined_gaps = ""

        progress_bar = st.progress(0)

        for i, file in enumerate(uploaded_files):
            st.info(f"Analyzing: {file.name}...")

            # Extract Text safely
            pdf_bytes = io.BytesIO(file.read())
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            # Get enough text to find budget and references
            text = "".join([page.get_text() for page in doc[:15]])

            # AI Analysis
            try:
                summary = analyze_paper(text, file.name, api_key)
                individual_summaries.append({"File": file.name, "Analysis": summary})
                combined_gaps += f"\n--- Gaps from {file.name} ---\n{summary}\n"
            except Exception as e:
                st.error(f"Error processing {file.name}: {e}")

            progress_bar.progress((i + 1) / len(uploaded_files))

        # --- DISPLAY RESULTS ---
        st.divider()
        st.header("🏁 Final Unified Research Solution")
        final_solution = synthesize_solution(combined_gaps, api_key)
        st.success(final_solution)

        st.divider()
        st.header("📑 Detailed Paper Summaries")
        for item in individual_summaries:
            with st.expander(f"View Analysis: {item['File']}"):
                st.markdown(item['Analysis'])

        # --- DOWNLOAD REPORT ---
        full_report = f"UNIFIED SOLUTION\n{final_solution}\n\n" + combined_gaps
        st.download_button("📥 Download Full Report", full_report, "Research_Report.txt")