# Functional Features (Invariants)

### 1. Dynamic Persona Discovery

- Personas are loaded from `personas/*.yaml` files.
- The Engine must snake_case the display name for file lookup (e.g., "Tech Lead" -> `tech_lead.yaml`).
- Each YAML must contain a `system_prompt` key.

### 2. The 5-Pillar Context Engine

The system requires and validates the following directory structure:

- `notebooks/`: Target `.ipynb` files (extracted as code + markdown).
- `data_dictionary/`: Meta-data text/csv/md files (injected into `{stats}`).
- `documents/`: PDF reference files (text extracted and injected into `{stats}`).
- `data/`: Raw datasets (inventoried for the LLM to verify file availability).
- `personas/`: YAML configuration for individual agents.

### 3. CLI Utilities

- `kmds-check`: A standalone utility to verify the 5-Pillar structure before running an audit.
