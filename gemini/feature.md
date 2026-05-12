# Functional Features (Invariants)

### 1. Dynamic Persona Discovery

* **Source of Truth:** Personas are strictly loaded from the `personas/` directory as `.yaml` files.
* **Naming Convention:** The engine maps display names to filenames using snake\_case (e.g., "Tech Lead" → `tech_lead.yaml`).
* **Configuration:** Each YAML file must contain a `system_prompt` key.

### 2. The 5-Pillar Context Engine

The system enforces a strict directory structure. An audit cannot proceed unless these 5 pillars are validated:

1. **`notebooks/`**: Target `.ipynb` files (Content extracted: Code cells + Markdown cells).
2. **`data_dictionary/`**: Metadata files (`.txt`, `.md`, `.csv`) injected into the `{stats}` prompt variable.
3. **`documents/`**: Supporting PDF files (Text extracted and injected into `{stats}`).
4. **`data/`**: Raw datasets (Directory scanned for filenames to verify data availability).
5. **`personas/`**: Agent configuration files.

### 3. CLI Utilities

* **`kmds-check`**: A standalone "Pre-Flight" utility that validates the 5-Pillar structure without invoking the heavy LLM engine.

### 4. Structured Output

* The API response is a list of objects strictly following this schema:
  `{"notebook": str, "persona": str, "analysis": dict}`
