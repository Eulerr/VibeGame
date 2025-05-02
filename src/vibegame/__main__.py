"""Main entry point for VibeGame."""

import os
import json
import argparse
from .creator.minimal_creator import GameCreator
from .generator.game_generator import GameGenerator
from .core.game_runner import GameRunner

def create_game(api_key: str, description: str) -> None:
    """Create a new game from description."""
    print("Starting game creation...")
    
    creator = GameCreator(api_key)
    print("Creating game configuration...")
    game_config = creator.create_game(description)
    
    print("\nGenerated Game Configuration:")
    print(json.dumps(game_config, indent=2))
    
    generator = GameGenerator(api_key)
    print("\nGenerating game implementation...")
    implementation = generator.generate_game()
    
    print("\nGame implementation generated successfully!")
    print("Check game_implementation.json for the generated code")
    print("Check requirements.txt for the required dependencies")

def run_game() -> None:
    """Run an existing game implementation."""
    runner = GameRunner()
    runner.run()

def main():
    """Run the game creation and generation pipeline."""
    parser = argparse.ArgumentParser(description="VibeGame - 2D Game Builder")
    parser.add_argument("--create", action="store_true", help="Create a new game")
    parser.add_argument("--run", action="store_true", help="Run an existing game")
    parser.add_argument("--description", type=str, help="Game description for creation")
    args = parser.parse_args()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Please set GEMINI_API_KEY environment variable")
    
    if args.create:
        if not args.description:
            raise ValueError("Please provide a game description with --description")
        create_game(api_key, args.description)
    elif args.run:
        run_game()
    else:
        # Default behavior: create and run
        description = """
        I want to create a 2D platformer where you play as a wizard who can shoot fireballs and teleport. 
        The game should have a dark fantasy theme with castles and dungeons.
        """
        create_game(api_key, description)
        run_game()

if __name__ == "__main__":
    main() 