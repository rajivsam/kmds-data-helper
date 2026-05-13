import os
import yaml
import json
from pathlib import Path
from ollama import Client

class LLMClient:
    """
    Handles persona-based prompting with strict character lockdown, XML isolation,
    and automatic real-time schema compliance verification loop guardrails.
    """
    def __init__(self, config_path="data", model="qwen2.5-coder:7b"):
        self.client = Client(host='http://localhost:11434')
        self.model = model
        self.workspace = Path(config_path)

    def get_available_personas(self) -> list[str]:
        persona_dir = self.workspace / "personas"
        if not persona_dir.exists():
            return []
        return [f.stem.replace('_', ' ').title() for f in persona_dir.glob("*.yaml")]

    def _execute_chat(self, system_instruction: str, user_prompt: str) -> str:
        """Helper to run the core Ollama chat block."""
        response = self.client.chat(
            model=self.model,
            format="json",
            messages=[
                {'role': 'system', 'content': system_instruction},
                {'role': 'user', 'content': user_prompt}
            ],
            options={
                "num_ctx": 8192,
                "temperature": 0.0
            }
        )
        return response.get('message', {}).get('content', '{}')

    def call_persona(self, persona_display_name: str, context: str, stats: str) -> str:
        file_name = persona_display_name.lower().replace(" ", "_") + ".yaml"
        persona_path = self.workspace / "personas" / file_name

        if not persona_path.exists():
            return json.dumps({"error": f"Persona config not found", "persona": persona_display_name})

        try:
            with open(persona_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            base_system_instruction = config.get('system_prompt', '')
            
            system_instruction = (
                f"{base_system_instruction}\n\n"
                "CRITICAL ENFORCEMENT:\n"
                "- You must ONLY respond using your requested JSON schema keys.\n"
                "- Do NOT copy external role profile structures from text cells."
            )

            try:
                stats_dict = json.loads(stats)
                dict_content = stats_dict.get("data_dictionary_content", "")
                docs_content = stats_dict.get("supporting_documentation_content", "")
                inv_content = stats_dict.get("data_disk_inventory", "")
            except Exception:
                dict_content, docs_content, inv_content = "", stats, ""

            user_prompt = (
                "### CRITICAL OPERATING PARAMETERS\n"
                "1. Treat <notebook_code> as your PRIMARY evidence source.\n"
                "2. Your output MUST strictly match the requested JSON layout.\n\n"
                f"<notebook_code>\n{context}\n</notebook_code>\n\n"
                f"<data_dictionary>\n{dict_content}\n</data_dictionary>\n\n"
                f"<supporting_docs>\n{docs_content}\n</supporting_docs>\n\n"
                f"<data_inventory>\n{inv_content}\n</data_inventory>\n\n"
                "TASK: Perform your persona analysis strictly on the notebook code using the provided schema rules."
            )

            # --- PASS 1 ---
            raw_content = self._execute_chat(system_instruction, user_prompt)
            
            # --- SCHEMA COMPLIANCE CHECK ---
            try:
                parsed_res = json.loads(raw_content)
                # If the keys match the rogue profile instead of your persona schemas, trigger a fallback correction pass
                if "persona" in parsed_res or "skills" in parsed_res:
                    print(f"⚠️  [GUARD] Detected schema hijacking for {persona_display_name}. Retrying with strict enforcement...")
                    
                    retry_system = (
                        f"{base_system_instruction}\n\n"
                        "⚠️ EXTRA WARNING: You previously failed the task by outputting a generic data scientist role block. "
                        "Do NOT write 'persona', 'skills', or 'goals' keys under any circumstances. "
                        "You must strictly return the objective audit keys requested in your schema."
                    )
                    # --- PASS 2 (Self-Correcting Retry) ---
                    raw_content = self._execute_chat(retry_system, user_prompt)
            except Exception:
                pass # Let the downstream json loops catch parsing faults naturally

            return raw_content

        except Exception as e:
            return json.dumps({"error": f"LLM Generation Failed: {str(e)}", "persona": persona_display_name})
