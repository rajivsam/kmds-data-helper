import json
import os
import pymupdf4llm
import dataprofiler as dp
import nbformat
from pathlib import Path
from ollama import Client

class KMDS_LLM_Engine:
    def __init__(self, model="qwen2.5-coder:7b"):
        self.client = Client(host='http://localhost:11434')
        self.model = model

        # --- PATH ANCHORING (Root: /documents, /data, /notebooks) ---
        self.base_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
        self.paths = {
            "pdf_processing": self.base_dir / "documents",
            "data_profiling": self.base_dir / "data",
            "notebook_analysis": self.base_dir / "notebooks"
        }
        
        self.active_features = {k: False for k in self.paths.keys()}
        self._run_system_checks()

    def _run_system_checks(self):
        """Guardrail logic to verify directory structure and file availability."""
        print(f"\n🔍 [KMDS] Initializing Engine at: {self.base_dir}")
        
        requirements = {
            "pdf_processing": ("*.pdf", "Architect Pass (PDF)"),
            "data_profiling": ("**/*", "Scientist/Engineer Pass (Data Samples)"),
            "notebook_analysis": ("*.ipynb", "Development Pass (Notebooks)")
        }

        missing_notices = []
        for feature, (pattern, label) in requirements.items():
            target_dir = self.paths[feature]
            if target_dir.is_dir() and any(target_dir.glob(pattern)):
                self.active_features[feature] = True
            else:
                missing_notices.append(f"- {label}: Expected files in /{target_dir.relative_to(self.base_dir)}/")

        if missing_notices:
            print("⚠️  LLM-based features partially limited:")
            for notice in missing_notices: print(notice)
            print("👉 To enable, populate directories as specified in the README.\n")
        else:
            print("✅ All systems go. Full repository context enabled.\n")

    def get_project_ground_truth(self):
        """
        Consolidated Ground Truth:
        - Scans /documents for .txt descriptions.
        - Scans /data for physical CSV schema (ignoring output files).
        """
        all_truth = []

        # 1. Pull Context from Text Files in /documents
        if self.active_features["pdf_processing"]:
            txt_files = list(self.paths["pdf_processing"].glob("*.txt"))
            for txt_path in txt_files:
                try:
                    with open(txt_path, 'r', encoding='utf-8') as f:
                        all_truth.append({
                            "source": txt_path.name,
                            "type": "documentation_description",
                            "content": f.read()[:5000]
                        })
                except Exception as e:
                    print(f"[-] Failed to read {txt_path.name}: {e}")

        # 2. Pull Schema from Data Files in /data
        if self.active_features["data_profiling"]:
            csv_files = list(self.paths["data_profiling"].glob("**/*.csv"))
            for csv_path in csv_files:
                if "kmds_output" in csv_path.name:
                    continue
                try:
                    data = dp.Data(str(csv_path))
                    profile = dp.Profiler(data)
                    report = profile.report(report_options={"output_format": "pretty"})
                    data_stats = report.get('data_stats', [])
                    names = [c.get('column_name') for c in data_stats] if isinstance(data_stats, list) else data_stats.keys()
                    all_truth.append({
                        "source": csv_path.name,
                        "type": "physical_schema",
                        "columns": [name for name in names]
                    })
                except Exception as e:
                    print(f"[-] Ground truth extraction failed for {csv_path.name}: {e}")
        return all_truth

    def generate_summary(self, pdf_path, user_query="data dictionary summary"):
        if not self.active_features["pdf_processing"]:
            return {"summary_text": "Feature disabled: No documents found."}
        print(f"[*] Architect Pass: Summarizing {os.path.basename(pdf_path)}")
        md_text = pymupdf4llm.to_markdown(str(pdf_path))
        prompt = f"Role: Data Architect. Task: Create JSON summary. Context: {md_text[:12000]}. Return ONLY JSON: {{\"title\": \"...\", \"summary_text\": \"...\", \"entities\": []}}"
        response = self.client.generate(model=self.model, prompt=prompt, format="json")
        raw = json.loads(response['response'])
        return {
            "title": raw.get("title", "Untitled"),
            "summary_text": raw.get("summary_text") or raw.get("description", "No summary."),
            "entities": raw.get("entities", [])
        }

    def generate_data_report(self, sample_path):
        if not self.active_features["data_profiling"]:
            return {"modeling_readiness": "Feature disabled: No data found."}
        print(f"[*] Scientist Pass: Analyzing {os.path.basename(sample_path)}")
        domain_context = ""
        if self.active_features["pdf_processing"]:
            txt_files = list(self.paths["pdf_processing"].glob("*.txt"))
            for txt_path in txt_files:
                try:
                    with open(txt_path, 'r', encoding='utf-8') as f:
                        domain_context += f"\nSource ({txt_path.name}):\n{f.read()[:2000]}\n"
                except: pass
        data = dp.Data(str(sample_path))
        profile = dp.Profiler(data)
        report = profile.report(report_options={"output_format": "pretty"})
        stats_summary = {
            "row_count": report.get('global_stats', {}).get('row_count', 0),
            "columns": [{"name": c.get('column_name'), "type": c.get('data_type')} for c in report.get('data_stats', [])]
        }
        prompt = f"Role: Lead Data Scientist. Context: {domain_context}. Data Stats: {json.dumps(stats_summary)}. Return ONLY JSON: {{\"quality_score\": \"...\", \"technical_observations\": \"...\", \"data_quality_warnings\": [], \"modeling_readiness\": \"...\"}}"
        response = self.client.generate(model=self.model, prompt=prompt, format="json")
        return json.loads(response['response'])

    def extract_definitions(self, pdf_path, ground_truth=None):
        if not self.active_features["pdf_processing"]: return []
        print(f"[*] Engineer Pass: Extracting fields from {os.path.basename(pdf_path)}")
        md_text = pymupdf4llm.to_markdown(str(pdf_path))
        prompt = f"Role: Senior Data Engineer. Documentation: {md_text[:10000]}. Ground Truth: {json.dumps(ground_truth)}. Return ONLY JSON list: [{{\"field_name\": \"...\", \"data_type\": \"...\", \"description\": \"...\"}}]"
        response = self.client.generate(model=self.model, prompt=prompt, format="json", options={"num_ctx": 16000})
        try:
            raw_list = json.loads(response['response'])
            return [{"field_name": item.get("field_name") or item.get("name"), "data_type": item.get("data_type", "string"), "description": item.get("description", "N/A")} for item in raw_list if isinstance(item, dict)]
        except: return []

    def parse_notebook(self, nb_path):
        if not self.active_features["notebook_analysis"]: return None
        with open(nb_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        return {
            "markdown": [c.source for c in nb.cells if c.cell_type == 'markdown'],
            "code": [c.source for c in nb.cells if c.cell_type == 'code']
        }

    def run_development_pass(self):
        """
        Stage 1: Individual Notebook Analysis (Data Scientist Persona)
        Stage 2: Project-wide Synthesis (Tech Lead Persona)
        """
        if not self.active_features["notebook_analysis"]:
            return {"error": "Notebooks folder is empty or missing."}

        notebook_reports = []
        notebook_files = list(self.paths["notebook_analysis"].glob("*.ipynb"))

        # --- STAGE 1: DATA SCIENTIST PASS ---
        for nb_file in notebook_files:
            print(f"[*] Scientist Persona: Analyzing logic in {nb_file.name}...")
            content = self.parse_notebook(nb_file)
            
            prompt = f"""
            Role: Senior Data Scientist.
            Notebook Name: {nb_file.name}
            Content (Markdown & Code): {json.dumps(content)[:15000]}
            
            Evaluate: Experimental logic, feature engineering validity, and narrative clarity.
            Return ONLY JSON: 
            {{"notebook": "{nb_file.name}", "logic_score": 1-10, "observations": [], "risks": []}}
            """
            response = self.client.generate(model=self.model, prompt=prompt, format="json")
            notebook_reports.append(json.loads(response['response']))

        # --- STAGE 2: TECH LEAD AGGREGATOR ---
        print("[*] Tech Lead Persona: Synthesizing project-wide report...")
        tl_prompt = f"""
        Role: Technical Lead.
        Input: Summary of all analyzed notebooks in this project: {json.dumps(notebook_reports)}
        
        Evaluate: Project-wide redundancy, architectural health, and deployment readiness.
        Return ONLY JSON:
        {{
            "project_health": "...",
            "technical_debt_warnings": [],
            "deployment_readiness_score": 1-10,
            "refactoring_roadmap": []
        }}
        """
        tl_response = self.client.generate(model=self.model, prompt=tl_prompt, format="json")
        
        return {
            "individual_reports": notebook_reports,
            "project_summary": json.loads(tl_response['response'])
        }
