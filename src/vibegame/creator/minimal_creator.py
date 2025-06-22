"""Game description to configuration converter using Gemini."""

import json
import google.generativeai as genai
from ..core.config import GameConfig

class GameCreator:
    """Creates game configurations from natural language descriptions."""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')
        self.config = GameConfig()
    
    def create_game(self, description: str) -> dict:
        """Create a game configuration from natural language description."""
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
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up the response text
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            # Parse the JSON
            game_config = json.loads(response_text)
            
            # Save the configuration
            with open('game_config.json', 'w') as f:
                json.dump(game_config, f, indent=2)
            
            return game_config
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            print("Raw response:", response.text)
            raise
        except Exception as e:
            print(f"Error: {e}")
            print("Raw response:", response.text)
            raise 