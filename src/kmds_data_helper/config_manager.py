import yaml
from pathlib import Path
from typing import Dict, Any

class ConfigManager:
    """
    The central source of truth for the KMDS Workspace configuration.
    Resolves explicit layout directory maps from kmds_config.yaml.
    """
    def __init__(self, workspace_path: str = "."):
        self.workspace = Path(workspace_path)
        self.config_path = self.workspace / "kmds_config.yaml"
        self.config = self._load_config()
        
        # Centralized pathing map: Separates KMDS 'documents' from Sphinx 'docs'
        self.paths = {
            "notebooks": self.get_directory_path("notebooks"),
            "personas": self.get_directory_path("personas"),
            "documents": self.get_directory_path("documents"), 
            "data_dictionary": self.get_directory_path("data_dictionary"),
            "data": self.get_directory_path("data"),
            "sphinx_docs": self.workspace / "docs", # Isolated Sphinx tree
            "output": self.workspace / "output"
        }

    def _load_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            return {}
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}

    def get_directory_path(self, key: str) -> Path:
        """Resolves the configured folder path against the workspace root."""
        dirs = self.config.get("directories", {})
        fallback_map = {
            "notebooks": "notebooks",
            "personas": "personas",
            "documents": "documents",
            "data_dictionary": "data_dictionary",
            "data": "data"
        }
        folder_name = dirs.get(key, fallback_map.get(key, key))
        return self.workspace / folder_name
