"""Game implementation generator using Gemini."""

import json
import google.generativeai as genai
from typing import Dict, List, Set
from pathlib import Path
from ..core.config import GameConfig

class GameGenerator:
    """Generates game implementations from configurations."""
    
    def __init__(self, api_key: str):
        print("Initializing GameGenerator...")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro-exp-03-25')
        self.config = GameConfig()
        self.components = {
            "movement": {},
            "combat": {},
            "physics": {},
            "ai": {}
        }
        print("GameGenerator initialized successfully")

    def generate_component(self, component_type: str, requirements: Dict) -> Dict:
        """Generate a specific game component using Gemini."""
        print(f"\nGenerating {component_type} component...")
        print(f"Requirements: {json.dumps(requirements, indent=2)}")
        
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
        
        print("Sending prompt to Gemini...")
        response = self.model.generate_content(prompt)
        print("Received response from Gemini")
        
        code = response.text
        print(f"Generated code length: {len(code)} characters")
        
        dependencies = self._extract_dependencies(code)
        print(f"Extracted dependencies: {dependencies}")
        
        return {
            "code": code,
            "dependencies": dependencies
        }

    def _extract_dependencies(self, code: str) -> List[str]:
        """Extract required dependencies from generated code."""
        print("Extracting dependencies from code...")
        dependencies: Set[str] = set()
        if "import pygame" in code:
            dependencies.add("pygame")
        if "import numpy" in code:
            dependencies.add("numpy")
        return list(dependencies)

    def generate_game(self) -> Dict:
        """Generate complete game implementation."""
        print("\nStarting game generation...")
        game_config = self.config.load()
        print("Loaded game configuration")
        
        if not game_config:
            raise ValueError("No game configuration found. Please create one first.")
            
        game_components = {}
        all_dependencies: Set[str] = set()
        
        # Generate movement component
        if "movement" in game_config["mechanics"]:
            print("\nGenerating movement component...")
            movement = self.generate_component("movement", game_config["mechanics"]["movement"])
            game_components["movement"] = movement
            all_dependencies.update(movement["dependencies"])
            print("Movement component generated")
        
        # Generate combat component
        if "combat" in game_config["mechanics"]:
            print("\nGenerating combat component...")
            combat = self.generate_component("combat", game_config["mechanics"]["combat"])
            game_components["combat"] = combat
            all_dependencies.update(combat["dependencies"])
            print("Combat component generated")
        
        # Generate physics component based on game type
        print("\nGenerating physics component...")
        physics_reqs = {
            "type": game_config["game_type"],
            "settings": game_config["mechanics"].get("movement", {})
        }
        physics = self.generate_component("physics", physics_reqs)
        game_components["physics"] = physics
        all_dependencies.update(physics["dependencies"])
        print("Physics component generated")
        
        # Generate AI component if enemies exist
        if game_config["assets"].get("enemies"):
            print("\nGenerating AI component...")
            ai_reqs = {
                "enemy_types": game_config["assets"]["enemies"],
                "difficulty": game_config["level_design"]["difficulty"]
            }
            ai = self.generate_component("ai", ai_reqs)
            game_components["ai"] = ai
            all_dependencies.update(ai["dependencies"])
            print("AI component generated")
        
        implementation = {
            "components": game_components,
            "dependencies": list(all_dependencies)
        }
        
        print("\nSaving implementation...")
        with open('game_implementation.json', 'w') as f:
            json.dump(implementation, f, indent=2)
        print("Implementation saved to game_implementation.json")
        
        print("\nSaving requirements...")
        with open('requirements.txt', 'w') as f:
            for dep in implementation["dependencies"]:
                f.write(f"{dep}\n")
        print("Requirements saved to requirements.txt")
        
        print("\nGame generation completed successfully!")
        return implementation 