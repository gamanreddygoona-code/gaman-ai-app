"""
game_knowledge_base.py
──────────────────────
Comprehensive game knowledge base.
Teaches the AI how EVERY game works - mechanics, rules, physics, scoring.

Games covered:
- Action: Shooter, Platformer, Beat-em-up, Fighting
- Puzzle: Tetris, Match-3, Sudoku, Chess
- Strategy: Tower Defense, RTS, Turn-based
- Adventure: RPG, Dungeon, Exploration
- Sports: Racing, Football, Basketball
- Casual: Flappy Bird, Snake, Pac-Man
- Arcade: Space Invaders, Asteroids, Breakout
- Simulation: City Builder, Farm Simulator
- Multiplayer: Arena, Battle Royale
- Educational: Math games, Typing, Quiz

"""

GAME_KNOWLEDGE = {
    # ──── ACTION GAMES ────
    "shooter": {
        "name": "Shooter Game",
        "description": "Player controls character that shoots at enemies",
        "mechanics": [
            "Move with arrow keys or WASD",
            "Aim with mouse or analog stick",
            "Shoot with space or mouse click",
            "Reload ammunition",
            "Dodge incoming fire",
        ],
        "physics": {
            "gravity": False,
            "collision": "bullet vs enemy",
            "projectiles": "bullets travel in straight line",
            "damage": "each hit reduces health"
        },
        "scoring": "Points for each enemy killed, bonus for headshots",
        "difficulty": "Enemy speed and accuracy increase over time",
        "variations": ["Top-down", "Side-scroll", "First-person", "Tower Defense"]
    },

    "platformer": {
        "name": "Platformer Game",
        "description": "Jump across platforms to reach the goal",
        "mechanics": [
            "Move left/right with arrow keys",
            "Jump with spacebar",
            "Climb ladders/ropes",
            "Slide down surfaces",
            "Double jump ability (optional)",
        ],
        "physics": {
            "gravity": True,
            "jump_height": "variable based on button hold time",
            "collision": "pixel-perfect or box collision",
            "momentum": "acceleration and deceleration",
            "wall_jump": "bounce off walls"
        },
        "scoring": "Time taken, coins collected, enemies defeated",
        "difficulty": "More platforms, narrower gaps, moving obstacles",
        "variations": ["2D Side-scroll", "Isometric", "3D Platformer"]
    },

    "fighting": {
        "name": "Fighting Game",
        "description": "One-on-one combat with combos and special moves",
        "mechanics": [
            "Move left/right",
            "Jump",
            "Punch (light, medium, heavy)",
            "Kick (light, medium, heavy)",
            "Block/Guard",
            "Special moves (hadouken, spinning kick, etc)",
            "Combos (multiple hits in sequence)",
        ],
        "physics": {
            "hit_detection": "collision between attacks and body",
            "knockback": "push opponent back on hit",
            "stun": "brief freeze after being hit",
            "block_reduction": "reduces damage by 50%"
        },
        "scoring": "Health bar depletion, first to 3 wins",
        "difficulty": "AI opponent learns and counters player strategies",
        "variations": ["2D Fighting", "3D Fighting", "Tag Team", "Party Fighting"]
    },

    # ──── PUZZLE GAMES ────
    "tetris": {
        "name": "Tetris",
        "description": "Drop falling blocks to fill lines",
        "mechanics": [
            "Blocks fall from top",
            "Move left/right with arrow keys",
            "Rotate with Z/X or up arrow",
            "Drop with spacebar",
            "Complete horizontal lines to clear them",
        ],
        "physics": {
            "gravity": "blocks accelerate downward",
            "rotation": "4 orientations per piece",
            "collision": "blocks stop at bottom or on other blocks",
            "line_clear": "entire row filled disappears"
        },
        "scoring": "1 line = 100 pts, 2 lines = 300 pts, 4 lines = 800 pts",
        "difficulty": "Speed increases each level",
        "variations": ["Classic", "Rotations allowed", "Ghost piece visible"]
    },

    "match3": {
        "name": "Match-3 (Candy Crush style)",
        "description": "Match 3+ gems to clear them and score points",
        "mechanics": [
            "Tap gems to select",
            "Swap adjacent gems",
            "Match 3+ same color in row/column",
            "Matched gems disappear",
            "Gems above fall down",
            "Cascade effect for extra points",
        ],
        "physics": {
            "gravity": "gems fall to fill gaps",
            "cascade": "new matches from falling gems",
            "power_ups": "special gems for bonus matches"
        },
        "scoring": "3 match = 100 pts, 4+ match = 500+ pts",
        "difficulty": "Limited moves per level, obstacles increase",
        "variations": ["Timed", "Move-limited", "Jelly mode", "Multi-level board"]
    },

    "chess": {
        "name": "Chess",
        "description": "Strategic board game with pieces having unique movements",
        "mechanics": [
            "6 piece types: Pawn, Rook, Knight, Bishop, Queen, King",
            "Each piece moves differently",
            "Capture opponent pieces",
            "Check/Checkmate opponent",
            "Promotion when pawn reaches end",
        ],
        "physics": None,
        "scoring": "Checkmate opponent = win, material advantage = winning position",
        "difficulty": "AI uses minimax algorithm, evaluates board positions",
        "variations": ["3D Chess", "Fairy Chess (custom pieces)", "Blitz mode"]
    },

    # ──── STRATEGY GAMES ────
    "tower_defense": {
        "name": "Tower Defense",
        "description": "Place towers to defend against enemy waves",
        "mechanics": [
            "Enemies follow set path",
            "Click to place towers",
            "Towers shoot at enemies",
            "Sell towers for money",
            "Upgrade towers",
            "Multiple waves of enemies",
            "Health bar depletes when enemies reach end",
        ],
        "physics": {
            "projectiles": "travel to target",
            "range": "towers only attack within range",
            "targeting": "closest, strongest, first, or last",
            "damage": "cumulative from multiple towers"
        },
        "scoring": "Waves survived, enemies killed, money left",
        "difficulty": "Enemy health/speed increases, more waves",
        "variations": ["Standard", "Maze mode", "Reverse (defend attackers)", "Coop"]
    },

    # ──── CASUAL GAMES ────
    "flappy_bird": {
        "name": "Flappy Bird",
        "description": "Tap to fly through pipe obstacles",
        "mechanics": [
            "Bird falls due to gravity",
            "Click/tap to make bird flap (go up)",
            "Navigate through pipes",
            "Don't hit pipes or ground",
            "Score increases per pipe passed",
        ],
        "physics": {
            "gravity": "constant downward force",
            "flap": "instant upward velocity",
            "collision": "any touch = game over"
        },
        "scoring": "1 point per pipe",
        "difficulty": "Pipes move faster, gaps become narrower",
        "variations": ["Original", "Multiple obstacles", "Different bird skins"]
    },

    "snake": {
        "name": "Snake",
        "description": "Control snake to eat food and grow longer",
        "mechanics": [
            "Snake moves in one direction",
            "Arrow keys to change direction",
            "Eat food to grow",
            "Can't reverse into self",
            "Wrap around edges (optional)",
        ],
        "physics": {
            "movement": "continuous, grid-based",
            "growth": "add segment when food eaten",
            "collision": "with self = game over"
        },
        "scoring": "1 point per food eaten",
        "difficulty": "Speed increases as snake grows",
        "variations": ["Grid size", "Obstacles", "Multiplayer", "Walls"]
    },

    # ──── ARCADE GAMES ────
    "space_invaders": {
        "name": "Space Invaders",
        "description": "Destroy descending alien waves",
        "mechanics": [
            "Player ship moves left/right",
            "Shoot upward at aliens",
            "Aliens move side to side, slowly descend",
            "Aliens shoot back",
            "Clear all aliens = next wave",
            "Player destroyed by alien = game over",
        ],
        "physics": {
            "gravity": False,
            "bullets": "travel straight up/down",
            "collision": "bullet vs alien removes both"
        },
        "scoring": "Points for each alien type destroyed",
        "difficulty": "Waves move faster, shoot faster",
        "variations": ["Classic", "Modern remake", "3D version"]
    },

    # ──── RPG GAMES ────
    "rpg": {
        "name": "RPG (Role-Playing Game)",
        "description": "Control character in world with quests and progression",
        "mechanics": [
            "Move character with arrow keys",
            "Talk to NPCs to get quests",
            "Fight enemies in real-time or turn-based",
            "Gain experience and level up",
            "Equip weapons and armor",
            "Inventory management",
            "Quest tracking",
        ],
        "physics": {
            "movement": "collision with walls/NPCs",
            "combat": "attacks have cooldown and range",
            "damage": "based on weapon and stats"
        },
        "scoring": "Experience points for quests/enemies, gold for items",
        "difficulty": "Enemy level scales with player level",
        "variations": ["Action RPG", "Turn-based RPG", "MMORPG", "Roguelike"]
    },

    # ──── RACING GAMES ────
    "racing": {
        "name": "Racing Game",
        "description": "Race against opponents or clock",
        "mechanics": [
            "Accelerate with W or up arrow",
            "Brake with S or down arrow",
            "Steer with A/D or left/right",
            "Drift around corners",
            "Use boost for speed",
            "Finish before time limit or opponents",
        ],
        "physics": {
            "acceleration": "gradual speed increase",
            "friction": "slows down when not accelerating",
            "drift": "turn tighter with speed loss",
            "collision": "bounce or crash"
        },
        "scoring": "Position (1st, 2nd, 3rd), lap times",
        "difficulty": "More opponents, tighter tracks, weather effects",
        "variations": ["Circuit", "Drag race", "Off-road", "Hover craft"]
    },

    # ──── SPORTS GAMES ────
    "basketball": {
        "name": "Basketball Game",
        "description": "Score by shooting ball into basket",
        "mechanics": [
            "Dribble with arrow keys",
            "Pass with spacebar",
            "Shoot with click (hold for power)",
            "Defend opponent with collision",
            "Rebound after miss",
            "First to score target wins",
        ],
        "physics": {
            "gravity": "ball falls",
            "arc": "parabolic trajectory",
            "bounce": "off rim/ground",
            "collision": "player vs player pushing"
        },
        "scoring": "2 points for normal shot, 3 for behind line, 1 for free throw",
        "difficulty": "Opponent skill increases, tighter defense",
        "variations": ["One-on-one", "Team", "Horse", "Free throw challenge"]
    },

    # ──── EDUCATIONAL GAMES ────
    "math_game": {
        "name": "Math Game",
        "description": "Solve math problems quickly",
        "mechanics": [
            "Problem appears on screen",
            "Type answer",
            "Press enter to submit",
            "Correct = points, Incorrect = lose life",
            "Time limit per question",
        ],
        "physics": None,
        "scoring": "Points for correct answers, bonus for speed",
        "difficulty": "Larger numbers, harder operations, shorter time",
        "variations": ["Addition", "Multiplication", "Algebra", "Geometry"]
    },

    "typing_game": {
        "name": "Typing Game",
        "description": "Type words/sentences accurately and quickly",
        "mechanics": [
            "Words appear on screen",
            "Type them correctly",
            "Incorrect keystroke = penalty",
            "Speed and accuracy scored",
        ],
        "physics": None,
        "scoring": "Words per minute, accuracy percentage",
        "difficulty": "Longer words, faster pace, harder sentences",
        "variations": ["Words only", "Sentences", "Code typing", "Story mode"]
    },
}


