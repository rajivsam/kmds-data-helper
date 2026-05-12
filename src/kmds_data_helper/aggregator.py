import asyncio
import json
from typing import Dict, Any
from .llm_client import LLMClient  # Adjust import based on your final structure

class PersonaAggregator:
    """
    The primary entry point for KMDS Data Helper.
    Discovers all personas and runs parallel audits to generate a 
    consolidated knowledge dictionary.
    """
    def __init__(self, workspace_path: str, max_concurrent: int = 2):
        self.client = LLMClient(config_path=workspace_path)
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def _audit_task(self, persona: str, context: str, stats: str) -> Dict[str, Any]:
        """Internal task to handle a single persona audit with safety limits."""
        async with self.semaphore:
            raw_response = await asyncio.to_thread(
                self.client.call_persona, persona, context, stats
            )
            try:
                return json.loads(raw_response)
            except json.JSONDecodeError:
                return {"error": "JSON_PARSE_FAILURE", "raw": raw_response}

    async def collect_summaries(self, context: str, stats: str) -> Dict[str, Any]:
        """
        Runs all discovered personas in parallel and returns a dictionary 
        indexed by Persona Name.
        """
        personas = self.client.get_available_personas()
        
        # Build tasks
        task_map = {
            p: self._audit_task(p, context, stats) 
            for p in personas
        }
        
        # Execute concurrently
        results = await asyncio.gather(*task_map.values())
        
        # Return composite object: { "Scientist": {...}, "Tech Lead": {...} }
        return dict(zip(task_map.keys(), results))
