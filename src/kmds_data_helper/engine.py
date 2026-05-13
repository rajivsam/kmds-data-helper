import asyncio
import nbformat
import json
import os
import yaml
from pathlib import Path
from pypdf import PdfReader
from typing import Dict, List, Any
from .llm_client import LLMClient
from .utils import parse_notebook_with_outputs

class KMDSEngine:
    """
    Orchestrates the KMDS audit with strict context separation to prevent 
    document content leaking over notebook execution code.
    """
    def __init__(self, llm_client: LLMClient, config_dir: Path, config_file: Path):
        self.llm_client = llm_client
        self.config_dir = config_dir
        self.config_file = config_file
        # CRITICAL VRAM GUARD: Limits execution to 1 concurrent GPU process
        self.semaphore = asyncio.Semaphore(1)

    def _get_explicit_path(self, pillar_key: str, default_name: str) -> Path:
        """Reads kmds_config.yaml to extract custom path overrides dynamically."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    cfg = yaml.safe_load(f) or {}
                directories = cfg.get("directories", {})
                if pillar_key in directories:
                    return self.config_dir / directories[pillar_key]
            except Exception as e:
                print(f"[WARN] Error reading config file mapping: {e}")
        return self.config_dir / default_name

    def _load_data_dictionary(self) -> str:
        dict_path = self._get_explicit_path("data_dictionary", "data_dictionary")
        parts = []
        if dict_path.exists():
            for f in dict_path.glob("*"):
                if f.is_file() and not f.name.startswith('.'):
                    parts.append(f"--- File: {f.name} ---\n{f.read_text(encoding='utf-8')[:1500]}")
        return "\n".join(parts) if parts else "No data dictionary files identified."

    def _load_documents(self) -> str:
        """Loads context from both PDFs and Markdown documentation files."""
        doc_path = self._get_explicit_path("documents", "documents")
        if not doc_path.exists():
            doc_path = self.config_dir / "docs"
        
        parts = []
        if doc_path.exists():
            # 1. Process all PDF assets
            for f in doc_path.glob("*.pdf"):
                try:
                    reader = PdfReader(str(f))
                    text = " ".join([p.extract_text() for p in reader.pages[:3]])
                    parts.append(f"--- Document (PDF): {f.name} ---\n{text}")
                except Exception as e:
                    print(f"[WARN] Failed to read PDF {f.name}: {e}")
            
            # 2. NEW: Process all Markdown guidance assets
            for f in doc_path.glob("*.md"):
                try:
                    # Read markdown files directly as text strings
                    text = f.read_text(encoding='utf-8')[:4000]
                    parts.append(f"--- Document (Markdown): {f.name} ---\n{text}")
                except Exception as e:
                    print(f"[WARN] Failed to read Markdown asset {f.name}: {e}")
                    
        return "\n\n".join(parts) if parts else "No tracking documentation files identified."

    def _load_data_inventory(self) -> str:
        data_path = self._get_explicit_path("data", "data")
        if data_path.exists():
            files = [f.name for f in data_path.glob("*") if f.is_file() and not f.name.startswith('.')]
            if files:
                return f"Available datasets on disk: {', '.join(files)}"
        return "No trackable files located on disk data partition."

    async def analyze_notebook_persona(self, nb_path: str, persona_name: str) -> Dict[str, Any]:
        """Preps structured, bounded context blocks and executes LLM call."""
        notebook_code = parse_notebook_with_outputs(nb_path) 
        
        # Build strict, non-leaking dictionary statistics block
        stats_payload = {
            "data_dictionary_content": self._load_data_dictionary(),
            "supporting_documentation_content": self._load_documents(),
            "data_disk_inventory": self._load_data_inventory()
        }
        
        # Convert statistics payload into standard JSON string to isolate it cleanly
        project_stats_str = json.dumps(stats_payload, indent=2)
        
        async with self.semaphore:
            loop = asyncio.get_running_loop()
            resp_str = await loop.run_in_executor(
                None, self.llm_client.call_persona, persona_name, notebook_code, project_stats_str
            )
            
            try:
                result = json.loads(resp_str) if isinstance(resp_str, str) else resp_str
                return {
                    "notebook": Path(nb_path).name,
                    "persona": persona_name,
                    "analysis": result
                }
            except Exception as e:
                return {
                    "error": "JSON Parse Failure",
                    "persona": persona_name,
                    "notebook": Path(nb_path).name,
                    "raw": str(resp_str)
                }

    async def run_full_audit_async(self, notebook_paths: List[str]) -> List[Dict[str, Any]]:
        personas = self.llm_client.get_available_personas()
        tasks = []
        for path in notebook_paths:
            for persona in personas:
                tasks.append(self.analyze_notebook_persona(path, persona))
        return await asyncio.gather(*tasks)
