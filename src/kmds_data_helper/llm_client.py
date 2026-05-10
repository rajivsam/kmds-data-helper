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
        self.cfg = ConfigManager(config_path)

    def call_persona(self, persona: str, context: str, stats: str) -> str:
        """
        Fetches system prompt from YAML and generates response.
        Uses string replacement to avoid KeyError with literal JSON braces.
        """
        persona_data = self.cfg.get_persona(persona)
        system_prompt = persona_data['system_prompt']
        
        # FIX: Manual replacement instead of .format() to avoid curly brace errors
        prompt = system_prompt.replace("{context}", context).replace("{stats}", stats)

        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                format="json",  # Instructs Ollama to use JSON mode
                options={"num_ctx": 8192} 
            )

            return response.get('response', '{}')

        except Exception as e:
            return json.dumps({
                "error": f"LLM Generation Failed: {str(e)}", 
                "quality_score": 0, 
                "insight": "N/A"
            })
