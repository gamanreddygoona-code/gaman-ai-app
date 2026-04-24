"""
scene_generator.py
──────────────────
Generates Three.js scene code from natural-language prompts.
Runs on CPU only — the browser's GPU does the 3D rendering.
"""

from __future__ import annotations
import re
import random


# ── Object library (procedural primitives & composite shapes) ────
SHAPES = {
    "cube":     "new THREE.BoxGeometry(1,1,1)",
    "box":      "new THREE.BoxGeometry(1,1,1)",
    "sphere":   "new THREE.SphereGeometry(0.7, 32, 32)",
    "ball":     "new THREE.SphereGeometry(0.7, 32, 32)",
    "cylinder": "new THREE.CylinderGeometry(0.5, 0.5, 1.5, 32)",
    "cone":     "new THREE.ConeGeometry(0.6, 1.2, 32)",
    "torus":    "new THREE.TorusGeometry(0.6, 0.2, 16, 100)",
    "donut":    "new THREE.TorusGeometry(0.6, 0.2, 16, 100)",
    "pyramid":  "new THREE.ConeGeometry(0.7, 1, 4)",
    "plane":    "new THREE.PlaneGeometry(2, 2)",
}

COLORS = {
    "red":    0xff3333, "green":  0x33cc66, "blue": 0x3366ff,
    "yellow": 0xffdd33, "orange": 0xff8833, "purple": 0xaa33ff,
    "pink":   0xff66cc, "white":  0xffffff, "black": 0x222222,
    "gray":   0x888888, "brown":  0x8b5a2b, "cyan":  0x33cccc,
    "gold":   0xffd700, "silver": 0xc0c0c0,
}

THEMES = {
    "forest":  {"bg": 0x88cc88, "ground": 0x3e7a34, "fog": True},
    "space":   {"bg": 0x000011, "ground": 0x111133, "fog": False, "stars": True},
    "desert":  {"bg": 0xffcc88, "ground": 0xe5b96c, "fog": False},
    "ocean":   {"bg": 0x66ccee, "ground": 0x0099cc, "fog": False},
    "city":    {"bg": 0xaabbcc, "ground": 0x666666, "fog": True},
    "sunset":  {"bg": 0xff8866, "ground": 0x553344, "fog": False},
    "night":   {"bg": 0x0a0a2a, "ground": 0x1a1a3a, "fog": False, "stars": True},
    "snow":    {"bg": 0xeeeeff, "ground": 0xffffff, "fog": True},
    "lava":    {"bg": 0xff3300, "ground": 0x661100, "fog": False},
}


def detect_shapes(prompt: str) -> list[str]:
    """Pick up all shape keywords mentioned in the prompt."""
    p = prompt.lower()
    found = []
    for name in SHAPES:
        if re.search(rf"\b{name}s?\b", p):
            found.append(name)
    return found or ["cube"]


def detect_color(prompt: str) -> int | None:
    p = prompt.lower()
    for name, hexv in COLORS.items():
        if re.search(rf"\b{name}\b", p):
            return hexv
    return None


def detect_theme(prompt: str) -> dict | None:
    p = prompt.lower()
    for name, cfg in THEMES.items():
        if name in p:
            return {**cfg, "name": name}
    return None


def detect_count(prompt: str) -> int:
    m = re.search(r"\b(\d{1,3})\b", prompt)
    if m:
        return min(int(m.group(1)), 200)
    words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
             "ten": 10, "twenty": 20, "fifty": 50, "many": 25, "few": 4}
    for w, n in words.items():
        if re.search(rf"\b{w}\b", prompt.lower()):
            return n
    return 1


def wants_game(prompt: str) -> bool:
    p = prompt.lower()
    return any(k in p for k in ["game", "play", "control", "move", "shoot", "jump", "dodge", "puzzle", "platform", "shooter", "collect", "maze"])


def detect_game_type(prompt: str) -> str:
    p = prompt.lower()
    if any(k in p for k in ["shoot", "shooter", "enemy", "enemies", "fire", "bullet"]):
        return "shooter"
    if any(k in p for k in ["jump", "platform", "platformer"]):
        return "platformer"
    if any(k in p for k in ["puzzle", "maze", "solve", "match"]):
        return "puzzle"
    if any(k in p for k in ["dodge", "avoid", "run", "endless"]):
        return "dodger"
    return "collector"