def get_game_info(game_type: str) -> dict:
    """Get comprehensive game information."""
    return GAME_KNOWLEDGE.get(game_type.lower(), {})


def list_all_games() -> list:
    """Get list of all available games."""
    return list(GAME_KNOWLEDGE.keys())


def teach_game(game_type: str) -> str:
    """Generate teaching text for a game."""
    info = get_game_info(game_type)
    if not info:
        return f"Game '{game_type}' not found in knowledge base."

    teaching = f"""
🎮 **{info['name']}**

**What is it?**
{info['description']}

**How to Play:**
"""
    for i, mechanic in enumerate(info['mechanics'], 1):
        teaching += f"\n{i}. {mechanic}"

    if info.get('physics'):
        teaching += "\n\n**Physics & Mechanics:**\n"
        for key, value in info['physics'].items():
            teaching += f"- {key}: {value}\n"

    teaching += f"\n**Scoring:** {info['scoring']}"
    teaching += f"\n**Difficulty:** {info['difficulty']}"
    teaching += f"\n**Variations:** {', '.join(info['variations'])}"

    return teaching


if __name__ == "__main__":
    print("🎮 Game Knowledge Base\n")
    print(f"Total games: {len(GAME_KNOWLEDGE)}")
    print(f"\nAvailable games:")
    for game in list_all_games():
        print(f"  - {game}")

    print("\n" + "="*60)
    print("\n📚 Sample Teaching (Tetris):\n")
    print(teach_game("tetris"))
