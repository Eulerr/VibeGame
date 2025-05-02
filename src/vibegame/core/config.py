"""Game configuration handling."""

import json
from pathlib import Path
from typing import Dict, Any

class GameConfig:
    """Handles game configuration loading and saving."""
    
    def __init__(self, config_path: str = "game_config.json"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        return self.config
    
    def save(self, config: Dict[str, Any]) -> None:
        """Save configuration to file."""
        self.config = config
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default) 