# ═══════════════════════════════════════════════════════════════
# SCENE CODE BUILDERS
# ═══════════════════════════════════════════════════════════════

def build_scene(prompt: str) -> dict:
    """Returns {'code': threejs_js_code, 'type': 'scene'|'game', 'description': str}"""
    shapes = detect_shapes(prompt)
    color  = detect_color(prompt)
    theme  = detect_theme(prompt) or {"bg": 0x87ceeb, "ground": 0x556b2f, "fog": False, "name": "default"}
    count  = detect_count(prompt)
    game   = wants_game(prompt)

    if game:
        return build_game(prompt, shapes, color, theme)
    return build_static_scene(prompt, shapes, color, theme, count)


def build_static_scene(prompt: str, shapes: list[str], color: int | None, theme: dict, count: int) -> dict:
    """Scene with randomly-placed objects, orbit camera."""
    obj_code_lines = []
    for i in range(count):
        shape = random.choice(shapes)
        c = color if color is not None else random.choice(list(COLORS.values()))
        x = round(random.uniform(-8, 8), 2)
        z = round(random.uniform(-8, 8), 2)
        y = round(random.uniform(0.5, 2), 2)
        obj_code_lines.append(
            f"  {{ geo: {SHAPES[shape]}, color: 0x{c:06x}, pos: [{x}, {y}, {z}] }}"
        )

    objects_js = ",\n".join(obj_code_lines)
    stars_js = "addStars();" if theme.get("stars") else ""
    fog_js = f"scene.fog = new THREE.Fog(0x{theme['bg']:06x}, 5, 40);" if theme.get("fog") else ""

    code = SCENE_TEMPLATE.format(
        bg=f"0x{theme['bg']:06x}",
        ground=f"0x{theme['ground']:06x}",
        objects=objects_js,
        stars=stars_js,
        fog=fog_js,
    )

    return {
        "code": code,
        "type": "scene",
        "description": f"{count} {', '.join(shapes)} in a {theme['name']} scene",
    }


def build_game(prompt: str, shapes: list[str], color: int | None, theme: dict) -> dict:
    """Build the right game template based on detected type."""
    c = color if color is not None else 0xffdd33
    kind = detect_game_type(prompt)

    template_map = {
        "collector":  GAME_TEMPLATE,
        "shooter":    SHOOTER_TEMPLATE,
        "platformer": PLATFORMER_TEMPLATE,
        "dodger":     DODGER_TEMPLATE,
        "puzzle":     PUZZLE_TEMPLATE,
    }
    template = template_map.get(kind, GAME_TEMPLATE)

    code = template.format(
        bg=f"0x{theme['bg']:06x}",
        ground=f"0x{theme['ground']:06x}",
        player_color=f"0x{c:06x}",
    )
    descriptions = {
        "collector":  f"WASD collector game ({theme['name']} theme)",
        "shooter":    f"Top-down shooter ({theme['name']} theme) — WASD move, SPACE shoot",
        "platformer": f"Side-scroll platformer ({theme['name']} theme) — A/D move, SPACE jump",
        "dodger":     f"Endless dodger ({theme['name']} theme) — A/D dodge falling obstacles",
        "puzzle":     f"Memory match puzzle ({theme['name']} theme) — click matching pairs",
    }
    return {"code": code, "type": "game", "description": descriptions[kind]}


# ═══════════════════════════════════════════════════════════════
# THREE.JS CODE TEMPLATES (injected into the /3d page)
# ═══════════════════════════════════════════════════════════════

