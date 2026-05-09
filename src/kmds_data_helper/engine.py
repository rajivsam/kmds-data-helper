import json
from .config_manager import KMDSConfigManager
from .data_processor import KMDSDataProcessor
from .llm_client import LLMInterface

class KMDSEngine:
    def __init__(self):
        self.config = KMDSConfigManager()
        self.data = KMDSDataProcessor(self.config)
        self.llm = LLMInterface(self.config)

    def run_development_pass(self):
        """
        Runs the multi-persona development pass:
        Stage 1: Scientist Pass (Individual Notebook Analysis)
        Stage 2: Tech Lead Pass (Project Synthesis)
        """
        reports = []
        notebook_files = list(self.config.paths["notebooks"].glob("*.ipynb"))

        if not notebook_files:
            return {"error": "No notebooks found in directory."}

        # --- STAGE 1: SCIENTIST PASS ---
        for nb in notebook_files:
            print(f"[*] Scientist Persona: Analyzing {nb.name}...")
            content = self.data.read_notebook(nb)
            
            # Request analysis from the Scientist persona
            res = self.llm.ask_persona('scientist', context=nb.name, stats=json.dumps(content)[:15000])
            
            # Robustness: Ensure the response is a dictionary
            if isinstance(res, str) or res is None:
                res = {"notebook": nb.name, "raw_output": str(res) or "Timeout"}
            
            reports.append(res)

        # --- STAGE 2: TECH LEAD PASS (AGGREGATION) ---
        print("[*] Tech Lead Persona: Synthesizing project-wide report...")
        tl_response = self.llm.ask_persona('tech_lead', context="Full Project Synthesis", stats=json.dumps(reports))
        
        # --- THE JSON SHIELD ---
        # Catch cases where the LLM returns a string instead of a JSON object
        if isinstance(tl_response, str) or tl_response is None:
            tl_response = {
                "project_summary": {
                    "project_health": str(tl_response) if tl_response else "Timeout/No Response",
                    "technical_debt_warnings": ["LLM failed to provide structured JSON"],
                    "deployment_readiness_score": "N/A"
                }
            }

        # Ensure the 'project_summary' key exists for main.py
        if "project_summary" not in tl_response:
            # Look for hallucinated keys (common in 7B models)
            inner = tl_response.get("summary") or tl_response.get("report") or tl_response
            tl_response = {"project_summary": inner}
        
        # Final combined object
        final_report = {
            "individual_reports": reports,
            "project_summary": tl_response["project_summary"]
        }

        # --- ISOLATION STEP: Save result to /output ---
        output_path = self.config.paths["output"] / "kmds_summary.json"
        with open(output_path, 'w') as f:
            json.dump(final_report, f, indent=4)
        
        print(f"✅ Full report saved to: {output_path}")
        return final_report
