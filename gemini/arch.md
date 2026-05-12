# Architectural Guardrails

### 1. VRAM & Concurrency Control

- **Hardware Limit**: 6GB VRAM (RTX 3050).
- **Concurrency Pattern**: `asyncio.Semaphore(1)` is mandatory in the Engine.
- **Safety**: Multiple API requests (FastAPI) are queued; only one LLM inference is processed at a time.

### 2. Execution Pattern

- **Engine**: Handles file I/O, notebook extraction, and the persona loop.
- **Service**: Acts as the "Gatekeeper" performing strict path resolution and validation.
- **LLM Client**: Manages the Ollama interface and JSON formatting.

### 3. Event Loop Stability

- Use `asyncio.get_running_loop()` for offloading synchronous calls to `run_in_executor`.
- Ensure all paths use `.resolve()` to avoid CWD (Current Working Directory) mismatches.
