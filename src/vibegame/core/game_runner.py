"""Game runner that executes generated game code."""

import json
import importlib.util
import os
import sys
import re
from pathlib import Path
from typing import Dict, Any

class GameRunner:
    """Executes generated game code."""
    
    def __init__(self, implementation_path: str = "game_implementation.json"):
        self.implementation_path = Path(implementation_path)
        self.game_components: Dict[str, Any] = {}
        self.game_instance = None
    
    def load_implementation(self) -> None:
        """Load the game implementation from JSON."""
        print("Loading game implementation...")
        with open(self.implementation_path, 'r') as f:
            implementation = json.load(f)
        self.game_components = implementation["components"]
        print("Game implementation loaded successfully")
    
    def _clean_code(self, code: str) -> str:
        """Clean the generated code by removing markdown and comments."""
        # Remove markdown code block markers
        code = re.sub(r'```python\n?', '', code)
        code = re.sub(r'```\n?', '', code)
        
        # Remove markdown-style comments
        code = re.sub(r'\*.*\*', '', code)
        code = re.sub(r'#.*\*.*\*', '', code)
        
        # Remove empty lines
        code = '\n'.join(line for line in code.split('\n') if line.strip())
        
        return code
    
    def _create_module(self, name: str, code: str) -> None:
        """Create a Python module from code string."""
        print(f"Cleaning {name} code...")
        cleaned_code = self._clean_code(code)
        
        print(f"Creating {name} module...")
        spec = importlib.util.spec_from_loader(name, loader=None)
        module = importlib.util.module_from_spec(spec)
        
        # Create a temporary file for debugging
        temp_file = Path(f"temp_{name.split('.')[-1]}.py")
        temp_file.write_text(cleaned_code)
        print(f"Saved cleaned code to {temp_file}")
        
        try:
            exec(cleaned_code, module.__dict__)
            sys.modules[name] = module
            return module
        except Exception as e:
            print(f"Error in {name} code:")
            print(cleaned_code)
            raise
    
    def initialize_game(self) -> None:
        """Initialize the game from components."""
        print("\nInitializing game components...")
        
        # Create modules for each component
        for component_type, component in self.game_components.items():
            print(f"\nProcessing {component_type} component...")
            module_name = f"vibegame.components.{component_type}"
            self._create_module(module_name, component["code"])
        
        # Import and initialize the game
        print("\nCreating game instance...")
        try:
            from vibegame.components.movement import MovementComponent
            from vibegame.components.combat import CombatComponent
            from vibegame.components.physics import PhysicsComponent
            from vibegame.components.ai import AIComponent
            
            # Initialize components
            movement = MovementComponent()
            combat = CombatComponent()
            physics = PhysicsComponent()
            ai = AIComponent() if "ai" in self.game_components else None
            
            # Create game instance
            self.game_instance = {
                "movement": movement,
                "combat": combat,
                "physics": physics,
                "ai": ai
            }
            print("Game instance created successfully")
        except ImportError as e:
            print(f"Error importing components: {e}")
            raise
    
    def run(self) -> None:
        """Run the game."""
        if not self.game_instance:
            self.load_implementation()
            self.initialize_game()
        
        print("\nStarting game...")
        try:
            # Main game loop
            while True:
                # Update components
                self.game_instance["movement"].update()
                self.game_instance["combat"].update()
                self.game_instance["physics"].update()
                if self.game_instance["ai"]:
                    self.game_instance["ai"].update()
                
                # Render frame
                # Add rendering code here
                
        except KeyboardInterrupt:
            print("\nGame stopped by user")
        except Exception as e:
            print(f"\nError running game: {e}")
            raise 