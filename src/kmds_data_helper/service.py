import os
from pathlib import Path
from typing import Dict, Optional
from kmds_data_helper.engine import KMDSEngine
from kmds_data_helper.utils import save_kmds_json

class KMDSReportService:
    """
    The main entry point for backend integration.
    Wraps the KMDSEngine and persona logic into a simple API.
    """
    def __init__(self, llm_client, output_dir: str = "output"):
        self.engine = KMDSEngine(llm_client)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_comprehensive_report(self, notebook_dir: str) -> Dict:
        """
        Executes the full pipeline:
        1. Stage 1: Individual Notebook Analysis (Scientist + Modeling DS)
        2. Stage 2: Project Synthesis (Strategic Tech Lead)
        """
        if not os.path.exists(notebook_dir):
            raise FileNotFoundError(f"Notebook directory not found: {notebook_dir}")

        # Execute Stage 1 (Now returns list of dicts with nested JSON)
        notebook_insights = self.engine.run_stage_1(notebook_dir)
        
        # Execute Stage 2 (Now returns a dict via the engine's safe_json_parse)
        strategic_summary = self.engine.run_strategic_synthesis(
            stage_1_results=notebook_insights, 
            output_dir=str(self.output_dir)
        )

        # Build the final payload - structure remains consistent for the API
        final_report = {
            "status": "success",
            "project_summary": strategic_summary,  # This is now a Dict
            "notebook_details": notebook_insights, # This is now a List[Dict]
            "metadata": {
                "total_notebooks": len(notebook_insights),
                "output_directory": str(self.output_dir)
            }
        }

        # Save the full payload
        save_kmds_json(final_report, str(self.output_dir / "full_service_report.json"))
        
        return final_report

    def get_last_report(self) -> Optional[Dict]:
        """Utility for backend to fetch the latest generated JSON."""
        report_path = self.output_dir / "full_service_report.json"
        if report_path.exists():
            import json
            with open(report_path, 'r') as f:
                return json.load(f)
        return None
