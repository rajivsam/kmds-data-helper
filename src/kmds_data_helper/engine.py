import json
import logging
from datetime import datetime
from .config_manager import KMDSConfigManager
from .data_processor import KMDSDataProcessor
from .llm_client import LLMInterface

# Setup basic logging for visibility in terminal
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class KMDSEngine:
    def __init__(self):
        self.config = KMDSConfigManager()
        self.data = KMDSDataProcessor(self.config)
        self.llm = LLMInterface(self.config)

    def run_development_pass(self):
        """
        Runs the multi-persona development pass:
        Stage 1: Deep Analysis (Scientist & Modeling DS)
        Stage 2: Strategic Synthesis (Strategic Tech Lead)
        """
        reports = []
        # Header for the synthesis context
        aggregated_findings = f"AGGREGATED PROJECT INSIGHTS (Generated: {datetime.now().isoformat()}):\n"
        
        try:
            notebook_files = list(self.config.paths["notebooks"].glob("*.ipynb"))
        except Exception as e:
            return {"error": f"Failed to access notebook directory: {str(e)}"}

        if not notebook_files:
            logging.warning("No notebooks found to analyze.")
            return {"error": "No notebooks found in directory."}

        # --- STAGE 1: INDIVIDUAL NOTEBOOK ANALYSIS ---
        for nb in notebook_files:
            logging.info(f"[*] Stage 1: Processing '{nb.name}'...")
            
            try:
                content = self.data.read_notebook(nb)
                # Keep within model limits while providing enough context
                stats_context = json.dumps(content)[:15000]
            except Exception as e:
                logging.error(f"Failed to read {nb.name}: {str(e)}")
                continue

            # Parallel perspective: Quality + Mathematical Rigor
            sci_res = self.llm.ask_persona('scientist', context=nb.name, stats=stats_context)
            mod_res = self.llm.ask_persona('modeling_ds', context=nb.name, stats=stats_context)

            # Standardize output for reporting
            nb_entry = {
                "notebook": nb.name,
                "analysis_timestamp": datetime.now().isoformat(),
                "scientist_report": sci_res if isinstance(sci_res, dict) else {"error": str(sci_res)},
                "modeling_report": mod_res if isinstance(mod_res, dict) else {"error": str(mod_res)}
            }
            reports.append(nb_entry)

            # Build cleaned memory for Stage 2
            aggregated_findings += f"\n### File: {nb.name} ###\n"
            aggregated_findings += f"Data Scientist Observations: {json.dumps(nb_entry['scientist_report'])}\n"
            aggregated_findings += f"Modeling Justification: {json.dumps(nb_entry['modeling_report'])}\n"

        # --- STAGE 2: STRATEGIC SYNTHESIS ---
        logging.info("[*] Stage 2: Running Strategic Synthesis...")
        
        # Pull high-level project context (Architect perspective or Doc summary)
        project_context = "Comprehensive repository analysis of data quality and modeling rigor."
        
        tl_response = self.llm.ask_persona(
            'strategic_lead', 
            context=project_context, 
            stats=aggregated_findings
        )

        # Final consolidation
        final_report = {
            "metadata": {
                "total_notebooks_processed": len(reports),
                "run_date": datetime.now().isoformat()
            },
            "individual_notebook_reports": reports,
            "strategic_summary": tl_response if isinstance(tl_response, dict) else {"raw_output": str(tl_response)}
        }

        # --- PERSISTENCE ---
        try:
            output_path = self.config.paths["output"] / "kmds_strategic_summary.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(final_report, f, indent=4)
            logging.info(f"✅ Robust report successfully saved to: {output_path}")
        except Exception as e:
            logging.error(f"❌ Failed to save report: {str(e)}")

        return final_report
