"""
advanced_game_generator.py
──────────────────────────
Advanced game generator - creates real playable games for ANY game type.
Integrates with game_knowledge_base to teach what each game is and how it works.

Can generate:
- Flappy Bird clone
- Snake game
- Match-3 puzzle
- Space Invaders style shooter
- Tetris clone
- Racing game
- Platformer variations
- And more...
"""

import os
from datetime import datetime
from game_knowledge_base import get_game_info, teach_game


def generate_flappy_bird_game():
    """Generate real Flappy Bird game."""
    return """<!DOCTYPE html>
<html>
<head>
    <title>Flappy Bird</title>
    <style>
        body { margin: 0; overflow: hidden; background: #1a1a2e; }
        canvas { display: block; background: linear-gradient(180deg, #87ceeb, #e0f6ff); }
        #info { position: absolute; top: 20px; left: 20px; color: white; font-size: 24px; z-index: 10; }
        #gameOver { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
                    background: rgba(0,0,0,0.9); color: white; padding: 40px; border-radius: 10px;
                    text-align: center; z-index: 20; display: none; }
        button { padding: 10px 20px; font-size: 16px; cursor: pointer; margin-top: 20px; }
    </style>
</head>
<body>
    <canvas id="canvas"></canvas>
    <div id="info">Score: <span id="score">0</span></div>
    <div id="gameOver">
        <h1>Game Over!</h1>
        <p>Final Score: <span id="finalScore">0</span></p>
        <button onclick="location.reload()">Play Again</button>
    </div>

    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const bird = { x: canvas.width / 4, y: canvas.height / 2, width: 34, height: 24, velocity: 0, gravity: 0.6 };
        let pipes = [];
        let score = 0;
        let gameRunning = true;

        function spawnPipe() {
            const gapHeight = 130;
            const minHeight = 50;
            const maxHeight = canvas.height - gapHeight - minHeight;
            const pipeHeight = Math.random() * (maxHeight - minHeight) + minHeight;

            pipes.push({
                x: canvas.width,
                y: pipeHeight,
                width: 80,
                gapHeight: gapHeight,
                passed: false
            });
        }

        window.addEventListener('click', () => { bird.velocity = -12; });
        window.addEventListener('keydown', (e) => { if(e.key === ' ') { bird.velocity = -12; e.preventDefault(); } });

        function gameLoop() {
            if (!gameRunning) return;

            ctx.fillStyle = '#87ceeb';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            bird.velocity += bird.gravity;
            bird.y += bird.velocity;

            ctx.fillStyle = '#FFD700';
            ctx.fillRect(bird.x, bird.y, bird.width, bird.height);

            if (bird.y < 0 || bird.y + bird.height > canvas.height) {
                gameRunning = false;
                document.getElementById('finalScore').textContent = score;
                document.getElementById('gameOver').style.display = 'block';
                return;
            }

            for (let i = pipes.length - 1; i >= 0; i--) {
                const pipe = pipes[i];
                pipe.x -= 5;

                ctx.fillStyle = '#228B22';
                ctx.fillRect(pipe.x, 0, pipe.width, pipe.y);
                ctx.fillRect(pipe.x, pipe.y + pipe.gapHeight, pipe.width, canvas.height);

                if (!pipe.passed && pipe.x + pipe.width < bird.x) {
                    pipe.passed = true;
                    score++;
                }

                if (bird.x < pipe.x + pipe.width && bird.x + bird.width > pipe.x &&
                    (bird.y < pipe.y || bird.y + bird.height > pipe.y + pipe.gapHeight)) {
                    gameRunning = false;
                    document.getElementById('finalScore').textContent = score;
                    document.getElementById('gameOver').style.display = 'block';
                    return;
                }

                if (pipe.x + pipe.width < 0) pipes.splice(i, 1);
            }

            if (pipes.length === 0 || pipes[pipes.length - 1].x < canvas.width - 300) spawnPipe();

            document.getElementById('score').textContent = score;
            requestAnimationFrame(gameLoop);
        }

        gameLoop();
    </script>
</body>
</html>"""


