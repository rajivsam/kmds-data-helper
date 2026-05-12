# Architectural Guardrails

### 1. Hardware Constraints

* **VRAM Limit**: 6GB (RTX 3050).
* **Context Window**: Prompts must be concise to fit within \~4k-8k tokens (depending on model quantization).

### 2. Concurrency & Safety

* **The Golden Rule**: `asyncio.Semaphore(1)` must wrap every LLM inference call in `engine.py`.
* **Traffic Pattern**: The FastAPI layer accepts parallel requests (High Throughput), but the Engine processes them sequentially (Safe Execution).
* **Thread Safety**: Use `asyncio.get_running_loop()` when offloading synchronous LLM calls to `run_in_executor`.

### 3. Concern Separation

* **`service.py`**: The Gatekeeper. Handles path resolution (`.resolve()`) and strict validation.
* **`engine.py`**: The Orchestrator. Handles file I/O and the Persona Loop.
* **`llm_client.py`**: The Interface. Handles dynamic discovery and JSON formatting.

### 4. Path Robustness

* All file operations must use `pathlib.Path.resolve()` to ensure the server works correctly regardless of the shell's Current Working Directory (CWD).
