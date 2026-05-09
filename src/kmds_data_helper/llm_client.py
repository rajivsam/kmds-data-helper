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
        # 1. Formatting ensures context/stats are injected correctly
        prompt = persona_data['system_prompt'].format(**kwargs)

        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                format="json",  # Instructs Ollama to use JSON mode
                options={"num_ctx": 8192} 
            )

            # 2. Safety check: ensure response is not empty
            if not response.get('response'):
                return {"error": "Empty response from model", "role": role}

            return json.loads(response['response'])

        except json.JSONDecodeError:
            # The "Shield" fallback if JSON is malformed
            return {"error": "Invalid JSON returned", "raw": response.get('response', '')}
        except Exception as e:
            return {"error": str(e), "role": role}
