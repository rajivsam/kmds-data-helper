import dataprofiler as dp
import nbformat
from pathlib import Path

class KMDSDataProcessor:
    def __init__(self, config_manager):
        self.cfg = config_manager
        
        # Track which features are enabled based on file availability
        self.active_features = {
            "pdf_processing": False,
            "data_profiling": False,
            "notebook_analysis": False
        }
        self._run_system_checks()

    def _run_system_checks(self):
        """Internal guardrail to verify if directories contain valid files."""
        # 1. Check for PDFs in documents
        if any(self.cfg.paths["docs"].glob("*.pdf")):
            self.active_features["pdf_processing"] = True
            
        # 2. Check for CSVs in data (excluding output folder)
        if any(self.cfg.paths["data"].glob("**/*.csv")):
             self.active_features["data_profiling"] = True
             
        # 3. Check for Notebooks in notebooks folder
        if any(self.cfg.paths["notebooks"].glob("*.ipynb")):
            self.active_features["notebook_analysis"] = True

    def get_ground_truth(self):
        """Scans /docs and /data while respecting /output isolation."""
        truth = []
        
        # 1. Documentation Ingestion (Text files)
        for txt in self.cfg.paths["docs"].glob("*.txt"):
            with open(txt, 'r', encoding='utf-8') as f:
                truth.append({"source": txt.name, "type": "doc", "content": f.read()[:5000]})

        # 2. Data Ingestion with feedback loop protection
        for csv in self.cfg.paths["data"].glob("**/*.csv"):
            # Isolation check: Ignore if file lives in the output directory
            if str(self.cfg.paths["output"].resolve()) in str(csv.resolve()):
                continue
                
            try:
                profile = dp.Profiler(dp.Data(str(csv)))
                report = profile.report(report_options={"output_format": "pretty"})
                truth.append({
                    "source": csv.name,
                    "type": "physical_schema",
                    "columns": [c.get('column_name') for c in report.get('data_stats', [])]
                })
            except Exception as e:
                print(f"[-] Profile failed for {csv.name}: {e}")
        return truth

    def read_notebook(self, nb_path):
        """Parses .ipynb files into markdown and code chunks."""
        with open(nb_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        return {
            "markdown": [c.source for c in nb.cells if c.cell_type == 'markdown'],
            "code": [c.source for c in nb.cells if c.cell_type == 'code']
        }
