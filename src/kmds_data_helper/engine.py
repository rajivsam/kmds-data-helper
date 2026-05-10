import json
from pathlib import Path
from typing import List, Dict, Any
from kmds_data_helper.utils import parse_notebook_with_outputs, save_kmds_json

class KMDSEngine:
    def __init__(self, llm_client):
        """Initializes with an LLM client."""
        self.llm = llm_client

    def _safe_json_parse(self, data: Any, fallback_key: str) -> Dict:
        """Handles both raw strings and dictionaries with key normalization."""
        parsed = {}
        if isinstance(data, dict):
            parsed = data
        else:
            try:
                # Clean markdown and parse string
                clean_text = str(data).strip().replace("```json", "").replace("```", "").strip()
                parsed = json.loads(clean_text)
            except Exception:
                parsed = {fallback_key: str(data)}

        # --- KEY NORMALIZATION ---
        if isinstance(parsed, dict):
            # Find any key containing "score" and map it to quality_score
            for k in list(parsed.keys()):
                if "score" in k.lower():
                    val = parsed.pop(k)
                    try:
                        parsed["quality_score"] = int(float(val))
                    except:
                        parsed["quality_score"] = 0
            
            # Ensure required keys exist for the API contract
            if "quality_score" not in parsed:
                parsed["quality_score"] = 0
            if fallback_key not in parsed:
                parsed[fallback_key] = "No insight found"
        
        return parsed

    def process_notebook_stage(self, nb_path: Path) -> Dict:
        """Stage 1: Multi-Persona Notebook Analysis."""
        print(f"[*] Analyzing Notebook: {nb_path.name}")
        
        # Default structure to prevent crashes
        result = {
            "notebook_name": nb_path.name,
            "scientist_insight": {"quality_score": 0, "insight": "Pending..."},
            "modeling_insight": {"exploratory_summary": "Pending...", "model_justification": "N/A"}
        }
        
        try:
            full_content = parse_notebook_with_outputs(str(nb_path))
            
            # Pass 1: Scientist
            print(f"    -> Running Scientist Persona...")
            sci_raw = self.llm.call_persona(
                persona="scientist",
                context=full_content,
                stats="REQUIRED JSON: {quality_score: int, insight: string}"
            )
            result["scientist_insight"] = self._safe_json_parse(sci_raw, "insight")
            
            # Pass 2: Modeling DS
            print(f"    -> Running Modeling DS Persona...")
            mod_raw = self.llm.call_persona(
                persona="modeling_ds",
                context=full_content,
                stats="REQUIRED JSON: {exploratory_summary: string, model_justification: string}"
            )
            result["modeling_insight"] = self._safe_json_parse(mod_raw, "exploratory_summary")
            
            return result
        except Exception as e:
            print(f" [!] Error processing {nb_path.name}: {e}")
            return result

    def run_stage_1(self, notebook_dir: str) -> List[Dict]:
        results = []
        nb_folder = Path(notebook_dir)
        for nb_file in sorted(nb_folder.glob("*.ipynb")):
            insight = self.process_notebook_stage(nb_file)
            results.append(insight)
        return results

    def run_strategic_synthesis(self, stage_1_results: List[Dict], output_dir: str):
        """Stage 2: Global project-wide synthesis."""
        print("[*] Running Strategic Synthesis...")
        summary_stats = str(stage_1_results)
        
        try:
            strategic_raw = self.llm.call_persona(
                persona="strategic_lead",
                context="Full Project Synthesis",
                stats=f"REQUIRED JSON: {{strategic_alignment: string, production_roadmap: string}} DATA: {summary_stats}"
            )
            
            report_dict = self._safe_json_parse(strategic_raw, "strategic_alignment")
            
            # Ensure synthesis keys exist
            if "production_roadmap" not in report_dict:
                report_dict["production_roadmap"] = "N/A"
            
            save_path = Path(output_dir) / "kmds_strategic_summary.json"
            save_kmds_json(
                {"strategic_report": report_dict, "notebook_details": stage_1_results},
                str(save_path)
            )
            return report_dict
        except Exception as e:
            print(f" [!] Strategic Synthesis Failed: {e}")
            return {
                "strategic_alignment": f"Synthesis Error: {str(e)}", 
                "production_roadmap": "N/A"
            }