SCENE_TEMPLATE = """
const scene = new THREE.Scene();
scene.background = new THREE.Color({bg});
{fog}

const camera = new THREE.PerspectiveCamera(60, container.clientWidth/container.clientHeight, 0.1, 200);
camera.position.set(8, 6, 12);
camera.lookAt(0, 0, 0);

const renderer = new THREE.WebGLRenderer({{ antialias: true }});
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(container.clientWidth, container.clientHeight);
renderer.shadowMap.enabled = true;
container.innerHTML = '';
container.appendChild(renderer.domElement);

// Lights
const ambient = new THREE.AmbientLight(0xffffff, 0.55);
scene.add(ambient);
const sun = new THREE.DirectionalLight(0xffffff, 0.9);
sun.position.set(10, 20, 10);
sun.castShadow = true;
scene.add(sun);

// Ground
const ground = new THREE.Mesh(
  new THREE.PlaneGeometry(60, 60),
  new THREE.MeshStandardMaterial({{ color: {ground} }})
);
ground.rotation.x = -Math.PI/2;
ground.receiveShadow = true;
scene.add(ground);

// Stars helper
function addStars() {{
  const g = new THREE.BufferGeometry();
  const pts = [];
  for (let i=0; i<800; i++) pts.push((Math.random()-0.5)*200, Math.random()*100, (Math.random()-0.5)*200);
  g.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
  scene.add(new THREE.Points(g, new THREE.PointsMaterial({{ color: 0xffffff, size: 0.3 }})));
}}
{stars}

// Objects
const objects = [
{objects}
];

const meshes = [];
objects.forEach(o => {{
  const mat = new THREE.MeshStandardMaterial({{ color: o.color, roughness: 0.5 }});
  const mesh = new THREE.Mesh(o.geo, mat);
  mesh.position.set(...o.pos);
  mesh.castShadow = true;
  scene.add(mesh);
  meshes.push(mesh);
}});

// Camera orbit
let angle = 0;
function animate() {{
  requestAnimationFrame(animate);
  angle += 0.003;
  camera.position.x = Math.cos(angle) * 14;
  camera.position.z = Math.sin(angle) * 14;
  camera.lookAt(0, 1, 0);
  meshes.forEach((m, i) => m.rotation.y += 0.005 + i*0.0005);
  renderer.render(scene, camera);
}}
animate();

window.addEventListener('resize', () => {{
  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
}});
"""


GAME_TEMPLATE = """
const scene = new THREE.Scene();
scene.background = new THREE.Color({bg});

const camera = new THREE.PerspectiveCamera(70, container.clientWidth/container.clientHeight, 0.1, 200);
camera.position.set(0, 8, 10);
camera.lookAt(0, 0, 0);

const renderer = new THREE.WebGLRenderer({{ antialias: true }});
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(container.clientWidth, container.clientHeight);
container.innerHTML = '';
container.appendChild(renderer.domElement);

const ambient = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambient);
const dir = new THREE.DirectionalLight(0xffffff, 0.8);
dir.position.set(5, 10, 5);
scene.add(dir);

const ground = new THREE.Mesh(
  new THREE.PlaneGeometry(40, 40),
  new THREE.MeshStandardMaterial({{ color: {ground} }})
);
ground.rotation.x = -Math.PI/2;
scene.add(ground);

// Player
const player = new THREE.Mesh(
  new THREE.BoxGeometry(1, 1, 1),
  new THREE.MeshStandardMaterial({{ color: {player_color} }})
);
player.position.y = 0.5;
scene.add(player);

// Coins
const coins = [];
function spawnCoin() {{
  const c = new THREE.Mesh(
    new THREE.TorusGeometry(0.35, 0.12, 12, 24),
    new THREE.MeshStandardMaterial({{ color: 0xffd700 }})
  );
  c.position.set((Math.random()-0.5)*30, 0.5, (Math.random()-0.5)*30);
  c.rotation.x = Math.PI/2;
  scene.add(c);
  coins.push(c);
}}
for (let i=0; i<12; i++) spawnCoin();

// HUD
const hud = document.createElement('div');
hud.style.cssText = 'position:absolute;top:10px;left:10px;color:white;font:bold 18px sans-serif;background:rgba(0,0,0,0.5);padding:8px 12px;border-radius:6px;';
hud.textContent = 'Score: 0  |  WASD to move';
container.style.position = 'relative';
container.appendChild(hud);
let score = 0;

// Controls
const keys = {{}};
window.addEventListener('keydown', e => keys[e.key.toLowerCase()] = true);
window.addEventListener('keyup',   e => keys[e.key.toLowerCase()] = false);

function animate() {{
  requestAnimationFrame(animate);

  const speed = 0.18;
  if (keys['w']) player.position.z -= speed;
  if (keys['s']) player.position.z += speed;
  if (keys['a']) player.position.x -= speed;
  if (keys['d']) player.position.x += speed;
  player.position.x = Math.max(-19, Math.min(19, player.position.x));
  player.position.z = Math.max(-19, Math.min(19, player.position.z));

  // Collect coins
  for (let i = coins.length - 1; i >= 0; i--) {{
    const c = coins[i];
    c.rotation.z += 0.05;
    if (player.position.distanceTo(c.position) < 0.9) {{
      scene.remove(c);
      coins.splice(i, 1);
      score++;
      hud.textContent = 'Score: ' + score + '  |  WASD to move';
      spawnCoin();
    }}
  }}

  // Camera follow
  camera.position.x = player.position.x;
  camera.position.z = player.position.z + 10;
  camera.lookAt(player.position);

  renderer.render(scene, camera);
}}
animate();

window.addEventListener('resize', () => {{
  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
}});
"""



