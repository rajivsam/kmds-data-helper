---

## KMDS Data Helper

A CLI tool that uses Ollama and DataProfiler to provide an intelligent, persona-based analysis of Data Science repositories. It reconciles documentation, raw data, and Jupyter notebooks to assess project health and technical readiness.

## 📂 The KMDS Standard Structure

To enable the full suite of LLM-based features, organize your cloned repository according to this structure:

```text
your-repo-name/
├── documents/       # PDFs (Specs/Papers) and .txt (Data Dictionaries)
├── data/            # Raw data samples (CSV, Parquet, etc.)
├── notebooks/       # Jupyter Notebooks (.ipynb) for analysis
└── kmds-helper      # The CLI tool (anchored to this root)
```

## 🧠 Integrated Personas

The tool analyzes your project through four distinct technical lenses:

1. The Architect (PDF Pass): Summarizes business intent and identifies key entities from technical documentation.
2. The Scientist (Data Pass): Profiles raw data and cross-references it against `.txt` descriptions in `/documents` to verify domain alignment.
3. The Engineer (Extraction Pass): Reconciles the "Physical Schema" of your data with the "Documented Schema" to generate a unified `kmds_output.csv`.
4. The Tech Lead (Dev Pass): Aggregates logic from all notebooks to identify technical debt, code redundancy, and deployment readiness.

## 🚀 Getting Started

## 1. Requirements

* Ollama: Running locally with your chosen model (default: `qwen2.5-coder:7b`).
* Python: 3.10+ managed via `uv` or `pip`.

## 2. Installation

```bash
# Clone and install dependencies
uv add nbformat pymupdf4llm dataprofiler ollama rich
```

## 3. Usage

Run the helper from the root of your target repository:

```bash
python main.py
```

## ⚠️ Important Guidelines

* Context Isolation: Keep human-readable descriptions (`.txt` files) in `/documents` and machine-readable evidence (`.csv` files) in `/data`.
* Guardrails: The engine automatically disables features if the corresponding directory is missing or empty.
* Advisory Nature: All assessments (Quality Scores, Readiness Ratings) are guidelines based on configurable LLM prompts and should be used as an expert peer-review tool, not an absolute metric.

---

Next Session: Implementing the `/output` isolation and prompt configuration.

---

Ready to stash this and head out? I’ve got the `kmds_dev_phase_v2` context saved and waiting for you!
