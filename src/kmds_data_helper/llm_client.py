import json
from ollama import Client
from kmds_data_helper.config_manager import ConfigManager

class LLMClient:
    """
    Standardized LLM client for the KMDS Data Helper.
    Handles persona-based prompting and JSON enforcement.
    """
    def __init__(self, config_path="kmds_config.yaml", model="qwen2.5-coder:7b"):
        self.client = Client(host='http://localhost:11434')
        self.model = model
        # Store the path so we can update it if needed
        self.config_path = config_path
        self.cfg = ConfigManager(self.config_path)

    def set_config_path(self, new_path: str):
        """
        Updates the ConfigManager to point to a new workspace.
        This fixes the 'list indices' error by ensuring personas are found.
        """
        self.config_path = new_path
        self.cfg = ConfigManager(new_path)

    def call_persona(self, persona: str, context: str, stats: str) -> str:
        """
        Fetches system prompt from YAML and generates response.
        """
        persona_data = self.cfg.get_persona(persona)
        
        # Validation: If the persona wasn't found, return an error JSON
        if not persona_data or 'system_prompt' not in persona_data:
            return json.dumps({"error": f"Persona {persona} not found in {self.config_path}"})

        system_prompt = persona_data['system_prompt']
        
        # Manual replacement to avoid curly brace errors in JSON
        prompt = system_prompt.replace("{context}", context).replace("{stats}", stats)

        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                format="json", 
                options={"num_ctx": 8192} 
            )

            return response.get('response', '{}')

        except Exception as e:
            return json.dumps({
                "error": f"LLM Generation Failed: {str(e)}", 
                "quality_score": 0, 
                "insight": "N/A"
            })
