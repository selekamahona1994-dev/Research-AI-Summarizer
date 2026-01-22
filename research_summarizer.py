import os
import fitz  # PyMuPDF
import ollama
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# --- PATH LOGIC ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "papers")
OUTPUT_EXCEL = os.path.join(BASE_DIR, "Research_Analysis.xlsx")
OUTPUT_SOLUTION = os.path.join(BASE_DIR, "Unified_Solution.txt")
OUTPUT_IMAGE = os.path.join(BASE_DIR, "Research_WordCloud.png")


def extract_content(pdf_path):
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            target_pages = list(range(min(12, len(doc)))) + list(range(max(0, len(doc) - 5), len(doc)))
            for p in sorted(set(target_pages)):
                text += doc[p].get_text()
    except Exception as e:
        return f"Error: {e}"
    return text


def ai_process(text):
    prompt = f"""
    Summarize this research paper strictly using these headers:
    TITLE, ABSTRACT, TOC, INTRODUCTION, LITERATURE REVIEW, DESIGN/METHODOLOGY, 
    IMPLICATION, REFERENCES, SCHEDULE/BUDGET, RESEARCH GAP.

    TEXT: {text[:15000]}
    """
    response = ollama.generate(model='llama3', prompt=prompt)
    return response['response']


def generate_visuals(combined_text):
    """Creates and saves a Word Cloud of the research themes."""
    print("🎨 Generating Research Word Cloud...")
    wordcloud = WordCloud(
        width=1600,
        height=800,
        background_color='white',
        colormap='viridis',
        max_words=100
    ).generate(combined_text)

    plt.figure(figsize=(20, 10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.tight_layout(padding=0)
    plt.savefig(OUTPUT_IMAGE)
    plt.close()


def main():
    if not os.path.exists(INPUT_DIR):
        os.makedirs(INPUT_DIR)
        print(f"Folder created. Add PDFs to: {INPUT_DIR}")
        return

    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.pdf')]
    if not files:
        print("Please paste your PDFs into the 'papers' folder.")
        return

    all_summaries = []
    gaps_collected = ""
    full_corpus = ""  # This will hold text for the word cloud

    print(f"🚀 Processing {len(files[:10])} papers...")

    for file in files[:10]:
        print(f"Reading: {file}")
        path = os.path.join(INPUT_DIR, file)
        text = extract_content(path)
        full_corpus += text  # Accumulate text for visual

        summary = ai_process(text)
        all_summaries.append({"Filename": file, "Full Summary": summary})

        if "GAP" in summary.upper():
            gaps_collected += f"\nGap from {file}: " + summary.upper().split("GAP")[-1]

    # 1. Generate Word Cloud
    generate_visuals(full_corpus)

    # 2. Unified Solution
    print("🧠 Synthesizing Unified Research Solution...")
    sol_prompt = f"Propose one master research project that solves all these gaps: {gaps_collected}"
    final_sol = ollama.generate(model='llama3', prompt=sol_prompt)

    # 3. Save Files
    pd.DataFrame(all_summaries).to_excel(OUTPUT_EXCEL, index=False)
    with open(OUTPUT_SOLUTION, "w", encoding="utf-8") as f:
        f.write(final_sol['response'])

    print(f"\n✅ SUCCESS!")
    print(f"Excel Report: {OUTPUT_EXCEL}")
    print(f"Word Cloud Image: {OUTPUT_IMAGE}")
    print(f"Unified Solution: {OUTPUT_SOLUTION}")


if __name__ == "__main__":
    main()