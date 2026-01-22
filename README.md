# 📚 Multi-Paper Research AI Analyzer
An automated pipeline to summarize 10 academic papers using local AI (Ollama/Llama3). 

## 🧠 AI Logic: How it works
This app uses **Natural Language Processing (NLP)** to scan specific "semantic anchors" in research papers:
- **Research Gaps**: It identifies phrases like *"future research should..."*, *"limitations include..."*, and *"this area remains unexplored."*
- **Methodology**: It classifies papers into Qualitative, Quantitative, or Mixed-Methods based on keywords like *"p-value"*, *"ethnography"*, or *"thematic analysis."*

## 🛠️ Requirements
1. **Ollama**: Installed and running `llama3`.
2. **Anaconda**: Environment with Python 3.10+.
3. **Libraries**: `pip install -r requirements.txt`

## 📊 Outputs Generated
- `Research_Analysis.xlsx`: Full tabular summary.
- `Methodology_Distribution.png`: Pie chart of research types.
- `Top_Citations.png`: Bar chart of influential authors.
- `Unified_Solution.txt`: An AI-generated abstract and project proposal bridging all 10 papers.