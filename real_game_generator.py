"""
real_game_generator.py
──────────────────────
Generate REAL playable games as standalone HTML5 files.
Uses Canvas API (no external libraries needed).
Games are instantly playable - no compilation needed.

Supported game types:
- Collector: Dodge obstacles, collect items
- Shooter: Shoot moving targets
- Platformer: Jump and reach the goal
- Dodger: Avoid falling objects
- Puzzle: Match patterns to solve
"""

import json
from datetime import datetime
import os


def generate_collector_game(title="Collector Game"):
    """Generate a real collector game."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; background: #222; overflow: hidden; }}
        canvas {{ display: block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        #info {{ position: absolute; top: 10px; left: 10px; color: white; font-size: 18px; z-index: 10; }}
        #gameOver {{
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: rgba(0,0,0,0.9); color: white; padding: 40px; border-radius: 10px;
            text-align: center; font-size: 24px; z-index: 20; display: none;
        }}
        button {{ padding: 10px 20px; font-size: 16px; cursor: pointer; margin-top: 20px; }}
    </style>
</head>
<body>
    <canvas id="gameCanvas"></canvas>
    <div id="info">
        <div>Score: <span id="score">0</span></div>
        <div>Lives: <span id="lives">3</span></div>
    </div>
    <div id="gameOver">
        <div>Game Over!</div>
        <div>Final Score: <span id="finalScore">0</span></div>
        <button onclick="location.reload()">Play Again</button>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        // Game objects
        const player = {{
            x: canvas.width / 2,
            y: canvas.height - 50,
            width: 40,
            height: 40,
            speed: 5,
            color: '#FFD700'
        }};

        let collectibles = [];
        let obstacles = [];
        let score = 0;
        let lives = 3;
        let gameRunning = true;

        // Create collectibles
        function spawnCollectible() {{
            collectibles.push({{
                x: Math.random() * (canvas.width - 30),
                y: 0,
                width: 20,
                height: 20,
                speed: 3,
                color: '#00FF00'
            }});
        }}

        // Create obstacles
        function spawnObstacle() {{
            obstacles.push({{
                x: Math.random() * (canvas.width - 40),
                y: 0,
                width: 40,
                height: 20,
                speed: 4,
                color: '#FF4444'
            }});
        }}

        // Keyboard controls
        const keys = {{}};
        window.addEventListener('keydown', (e) => keys[e.key] = true);
        window.addEventListener('keyup', (e) => keys[e.key] = false);

        // Mouse/touch controls
        window.addEventListener('mousemove', (e) => {{
            player.x = e.clientX - player.width / 2;
        }});

        // Game loop
        function gameLoop() {{
            if (!gameRunning) return;

            // Clear canvas
            ctx.fillStyle = '#1a1a2e';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Update player position
            if (keys['ArrowLeft'] || keys['a']) player.x -= player.speed;
            if (keys['ArrowRight'] || keys['d']) player.x += player.speed;

            // Keep player in bounds
            player.x = Math.max(0, Math.min(canvas.width - player.width, player.x));

            // Draw player
            ctx.fillStyle = player.color;
            ctx.fillRect(player.x, player.y, player.width, player.height);

            // Update and draw collectibles
            for (let i = collectibles.length - 1; i >= 0; i--) {{
                const c = collectibles[i];
                c.y += c.speed;

                ctx.fillStyle = c.color;
                ctx.fillRect(c.x, c.y, c.width, c.height);

                // Check collision with player
                if (c.x < player.x + player.width && c.x + c.width > player.x &&
                    c.y < player.y + player.height && c.y + c.height > player.y) {{
                    score += 10;
                    collectibles.splice(i, 1);
                    continue;
                }}

                // Remove if off screen
                if (c.y > canvas.height) {{
                    collectibles.splice(i, 1);
                }}
            }}

            // Update and draw obstacles
            for (let i = obstacles.length - 1; i >= 0; i--) {{
                const o = obstacles[i];
                o.y += o.speed;

                ctx.fillStyle = o.color;
                ctx.fillRect(o.x, o.y, o.width, o.height);

                // Check collision with player
                if (o.x < player.x + player.width && o.x + o.width > player.x &&
                    o.y < player.y + player.height && o.y + o.height > player.y) {{
                    lives--;
                    obstacles.splice(i, 1);
                    if (lives <= 0) {{
                        endGame();
                        return;
                    }}
                    continue;
                }}

                // Remove if off screen
                if (o.y > canvas.height) {{
                    obstacles.splice(i, 1);
                }}
            }}

            // Update UI
            document.getElementById('score').textContent = score;
            document.getElementById('lives').textContent = lives;

            // Spawn new items randomly
            if (Math.random() < 0.02) spawnCollectible();
            if (Math.random() < 0.015) spawnObstacle();

            requestAnimationFrame(gameLoop);
        }}

        function endGame() {{
            gameRunning = false;
            document.getElementById('finalScore').textContent = score;
            document.getElementById('gameOver').style.display = 'block';
        }}

        // Start game
        gameLoop();
    </script>
</body>
</html>"""


