import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import io
import os
from groq import Groq  # For online AI processing

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI Research Summarizer", layout="wide")
st.title("🔬 Research-AI-Summarizer Web")

# --- SIDEBAR: API CONFIG ---
with st.sidebar:
    st.header("Settings")
    # Users provide their own key online, or you can set it in Streamlit Secrets
    api_key = st.text_input("Enter Groq API Key", type="password")
    st.info("Get a free key at console.groq.com")


# --- FUNCTIONS ---
def extract_text_from_pdf(uploaded_file):
    """Extracts text from an uploaded PDF stream."""
    text = ""
    pdf_stream = io.BytesIO(uploaded_file.read())
    with fitz.open(stream=pdf_stream, filetype="pdf") as doc:
        # Extract first 12 and last 5 pages for context
        target_pages = list(range(min(12, len(doc)))) + list(range(max(0, len(doc) - 5), len(doc)))
        for p in sorted(set(target_pages)):
            text += doc[p].get_text()
    return text


def ai_process_cloud(text, key):
    """Processes text using Groq Cloud API (Llama 3)."""
    client = Groq(api_key=key)
    prompt = f"Summarize this research paper. Identify: 1. METHOD_TYPE 2. KEY_AUTHORS 3. RESEARCH GAP. \n\nText: {text[:8000]}"
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content


# --- MAIN APP LOGIC ---
uploaded_files = st.file_uploader("Upload your Research Papers (PDF)", type="pdf", accept_multiple_files=True)

if uploaded_files:
    if st.button("🚀 Run Analysis"):
        if not api_key:
            st.error("Please enter an API Key to start.")
        else:
            all_summaries = []
            combined_text = ""

            progress_bar = st.progress(0)
            for i, file in enumerate(uploaded_files):
                st.write(f"Processing {file.name}...")
                text = extract_text_from_pdf(file)
                combined_text += text

                # AI Summary
                summary = ai_process_cloud(text, api_key)
                all_summaries.append({"Filename": file.name, "Summary": summary})
                progress_bar.progress((i + 1) / len(uploaded_files))

            # --- DISPLAY VISUALS ---
            st.divider()
            st.subheader("📊 Research Visualizations")

            col1, col2 = st.columns(2)
            with col1:
                wc = WordCloud(width=800, height=400, background_color='white').generate(combined_text)
                fig, ax = plt.subplots()
                ax.imshow(wc)
                ax.axis('off')
                st.pyplot(fig)  # Correct way to show plots in Streamlit

            with col2:
                df = pd.DataFrame(all_summaries)
                st.dataframe(df)

            # --- DOWNLOAD RESULTS ---
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Analysis (CSV)",
                data=csv,
                file_name="Research_Results.csv",
                mime="text/csv"
            )  #