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

## 📦 Packaged Usage (v1)
This first version assumes a fixed repository structure. A user can install the package, run the knowledge-graph aggregator in a cloned repo, and produce a KMDS knowledge graph.

### Required folders in the cloned repo
- `documents/`
- `notebooks/`
- `data_dictionary/`
- `output/`

### Expected helper output artifacts
At least one of these files should exist in `output/`:
- `full_service_report.json`
- `kmds_summary.json`
- `kmds_strategic_summary.json`

### Install
From the project root:
```bash
pip install -e .
```

### Generate knowledge graph from helper outputs
```bash
kmds-kb --workspace . --project-file project_knowledge_graph.xml --mode auto
```

The command validates the required folders, ingests the helper output artifacts, and writes:
- `project_knowledge_graph.xml`

### Adapter command (direct use)
You can also run the output adapter directly for a single file:
```bash
kmds-analyze --input output/full_service_report.json --project-file project_knowledge_graph.xml --create-project --workflow-name kmds_project_workflow --mode auto
```

### Backward-compatible template script
If you are using the template script path, this remains supported:
```bash
python kb_aggregator.py --workspace . --project-file project_knowledge_graph.xml --mode auto
```

### Common failure messages
- Missing folder(s): one or more required directories are absent.
- No helper output files found: none of the expected JSON artifacts are present in `output/`.
- Project file already exists in create mode: rerun with update mode or choose a new target path.

---