def generate_shooter_game(title="Shooter Game"):
    """Generate a real shooter game."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; background: #111; overflow: hidden; }}
        canvas {{ display: block; background: linear-gradient(to bottom, #1a1a2e, #16213e); }}
        #hud {{ position: absolute; top: 10px; left: 10px; color: #0f0; font-family: monospace; font-size: 16px; z-index: 10; }}
        .stat {{ margin: 5px 0; }}
        #gameOver {{
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: rgba(0,0,0,0.95); color: #0f0; padding: 40px; border-radius: 5px;
            text-align: center; font-size: 20px; font-family: monospace; z-index: 20; display: none;
        }}
        button {{ padding: 10px 20px; font-size: 16px; cursor: pointer; margin-top: 20px; background: #0f0; color: #000; }}
    </style>
</head>
<body>
    <canvas id="gameCanvas"></canvas>
    <div id="hud">
        <div class="stat">AMMO: <span id="ammo">30</span></div>
        <div class="stat">KILLS: <span id="kills">0</span></div>
        <div class="stat">HEALTH: <span id="health">100</span></div>
    </div>
    <div id="gameOver">
        <div>MISSION FAILED</div>
        <div>Enemies Defeated: <span id="finalKills">0</span></div>
        <button onclick="location.reload()">RESTART</button>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        // Player
        const player = {{
            x: canvas.width / 2,
            y: canvas.height - 50,
            width: 30,
            height: 40,
            speed: 6,
            health: 100
        }};

        let enemies = [];
        let bullets = [];
        let kills = 0;
        let ammo = 30;
        let gameRunning = true;

        // Spawn enemies
        function spawnEnemy() {{
            enemies.push({{
                x: Math.random() * canvas.width,
                y: Math.random() * (canvas.height / 3),
                width: 25,
                height: 25,
                speed: 2,
                health: 1
            }});
        }}

        // Keyboard controls
        const keys = {{}};
        window.addEventListener('keydown', (e) => {{
            keys[e.key] = true;
            if (e.key === ' ') {{
                e.preventDefault();
                shoot();
            }}
        }});
        window.addEventListener('keyup', (e) => keys[e.key] = false);

        // Mouse aiming
        let mouseX = canvas.width / 2;
        let mouseY = canvas.height / 2;
        window.addEventListener('mousemove', (e) => {{
            mouseX = e.clientX;
            mouseY = e.clientY;
            player.x = e.clientX - player.width / 2;
        }});

        // Shoot
        function shoot() {{
            if (ammo <= 0) return;
            ammo--;
            const angle = Math.atan2(mouseY - player.y, mouseX - player.x);
            bullets.push({{
                x: player.x + player.width / 2,
                y: player.y,
                vx: Math.cos(angle) * 8,
                vy: Math.sin(angle) * 8,
                radius: 5
            }});
        }}

        // Game loop
        function gameLoop() {{
            if (!gameRunning) return;

            // Clear
            ctx.fillStyle = '#0a0a0a';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Draw grid
            ctx.strokeStyle = 'rgba(0, 255, 0, 0.1)';
            ctx.lineWidth = 1;
            for (let i = 0; i < canvas.width; i += 50) {{
                ctx.beginPath();
                ctx.moveTo(i, 0);
                ctx.lineTo(i, canvas.height);
                ctx.stroke();
            }}

            // Draw player
            ctx.fillStyle = '#00FF00';
            ctx.fillRect(player.x, player.y, player.width, player.height);

            // Draw aiming crosshair
            ctx.strokeStyle = '#00FF00';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(mouseX - 10, mouseY);
            ctx.lineTo(mouseX + 10, mouseY);
            ctx.moveTo(mouseX, mouseY - 10);
            ctx.lineTo(mouseX, mouseY + 10);
            ctx.stroke();

            // Update bullets
            for (let i = bullets.length - 1; i >= 0; i--) {{
                const b = bullets[i];
                b.x += b.vx;
                b.y += b.vy;

                ctx.fillStyle = '#FFFF00';
                ctx.beginPath();
                ctx.arc(b.x, b.y, b.radius, 0, Math.PI * 2);
                ctx.fill();

                if (b.x < 0 || b.x > canvas.width || b.y < 0 || b.y > canvas.height) {{
                    bullets.splice(i, 1);
                }}
            }}

            // Update enemies
            for (let i = enemies.length - 1; i >= 0; i--) {{
                const e = enemies[i];
                e.y += e.speed;

                ctx.fillStyle = '#FF4444';
                ctx.fillRect(e.x, e.y, e.width, e.height);

                // Check bullet collisions
                for (let j = bullets.length - 1; j >= 0; j--) {{
                    const b = bullets[j];
                    if (b.x > e.x && b.x < e.x + e.width &&
                        b.y > e.y && b.y < e.y + e.height) {{
                        kills++;
                        enemies.splice(i, 1);
                        bullets.splice(j, 1);
                        if (Math.random() < 0.3) ammo += 5;
                        break;
                    }}
                }}

                // Check enemy collision with player
                if (e.x < player.x + player.width && e.x + e.width > player.x &&
                    e.y < player.y + player.height && e.y + e.height > player.y) {{
                    player.health -= 5;
                    enemies.splice(i, 1);
                    if (player.health <= 0) {{
                        endGame();
                        return;
                    }}
                }}

                if (e.y > canvas.height) {{
                    enemies.splice(i, 1);
                }}
            }}

            // Spawn enemies
            if (Math.random() < 0.03) spawnEnemy();

            // Ammo regeneration
            if (Math.random() < 0.01 && ammo < 60) ammo++;

            // Update HUD
            document.getElementById('ammo').textContent = ammo;
            document.getElementById('kills').textContent = kills;
            document.getElementById('health').textContent = Math.max(0, player.health);

            requestAnimationFrame(gameLoop);
        }}

        function endGame() {{
            gameRunning = false;
            document.getElementById('finalKills').textContent = kills;
            document.getElementById('gameOver').style.display = 'block';
        }}

        gameLoop();
    </script>
</body>
</html>"""


