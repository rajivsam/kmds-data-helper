import importlib.resources as pkg_resources
from pathlib import Path
from typing import Optional, List, Any, Dict
import json
import asyncio
import sys
import yaml
from .engine import KMDSEngine 
from .config_manager import ConfigManager
from .data_processor import KMDSDataProcessor
from .kmds_check import check_project_structure

class KMDSReportService:
    """
    Service layer for KMDS. Coordinates lifecycle operations by leveraging
    the ConfigManager abstraction layer across all sub-components.
    """
    
    REPO_URL = "github.com"

    def __init__(self, llm_client, config_path: Optional[str] = None, output_dir: str = "output"):
        # 1. Instantiate the Central Abstraction Layer Immediately
        resolved_path = Path(config_path) if config_path else self._get_default_data_path()
        workspace_dir = resolved_path if resolved_path.is_dir() else resolved_path.parent
        
        self.config_manager = ConfigManager(workspace_path=str(workspace_dir))
        self.config_dir = self.config_manager.workspace
        self.config_file = self.config_manager.config_path

        # 2. Server-safe Structural Check (Intercepts sys.exit from killing Uvicorn)
        self._run_structural_baseline_check()

        # 3. Transparent, Unmasked Dataset Profile Extraction
        self._execute_dataset_profiler()

        # 4. Perform 5-Pillar Statistical Health Check
        self._validate_and_summarize_config()

        # 5. Setup Infrastructure & Engine
        self.output_dir = self.config_manager.paths["output"]
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.engine = KMDSEngine(llm_client, config_dir=self.config_dir, config_file=self.config_file)
        self.llm_client = llm_client

    def _run_structural_baseline_check(self):
        """
        Intercepts sys.exit calls inside kmds_check to keep the API server alive.
        """
        print("🔍 [PRE-FLIGHT] Verifying structural 5-Pillar baseline integrity via kmds_check...")
        try:
            original_exit = sys.exit
            def mock_exit(code):
                if code != 0:
                    raise ValueError(f"kmds-check reported workspace failure code: {code}")
                raise StopIteration()
                
            sys.exit = mock_exit
            try:
                check_project_structure(str(self.config_dir.resolve()))
            except StopIteration:
                print("✅ [PRE-FLIGHT] Directory architecture verified via kmds_check.")
            finally:
                sys.exit = original_exit
        except Exception as e:
            raise ValueError(f"KMDS structural check triggered verification failure: {e}")

    def _execute_dataset_profiler(self):
        """
        Passes the complete ConfigManager directly to KMDSDataProcessor.
        Errors are left unmasked so they surface clearly in the terminal output.
        """
        print("📊 [PRE-FLIGHT] Compiling grounding insights via KMDSDataProcessor...")
        processor = KMDSDataProcessor(config_manager=self.config_manager)
        ground_truth = processor.get_ground_truth()
        
        if ground_truth:
            report_target = self.config_manager.paths["documents"] / "dataprofiler_baseline_report.json"
            with open(report_target, 'w', encoding='utf-8') as f:
                json.dump(ground_truth, f, indent=4)
            print(f"✅ [PRE-FLIGHT] Baseline telemetry written cleanly to: {report_target.name}")
        else:
            print("[INFO] No profiling metrics extracted.")

    def _validate_and_summarize_config(self):
        """STRICT VALIDATION: Confirms existence of folders and files via ConfigManager paths."""
        validation_map = {
            "notebooks": ("notebooks", "*.ipynb"),
            "personas": ("personas", "*.yaml"),
            "documents": ("documents", "*"), 
            "data_dictionary": ("data_dictionary", "*"),
            "data": ("data", "*") 
        }
        
        errors = []
        summary = {}

        for pillar, (path_key, pattern) in validation_map.items():
            target_path = self.config_manager.paths[path_key]
            
            if not target_path.exists() or not target_path.is_dir():
                errors.append(f"MISSING DIRECTORY: '{target_path.name}/' must exist at {target_path.parent.resolve()}")
                continue
            
            files = list(target_path.glob(pattern))
            if not files and pillar in ["notebooks", "personas"]:
                errors.append(f"EMPTY DATA: '{target_path.name}/' exists but has no valid tracking units.")
            else:
                summary[pillar] = len(files)

        if errors:
            print(f"\n{'!'*70}\nKMDS STRUCTURE VALIDATION FAILED\n{'!'*70}")
            for err in errors:
                print(f" -> {err}")
            raise ValueError("Directory structure validation failed. Audit aborted.")

        print(f"--- KMDS Structure Verified ---")
        for folder, count in summary.items():
            print(f" - {folder.capitalize()}: {count} file(s) identified.")
        print("-" * 31 + "\n")

    def _get_default_data_path(self) -> Path:
        try:
            return pkg_resources.files("kmds_data_helper") / "data"
        except Exception:
            return Path("data")

    async def run_audit(self, 
                        notebook_paths: Optional[List[str]] = None, 
                        requested_personas: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Asynchronous entry point that supports subset filtering of notebooks and personas."""
        if not notebook_paths:
            nb_dir = self.config_manager.paths["notebooks"]
            notebook_paths = [str(p.resolve()) for p in nb_dir.glob("*.ipynb")]
            
        if not notebook_paths:
            return []

        available_personas = self.llm_client.get_available_personas()
        
        if requested_personas:
            active_personas = [p for p in requested_personas if p in available_personas]
            if not active_personas:
                raise ValueError(f"None of the requested personas {requested_personas} were found.")
        else:
            active_personas = available_personas
            
        tasks = []
        for path in notebook_paths:
            for persona in active_personas:
                tasks.append(self.engine.analyze_notebook_persona(path, persona))
        
        return await asyncio.gather(*tasks)
