import json
from typing import Dict, Any, List

class PersonaAggregator:
    """
    Knowledge Dictionary Builder.
    Consolidates individual persona reports into a single grounded 
    knowledge base for strategic synthesis.
    """
    def __init__(self):
        # Stores the grounded findings for the full project
        self.knowledge_dict: Dict[str, Any] = {}

    def add_audit_result(self, result: Dict[str, Any]):
        """
        Ingests a result from KMDSEngine and maps it to the knowledge dictionary.
        Input format: {"notebook": "...", "persona": "...", "analysis": {...}}
        """
        persona = result.get("persona")
        notebook = result.get("notebook")
        data = result.get("analysis", {})

        # Grounding Safeguard: Only aggregate successful, non-error findings
        if "error" not in data:
            if persona not in self.knowledge_dict:
                self.knowledge_dict[persona] = {}
            
            # Index findings by notebook for multi-notebook project tracking
            self.knowledge_dict[persona][notebook] = data

    def get_grounded_stats(self) -> str:
        """
        Formats the current knowledge dictionary into a string for the 
        Strategic Lead's RUN_STATS input.
        """
        if not self.knowledge_dict:
            return "NO PRIOR AUDIT EVIDENCE FOUND."

        summary = "KMDS GROUNDED EVIDENCE DICTIONARY:\n"
        for persona, notebooks in self.knowledge_dict.items():
            for nb_name, findings in notebooks.items():
                summary += f"[{persona}] Evidence from {nb_name}: {json.dumps(findings)}\n"
        
        return summary