# ═══════════════════════════════════════════════════════════════
# SHOOTER — top-down, WASD move + SPACE shoot
# ═══════════════════════════════════════════════════════════════
SHOOTER_TEMPLATE = """
const scene = new THREE.Scene();
scene.background = new THREE.Color({bg});
const camera = new THREE.PerspectiveCamera(60, container.clientWidth/container.clientHeight, 0.1, 200);
camera.position.set(0, 22, 0); camera.lookAt(0, 0, 0);
const renderer = new THREE.WebGLRenderer({{ antialias: true }});
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(container.clientWidth, container.clientHeight);
container.innerHTML = ''; container.appendChild(renderer.domElement);

scene.add(new THREE.AmbientLight(0xffffff, 0.8));
const ground = new THREE.Mesh(new THREE.PlaneGeometry(50, 50), new THREE.MeshStandardMaterial({{ color: {ground} }}));
ground.rotation.x = -Math.PI/2; scene.add(ground);

const player = new THREE.Mesh(new THREE.ConeGeometry(0.6, 1.4, 8), new THREE.MeshStandardMaterial({{ color: {player_color} }}));
player.position.y = 0.7; player.rotation.x = Math.PI/2; scene.add(player);

const bullets = [], enemies = [];
function spawnEnemy() {{
  const e = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), new THREE.MeshStandardMaterial({{ color: 0xff3333 }}));
  const side = Math.floor(Math.random()*4);
  if (side===0) e.position.set(-20, 0.5, (Math.random()-0.5)*30);
  else if (side===1) e.position.set(20, 0.5, (Math.random()-0.5)*30);
  else if (side===2) e.position.set((Math.random()-0.5)*30, 0.5, -20);
  else e.position.set((Math.random()-0.5)*30, 0.5, 20);
  scene.add(e); enemies.push(e);
}}
for (let i=0; i<5; i++) spawnEnemy();

const hud = document.createElement('div');
hud.style.cssText = 'position:absolute;top:10px;left:10px;color:white;font:bold 16px sans-serif;background:rgba(0,0,0,0.6);padding:8px 12px;border-radius:6px;';
hud.textContent = 'Kills: 0 | HP: 3 | WASD move, SPACE shoot';
container.style.position = 'relative'; container.appendChild(hud);
let kills = 0, hp = 3, aim = 0;

const keys = {{}};
window.addEventListener('keydown', e => {{
  keys[e.key.toLowerCase()] = true;
  if (e.code === 'Space') {{
    const b = new THREE.Mesh(new THREE.SphereGeometry(0.2, 8, 8), new THREE.MeshBasicMaterial({{ color: 0xffff00 }}));
    b.position.copy(player.position);
    b.vx = Math.cos(aim)*0.6; b.vz = Math.sin(aim)*0.6;
    scene.add(b); bullets.push(b);
  }}
}});
window.addEventListener('keyup', e => keys[e.key.toLowerCase()] = false);

let spawnTick = 0;
function animate() {{
  requestAnimationFrame(animate);
  const sp = 0.18; let dx=0,dz=0;
  if (keys['w']) dz -= sp; if (keys['s']) dz += sp;
  if (keys['a']) dx -= sp; if (keys['d']) dx += sp;
  if (dx||dz) aim = Math.atan2(dz, dx);
  player.position.x += dx; player.position.z += dz;
  player.position.x = Math.max(-24, Math.min(24, player.position.x));
  player.position.z = Math.max(-24, Math.min(24, player.position.z));
  for (let i = bullets.length-1; i >= 0; i--) {{
    const b = bullets[i]; b.position.x += b.vx; b.position.z += b.vz;
    if (Math.abs(b.position.x) > 26 || Math.abs(b.position.z) > 26) {{ scene.remove(b); bullets.splice(i,1); continue; }}
    for (let j = enemies.length-1; j >= 0; j--) {{
      if (b.position.distanceTo(enemies[j].position) < 1) {{
        scene.remove(enemies[j]); enemies.splice(j,1);
        scene.remove(b); bullets.splice(i,1);
        kills++; spawnEnemy(); break;
      }}
    }}
  }}
  for (const e of enemies) {{
    const d = player.position.clone().sub(e.position).normalize().multiplyScalar(0.04);
    e.position.add(d);
    if (e.position.distanceTo(player.position) < 1) {{
      e.position.set((Math.random()-0.5)*40, 0.5, -20);
      hp--; if (hp <= 0) {{ hud.textContent = 'Game Over - Kills: ' + kills; return; }}
    }}
  }}
  spawnTick++; if (spawnTick > 120) {{ spawnTick = 0; spawnEnemy(); }}
  hud.textContent = 'Kills: ' + kills + ' | HP: ' + hp + ' | WASD move, SPACE shoot';
  renderer.render(scene, camera);
}}
animate();
window.addEventListener('resize', () => {{
  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
}});
"""


