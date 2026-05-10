import yaml
import json
import nbformat
from pathlib import Path
from typing import List, Dict, Any

class KMDSEngine:
    def __init__(self, llm_client, config_dir: Path, config_file: Path):
        """
        Initializes the engine and synchronizes the LLMClient with the workspace.
        """
        self.llm_client = llm_client
        self.config_dir = config_dir
        self.config_file = config_file
        
        # 1. Load the master configuration
        with open(self.config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # 2. Sync the LLMClient to look at the same project YAML
        if hasattr(self.llm_client, 'set_config_path'):
            self.llm_client.set_config_path(str(self.config_file))
            print(f"DEBUG: Synchronized LLMClient with config: {self.config_file.name}")
        
        # 3. Prime the client's internal persona dictionary as a fail-safe
        self._prime_llm_client_personas()

    def _prime_llm_client_personas(self):
        """Injects persona data into the LLMClient's internal lookup dictionary."""
        persona_dir = self.config_dir / "personas"
        if not persona_dir.exists():
            return

        if not hasattr(self.llm_client, 'personas') or not isinstance(self.llm_client.personas, dict):
            self.llm_client.personas = {}

        for p_file in persona_dir.glob("*.yaml"):
            p_key = p_file.stem 
            with open(p_file, 'r') as f:
                try:
                    p_data = yaml.safe_load(f)
                    self.llm_client.personas[p_key] = p_data
                except Exception as e:
                    print(f"      [!] Failed to load {p_file.name}: {e}")
        
        print(f"DEBUG: Primed LLMClient with {len(self.llm_client.personas)} local personas.")

    def _safe_json_parse(self, response_data: Any) -> Dict[str, Any]:
        """Robust parser to handle list or string responses from the LLMClient."""
        try:
            # Extract content if response is a list (Chat history format)
            if isinstance(response_data, list):
                if len(response_data) > 0 and isinstance(response_data[-1], dict):
                    text = response_data[-1].get('content', str(response_data[-1]))
                else:
                    text = str(response_data[-1]) if response_data else ""
            else:
                text = response_data

            if isinstance(text, dict):
                return text

            clean_text = str(text).strip()
            if "```json" in clean_text:
                clean_text = clean_text.split("```json")[-1].split("```")[0]
            elif "```" in clean_text:
                clean_text = clean_text.split("```")[1]
            
            return json.loads(clean_text.strip())
        except Exception:
            return {}

    def _format_notebook_context(self, nb_path: Path) -> str:
        """Extracts code and execution results for high-fidelity context."""
        try:
            with open(nb_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
            context = []
            for cell in nb.cells:
                if cell.cell_type == 'code':
                    source = cell.source.strip()
                    # Capture only plain text execution results
                    outputs = [str(out.data.get('text/plain', '')) 
                               for out in cell.get('outputs', []) 
                               if out.output_type == 'execute_result']
                    context.append(f"CODE:\n{source}\nRESULT:\n{' '.join(outputs)}")
            return "\n---\n".join(context)[:5000]
        except Exception as e:
            return f"Error reading notebook {nb_path.name}: {str(e)}"

    def run_audit(self, notebook_paths: List[str]) -> List[Dict[str, Any]]:
        """Main audit loop utilizing the verified LLMClient handshake."""
        results = []
        persona_keys = self.config.get("personas", [])
        
        for nb_path_str in notebook_paths:
            nb_path = Path(nb_path_str)
            nb_context = self._format_notebook_context(nb_path)
            nb_entry = {"notebook_name": nb_path.name}
            
            for p_key in persona_keys:
                print(f"    [>] Running {p_key.capitalize()} analysis for {nb_path.name}...")
                try:
                    # Final Aligned Handshake
                    response = self.llm_client.call_persona(
                        p_key, 
                        f"Audit this notebook: {nb_path.name}", 
                        nb_context
                    )
                    nb_entry[f"{p_key}_insight"] = self._safe_json_parse(response)
                except Exception as e:
                    print(f"      [!] Client Error on {p_key}: {e}")
                    nb_entry[f"{p_key}_insight"] = {}

            results.append(nb_entry)
        
        print(f"\n[ENGINE] Audit Complete for {len(notebook_paths)} notebooks.")
        return results
