import importlib.resources as pkg_resources
from pathlib import Path
from typing import Optional, List
import yaml
from .engine import KMDSEngine 

class KMDSReportService:
    """
    Service layer for KMDS. Handles configuration discovery, 
    validation, and orchestration of the KMDSEngine.
    """
    
    REPO_URL = "https://github.com"

    def __init__(self, llm_client, config_path: Optional[str] = None, output_dir: str = "output"):
        # 1. Resolve Pathing
        path = Path(config_path) if config_path else self._get_default_data_path()
        
        if path.is_dir():
            self.config_dir = path
            self.config_file = path / "kmds_config.yaml"
        else:
            self.config_dir = path.parent
            self.config_file = path

        # 2. Validate the 5-Pillar Structure
        self._validate_and_summarize_config()

        # 3. Setup Infrastructure
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 4. Initialize Engine
        self.engine = KMDSEngine(llm_client, config_dir=self.config_dir, config_file=self.config_file)

    def _validate_and_summarize_config(self):
        """
        STRICT VALIDATION: Confirms existence of folders and correct file types.
        Supports: notebooks, personas, documents, data_dictionary, and data.
        """
        validation_map = {
            "notebooks": "*.ipynb",
            "personas": "*.yaml",
            "documents": "*.pdf",
            "data_dictionary": "*",
            "data": "*" 
        }
        
        errors = []
        summary = {}

        for folder, pattern in validation_map.items():
            target_path = self.config_dir / folder
            
            # 1. Existence Check
            if not target_path.exists() or not target_path.is_dir():
                errors.append(f"MISSING DIRECTORY: '{folder}/' must exist in {self.config_dir.resolve()}")
                continue
            
            # 2. File Type & Content Check
            files = list(target_path.glob(pattern))
            
            # Allow 'data' and 'data_dictionary' to be empty if just starting, 
            # but notebooks and personas are mandatory for an audit.
            if not files and folder in ["notebooks", "personas"]:
                errors.append(f"EMPTY/REQUIRED DATA: '{folder}/' exists but has no {pattern} files.")
            else:
                summary[folder] = len(files)

        if errors:
            print(f"\n{'!'*70}\nKMDS STRUCTURE VALIDATION FAILED\n{'!'*70}")
            for err in errors:
                print(f" -> {err}")
            print(f"\nREQUIRED LAYOUT:\n{self.config_dir.resolve()}/\n  ├── notebooks/ (.ipynb)\n  ├── personas/ (.yaml)\n  ├── documents/ (.pdf)\n  ├── data_dictionary/ (meta-data)\n  └── data/ (csv/parquet)\n{'!'*70}\n")
            raise ValueError("Directory structure validation failed. Audit aborted.")

        # Success Summary
        print(f"--- KMDS Structure Verified ---")
        for folder, count in summary.items():
            print(f" - {folder.capitalize()}: {count} file(s) identified.")
        print("-" * 31 + "\n")

    def _get_default_data_path(self) -> Path:
        try:
            return pkg_resources.files("kmds_data_helper") / "data"
        except Exception:
            return Path("data")

    async def run_full_audit(self, notebook_paths: Optional[List[str]] = None):
        """Asynchronous entry point for FastAPI."""
        if not notebook_paths:
            # Force absolute pathing to find the notebooks reliably
            nb_dir = (self.config_dir / "notebooks").resolve()
            notebook_paths = [str(p) for p in nb_dir.glob("*.ipynb")]
            
        if not notebook_paths:
            return []
            
        return await self.engine.run_full_audit_async(notebook_paths)
