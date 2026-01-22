import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import io
import os
from groq import Groq

# --- WEB PAGE CONFIGURATION ---
st.set_page_config(page_title="AI Research Summarizer", layout="wide")
st.title("🔬 Research-AI-Summarizer")

# --- API SECRET LOGIC ---
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Groq API Key", type="password")


# --- THIS IS THE FUNCTION YOU WERE LOOKING FOR ---
def ai_process(text, key):
    """Processes text using the NEW Llama 3.1 model."""
    client = Groq(api_key=key)
    # Using the updated model name here
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": f"Summarize this research: {text[:10000]}"}]
    )
    return completion.choices[0].message.content


# --- INTERFACE ---
uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files and api_key:
    if st.button("🚀 Start Analysis"):
        all_summaries = []
        all_text = ""

        for file in uploaded_files:
            # Extract text
            pdf_stream = io.BytesIO(file.read())
            doc = fitz.open(stream=pdf_stream, filetype="pdf")
            text = "".join([page.get_text() for page in doc[:5]])  # First 5 pages
            all_text += text

            # Get AI Summary
            summary = ai_process(text, api_key)
            all_summaries.append({"File": file.name, "Summary": summary})
            st.write(f"✅ Processed {file.name}")

        # Show Results
        st.divider()
        st.subheader("Summary Table")
        st.dataframe(pd.DataFrame(all_summaries))

        st.subheader("Research Word Cloud")
        wc = WordCloud(background_color='white').generate(all_text)
        fig, ax = plt.subplots()
        ax.imshow(wc)
        ax.axis('off')
        st.pyplot(fig)