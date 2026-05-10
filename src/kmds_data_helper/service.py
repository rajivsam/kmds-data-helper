import importlib.resources as pkg_resources
from pathlib import Path
from typing import Optional, List
import yaml
# Assuming engine.py is in the same directory
from .engine import KMDSEngine 

class KMDSReportService:
    """
    Service layer for KMDS. Handles configuration discovery, 
    validation, and orchestration of the KMDSEngine.
    """
    
    # The source of truth for developers to check the spec
    REPO_URL = "https://github.com"

    def __init__(self, llm_client, config_path: Optional[str] = None, output_dir: str = "output"):
        """
        Initializes the service.
        
        :param llm_client: The LLM client instance (e.g., OpenAI, Anthropic).
        :param config_path: Path to a directory (e.g., 'data2') or a specific 
                           YAML file. Falls back to package defaults if None.
        :param output_dir: Where generated reports will be stored.
        """
        # 1. Resolve Pathing
        path = Path(config_path) if config_path else self._get_default_data_path()
        
        if path.is_dir():
            self.config_dir = path
            self.config_file = path / "kmds_config.yaml"
        else:
            self.config_dir = path.parent
            self.config_file = path

        # 2. Validate & Complain (Feature 2)
        self._validate_and_summarize_config()

        # 3. Setup Infrastructure
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 4. Initialize Engine (Feature 1)
        self.engine = KMDSEngine(llm_client, config_dir=self.config_dir, config_file=self.config_file)

    def _validate_and_summarize_config(self):
        """
        Ensures the environment is ready. If not, provides a diagnostic 
        report with a link to the repo spec.
        """
        errors = []

        # Check: Does the YAML file exist?
        if not self.config_file.exists():
            errors.append(f"CONFIG NOT FOUND: Expected file at {self.config_file.absolute()}")

        # Check: Is the mandatory 'notebooks' folder present?
        notebooks_path = self.config_dir / "notebooks"
        if not notebooks_path.exists() or not notebooks_path.is_dir():
            errors.append(f"MISSING DIRECTORY: 'notebooks/' folder is required in {self.config_dir.absolute()}")
        elif not list(notebooks_path.glob("*.ipynb")):
            errors.append(f"NO DATA: 'notebooks/' exists but contains no .ipynb files.")

        if errors:
            print(f"\n{'!'*70}")
            print("KMDS CONFIGURATION ERROR")
            print(f"{'!'*70}")
            for err in errors:
                print(f" ERROR: {err}")
            print(f"\nHOW TO FIX:")
            print(f" 1. Ensure your config directory (e.g., 'data2') follows the expected structure.")
            print(f" 2. Check the correct YAML spec and folder layout at:")
            print(f"    {self.REPO_URL}")
            print(f"{'!'*70}\n")
            raise ValueError("KMDS failed to initialize. See diagnostic report above.")

        # Success Summary
        nb_count = len(list(notebooks_path.glob("*.ipynb")))
        print(f"--- KMDS Audit Initialized ---")
        print(f"Config Home: {self.config_dir.name}")
        print(f"Active Spec: {self.config_file.name}")
        print(f"Resources:   {nb_count} notebook(s) found for analysis.")
        print(f"------------------------------\n")

    def _get_default_data_path(self) -> Path:
        """Finds the 'data' folder inside the installed package."""
        try:
            # For Python 3.9+ using importlib.resources
            return pkg_resources.files("kmds_data_helper") / "data"
        except (ImportError, AttributeError, TypeError):
            # Fallback for local development
            return Path("data")

    def run_full_audit(self, notebook_paths: Optional[List[str]] = None):
        """Standard entry point for a complete multi-persona audit."""
        if not notebook_paths:
            nb_dir = self.config_dir / "notebooks"
            notebook_paths = [str(p) for p in nb_dir.glob("*.ipynb")]
            
        return self.engine.run_audit(notebook_paths)
