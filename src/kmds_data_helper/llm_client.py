import json
from ollama import Client


class LLMInterface:
    def __init__(self, config_manager, model="qwen2.5-coder:7b"):
        self.client = Client(host='http://localhost:11434')
        self.model = model
        self.cfg = config_manager

    def ask_persona(self, role, **kwargs):
        """Fetches system prompt from YAML and generates response."""
        persona_data = self.cfg.get_persona(role)
        # Injects context/stats into the YAML's system_prompt string
        prompt = persona_data['system_prompt'].format(**kwargs)

        response = self.client.generate(
            model=self.model,
            prompt=prompt,
            format="json",
            options={"num_ctx": 8192}  # Give the Tech Lead more "memory"
        )

        return json.loads(response['response'])
