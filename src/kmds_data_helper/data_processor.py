import pandas as pd
import csv as native_csv
from data_profiling import ProfileReport
import nbformat
from pathlib import Path

class KMDSDataProcessor:
    def __init__(self, config_manager):
        self.cfg = config_manager
        
        self.active_features = {
            "pdf_processing": False,
            "data_profiling": False,
            "notebook_analysis": False
        }
        self._run_system_checks()

    def _run_system_checks(self):
        """Internal guardrail to verify if directories contain valid files."""
        if any(self.cfg.paths["documents"].glob("*.pdf")):
            self.active_features["pdf_processing"] = True
            
        if any(self.cfg.paths["data"].glob("**/*.csv")):
             self.active_features["data_profiling"] = True
             
        if any(self.cfg.paths["notebooks"].glob("*.ipynb")):
            self.active_features["notebook_analysis"] = True

    def get_ground_truth(self):
        """
        Scans KMDS documents and data directories while protecting Sphinx tree structure.
        """
        truth = []
        
        # 1. Ingest text instructions from your KMDS 'documents' folder safely
        for txt in self.cfg.paths["documents"].glob("*.txt"):
            with open(txt, 'r', encoding='utf-8') as f:
                truth.append({"source": txt.name, "type": "doc", "content": f.read()[:5000]})

        # 2. Ingest tabular data schemas cleanly
        for csv_path in self.cfg.paths["data"].glob("**/*.csv"):
            if str(self.cfg.paths["output"].resolve()) in str(csv_path.resolve()):
                continue
                
            try:
                print(f"🔬 [PROFILER] Reading native file structures for {csv_path.name}...")
                
                with open(csv_path, 'r', encoding='utf-8-sig') as f:
                    sample = f.readline()
                    delimiter = ';' if ';' in sample else ','
                    f.seek(0)
                    reader = native_csv.reader(f, delimiter=delimiter)
                    columns_found = next(reader)
                
                columns_found = [c.strip().strip('"').strip("'") for c in columns_found if c.strip()]

                # Load a slice into pandas to inspect types
                df = pd.read_csv(
                    csv_path, 
                    header=0, 
                    names=columns_found, 
                    nrows=20, 
                    on_bad_lines='skip'
                )
                
                profile = ProfileReport(df, minimal=True, progress_bar=False)
                description = profile.get_description()
                
                type_insights = {}
                variables_map = description.get("variables", {})
                for col in columns_found:
                    col_type = variables_map.get(col, {}).get("type", "unknown")
                    type_insights[col] = str(col_type)

                truth.append({
                    "source": csv_path.name,
                    "type": "physical_schema",
                    "columns": columns_found,
                    "data_types": type_insights
                })
                print(f"✅ [PROFILER] Identified all {len(columns_found)} schema column parameters.")
                
            except Exception as e:
                print(f"[-] Profile extraction failed for {csv_path.name}: {e}")
                
        return truth

    def read_notebook(self, nb_path):
        with open(nb_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        return {
            "markdown": [c.source for c in nb.cells if c.cell_type == 'markdown'],
            "code": [c.source for c in nb.cells if c.cell_type == 'code']
        }
import pandas as pd
import csv as native_csv
import nbformat
from pathlib import Path

class KMDSDataProcessor:
    def __init__(self, config_manager):
        self.cfg = config_manager
        
        self.active_features = {
            "pdf_processing": False,
            "data_profiling": False,
            "notebook_analysis": False
        }
        self._run_system_checks()

    def _run_system_checks(self):
        """Internal guardrail to verify if directories contain valid files."""
        if any(self.cfg.paths["documents"].glob("*.pdf")):
            self.active_features["pdf_processing"] = True
            
        if any(self.cfg.paths["data"].glob("**/*.csv")):
             self.active_features["data_profiling"] = True
             
        if any(self.cfg.paths["notebooks"].glob("*.ipynb")):
            self.active_features["notebook_analysis"] = True

    def get_ground_truth(self):
        """
        Scans KMDS documents and data directories, ensuring full schema metrics
        are written without triggering internal pandas profiling type-errors.
        """
        truth = []
        
        # 1. Ingest text instructions from your KMDS 'documents' folder
        for txt in self.cfg.paths["documents"].glob("*.txt"):
            try:
                with open(txt, 'r', encoding='utf-8') as f:
                    truth.append({"source": txt.name, "type": "doc", "content": f.read()[:5000]})
            except Exception as e:
                print(f"[-] Failed reading text asset {txt.name}: {e}")

        # 2. Tabular Data Schema Profiling
        for csv_path in self.cfg.paths["data"].glob("**/*.csv"):
            if str(self.cfg.paths["output"].resolve()) in str(csv_path.resolve()):
                continue
                
            try:
                print(f"🔬 [PROFILER] Parsing file structure for {csv_path.name}...")
                
                # Step A: Native CSV stream lookahead to extract absolute raw headers
                with open(csv_path, 'r', encoding='utf-8-sig') as f:
                    sample = f.readline()
                    delimiter = ';' if ';' in sample else ','
                    f.seek(0)
                    reader = native_csv.reader(f, delimiter=delimiter)
                    columns_found = next(reader)
                
                # Trim quotation tokens and whitespaces cleanly
                columns_found = [c.strip().strip('"').strip("'") for c in columns_found if c.strip()]

                # Step B: Read Data Sample using standard pandas mapping engine
                df = pd.read_csv(
                    csv_path, 
                    header=0, 
                    names=columns_found, 
                    nrows=100, 
                    low_memory=False,
                    on_bad_lines='skip'
                )
                
                # Step C: Generate Type Insights explicitly using standard DataFrame analysis
                # This guarantees full column tracking without crashing on complex data rows
                type_insights = {}
                for col in df.columns:
                    # Cleanly deduce column profiling metric categories natively
                    if pd.api.types.is_numeric_dtype(df[col]):
                        type_insights[col] = "Numeric"
                    elif pd.api.types.is_bool_dtype(df[col]):
                        type_insights[col] = "Boolean"
                    elif pd.api.types.is_datetime64_any_dtype(df[col]):
                        type_insights[col] = "DateTime"
                    else:
                        type_insights[col] = "Categorical"

                truth.append({
                    "source": csv_path.name,
                    "type": "physical_schema",
                    "columns": list(df.columns),
                    "data_types": type_insights
                })
                print(f"✅ [PROFILER] Extracted all {len(df.columns)} active schema parameters.")
                
            except Exception as e:
                print(f"[-] Profile extraction failed for {csv_path.name}: {e}")
                
        return truth

    def read_notebook(self, nb_path):
        """Parses .ipynb files into markdown and code chunks."""
        with open(nb_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        return {
            "markdown": [c.source for c in nb.cells if c.cell_type == 'markdown'],
            "code": [c.source for c in nb.cells if c.cell_type == 'code']
        }
