import os
import fitz  # PyMuPDF
import ollama
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter

# --- PATH LOGIC ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "papers")
OUTPUT_EXCEL = os.path.join(BASE_DIR, "Research_Analysis.xlsx")
OUTPUT_SOLUTION = os.path.join(BASE_DIR, "Unified_Solution.txt")
OUTPUT_WC = os.path.join(BASE_DIR, "Research_WordCloud.png")
OUTPUT_CHART = os.path.join(BASE_DIR, "Top_Citations.png")
OUTPUT_PIE = os.path.join(BASE_DIR, "Methodology_Distribution.png")


def extract_content(pdf_path):
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            # Sampling the paper for AI analysis
            target_pages = list(range(min(12, len(doc)))) + list(range(max(0, len(doc) - 5), len(doc)))
            for p in sorted(set(target_pages)):
                text += doc[p].get_text()
    except Exception as e:
        return f"Error: {e}"
    return text


def ai_process(text):
    prompt = f"""
    Analyze this research paper and provide a summary with these headers:
    TITLE, ABSTRACT, TOC, INTRODUCTION, LITERATURE REVIEW, DESIGN/METHODOLOGY, 
    IMPLICATION, REFERENCE LIST, SCHEDULE/BUDGET, RESEARCH GAP.

    CRITICAL CLASSIFICATION (Choose ONE for each):
    METHOD_TYPE: [Qualitative, Quantitative, Mixed-Methods, or Review]
    KEY_AUTHORS: [List top 5 cited authors/papers, separated by commas]

    TEXT: {text[:15000]}
    """
    response = ollama.generate(model='llama3', prompt=prompt)
    return response['response']


def generate_pie_chart(methods):
    print("🥧 Generating Methodology Pie Chart...")
    counts = Counter(methods)
    labels = counts.keys()
    sizes = counts.values()

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99'])
    ax.set_title('Distribution of Research Methodologies')
    plt.savefig(OUTPUT_PIE)
    plt.close()


def generate_citation_chart(author_list):
    print("📊 Generating Citation Bar Chart...")
    counts = Counter(author_list).most_common(10)
    if not counts: return
    authors, frequencies = zip(*counts)
    plt.figure(figsize=(12, 6))
    plt.bar(authors, frequencies, color='skyblue')
    plt.xticks(rotation=45, ha='right')
    plt.title('Top 10 Cited Authors/Papers')
    plt.savefig(OUTPUT_CHART)
    plt.close()


def generate_wordcloud(combined_text):
    print("🎨 Generating Word Cloud...")
    wc = WordCloud(width=1200, height=600, background_color='white').generate(combined_text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.savefig(OUTPUT_WC)
    plt.close()


def main():
    if not os.path.exists(INPUT_DIR):
        os.makedirs(INPUT_DIR)
        print(f"Put PDFs in: {INPUT_DIR}");
        return

    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.pdf')]
    if not files:
        print("Folder is empty.");
        return

    all_summaries, all_cited_authors, all_methods = [], [], []
    gaps_collected, all_text_for_wc = "", ""

    print(f"🚀 Analyzing {len(files[:10])} papers...")

    for file in files[:10]:
        print(f"Processing: {file}")
        path = os.path.join(INPUT_DIR, file)
        text = extract_content(path)
        all_text_for_wc += text

        summary = ai_process(text)
        all_summaries.append({"Filename": file, "Full Summary": summary})

        # Extract Methodology for Pie Chart
        if "METHOD_TYPE:" in summary:
            method = summary.split("METHOD_TYPE:")[-1].split("\n")[0].strip()
            all_methods.append(method)

        # Extract Authors for Bar Chart
        if "KEY_AUTHORS:" in summary:
            names = [n.strip() for n in summary.split("KEY_AUTHORS:")[-1].split("\n")[0].split(",") if
                     len(n.strip()) > 2]
            all_cited_authors.extend(names)

        if "GAP" in summary.upper():
            gaps_collected += f"\nGap from {file}: " + summary.upper().split("GAP")[-1]

    # Generate all visuals
    generate_wordcloud(all_text_for_wc)
    generate_citation_chart(all_cited_authors)
    generate_pie_chart(all_methods)

    # Final Synthesis
    print("🧠 Creating Unified Solution...")
    sol_prompt = f"Propose one research project that solves all these gaps: {gaps_collected}"
    final_sol = ollama.generate(model='llama3', prompt=sol_prompt)

    pd.DataFrame(all_summaries).to_excel(OUTPUT_EXCEL, index=False)
    with open(OUTPUT_SOLUTION, "w", encoding="utf-8") as f:
        f.write(final_sol['response'])

    print(f"\n✅ COMPLETE! Check your folder for Excel, WordCloud, BarChart, and PieChart.")


if __name__ == "__main__":
    main()