# ═══════════════════════════════════════════════════════════════
# PLATFORMER — side-scroll, A/D + SPACE jump
# ═══════════════════════════════════════════════════════════════
PLATFORMER_TEMPLATE = """
const scene = new THREE.Scene();
scene.background = new THREE.Color({bg});
const camera = new THREE.PerspectiveCamera(55, container.clientWidth/container.clientHeight, 0.1, 200);
camera.position.set(0, 3, 12); camera.lookAt(0, 2, 0);
const renderer = new THREE.WebGLRenderer({{ antialias: true }});
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(container.clientWidth, container.clientHeight);
container.innerHTML = ''; container.appendChild(renderer.domElement);

scene.add(new THREE.AmbientLight(0xffffff, 0.7));

const platforms = [
  {{ x:0, y:0, w:6 }}, {{ x:8, y:1.5, w:3 }}, {{ x:14, y:3, w:3 }},
  {{ x:20, y:2, w:4 }}, {{ x:27, y:4, w:3 }}, {{ x:33, y:3, w:5 }},
];
const platMeshes = [];
platforms.forEach(p => {{
  const m = new THREE.Mesh(new THREE.BoxGeometry(p.w, 0.4, 2), new THREE.MeshStandardMaterial({{ color: {ground} }}));
  m.position.set(p.x, p.y, 0); scene.add(m); platMeshes.push({{ mesh: m, p }});
}});

const coins = [];
[8, 14, 20, 27, 33].forEach((x, i) => {{
  const c = new THREE.Mesh(new THREE.TorusGeometry(0.3, 0.1, 10, 20), new THREE.MeshStandardMaterial({{ color: 0xffd700 }}));
  c.position.set(x, platforms[i+1].y + 1, 0); scene.add(c); coins.push(c);
}});

const player = new THREE.Mesh(new THREE.BoxGeometry(0.8, 1.2, 0.8), new THREE.MeshStandardMaterial({{ color: {player_color} }}));
player.position.set(-2, 2, 0); scene.add(player);

const hud = document.createElement('div');
hud.style.cssText = 'position:absolute;top:10px;left:10px;color:white;font:bold 16px sans-serif;background:rgba(0,0,0,0.6);padding:8px 12px;border-radius:6px;';
hud.textContent = 'Coins: 0/5 | A/D move, SPACE jump';
container.style.position = 'relative'; container.appendChild(hud);

let vx = 0, vy = 0, onGround = false, coinsGot = 0;
const keys = {{}};
window.addEventListener('keydown', e => keys[e.key.toLowerCase()] = true);
window.addEventListener('keyup',   e => keys[e.key.toLowerCase()] = false);

function animate() {{
  requestAnimationFrame(animate);
  if (keys['a']) vx = -0.12; else if (keys['d']) vx = 0.12; else vx = 0;
  if (keys[' '] && onGround) {{ vy = 0.28; onGround = false; }}
  vy -= 0.012;
  player.position.x += vx; player.position.y += vy;
  onGround = false;
  for (const item of platMeshes) {{
    const p = item.p;
    if (Math.abs(player.position.x - p.x) < p.w/2 + 0.4 &&
        player.position.y > p.y + 0.2 && player.position.y < p.y + 0.9 && vy <= 0) {{
      player.position.y = p.y + 0.8; vy = 0; onGround = true;
    }}
  }}
  if (player.position.y < -10) {{ player.position.set(-2, 5, 0); vy = 0; }}
  for (let i = coins.length-1; i >= 0; i--) {{
    coins[i].rotation.y += 0.05;
    if (player.position.distanceTo(coins[i].position) < 1) {{
      scene.remove(coins[i]); coins.splice(i,1); coinsGot++;
    }}
  }}
  camera.position.x = player.position.x + 4;
  camera.lookAt(player.position.x, player.position.y, 0);
  hud.textContent = 'Coins: ' + coinsGot + '/5 | A/D move, SPACE jump' + (coinsGot===5 ? ' WIN!' : '');
  renderer.render(scene, camera);
}}
animate();
window.addEventListener('resize', () => {{
  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
}});
"""


