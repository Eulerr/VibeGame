"""Main entry point for VibeGame."""

import os
import json
from .creator.minimal_creator import GameCreator
from .generator.game_generator import GameGenerator

def main():
    """Run the game creation and generation pipeline."""
    print("Starting VibeGame pipeline...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Please set GEMINI_API_KEY environment variable")
    print("API key loaded successfully")
    
    # Example game description
    description = """
    I want to create a 2D platformer where you play as a wizard who can shoot fireballs and teleport. 
    The game should have a dark fantasy theme with castles and dungeons.
    """
    
    # Create game configuration
    print("\nInitializing GameCreator...")
    creator = GameCreator(api_key)
    print("Creating game configuration...")
    game_config = creator.create_game(description)
    
    print("\nGenerated Game Configuration:")
    print(json.dumps(game_config, indent=2))
    
    # Generate game implementation
    print("\nInitializing GameGenerator...")
    generator = GameGenerator(api_key)
    print("Generating game implementation...")
    implementation = generator.generate_game()
    
    print("\nGame implementation generated successfully!")
    print("Check game_implementation.json for the generated code")
    print("Check requirements.txt for the required dependencies")

if __name__ == "__main__":
    main() 