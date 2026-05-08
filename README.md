# KMDS Data Dictionary Helper (Backend Core)

An AI-powered engine designed to automate the creation of data dictionaries by reconciling business documentation (PDFs) with physical data schemas (CSVs).

This tool serves as a "Backend-First" proof of concept for integration into the [KMDS](https://github.com) ecosystem.

## 🚀 The Three-Phase Workflow

The helper executes a sequential, multi-persona analysis:

1. **The Architect Pass**: Summarizes the high-level business intent and entities from research papers or documentation.
2. **The Data Scientist Pass**: Uses `DataProfiler` to analyze the physical data quality, detecting modeling readiness and potential gaps.
3. **The Engineer Pass**: Performs deep field extraction, mapping cryptic CSV headers to human-readable definitions found in the text.

## 🛠️ Prerequisites

- **Ollama**: Must be running locally.
- **Model**: `qwen2.5-coder:7b` (run `ollama pull qwen2.5-coder:7b`)
- **Python**: 3.12+ managed via `uv`.

## 📦 Installation & Setup

1. **Sync Environment**:

   ```bash
   uv sync
   ```
2. **Install CLI Tool**:

   ```bash
   uv pip install -e .
   ```
3. **Stage Data**:

   - Place documentation PDFs in `data/pdfs/`
   - Place CSV/TXT samples in `data/samples/`

## ⌨️ Usage

Run the full end-to-end analysis via the CLI command:

```bash
kmds-helper
```

## 🏗️ Technical Architecture

- **Engine (`engine.py`)**: A standalone logic class that handles PDF-to-Markdown conversion (`PyMuPDF4LLM`), data profiling (`DataProfiler`), and LLM orchestration (`Ollama`).
- **Resilience**: Includes a validation layer to handle LLM hallucinations and re-map key variations (e.g., `name` -> `field_name`).
- **Compatibility**: Uses specific locks for `setuptools<70` and `urllib3<2` to ensure `DataProfiler` stability.

## 📝 Planned KMDS Integration

- Move `engine.py` into the `kmds.core` namespace.
- Wire the Architect and Scientist reports into KMDS "Knowledge Stashes".
- Replace the CLI output with the main KMDS UI.
