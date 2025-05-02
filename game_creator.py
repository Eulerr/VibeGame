import json
from typing import Dict, Any, List
from dataclasses import dataclass
import google.generativeai as genai
from pathlib import Path

# Initialize Gemini
genai.configure(api_key='YOUR_API_KEY')
model = genai.GenerativeModel('gemini-pro')

@dataclass
class GameDescription:
    game_type: str
    mechanics: Dict[str, Any]
    theme: Dict[str, Any]
    features: List[str]
    assets: Dict[str, Any]
    level_design: Dict[str, Any]

class GameCreator:
    def __init__(self):
        self.analysis_prompt = """
        Analyze the following game description and extract key components in a structured way.
        Consider the following aspects:

        1. Game Type and Core Mechanics:
           - What is the primary game genre?
           - What are the core gameplay mechanics?
           - How does the player interact with the world?
           - What special abilities or features are mentioned?

        2. Visual Style and Theme:
           - What is the art style?
           - What is the setting and atmosphere?
           - What are the key environments?
           - What is the overall mood?

        3. Game Systems:
           - What progression systems exist?
           - What are the win/lose conditions?
           - What are the key challenges?
           - What collectibles or items are mentioned?

        Return the analysis in the following JSON format:
        {
            "game_type": "string",
            "mechanics": {
                "movement": {...},
                "combat": {...},
                "special_abilities": [...]
            },
            "theme": {
                "style": "string",
                "setting": "string",
                "environments": [...]
            },
            "features": [...],
            "assets": {
                "player": {...},
                "enemies": [...],
                "environment": {...}
            },
            "level_design": {
                "type": "string",
                "difficulty": "string",
                "progression": {...}
            }
        }
        """

    def get_user_description(self) -> str:
        """Get game description from user with guided prompts."""
        print("Welcome to VibeGame Creator!")
        print("Let's create your game...\n")
        
        prompts = [
            "What kind of game do you want to create? (e.g., platformer, RPG, puzzle)",
            "Describe the main character and their abilities:",
            "What's the game's setting and visual style?",
            "What are the main challenges or goals?",
            "Any special features or mechanics you want to include?"
        ]
        
        description = ""
        for prompt in prompts:
            print(f"\n{prompt}")
            description += input() + "\n"
            
        return description

    def analyze_with_gemini(self, description: str) -> Dict[str, Any]:
        """Use Gemini to analyze the game description semantically."""
        full_prompt = f"{self.analysis_prompt}\n\nGame Description:\n{description}"
        
        try:
            response = model.generate_content(full_prompt)
            analysis = json.loads(response.text)
            return analysis
        except Exception as e:
            print(f"Error analyzing description: {e}")
            return None

    def refine_with_gemini(self, gdl: Dict[str, Any]) -> Dict[str, Any]:
        """Use Gemini to refine and complete the GDL."""
        refinement_prompt = f"""
        Review and refine this game configuration. Ensure it's complete and coherent.
        Add any missing but implied components, and suggest improvements.
        
        Current configuration:
        {json.dumps(gdl, indent=2)}
        
        Return the refined configuration in the same format.
        """
        
        try:
            response = model.generate_content(refinement_prompt)
            refined = json.loads(response.text)
            return refined
        except Exception as e:
            print(f"Error refining configuration: {e}")
            return gdl

    def generate_gdl(self, description: str) -> Dict[str, Any]:
        """Generate complete Game Description Language."""
        # Initial analysis with Gemini
        analysis = self.analyze_with_gemini(description)
        if not analysis:
            raise ValueError("Failed to analyze game description")
            
        # Refine the configuration
        refined = self.refine_with_gemini(analysis)
        
        return refined

    def save_gdl(self, gdl: Dict[str, Any], filename: str = "game_config.json"):
        """Save the GDL to a file."""
        with open(filename, 'w') as f:
            json.dump(gdl, f, indent=2)

def main():
    creator = GameCreator()
    
    try:
        # Get user description
        description = creator.get_user_description()
        
        # Generate GDL
        print("\nAnalyzing your game description...")
        gdl = creator.generate_gdl(description)
        
        # Present results
        print("\nHere's your game configuration:")
        print(json.dumps(gdl, indent=2))
        
        # Save configuration
        creator.save_gdl(gdl)
        print(f"\nConfiguration saved to game_config.json")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 