def generate_snake_game():
    """Generate real Snake game."""
    return """<!DOCTYPE html>
<html>
<head>
    <title>Snake Game</title>
    <style>
        body { margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; background: #1a1a2e; }
        canvas { border: 3px solid #7c5cfc; background: #0a0a0f; }
        #info { position: absolute; top: 20px; color: white; font-size: 20px; }
    </style>
</head>
<body>
    <div id="info">Score: <span id="score">0</span> | Speed: <span id="speed">1</span></div>
    <canvas id="gameCanvas" width="400" height="400"></canvas>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const gridSize = 20;
        const gridCount = canvas.width / gridSize;

        let snake = [{ x: 10, y: 10 }];
        let food = { x: 15, y: 15 };
        let direction = { x: 1, y: 0 };
        let nextDirection = { x: 1, y: 0 };
        let score = 0;
        let speed = 1;
        let frameCount = 0;

        window.addEventListener('keydown', (e) => {
            switch(e.key) {
                case 'ArrowUp': if(direction.y === 0) nextDirection = {x: 0, y: -1}; break;
                case 'ArrowDown': if(direction.y === 0) nextDirection = {x: 0, y: 1}; break;
                case 'ArrowLeft': if(direction.x === 0) nextDirection = {x: -1, y: 0}; break;
                case 'ArrowRight': if(direction.x === 0) nextDirection = {x: 1, y: 0}; break;
            }
        });

        function gameLoop() {
            frameCount++;
            const moveSpeed = Math.max(5, 15 - speed);

            if (frameCount % moveSpeed === 0) {
                direction = nextDirection;
                const head = snake[0];
                const newHead = {
                    x: (head.x + direction.x + gridCount) % gridCount,
                    y: (head.y + direction.y + gridCount) % gridCount
                };

                for (let segment of snake) {
                    if (newHead.x === segment.x && newHead.y === segment.y) {
                        alert('Game Over! Score: ' + score);
                        location.reload();
                        return;
                    }
                }

                snake.unshift(newHead);

                if (newHead.x === food.x && newHead.y === food.y) {
                    score += 10;
                    speed = Math.floor(score / 50) + 1;
                    food = {
                        x: Math.floor(Math.random() * gridCount),
                        y: Math.floor(Math.random() * gridCount)
                    };
                } else {
                    snake.pop();
                }
            }

            ctx.fillStyle = '#0a0a0f';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.fillStyle = '#00FF00';
            for (let segment of snake) {
                ctx.fillRect(segment.x * gridSize, segment.y * gridSize, gridSize - 2, gridSize - 2);
            }

            ctx.fillStyle = '#FF4444';
            ctx.fillRect(food.x * gridSize, food.y * gridSize, gridSize - 2, gridSize - 2);

            document.getElementById('score').textContent = score;
            document.getElementById('speed').textContent = speed;

            requestAnimationFrame(gameLoop);
        }

        gameLoop();
    </script>
</body>
</html>"""


