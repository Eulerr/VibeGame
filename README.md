# VibeGame

A 2D game builder platform with natural language interface.

## 🚀 Features

- Natural language game description to configuration
- Automatic game component generation
- Flexible game architecture
- Component-based design

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/VibeGame.git
cd VibeGame
```

2. Install dependencies:
```bash
uv venv
uv pip install -e .
```

3. Set up your Gemini API key:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

## 🎮 Usage

1. Run the game creation pipeline:
```bash
python -m vibegame
```

2. Or use the components individually:
```python
from vibegame.creator.minimal_creator import GameCreator
from vibegame.generator.game_generator import GameGenerator

# Create game configuration
creator = GameCreator(api_key)
game_config = creator.create_game("Your game description here")

# Generate game implementation
generator = GameGenerator(api_key)
implementation = generator.generate_game()
```

## 📁 Project Structure

```
VibeGame/
├── src/
│   └── vibegame/
│       ├── __init__.py
│       ├── __main__.py
│       ├── core/
│       │   └── config.py
│       ├── creator/
│       │   └── minimal_creator.py
│       └── generator/
│           └── game_generator.py
├── tests/
├── pyproject.toml
└── README.md
```

## 🔧 Development

1. Install development dependencies:
```bash
uv pip install -e ".[dev]"
```

2. Run tests:
```bash
pytest
```

## 📝 License

MIT License