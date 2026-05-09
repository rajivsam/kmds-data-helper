import os
import yaml
from pathlib import Path

class KMDSConfigManager:
    def __init__(self, config_path="kmds_config.yaml"):
        # Anchor to project root (assumes this file is in src/kmds_data_helper/)
        self.root = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
        self.paths = {
            "docs": self.root / self.config['directories']['documents'].replace("../", ""),
            "data": self.root / self.config['directories']['data'].replace("../", ""),
            "notebooks": self.root / self.config['directories']['notebooks'].replace("../", ""),
            "output": self.root / self.config['directories']['output'].replace("../", "")
        }
        
        # Ensure output isolation directory exists
        self.paths["output"].mkdir(parents=True, exist_ok=True)

    def get_persona(self, role):
        return self.config['personas'].get(role, {})
