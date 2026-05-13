import yaml
from pathlib import Path
from typing import Dict, Any

class ConfigManager:
    """
    Handles explicit workspace directory maps from kmds_config.yaml.
    Acts as the source of truth for the 5-Pillar storage locations.
    """
    def __init__(self, workspace_path: str = "."):
        self.workspace = Path(workspace_path)
        self.config_path = self.workspace / "kmds_config.yaml"
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            # Safe structural fallback mapping to your workspace root directory listing
            return {
                "directories": {
                    "notebooks": "notebooks",
                    "personas": "personas",
                    "documents": "documents",
                    "data_dictionary": "data_dictionary",
                    "data": "data"
                }
            }
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}

    def get_directory_path(self, key: str) -> Path:
        """Resolves the configured folder path against the workspace root."""
        dirs = self.config.get("directories", {})
        # Use fallback map matching your root 'ls' output
        fallback_map = {
            "notebooks": "notebooks",
            "personas": "personas",
            "documents": "documents",
            "data_dictionary": "data_dictionary",
            "data": "data"
        }
        folder_name = dirs.get(key, fallback_map.get(key, key))
        return self.workspace / folder_name
