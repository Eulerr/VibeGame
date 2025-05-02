"""Game implementation generator using Gemini."""

import json
import google.generativeai as genai
from typing import Dict, List, Set
from pathlib import Path
from ..core.config import GameConfig

class GameGenerator:
    """Generates game implementations from configurations."""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro-exp-03-25')
        self.config = GameConfig()
        self.components = {
            "movement": {},
            "combat": {},
            "physics": {},
            "ai": {}
        }

    def generate_component(self, component_type: str, requirements: Dict) -> Dict:
        """Generate a specific game component using Gemini."""
        prompt = f"""
        Create a {component_type} component for a game with these requirements:
        {json.dumps(requirements, indent=2)}
        
        Return a Python class implementation with:
        1. Required imports
        2. Class definition with proper inheritance
        3. Initialization method
        4. Core functionality methods
        5. Type hints and docstrings
        
        The code should be production-ready and follow Python best practices.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return {
                "code": response.text,
                "dependencies": self._extract_dependencies(response.text)
            }
        except Exception as e:
            print(f"Error generating {component_type} component: {e}")
            return None

    def _extract_dependencies(self, code: str) -> List[str]:
        """Extract required dependencies from generated code."""
        dependencies: Set[str] = set()
        if "import pygame" in code:
            dependencies.add("pygame")
        if "import numpy" in code:
            dependencies.add("numpy")
        return list(dependencies)

    def generate_game(self) -> Dict:
        """Generate complete game implementation."""
        game_config = self.config.load()
        if not game_config:
            raise ValueError("No game configuration found. Please create one first.")
            
        game_components = {}
        all_dependencies: Set[str] = set()
        
        # Generate movement component
        if "movement" in game_config["mechanics"]:
            movement = self.generate_component("movement", game_config["mechanics"]["movement"])
            if movement:
                game_components["movement"] = movement
                all_dependencies.update(movement["dependencies"])
        
        # Generate combat component
        if "combat" in game_config["mechanics"]:
            combat = self.generate_component("combat", game_config["mechanics"]["combat"])
            if combat:
                game_components["combat"] = combat
                all_dependencies.update(combat["dependencies"])
        
        # Generate physics component based on game type
        physics_reqs = {
            "type": game_config["game_type"],
            "settings": game_config["mechanics"].get("movement", {})
        }
        physics = self.generate_component("physics", physics_reqs)
        if physics:
            game_components["physics"] = physics
            all_dependencies.update(physics["dependencies"])
        
        # Generate AI component if enemies exist
        if game_config["assets"].get("enemies"):
            ai_reqs = {
                "enemy_types": game_config["assets"]["enemies"],
                "difficulty": game_config["level_design"]["difficulty"]
            }
            ai = self.generate_component("ai", ai_reqs)
            if ai:
                game_components["ai"] = ai
                all_dependencies.update(ai["dependencies"])
        
        implementation = {
            "components": game_components,
            "dependencies": list(all_dependencies)
        }
        
        # Save implementation
        with open('game_implementation.json', 'w') as f:
            json.dump(implementation, f, indent=2)
        
        # Save requirements
        with open('requirements.txt', 'w') as f:
            for dep in implementation["dependencies"]:
                f.write(f"{dep}\n")
        
        return implementation 