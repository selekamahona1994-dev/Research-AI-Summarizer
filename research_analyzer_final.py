import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import io

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI Research Summarizer", layout="wide")
st.title("🔬 Research-AI-Summarizer Web")
st.write("Upload your academic PDFs to identify research gaps and generate a synthesis.")

# --- SIDEBAR: API CONFIG ---
with st.sidebar:
    st.header("Settings")
    # For online use, users will need to provide an API key (e.g., Groq is free and fast)
    api_key = st.text_input("Enter your Groq/OpenAI API Key", type="password")
    st.info("Online hosting doesn't support local Ollama. Please use a Cloud API key.")

# --- UPLOAD COMPONENT ---
uploaded_files = st.file_uploader("Upload up to 10 Research Papers (PDF)", type="pdf", accept_multiple_files=True)

if uploaded_files:
    all_summaries = []
    all_methods = []
    all_cited_authors = []
    combined_text = ""
    gaps_collected = ""

    if st.button("🚀 Start AI Analysis"):
        if not api_key:
            st.error("Please enter an API Key in the sidebar to proceed.")
        else:
            progress_bar = st.progress(0)

            for i, uploaded_file in enumerate(uploaded_files[:10]):
                # 1. Extract Text from Uploaded PDF
                pdf_data = uploaded_file.read()
                doc = fitz.open(stream=pdf_data, filetype="pdf")
                text = ""
                # Get first 12 and last 5 pages
                target_pages = list(range(min(12, len(doc)))) + list(range(max(0, len(doc) - 5), len(doc)))
                for p in sorted(set(target_pages)):
                    text += doc[p].get_text()

                combined_text += text

                # 2. Simulated AI Process (Placeholders for Cloud API call)
                # In a real deployment, you would replace 'ollama.generate' with an API request
                st.write(f"Analyzing: {uploaded_file.name}...")

                # Placeholder for summary logic
                summary = f"SUMMARY for {uploaded_file.name}: METHOD_TYPE: Qualitative KEY_AUTHORS: Smith, Doe RESEARCH GAP: Needs more data."
                all_summaries.append({"Filename": uploaded_file.name, "Full Summary": summary})

                # Update Progress
                progress_bar.progress((i + 1) / len(uploaded_files))

            st.success("✅ Analysis Complete!")

            # --- VISUALS SECTION ---
            st.divider()
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🎨 Research Word Cloud")
                wc = WordCloud(width=800, height=400, background_color='white').generate(combined_text)
                fig, ax = plt.subplots()
                ax.imshow(wc)
                ax.axis('off')
                st.pyplot(fig)

            with col2:
                st.subheader("🥧 Methodology Distribution")
                # Example chart logic
                counts = {"Qualitative": 3, "Quantitative": 5, "Mixed": 2}
                fig2, ax2 = plt.subplots()
                ax2.pie(counts.values(), labels=counts.keys(), autopct='%1.1f%%')
                st.pyplot(fig2)

            # --- EXCEL DOWNLOAD ---
            df = pd.DataFrame(all_summaries)
            st.download_button(
                label="📥 Download Research Analysis (Excel)",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name="Research_Analysis.csv",
                mime="text/csv"
            )