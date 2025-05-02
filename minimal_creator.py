import json
import google.generativeai as genai

# Initialize Gemini
genai.configure(api_key='AIzaSyCkc7avbrni4SXu22l5DkQ8ww3ETV0oEzg')
model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')

def create_game(description: str) -> dict:
    """Create a game from natural language description using Gemini."""
    prompt = f"""
    Convert this game description into a structured game configuration.
    Focus on extracting game type, mechanics, and assets.
    
    Description: {description}
    
    Return a JSON with this structure:
    {{
        "game_type": "string",
        "mechanics": {{
            "movement": {{...}},
            "combat": {{...}},
            "special_abilities": {{...}}
        }},
        "level_design": {{
            "type": "string",
            "environments": [...]
        }},
        "assets": {{
            "player": "string",
            "enemies": [...],
            "environment": "string"
        }}
    }}
    """
    response = model.generate_content(prompt)
    return json.loads(response.text)

def main():
    # Example from interaction plan
    description = """
    I want to create a 2D platformer where you play as a wizard who can shoot fireballs and teleport. 
    The game should have a dark fantasy theme with castles and dungeons.
    """
    
    print("Creating game from description...")
    game_config = create_game(description)
    
    if game_config:
        print("\nGenerated Game Configuration:")
        print(json.dumps(game_config, indent=2))
        
        # Save to file
        with open('game_config.json', 'w') as f:
            json.dump(game_config, f, indent=2)
        print("\nSaved to game_config.json")

if __name__ == "__main__":
    main() 