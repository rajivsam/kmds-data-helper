import yaml
from pathlib import Path

class ConfigManager:
    """
    Handles loading and retrieving persona configurations from kmds_config.yaml.
    """
    def __init__(self, config_path: str = "kmds_config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self):
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found at {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def get_persona(self, role: str):
        """Retrieves a specific persona's prompt and mode."""
        personas = self.config.get('personas', {})
        if role not in personas:
            raise ValueError(f"Persona '{role}' not found in configuration.")
        return personas[role]

    def get_directories(self):
        return self.config.get('directories', {})

    def get_engine_settings(self):
        return self.config.get('engine_settings', {})
