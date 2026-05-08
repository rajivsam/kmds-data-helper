## Session Stashed: `kmds_data_dictionary_helper` (May 8, 2026)

This session focused on decoupling the backend logic from the frontend to resolve integration issues and ensure core reliability.

## 1. Core Strategic Decisions

* Backend Isolation: Pause all Flask, HTMX, and Tailwind UI development. Focus exclusively on `engine.py` to ensure high-confidence data extraction and merging.
* Validation Protocol: Transition to a CLI-based verification workflow using a dedicated test script (`test_engine.py`) to bypass web server overhead during logic debugging.
* Minimalist UX Philosophy: The system must produce a "Best Guess" output where users only audit and confirm mappings rather than manually browsing through reference terms. [1, 2, 3, 4]

## 2. Technical Architecture & Environment

* Environment Status: UV managed with specific compatibility locks: `setuptools<70` and `urllib3<2`.
* Engine Stack: Python 3.12, Capital One DataProfiler for CSV/Parquet schema inference, PyMuPDF4LLM for PDF-to-Markdown conversion, and Ollama (Qwen2.5-Coder:7b) for intelligent reconciliation.
* Data Handling: Implemented structured profiling that extracts global and column-level statistics to feed as "Ground Truth" into the LLM context. [3, 5, 6, 7]

## 3. Planned Enhancements for engine.py

* Sample Enrichment: Update the `DataProfiler` logic to include row samples (e.g., 3 examples per column) to help the LLM map cryptic headers (like `CID`) to descriptive PDF terms (like `Customer ID`).
* Context Optimization: Refine the Markdown input by stripping non-essential PDF text (headers/footers) to stay within the 16k context window for Qwen2.5-Coder.
* Confidence Scoring: Modify the prompt to have the LLM flag auto-matched vs. guessed rows to streamline the "minimal work" user interface later on. [6, 7, 8, 9, 10]

Next Step: Run the first end-to-end CLI test using `test_engine.py` to verify the JSON merge quality.

[1] [https://developers.openai.com](https://developers.openai.com/cookbook/articles/codex_exec_plans)

[2] [https://medium.com](https://medium.com/cwan-engineering/building-an-ai-powered-markdown-knowledge-base-system-for-your-engineering-team-4bccea3cdbfe)

[3] [https://www.youtube.com](https://www.youtube.com/watch?v=DeGaNdGRBSU&t=7)

[4] [https://medium.com](https://medium.com/imdoneio/%EF%B8%8F-%EF%B8%8F-markdown-the-most-important-tool-in-my-toolbox-3b18c96031e4)

[5] [https://arxiv.org](https://arxiv.org/html/2409.12186v1)

[6] [https://github.com](https://github.com/capitalone/DataProfiler)

[7] [https://pypi.org](https://pypi.org/project/DataProfiler/0.3.2/)

[8] [https://www.youtube.com](https://www.youtube.com/watch?v=T_vqhHHjkso&t=1)

[9] [https://huggingface.co](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct/discussions/14)

[10] [https://github.com](https://github.com/QwenLM/Qwen3-VL/issues/761)
