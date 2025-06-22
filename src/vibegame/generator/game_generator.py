"""Game generator that creates game implementations from configurations."""

import json
import os
import re
from typing import Dict, Any
import google.generativeai as genai

class GameGenerator:
    """Generates game implementations from configurations."""
    
    def __init__(self, api_key: str):
        """Initialize the game generator."""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')
    
    def _clean_code(self, code: str) -> str:
        """Clean the generated code by removing asterisks and fixing syntax."""
        # Remove all asterisks
        code = re.sub(r'\*', '', code)
        
        # Fix common syntax issues
        code = re.sub(r'from\s+typing\s+import\s+\*', 'from typing import Dict, Any', code)
        code = re.sub(r'class\s+(\w+):', r'class \1:', code)
        code = re.sub(r'def\s+(\w+):', r'def \1:', code)
        
        # Remove empty lines and extra whitespace
        code = '\n'.join(line for line in code.split('\n') if line.strip())
        
        return code
    
    def _generate_component_code(self, component_type: str, config: Dict[str, Any]) -> str:
        """Generate code for a specific component."""
        prompt = f"""
        Generate Python code for a {component_type} component based on this configuration:
        {json.dumps(config, indent=2)}
        
        IMPORTANT: 
        1. Output ONLY raw Python code - no markdown, no asterisks, no emphasis
        2. Use proper Python syntax and type hints
        3. Include necessary imports
        4. Follow PEP 8 style guidelines
        5. Make sure all mathematical expressions use proper operators (e.g., x**2 not x2)
        6. Do not use any markdown formatting or emphasis characters (*)
        7. Do not include any explanations or comments
        
        Example of correct format:
        from typing import Dict, Any
        
        class Component:
            def __init__(self, config: Dict[str, Any]):
                self.speed = config.get('speed', 0.0)
        
        Example of INCORRECT format (do not use):
        from * typing import * Dict, Any * class Component:
            def * __init__(self, config: Dict[str, Any]):
                self.speed = config.get('speed', 0.0)
        """
        
        response = self.model.generate_content(prompt)
        return self._clean_code(response.text)
    
    def generate_game(self, config_path: str = "game_config.json") -> Dict[str, Any]:
        """Generate a complete game implementation."""
        print("Generating game implementation...")
        
        # Load game configuration
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Generate components
        components = {}
        for component_type, component_config in config["mechanics"].items():
            print(f"Generating {component_type} component...")
            code = self._generate_component_code(component_type, component_config)
            components[component_type] = {"code": code}
        
        # Save implementation
        implementation = {"components": components}
        with open("game_implementation.json", 'w') as f:
            json.dump(implementation, f, indent=2)
        
        print("Game implementation generated successfully!")
        return implementation 