# ═══════════════════════════════════════════════════════════════
# DODGER — A/D to dodge falling blocks
# ═══════════════════════════════════════════════════════════════
DODGER_TEMPLATE = """
const scene = new THREE.Scene();
scene.background = new THREE.Color({bg});
const camera = new THREE.PerspectiveCamera(55, container.clientWidth/container.clientHeight, 0.1, 200);
camera.position.set(0, 5, 12); camera.lookAt(0, 2, 0);
const renderer = new THREE.WebGLRenderer({{ antialias: true }});
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(container.clientWidth, container.clientHeight);
container.innerHTML = ''; container.appendChild(renderer.domElement);
scene.add(new THREE.AmbientLight(0xffffff, 0.7));
const g = new THREE.Mesh(new THREE.PlaneGeometry(20, 60), new THREE.MeshStandardMaterial({{ color: {ground} }}));
g.rotation.x = -Math.PI/2; scene.add(g);

const player = new THREE.Mesh(new THREE.SphereGeometry(0.6, 24, 24), new THREE.MeshStandardMaterial({{ color: {player_color} }}));
player.position.set(0, 0.6, 0); scene.add(player);

const obstacles = [];
function spawnObstacle() {{
  const o = new THREE.Mesh(new THREE.BoxGeometry(1.2, 1.2, 1.2), new THREE.MeshStandardMaterial({{ color: 0xff2222 }}));
  o.position.set((Math.random()-0.5)*8, 0.6, -20);
  scene.add(o); obstacles.push(o);
}}

const hud = document.createElement('div');
hud.style.cssText = 'position:absolute;top:10px;left:10px;color:white;font:bold 16px sans-serif;background:rgba(0,0,0,0.6);padding:8px 12px;border-radius:6px;';
hud.textContent = 'Score: 0 | A/D to dodge';
container.style.position = 'relative'; container.appendChild(hud);

const keys = {{}}; let score = 0, dead = false, spawnT = 0, speed = 0.2;
window.addEventListener('keydown', e => keys[e.key.toLowerCase()] = true);
window.addEventListener('keyup',   e => keys[e.key.toLowerCase()] = false);

function animate() {{
  requestAnimationFrame(animate);
  if (dead) return;
  if (keys['a']) player.position.x -= 0.18;
  if (keys['d']) player.position.x += 0.18;
  player.position.x = Math.max(-4.5, Math.min(4.5, player.position.x));
  spawnT++; if (spawnT > 30) {{ spawnT = 0; spawnObstacle(); }}
  for (let i = obstacles.length-1; i >= 0; i--) {{
    obstacles[i].position.z += speed;
    if (obstacles[i].position.z > 3) {{ scene.remove(obstacles[i]); obstacles.splice(i,1); score++; }}
    else if (obstacles[i].position.distanceTo(player.position) < 1) {{ dead = true; hud.textContent = 'Game Over - Score: ' + score; return; }}
  }}
  speed += 0.0002;
  hud.textContent = 'Score: ' + score + ' | A/D to dodge';
  renderer.render(scene, camera);
}}
animate();
window.addEventListener('resize', () => {{
  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
}});
"""


