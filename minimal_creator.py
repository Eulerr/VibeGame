import json
import google.generativeai as genai

# Initialize Gemini
genai.configure(api_key='AIzaSyCkc7avbrni4SXu22l5DkQ8ww3ETV0oEzg')
model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')

def create_game(description: str) -> dict:
    """Create a game from natural language description using Gemini."""
    example_output = {
        "game_type": "platformer",
        "mechanics": {
            "movement": {
                "type": "platformer",
                "jump_height": 300,
                "move_speed": 200,
                "special_abilities": {
                    "teleport": {
                        "range": 200,
                        "cooldown": 5
                    }
                }
            },
            "combat": {
                "type": "magic",
                "spells": {
                    "fireball": {
                        "damage": 15,
                        "range": 300,
                        "cooldown": 2
                    }
                }
            }
        },
        "level_design": {
            "type": "side_scroller",
            "difficulty": "medium",
            "environments": ["castle", "dungeon"],
            "checkpoints": True
        },
        "assets": {
            "player": "wizard",
            "enemies": ["skeleton", "ghost"],
            "environment": "dark_fantasy"
        }
    }

    prompt = f"""
    Convert this game description into a structured game configuration.
    Focus on extracting game type, mechanics, and assets.
    
    Description: {description}
    
    Return ONLY a valid JSON with this structure:
    {{
        "game_type": "string",
        "mechanics": {{
            "movement": {{
                "type": "string",
                "jump_height": number,
                "move_speed": number,
                "special_abilities": {{
                    "ability_name": {{
                        "range": number,
                        "cooldown": number
                    }}
                }}
            }},
            "combat": {{
                "type": "string",
                "spells": {{
                    "spell_name": {{
                        "damage": number,
                        "range": number,
                        "cooldown": number
                    }}
                }}
            }}
        }},
        "level_design": {{
            "type": "string",
            "difficulty": "string",
            "environments": ["string"],
            "checkpoints": boolean
        }},
        "assets": {{
            "player": "string",
            "enemies": ["string"],
            "environment": "string"
        }}
    }}
    
    Here's an example of the expected output format:
    {json.dumps(example_output, indent=2)}
    
    Important: Include all numeric values and specific details for abilities and spells.
    Do not include any additional text or explanation, only the JSON.
    """
    
    try:
        response = model.generate_content(prompt)
        # Extract JSON from response
        response_text = response.text.strip()
        # Remove any markdown code block markers if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        return json.loads(response_text)
    except Exception as e:
        print(f"Error: {e}")
        print("Raw response:", response.text if 'response' in locals() else "No response")
        return None

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
    else:
        print("Failed to generate game configuration")

if __name__ == "__main__":
    main() 