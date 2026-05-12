import asyncio
import nbformat
import json
import os
from pathlib import Path
from pypdf import PdfReader
from typing import Dict, List, Any
from .llm_client import LLMClient

class KMDSEngine:
    """
    Orchestrates the KMDS audit by ingesting notebooks, documents, and data 
    context, then applying discovered personas via a VRAM-safe loop.
    """
    def __init__(self, llm_client: LLMClient, config_dir: Path, config_file: Path):
        self.llm_client = llm_client
        self.config_dir = config_dir
        # Limit to 1 concurrent LLM call to protect 6GB VRAM
        self.semaphore = asyncio.Semaphore(1)

    def _load_notebook(self, path: str) -> str:
        """Extracts code and markdown from .ipynb files."""
        with open(path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        return "\n\n".join([c.source for c in nb.cells if c.cell_type in ['code', 'markdown']])

    def _load_context_docs(self) -> str:
        """Gathers context from Data Dictionary, Documents, and Data inventory."""
        context_parts = []
        
        # 1. Metadata (Data Dictionary)
        dict_path = self.config_dir / "data_dictionary"
        if dict_path.exists():
            for f in dict_path.glob("*"):
                if f.is_file():
                    context_parts.append(f"DATA DICTIONARY ({f.name}):\n{f.read_text()[:1500]}")

        # 2. Supporting Docs (PDFs)
        doc_path = self.config_dir / "documents"
        if doc_path.exists():
            for f in doc_path.glob("*.pdf"):
                try:
                    reader = PdfReader(str(f))
                    text = " ".join([p.extract_text() for p in reader.pages[:3]])
                    context_parts.append(f"SUPPORTING DOCUMENT ({f.name}):\n{text}")
                except Exception as e:
                    print(f"[WARN] Failed to read PDF {f.name}: {e}")

        # 3. Data Inventory (Raw files available to the notebooks)
        data_path = self.config_dir / "data"
        if data_path.exists():
            data_files = [f.name for f in data_path.glob("*") if f.is_file()]
            if data_files:
                context_parts.append(f"AVAILABLE DATASETS ON DISK: {', '.join(data_files)}")

        return "\n\n".join(context_parts)

    async def analyze_notebook_persona(self, nb_path: str, persona_name: str) -> Dict[str, Any]:
        """Preps context and executes LLM call with VRAM protection."""
        context = self._load_notebook(nb_path)
        stats = self._load_context_docs()
        
        async with self.semaphore:
            # Python 3.12+ Tweak: Use get_running_loop for stability in active coroutines
            loop = asyncio.get_running_loop()
            resp_str = await loop.run_in_executor(
                None, self.llm_client.call_persona, persona_name, context, stats
            )
            
            try:
                # Handle cases where LLM might return a dict or string
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
        """Orchestrates all discovered personas against all found notebooks."""
        # Dynamically find personas available in the personas/ folder
        personas = self.llm_client.get_available_personas()
        
        tasks = []
        for path in notebook_paths:
            for persona in personas:
                tasks.append(self.analyze_notebook_persona(path, persona))
        
        # Parallel execution, sequential GPU usage via Semaphore
        return await asyncio.gather(*tasks)