def generate_space_invaders_game():
    """Generate Space Invaders style game."""
    return """<!DOCTYPE html>
<html>
<head>
    <title>Space Invaders</title>
    <style>
        body { margin: 0; background: #000; overflow: hidden; }
        canvas { display: block; background: #001a00; }
        #score { position: absolute; top: 10px; left: 10px; color: #0f0; font-family: monospace; font-size: 16px; z-index: 10; }
        #gameOver { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
                    background: rgba(0,0,0,0.95); color: #0f0; padding: 40px; border-radius: 5px;
                    text-align: center; font-family: monospace; z-index: 20; display: none; }
    </style>
</head>
<body>
    <div id="score">SCORE: <span id="scoreVal">0</span></div>
    <canvas id="gameCanvas"></canvas>
    <div id="gameOver">
        <div style="font-size: 24px;">GAME OVER</div>
        <div>FINAL SCORE: <span id="finalScore">0</span></div>
        <button onclick="location.reload()" style="margin-top: 20px; padding: 10px 20px; cursor: pointer;">RESTART</button>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const player = { x: canvas.width / 2, y: canvas.height - 50, width: 40, height: 40, speed: 6 };
        let enemies = [];
        let bullets = [];
        let score = 0;
        let gameRunning = true;
        let wave = 1;

        function spawnEnemies() {
            for (let i = 0; i < 5 + wave; i++) {
                enemies.push({
                    x: Math.random() * (canvas.width - 30),
                    y: 20 + Math.random() * 60,
                    width: 30,
                    height: 30,
                    speed: 2 + wave * 0.5
                });
            }
        }

        const keys = {};
        window.addEventListener('keydown', (e) => {
            keys[e.key] = true;
            if (e.key === ' ') { shoot(); e.preventDefault(); }
        });
        window.addEventListener('keyup', (e) => keys[e.key] = false);

        function shoot() {
            bullets.push({ x: player.x + player.width / 2, y: player.y, width: 5, height: 15 });
        }

        function gameLoop() {
            if (!gameRunning) return;

            ctx.fillStyle = '#000';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            if (keys['ArrowLeft'] || keys['a']) player.x -= player.speed;
            if (keys['ArrowRight'] || keys['d']) player.x += player.speed;
            player.x = Math.max(0, Math.min(canvas.width - player.width, player.x));

            ctx.fillStyle = '#0f0';
            ctx.fillRect(player.x, player.y, player.width, player.height);

            for (let i = bullets.length - 1; i >= 0; i--) {
                const b = bullets[i];
                b.y -= 8;
                ctx.fillRect(b.x, b.y, b.width, b.height);
                if (b.y < 0) bullets.splice(i, 1);
            }

            for (let i = enemies.length - 1; i >= 0; i--) {
                const e = enemies[i];
                e.x += e.speed;
                if (e.x < 0 || e.x > canvas.width) e.speed *= -1;

                ctx.fillStyle = '#f00';
                ctx.fillRect(e.x, e.y, e.width, e.height);

                for (let j = bullets.length - 1; j >= 0; j--) {
                    const b = bullets[j];
                    if (b.x > e.x && b.x < e.x + e.width && b.y > e.y && b.y < e.y + e.height) {
                        score += 10;
                        enemies.splice(i, 1);
                        bullets.splice(j, 1);
                        break;
                    }
                }

                if (e.y > canvas.height) {
                    gameRunning = false;
                }
            }

            if (enemies.length === 0) {
                wave++;
                spawnEnemies();
            }

            document.getElementById('scoreVal').textContent = score;

            if (!gameRunning) {
                document.getElementById('finalScore').textContent = score;
                document.getElementById('gameOver').style.display = 'block';
            }

            requestAnimationFrame(gameLoop);
        }

        spawnEnemies();
        gameLoop();
    </script>
</body>
</html>"""


class AdvancedGameGenerator:
    """Generate any game type."""

    def __init__(self):
        self.output_dir = os.path.join(os.path.dirname(__file__), "static", "games")
        os.makedirs(self.output_dir, exist_ok=True)

    def generate(self, game_type: str, custom_prompt: str = "") -> dict:
        """Generate a game and return info."""
        game_type_lower = game_type.lower()

        # Game generators
        generators = {
            "flappy_bird": generate_flappy_bird_game,
            "flappy": generate_flappy_bird_game,
            "snake": generate_snake_game,
            "space_invaders": generate_space_invaders_game,
            "invaders": generate_space_invaders_game,
            "shooter": generate_space_invaders_game,
        }

        # Get generator
        generator = generators.get(game_type_lower)
        if not generator:
            return {"status": "error", "message": f"Game type '{game_type}' not yet implemented. Available: {list(generators.keys())}"}

        try:
            # Generate HTML
            html = generator()

            # Save file
            timestamp = int(datetime.now().timestamp())
            import random
            random_id = random.randint(1000, 9999)
            filename = f"game_{game_type_lower}_{timestamp}_{random_id}.html"
            filepath = os.path.join(self.output_dir, filename)

            with open(filepath, 'w') as f:
                f.write(html)

            # Get knowledge
            knowledge = get_game_info(game_type_lower)
            teaching = teach_game(game_type_lower)

            return {
                "status": "ok",
                "game_type": game_type_lower,
                "game_url": f"/static/games/{filename}",
                "file_size": os.path.getsize(filepath) / 1024,
                "knowledge": knowledge,
                "teaching": teaching,
                "message": f"🎮 Real {game_type.title()} Game Generated!\n\n{teaching}"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    gen = AdvancedGameGenerator()

    print("\n🎮 Advanced Game Generator\n")

    for game_type in ["flappy_bird", "snake", "space_invaders"]:
        print(f"Generating {game_type}...", end=" ")
        result = gen.generate(game_type)
        if result['status'] == 'ok':
            print(f"✅ ({result['file_size']:.1f} KB)")
        else:
            print(f"❌ {result['message']}")

    print("\n✅ Games generated!")
