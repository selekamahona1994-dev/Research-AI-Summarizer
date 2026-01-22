import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
from groq import Groq
import io

# --- PAGE SETUP ---
st.set_page_config(page_title="Academic Research Architect", layout="wide")
st.title("🔬 10-Paper Research Synthesizer")
st.markdown("### Upload up to 10 Research Papers (PDF only)")

# --- API SETUP ---
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Groq API Key", type="password")


# --- VALIDATION LOGIC ---
def is_actually_research(text, filename, key):
    """A strict multi-step check to block CVs and non-research files."""

    # Step 1: Quick Keyword Check (The 'Red Flag' Test)
    text_lower = text.lower()
    research_keywords = ["abstract", "introduction", "methodology", "references", "conclusion", "results"]
    cv_keywords = ["experience", "skills", "hobbies", "curriculum vitae", "work history", "objective"]

    # Count how many research words vs CV words
    research_score = sum(1 for word in research_keywords if word in text_lower)
    cv_score = sum(1 for word in cv_keywords if word in text_lower)

    if cv_score > research_score:
        return False, "This looks like a CV or Resume."
    if research_score < 2:
        return False, "This does not contain standard research sections (Abstract, Intro, etc.)."

    # Step 2: Strict AI Confirmation
    client = Groq(api_key=key)
    prompt = f"""
    SYSTEM: You are a document classifier. Your job is to detect if a file is a formal ACADEMIC RESEARCH PAPER.
    REJECT: CVs, Resumes, Cover Letters, Invoices, and Books.
    TEXT SAMPLE: {text[:2000]}

    Is this a formal Research Paper? Answer only 'TRUE' or 'FALSE'.
    """
    chat = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0  # Makes it very strict
    )
    answer = chat.choices[0].message.content.strip().upper()

    if "TRUE" in answer:
        return True, "Valid Research Paper"
    return False, "AI classified this as a non-research document."


# --- ANALYSIS LOGIC ---
def analyze_paper(text, filename, key):
    client = Groq(api_key=key)
    prompt = f"""
    Extract ONLY from this research paper ({filename}):
    - TITLE & ABSTRACT
    - TOC, INTRO, LIT REVIEW
    - DESIGN & METHODOLOGY
    - IMPLICATIONS & CONTRIBUTION
    - REFERENCE LIST
    - SCHEDULE & BUDGET (If present)
    - RESEARCH GAP (Crucial)

    PAPER TEXT: {text[:15000]} 
    """
    chat = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return chat.choices[0].message.content


# --- USER INTERFACE ---
uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files and api_key:
    if st.button("🚀 Process Papers"):
        summaries = []
        gaps = ""

        for file in uploaded_files:
            pdf_bytes = io.BytesIO(file.read())
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            full_text = "".join([page.get_text() for page in doc[:10]])

            # THE NEW VALIDATION STEP
            is_valid, reason = is_actually_research(full_text, file.name, api_key)

            if is_valid:
                st.info(f"✅ Analyzing: {file.name}")
                summary = analyze_paper(full_text, file.name, api_key)
                summaries.append({"File": file.name, "Analysis": summary})
                gaps += f"\nGaps from {file.name}:\n{summary}\n"
            else:
                st.error(f"❌ Rejected {file.name}: {reason}")

        if summaries:
            st.divider()
            st.header("Individual Analyses")
            for s in summaries:
                with st.expander(f"View {s['File']}"):
                    st.markdown(s['Analysis'])