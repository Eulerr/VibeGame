# VibeGame Natural Language Interface

## 🎯 Core Objectives
- Create a natural language interface for game creation with gemini
- Convert user descriptions into structured GDL

## 🤖 Example Interaction

### User Input:
"I want to create a 2D platformer where you play as a wizard who can shoot fireballs and teleport. The game should have a dark fantasy theme with castles and dungeons."
LLM WORKING Like a fucking god.

### Generated GDL:
```json
{
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
        "checkpoints": true
    },
    "assets": {
        "player": "wizard",
        "enemies": ["skeleton", "ghost"],
        "environment": "dark_fantasy"
    }
}