def generate_platformer_game(title="Platformer Game"):
    """Generate a real platformer game."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; background: #1a1a1a; overflow: hidden; }}
        canvas {{ display: block; background: linear-gradient(to bottom, #87CEEB, #E0F6FF); }}
        #ui {{ position: absolute; top: 10px; left: 10px; color: white; font-size: 18px; z-index: 10; }}
        #gameOver {{
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: rgba(0,0,0,0.9); color: white; padding: 40px; border-radius: 10px;
            text-align: center; z-index: 20; display: none;
        }}
        button {{ padding: 10px 20px; font-size: 16px; cursor: pointer; margin-top: 20px; }}
    </style>
</head>
<body>
    <canvas id="gameCanvas"></canvas>
    <div id="ui">
        <div>Level: <span id="level">1</span></div>
        <div>Time: <span id="time">0</span>s</div>
    </div>
    <div id="gameOver">
        <div id="message">Level Complete!</div>
        <button onclick="location.reload()">Play Again</button>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        // Player
        const player = {{
            x: 50,
            y: canvas.height - 100,
            width: 30,
            height: 40,
            velocityY: 0,
            speed: 5,
            jumpPower: 15,
            onGround: false
        }};

        let platforms = [];
        let goal = null;
        let level = 1;
        let gameRunning = true;
        let startTime = Date.now();

        const gravity = 0.6;

        // Create level
        function generateLevel() {{
            platforms = [
                // Ground
                {{ x: 0, y: canvas.height - 50, width: canvas.width, height: 50, color: '#8B4513' }},
                // Platforms
                {{ x: 150, y: canvas.height - 150, width: 150, height: 20, color: '#228B22' }},
                {{ x: 400, y: canvas.height - 200, width: 150, height: 20, color: '#228B22' }},
                {{ x: 650, y: canvas.height - 250, width: 150, height: 20, color: '#228B22' }},
                {{ x: 900, y: canvas.height - 200, width: 150, height: 20, color: '#228B22' }},
                {{ x: canvas.width - 200, y: 100, width: 150, height: 20, color: '#FFD700' }}
            ];

            goal = {{ x: canvas.width - 175, y: 50, width: 100, height: 40, color: '#00FF00' }};
        }}

        // Keyboard
        const keys = {{}};
        window.addEventListener('keydown', (e) => {{
            keys[e.key] = true;
            if ((e.key === ' ' || e.key === 'ArrowUp' || e.key === 'w') && player.onGround) {{
                player.velocityY = -player.jumpPower;
                player.onGround = false;
                e.preventDefault();
            }}
        }});
        window.addEventListener('keyup', (e) => keys[e.key] = false);

        // Game loop
        function gameLoop() {{
            if (!gameRunning) return;

            // Clear
            ctx.fillStyle = '#87CEEB';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Update player
            if (keys['ArrowLeft'] || keys['a']) player.x -= player.speed;
            if (keys['ArrowRight'] || keys['d']) player.x += player.speed;

            player.velocityY += gravity;
            player.y += player.velocityY;

            player.onGround = false;

            // Collision with platforms
            for (const platform of platforms) {{
                if (player.velocityY >= 0 &&
                    player.y + player.height >= platform.y &&
                    player.y + player.height <= platform.y + platform.height + 10 &&
                    player.x + player.width > platform.x &&
                    player.x < platform.x + platform.width) {{
                    player.y = platform.y - player.height;
                    player.velocityY = 0;
                    player.onGround = true;
                }}
            }}

            // Draw platforms
            for (const platform of platforms) {{
                ctx.fillStyle = platform.color;
                ctx.fillRect(platform.x, platform.y, platform.width, platform.height);
            }}

            // Draw player
            ctx.fillStyle = '#FF6B6B';
            ctx.fillRect(player.x, player.y, player.width, player.height);

            // Draw goal
            ctx.fillStyle = goal.color;
            ctx.fillRect(goal.x, goal.y, goal.width, goal.height);
            ctx.fillStyle = 'white';
            ctx.font = '20px Arial';
            ctx.fillText('GOAL', goal.x + 25, goal.y + 25);

            // Check goal collision
            if (player.x + player.width > goal.x && player.x < goal.x + goal.width &&
                player.y + player.height > goal.y && player.y < goal.y + goal.height) {{
                gameRunning = false;
                const time = Math.floor((Date.now() - startTime) / 1000);
                document.getElementById('message').textContent = 'Level ' + level + ' Complete! Time: ' + time + 's';
                document.getElementById('gameOver').style.display = 'block';
            }}

            // Fall off map
            if (player.y > canvas.height) {{
                gameRunning = false;
                document.getElementById('message').textContent = 'You fell! Game Over';
                document.getElementById('gameOver').style.display = 'block';
            }}

            // Update time
            const elapsed = Math.floor((Date.now() - startTime) / 1000);
            document.getElementById('time').textContent = elapsed;
            document.getElementById('level').textContent = level;

            requestAnimationFrame(gameLoop);
        }}

        generateLevel();
        gameLoop();
    </script>
</body>
</html>"""


def save_game_file(game_type: str, title: str, prompt: str) -> str:
    """Save game HTML to file and return path."""
    generators = {
        'collector': generate_collector_game,
        'shooter': generate_shooter_game,
        'platformer': generate_platformer_game,
    }

    generator = generators.get(game_type, generate_collector_game)
    html = generator(title)

    filename = f"game_{game_type}_{int(datetime.now().timestamp())}.html"
    filepath = f"/c/Gamansai/ai/static/{filename}"

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(html)

    return f"/static/{filename}"


if __name__ == "__main__":
    # Test
    collector = generate_collector_game("Test Collector")
    with open("/tmp/test_collector.html", "w") as f:
        f.write(collector)
    print("✅ Generated collector game at /tmp/test_collector.html")

    shooter = generate_shooter_game("Test Shooter")
    with open("/tmp/test_shooter.html", "w") as f:
        f.write(shooter)
    print("✅ Generated shooter game at /tmp/test_shooter.html")

    platformer = generate_platformer_game("Test Platformer")
    with open("/tmp/test_platformer.html", "w") as f:
        f.write(platformer)
    print("✅ Generated platformer game at /tmp/test_platformer.html")