# ═══════════════════════════════════════════════════════════════
# PUZZLE — click to flip & match colored cubes
# ═══════════════════════════════════════════════════════════════
PUZZLE_TEMPLATE = """
const scene = new THREE.Scene();
scene.background = new THREE.Color({bg});
const camera = new THREE.PerspectiveCamera(55, container.clientWidth/container.clientHeight, 0.1, 200);
camera.position.set(0, 8, 8); camera.lookAt(0, 0, 0);
const renderer = new THREE.WebGLRenderer({{ antialias: true }});
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(container.clientWidth, container.clientHeight);
container.innerHTML = ''; container.appendChild(renderer.domElement);
scene.add(new THREE.AmbientLight(0xffffff, 0.9));
const plane = new THREE.Mesh(new THREE.PlaneGeometry(10, 10), new THREE.MeshStandardMaterial({{ color: {ground} }}));
plane.rotation.x = -Math.PI/2; plane.position.y = -0.01; scene.add(plane);

const palette = [0xff3333, 0x33cc66, 0x3366ff, 0xffdd33, 0xff66cc, 0x33cccc, 0xaa33ff, 0xffa500];
const pairs = [...palette, ...palette];
for (let i = pairs.length - 1; i > 0; i--) {{ const j = Math.floor(Math.random()*(i+1)); [pairs[i], pairs[j]] = [pairs[j], pairs[i]]; }}

const cubes = [];
for (let i = 0; i < 16; i++) {{
  const row = Math.floor(i/4), col = i%4;
  const c = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.9, 0.9), new THREE.MeshStandardMaterial({{ color: 0x555555 }}));
  c.position.set((col-1.5)*1.2, 0.45, (row-1.5)*1.2);
  c.userData = {{ color: pairs[i], revealed: false, matched: false }};
  scene.add(c); cubes.push(c);
}}

const hud = document.createElement('div');
hud.style.cssText = 'position:absolute;top:10px;left:10px;color:white;font:bold 16px sans-serif;background:rgba(0,0,0,0.6);padding:8px 12px;border-radius:6px;';
hud.textContent = 'Matches: 0/8 | Click cubes to flip';
container.style.position = 'relative'; container.appendChild(hud);

const raycaster = new THREE.Raycaster(); const mouse = new THREE.Vector2();
let first = null, second = null, matches = 0, locked = false;

renderer.domElement.addEventListener('click', e => {{
  if (locked) return;
  const r = renderer.domElement.getBoundingClientRect();
  mouse.x = ((e.clientX - r.left)/r.width)*2 - 1;
  mouse.y = -((e.clientY - r.top)/r.height)*2 + 1;
  raycaster.setFromCamera(mouse, camera);
  const hit = raycaster.intersectObjects(cubes)[0];
  if (!hit || hit.object.userData.matched || hit.object.userData.revealed) return;
  hit.object.material.color.setHex(hit.object.userData.color);
  hit.object.userData.revealed = true;
  if (!first) {{ first = hit.object; }}
  else {{
    second = hit.object; locked = true;
    setTimeout(() => {{
      if (first.userData.color === second.userData.color) {{
        first.userData.matched = second.userData.matched = true;
        matches++; hud.textContent = 'Matches: ' + matches + '/8' + (matches===8 ? ' WIN!' : '');
      }} else {{
        first.material.color.setHex(0x555555); second.material.color.setHex(0x555555);
        first.userData.revealed = second.userData.revealed = false;
      }}
      first = second = null; locked = false;
    }}, 800);
  }}
}});

function animate() {{ requestAnimationFrame(animate); renderer.render(scene, camera); }}
animate();
window.addEventListener('resize', () => {{
  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
}});
"""
