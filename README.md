# 🔬 Research-AI-Summarizer (v1.0)

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org)
[![Ollama](https://img.shields.io/badge/LLM-Llama3-orange.svg)](https://ollama.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An automated research intelligence suite that uses **Local LLMs (Llama 3)** to analyze batches of academic PDFs, identify research gaps, and propose unified solutions. This tool ensures 100% data privacy by processing everything on your local machine.

## 🚀 Key Accomplishments
- **Automated Extraction**: Successfully extracts text from complex PDF layouts using `PyMuPDF`.
- **Local AI Analysis**: Integrated with **Ollama** to summarize papers and detect "Research Gaps" without API costs.
- **Data Visualization**: Generates a **Research WordCloud**, a **Methodology Pie Chart**, and a **Citation Bar Chart**.
- **Synthesis Engine**: Cross-references multiple papers to generate a `Unified_Solution.txt` for new research proposals.
- **Academic Export**: Automatically builds a master Excel report (`Research_Summaries.xlsx`) of all findings.

## 📂 Project Structure
* `/papers/`: Drop your 10 academic PDFs here.
* `research_analyzer_final.py`: The main engine.
* `requirements.txt`: Environment dependencies.
* `_Wiki/`: Comprehensive documentation of findings and methodology.

## 🛠️ Setup & Usage
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt