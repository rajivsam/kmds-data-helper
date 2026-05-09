---
# KMDS Data Helper: Repo Architect Framework

A modular, multi-persona framework for analyzing data science repositories. Uses local LLMs (via Ollama) to synthesize insights from documentation, data schemas, and Jupyter notebooks.

## 📂 Project Structure
KMDS-Helper follows a strict modular architecture to separate concerns:
- `src/kmds_data_helper/`: Core logic modules (Config, Processing, LLM, Engine).
- `documents/`: Project documentation (.pdf, .txt).
- `data/`: Physical data assets (CSVs) - isolated from output.
- `notebooks/`: Experimental code (.ipynb).
- `output/`: Isolated directory for generated reports.

## 🛠️ Installation & Setup
1. **Environment**: Ensure you are using the local virtual environment.
   ```bash
   source .venv/bin/activate
   ```
2. **LLM Engine**: Requires [Ollama](https://ollama.com) running locally with the `qwen2.5-coder:7b` model.
3. **Dependencies**:
   ```bash
   pip install rich ollama dataprofiler pymupdf4llm nbformat pyyaml
   ```

## ⚙️ Configuration
The framework is controlled by `kmds_config.yaml` in the root directory. You can toggle persona behaviors (Scientist, Tech Lead, Architect) and pathing without changing Python code.

## 🚀 Usage
Run the main orchestrator from the project root:
```bash
python3 main.py
```

---
