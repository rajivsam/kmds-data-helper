# KMDS Data Helper: System Architecture & Requirements

KMDS Data Helper is a companion tool to the **KMDS (Knowledge Management for Data Science)** framework. It automates the generation of knowledge content from Jupyter notebooks, which can then be ingested into the KMDS Knowledge Graph.

## 1. Pre-requisites & Workspace Contract

To use this tool effectively, it must be run within a Data Science project repository that follows the standard KMDS directory structure.

### Project Structure Requirements

The tool expects the following directories to be present in the target workspace:

- `notebooks/`: Contains the `.ipynb` files for audit.
- `data/`: The source datasets referenced in notebooks.
- `output/`: Directory where the helper will write the final JSON audit.
- `documents/`: Supporting project documentation.

## 2. Request Trace Map

This section traces a single audit request from the client through the backend.

### Phase 1: The API Entry (Gatekeeper)

1. **Client Action**: Sends a `POST` request to `/analyze`.
2. **Actor**: `api.py` (FastAPI) / `KMDSReportService`
3. **Action**: Validates the presence of the required project structure.
4. **Result**: Returns **400 Bad Request** if the directory contract is not met.

### Phase 2: Orchestration (The Engine)

1. **Actor**: `KMDSEngine` (in `kmds_engine.py`)
2. **Action**: Scans the `notebooks/` folder and prepares the multi-persona audit loop.

### Phase 3: Intelligence (LLM Handshake)

1. **Actor**: `LLMClient` (in `llm_client.py`)
2. **Action**: Communicates with local **Ollama** instances to process persona-specific prompts.
3. **Result**: Returns structured JSON insights (Title, Summary, Entities).

### Phase 4: Persistence

1. **Actor**: `KMDSReportService`
2. **Action**: Aggregates all insights and saves `audit_results.json` to the project's `output/` directory.
