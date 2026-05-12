import os
import yaml
import json
from pathlib import Path
from ollama import Client

class LLMClient:
    """
    Handles persona-based prompting by discovering YAML files in the personas/ folder.
    """
    def __init__(self, config_path="data", model="qwen2.5-coder:7b"):
        self.client = Client(host='http://localhost:11434')
        self.model = model
        self.workspace = Path(config_path)

    def get_available_personas(self) -> list[str]:
        """
        Scans the personas/ directory for .yaml files.
        Returns the exact display names used for filtering in tests.
        """
        persona_dir = self.workspace / "personas"
        if not persona_dir.exists():
            return []
        
        # Maps 'tech_lead.yaml' -> 'Tech Lead'
        return [
            f.stem.replace('_', ' ').title() 
            for f in persona_dir.glob("*.yaml")
        ]

    def call_persona(self, persona_display_name: str, context: str, stats: str) -> str:
        """
        Loads the specific YAML file for a persona and executes the LLM call.
        """
        # Ensure we look for 'tech_lead.yaml' even if passed 'Tech Lead'
        file_name = persona_display_name.lower().replace(" ", "_") + ".yaml"
        persona_path = self.workspace / "personas" / file_name

        if not persona_path.exists():
            return json.dumps({
                "error": f"Persona config not found at {persona_path}",
                "persona": persona_display_name
            })

        try:
            with open(persona_path, 'r') as f:
                config = yaml.safe_load(f)
            
            system_prompt = config.get('system_prompt', '')
            if not system_prompt:
                return json.dumps({"error": f"No system_prompt found in {file_name}"})

            # Placeholder replacement
            final_prompt = system_prompt.replace("{context}", context).replace("{stats}", stats)

            # JSON-formatted generation
            response = self.client.generate(
                model=self.model,
                prompt=final_prompt,
                format="json",
                options={"num_ctx": 8192}
            )

            return response.get('response', '{}')

        except Exception as e:
            return json.dumps({
                "error": f"LLM Generation Failed: {str(e)}",
                "persona": persona_display_name
            })
