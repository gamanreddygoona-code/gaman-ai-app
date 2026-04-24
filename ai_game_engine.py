"""
ai_game_engine.py
─────────────────
Ludo-AI-style game generator.
Given a user prompt → returns REAL playable Three.js 3D game code + explanation.
No simulation. The code runs LIVE in the browser.
"""

import re


# ─────────────────────────────────────────────────────────────────────────────
# Template library  (each returns a full JS string that runs inside a <script>)
# ─────────────────────────────────────────────────────────────────────────────

def _racing_game(cfg: dict) -> str:
    sky   = cfg.get("sky",   "0x1a0033")
    road  = cfg.get("road",  "0x222222")
    car   = cfg.get("car",   "0xff2200")
    title = cfg.get("title", "Racing Game")
    return f"""
// ── {title} ── Three.js 3D Racing Game ──────────────────────────────────────
const scene    = new THREE.Scene();
scene.background = new THREE.Color({sky});
scene.fog        = new THREE.Fog({sky}, 30, 120);

const camera = new THREE.PerspectiveCamera(70, container.clientWidth / container.clientHeight, 0.1, 500);
camera.position.set(0, 5, -10);

const renderer = new THREE.WebGLRenderer({{ antialias: true }});
renderer.shadowMap.enabled = true;
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(container.clientWidth, container.clientHeight);
container.appendChild(renderer.domElement);

// Lights
scene.add(new THREE.AmbientLight(0xffffff, 0.6));
const sun = new THREE.DirectionalLight(0xffffff, 1.2);
sun.position.set(20, 40, 20);
sun.castShadow = true;
scene.add(sun);

// Road
const roadGeo  = new THREE.PlaneGeometry(10, 2000);
const roadMat  = new THREE.MeshLambertMaterial({{ color: {road} }});
const road     = new THREE.Mesh(roadGeo, roadMat);
road.rotation.x = -Math.PI / 2;
road.receiveShadow = true;
scene.add(road);

// Road markings
for (let z = -900; z < 900; z += 20) {{
  const mark = new THREE.Mesh(
    new THREE.PlaneGeometry(0.3, 6),
    new THREE.MeshLambertMaterial({{ color: 0xffffff }})
  );
  mark.rotation.x = -Math.PI / 2;
  mark.position.set(0, 0.02, z);
  scene.add(mark);
}}

// Side barriers
[-5.5, 5.5].forEach(x => {{
  for (let z = -900; z < 900; z += 4) {{
    const b = new THREE.Mesh(
      new THREE.BoxGeometry(0.4, 1.2, 3.5),
      new THREE.MeshLambertMaterial({{ color: x < 0 ? 0xff0000 : 0xffffff }})
    );
    b.position.set(x, 0.6, z);
    scene.add(b);
  }}
}});

// Player car
const carGroup = new THREE.Group();
const body = new THREE.Mesh(
  new THREE.BoxGeometry(2, 0.8, 4),
  new THREE.MeshLambertMaterial({{ color: {car} }})
);
body.position.y = 0.5;
carGroup.add(body);

const roof = new THREE.Mesh(
  new THREE.BoxGeometry(1.5, 0.6, 2),
  new THREE.MeshLambertMaterial({{ color: {car} }})
);
roof.position.set(0, 1.2, 0);
carGroup.add(roof);

[[1,0.3,-1.3],[−1,0.3,-1.3],[1,0.3,1.3],[−1,0.3,1.3]].forEach(([x,y,z])=>{{
  const w = new THREE.Mesh(
    new THREE.CylinderGeometry(0.4, 0.4, 0.3, 12),
    new THREE.MeshLambertMaterial({{ color: 0x111111 }})
  );
  w.rotation.z = Math.PI / 2;
  w.position.set(x, y, z);
  carGroup.add(w);
}});

carGroup.position.set(0, 0, 0);
scene.add(carGroup);

// Obstacles
const obstacles = [];
const obsMat    = new THREE.MeshLambertMaterial({{ color: 0xffaa00 }});
for (let i = 0; i < 30; i++) {{
  const obs = new THREE.Mesh(new THREE.BoxGeometry(1.5, 1.5, 1.5), obsMat);
  obs.position.set((Math.random() - 0.5) * 8, 0.75, -50 - i * 30);
  scene.add(obs);
  obstacles.push(obs);
}}

// Scenery trees
for (let i = 0; i < 60; i++) {{
  const side = Math.random() > 0.5 ? 1 : -1;
  const trunk = new THREE.Mesh(
    new THREE.CylinderGeometry(0.2, 0.2, 2, 6),
    new THREE.MeshLambertMaterial({{ color: 0x5c3d1e }})
  );
  trunk.position.set(side * (7 + Math.random() * 5), 1, -Math.random() * 800);
  scene.add(trunk);
  const top = new THREE.Mesh(
    new THREE.ConeGeometry(1.5, 4, 6),
    new THREE.MeshLambertMaterial({{ color: 0x228833 }})
  );
  top.position.set(trunk.position.x, 4, trunk.position.z);
  scene.add(top);
}}

// State
const keys = {{}};
window.addEventListener('keydown', e => {{ keys[e.key] = true;  e.preventDefault(); }});
window.addEventListener('keyup',   e => {{ keys[e.key] = false; }});

let speed = 0, score = 0, gameOver = false;

// HUD
const hud = document.createElement('div');
hud.style.cssText = 'position:absolute;top:16px;left:50%;transform:translateX(-50%);color:#fff;font:bold 22px monospace;text-shadow:0 0 8px #000;pointer-events:none;text-align:center;';
container.style.position = 'relative';
container.appendChild(hud);

const overlay = document.createElement('div');
overlay.style.cssText = 'position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,0.85);color:#fff;padding:32px 48px;border-radius:16px;text-align:center;font:bold 28px monospace;display:none;border:2px solid #ff2200;';
overlay.innerHTML = '<div id="goTitle">GAME OVER</div><div id="goScore" style="font-size:18px;margin:12px 0;"></div><button onclick="location.reload()" style="margin-top:10px;padding:10px 24px;background:#ff2200;color:#fff;border:none;border-radius:8px;font-size:16px;cursor:pointer;">Play Again</button>';
container.appendChild(overlay);

const instructions = document.createElement('div');
instructions.style.cssText = 'position:absolute;bottom:16px;left:50%;transform:translateX(-50%);color:#fff;font:14px monospace;text-shadow:0 0 6px #000;opacity:0.8;';
instructions.textContent = '← → Arrow Keys to steer  |  Dodge obstacles!';
container.appendChild(instructions);

function tick() {{
  requestAnimationFrame(tick);
  if (!gameOver) {{
    // Acceleration
    speed = Math.min(speed + 0.002, 0.6);
    score += speed;

    // Steering
    if ((keys['ArrowLeft']  || keys['a']) && carGroup.position.x > -3.8) carGroup.position.x -= 0.12;
    if ((keys['ArrowRight'] || keys['d']) && carGroup.position.x <  3.8) carGroup.position.x += 0.12;

    // Move world forward
    obstacles.forEach(obs => {{
      obs.position.z += speed * 60 * 0.016;
      if (obs.position.z > 10) obs.position.z -= 900;

      // Collision
      if (Math.abs(obs.position.z - carGroup.position.z) < 2.5 &&
          Math.abs(obs.position.x - carGroup.position.x) < 1.8) {{
        gameOver = true;
        overlay.style.display = 'block';
        document.getElementById('goScore').textContent = 'Score: ' + Math.floor(score);
      }}
    }});

    // Camera follow
    camera.position.set(carGroup.position.x * 0.3, 5 + speed * 3, carGroup.position.z - 12);
    camera.lookAt(carGroup.position.x, 1, carGroup.position.z + 20);

    hud.innerHTML = '🏁 Score: ' + Math.floor(score) + '&nbsp;&nbsp;&nbsp;Speed: ' + Math.floor(speed * 200) + ' km/h';
  }}
  renderer.render(scene, camera);
}}
tick();

window.addEventListener('resize', () => {{
  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
}});
"""


def _fps_game(cfg: dict) -> str:
    sky   = cfg.get("sky",   "0x87ceeb")
    floor = cfg.get("floor", "0x4a7c3f")
    title = cfg.get("title", "FPS Shooter")
    return f"""
// ── {title} ── Three.js FPS Shooter ─────────────────────────────────────────
const scene    = new THREE.Scene();
scene.background = new THREE.Color({sky});
scene.fog        = new THREE.FogExp2({sky}, 0.04);

const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 200);
camera.position.set(0, 1.7, 0);

const renderer = new THREE.WebGLRenderer({{ antialias: true }});
renderer.shadowMap.enabled = true;
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(container.clientWidth, container.clientHeight);
container.style.cursor = 'crosshair';
container.appendChild(renderer.domElement);

scene.add(new THREE.AmbientLight(0xffffff, 0.5));
const sun = new THREE.DirectionalLight(0xffffff, 1.0);
sun.position.set(50, 80, 30);
sun.castShadow = true;
scene.add(sun);

// Floor
const flr = new THREE.Mesh(
  new THREE.PlaneGeometry(100, 100),
  new THREE.MeshLambertMaterial({{ color: {floor} }})
);
flr.rotation.x = -Math.PI / 2;
flr.receiveShadow = true;
scene.add(flr);

// Walls / cover
const wallMat = new THREE.MeshLambertMaterial({{ color: 0x8b6914 }});
[[0,1.5,-20,20,3,1],[0,1.5,20,20,3,1],[−20,1.5,0,1,3,20],[20,1.5,0,1,3,20]].forEach(([x,y,z,w,h,d])=>{{
  const wall = new THREE.Mesh(new THREE.BoxGeometry(w,h,d), wallMat);
  wall.position.set(x,y,z); wall.castShadow=true; wall.receiveShadow=true;
  scene.add(wall);
}});

// Crates for cover
for (let i = 0; i < 20; i++) {{
  const c = new THREE.Mesh(
    new THREE.BoxGeometry(1.5,1.5,1.5),
    new THREE.MeshLambertMaterial({{ color: 0x8b6914 }})
  );
  c.position.set((Math.random()-0.5)*35, 0.75, (Math.random()-0.5)*35);
  c.castShadow = true;
  scene.add(c);
}}

// Enemies
const enemies = [];
const enemyMat = new THREE.MeshLambertMaterial({{ color: 0xff3300 }});
for (let i = 0; i < 10; i++) {{
  const g = new THREE.Group();
  const body = new THREE.Mesh(new THREE.BoxGeometry(0.8,1.4,0.5), enemyMat);
  body.position.y = 0.7;
  g.add(body);
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.35,8,8), enemyMat);
  head.position.y = 1.7;
  g.add(head);
  g.position.set((Math.random()-0.5)*30, 0, (Math.random()-0.5)*30);
  g.userData = {{ hp:3, speed: 0.02 + Math.random()*0.03, alive:true }};
  scene.add(g);
  enemies.push(g);
}}

// Bullets
const bullets = [];
const bulletMat = new THREE.MeshBasicMaterial({{ color: 0xffff00 }});

// Crosshair overlay
container.style.position = 'relative';
const crosshair = document.createElement('div');
crosshair.style.cssText = 'position:absolute;top:50%;left:50%;width:20px;height:20px;transform:translate(-50%,-50%);pointer-events:none;';
crosshair.innerHTML = '<svg width="20" height="20"><line x1="10" y1="0" x2="10" y2="20" stroke="white" stroke-width="2"/><line x1="0" y1="10" x2="20" y2="10" stroke="white" stroke-width="2"/></svg>';
container.appendChild(crosshair);

const hud = document.createElement('div');
hud.style.cssText = 'position:absolute;top:12px;left:50%;transform:translateX(-50%);color:#fff;font:bold 20px monospace;text-shadow:0 0 6px #000;pointer-events:none;';
container.appendChild(hud);

const instr = document.createElement('div');
instr.style.cssText = 'position:absolute;bottom:12px;left:50%;transform:translateX(-50%);color:#fff;font:13px monospace;opacity:0.8;pointer-events:none;';
instr.textContent = 'WASD: Move  |  Mouse: Aim  |  Click: Shoot';
container.appendChild(instr);

// Pointer lock
let yaw=0, pitch=0;
renderer.domElement.addEventListener('click', () => renderer.domElement.requestPointerLock());
document.addEventListener('pointerlockchange', () => {{}});
document.addEventListener('mousemove', e => {{
  if (document.pointerLockElement === renderer.domElement) {{
    yaw   -= e.movementX * 0.002;
    pitch -= e.movementY * 0.002;
    pitch  = Math.max(-1.2, Math.min(1.2, pitch));
  }}
}});

const keys={{}};
window.addEventListener('keydown', e=>{{ keys[e.key]=true; e.preventDefault(); }});
window.addEventListener('keyup',   e=>{{ keys[e.key]=false; }});

let kills=0, hp=100, gameOver=false;
const ammoEl = document.createElement('div');
ammoEl.style.cssText='position:absolute;bottom:50px;right:24px;color:#fff;font:bold 22px monospace;text-shadow:0 0 6px #000;';
container.appendChild(ammoEl);

document.addEventListener('click', () => {{
  if (!gameOver && document.pointerLockElement === renderer.domElement) shootBullet();
}});

function shootBullet() {{
  const dir = new THREE.Vector3(0,0,-1).applyQuaternion(camera.quaternion);
  const b = new THREE.Mesh(new THREE.SphereGeometry(0.06,6,6), bulletMat);
  b.position.copy(camera.position).add(dir.clone().multiplyScalar(0.5));
  b.userData = {{ vel: dir.multiplyScalar(0.8), life: 120 }};
  scene.add(b); bullets.push(b);
}}

const clock = new THREE.Clock();
function tick() {{
  requestAnimationFrame(tick);
  const dt = clock.getDelta();
  if (!gameOver) {{
    // Movement
    const fwd  = new THREE.Vector3(-Math.sin(yaw), 0, -Math.cos(yaw));
    const right = new THREE.Vector3(Math.cos(yaw), 0, -Math.sin(yaw));
    const spd   = 0.12;
    if (keys['w']||keys['ArrowUp'])    camera.position.addScaledVector(fwd,  spd);
    if (keys['s']||keys['ArrowDown'])  camera.position.addScaledVector(fwd, -spd);
    if (keys['a']||keys['ArrowLeft'])  camera.position.addScaledVector(right,-spd);
    if (keys['d']||keys['ArrowRight']) camera.position.addScaledVector(right, spd);
    camera.position.clamp(new THREE.Vector3(-19,1.7,-19), new THREE.Vector3(19,1.7,19));
    camera.rotation.order = 'YXZ';
    camera.rotation.y = yaw; camera.rotation.x = pitch;

    // Bullets
    for (let i=bullets.length-1; i>=0; i--) {{
      const b = bullets[i];
      b.position.add(b.userData.vel);
      b.userData.life--;
      if (b.userData.life <= 0) {{ scene.remove(b); bullets.splice(i,1); continue; }}
      for (const en of enemies) {{
        if (!en.userData.alive) continue;
        if (b.position.distanceTo(en.position) < 1.2) {{
          en.userData.hp--;
          scene.remove(b); bullets.splice(i,1);
          if (en.userData.hp<=0) {{
            en.userData.alive=false;
            scene.remove(en); kills++;
          }}
          break;
        }}
      }}
    }}

    // Enemy AI
    enemies.forEach(en => {{
      if (!en.userData.alive) return;
      const diff = new THREE.Vector3().subVectors(camera.position, en.position);
      diff.y=0; diff.normalize();
      en.position.addScaledVector(diff, en.userData.speed);
      en.lookAt(camera.position);
      if (en.position.distanceTo(camera.position) < 1.5) {{
        hp = Math.max(0, hp - 0.3);
        if (hp<=0) {{ gameOver=true; showGameOver(); }}
      }}
    }});

    hud.textContent = '💀 Kills: '+kills+'   ❤️ HP: '+Math.floor(hp);
    if (enemies.filter(e=>e.userData.alive).length===0) {{
      gameOver=true; showWin();
    }}
  }}
  renderer.render(scene, camera);
}}

function showGameOver() {{
  const ov=document.createElement('div');
  ov.style.cssText='position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,0.85);color:#f00;padding:32px 48px;border-radius:16px;text-align:center;font:bold 32px monospace;border:2px solid #f00;';
  ov.innerHTML='GAME OVER<br><span style="font-size:18px">Kills: '+kills+'</span><br><button onclick="location.reload()" style="margin-top:14px;padding:10px 24px;background:#f00;color:#fff;border:none;border-radius:8px;font-size:16px;cursor:pointer;">Retry</button>';
  container.appendChild(ov);
}}
function showWin() {{
  const ov=document.createElement('div');
  ov.style.cssText='position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,0.85);color:#0f0;padding:32px 48px;border-radius:16px;text-align:center;font:bold 32px monospace;border:2px solid #0f0;';
  ov.innerHTML='YOU WIN! 🎉<br><span style="font-size:18px">All enemies defeated!</span><br><button onclick="location.reload()" style="margin-top:14px;padding:10px 24px;background:#0a0;color:#fff;border:none;border-radius:8px;font-size:16px;cursor:pointer;">Play Again</button>';
  container.appendChild(ov);
}}
tick();
window.addEventListener('resize',()=>{{ camera.aspect=container.clientWidth/container.clientHeight; camera.updateProjectionMatrix(); renderer.setSize(container.clientWidth,container.clientHeight); }});
"""


def _platformer_game(cfg: dict) -> str:
    sky   = cfg.get("sky",   "0x87ceeb")
    floor = cfg.get("floor", "0x22aa55")
    hero  = cfg.get("hero",  "0xff6600")
    title = cfg.get("title", "3D Platformer")
    return f"""
// ── {title} ── Three.js 3D Platformer ───────────────────────────────────────
const scene    = new THREE.Scene();
scene.background = new THREE.Color({sky});
scene.fog        = new THREE.Fog({sky}, 40, 100);

const camera = new THREE.PerspectiveCamera(65, container.clientWidth/container.clientHeight, 0.1, 200);
const renderer = new THREE.WebGLRenderer({{ antialias:true }});
renderer.shadowMap.enabled = true;
renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
renderer.setSize(container.clientWidth, container.clientHeight);
container.appendChild(renderer.domElement);

scene.add(new THREE.AmbientLight(0xffffff, 0.6));
const sun = new THREE.DirectionalLight(0xffffff, 1.2);
sun.position.set(30, 50, 20); sun.castShadow=true;
scene.add(sun);

// Platforms
const platforms = [];
const platMat = new THREE.MeshLambertMaterial({{ color: {floor} }});
function makePlatform(x,y,z,w,d) {{
  const p = new THREE.Mesh(new THREE.BoxGeometry(w,0.5,d), platMat);
  p.position.set(x,y,z); p.receiveShadow=true; p.castShadow=true;
  scene.add(p); platforms.push(p);
}}
// Ground + ascending platforms
makePlatform(0,-1,0,20,20);
makePlatform(12,1,0,6,4);
makePlatform(20,3,0,5,4);
makePlatform(28,6,0,6,4);
makePlatform(36,9,2,5,5);
makePlatform(36,12,-6,6,4);
makePlatform(28,15,-10,5,4);
makePlatform(20,18,-10,6,4);
makePlatform(12,21,-10,5,4);
makePlatform(4,24,-10,6,4);
// Moving platform
const movPlat = new THREE.Mesh(new THREE.BoxGeometry(5,0.5,4), new THREE.MeshLambertMaterial({{color:0xffaa00}}));
movPlat.position.set(4,24,-2); scene.add(movPlat); platforms.push(movPlat);

// Coins
const coins=[], coinMat=new THREE.MeshLambertMaterial({{color:0xffd700}});
[[12,2,0],[20,4,0],[28,7,0],[36,10,2],[36,13,-6],[28,16,-10],[20,19,-10],[12,22,-10],[4,25,-10]].forEach(([x,y,z])=>{{
  const c=new THREE.Mesh(new THREE.CylinderGeometry(0.4,0.4,0.15,16), coinMat);
  c.position.set(x,y+0.5,z); c.userData.collected=false;
  scene.add(c); coins.push(c);
}});

// Goal flag
const flagPole = new THREE.Mesh(new THREE.CylinderGeometry(0.1,0.1,3,8), new THREE.MeshLambertMaterial({{color:0xffffff}}));
flagPole.position.set(4,26.5,-10); scene.add(flagPole);
const flag = new THREE.Mesh(new THREE.BoxGeometry(1.2,0.8,0.1), new THREE.MeshLambertMaterial({{color:0xff0000}}));
flag.position.set(4.6,28,-10); scene.add(flag);

// Hero
const hero = new THREE.Group();
const heroBody = new THREE.Mesh(new THREE.BoxGeometry(0.8,1,0.6), new THREE.MeshLambertMaterial({{color:{hero}}}));
heroBody.position.y=0.5; hero.add(heroBody);
const heroHead = new THREE.Mesh(new THREE.SphereGeometry(0.35,8,8), new THREE.MeshLambertMaterial({{color:0xffddaa}}));
heroHead.position.y=1.3; hero.add(heroHead);
hero.position.set(0,0.5,0); hero.castShadow=true;
scene.add(hero);

container.style.position='relative';
const hud=document.createElement('div');
hud.style.cssText='position:absolute;top:12px;left:50%;transform:translateX(-50%);color:#fff;font:bold 20px monospace;text-shadow:0 2px 6px #000;pointer-events:none;';
container.appendChild(hud);
const instr=document.createElement('div');
instr.style.cssText='position:absolute;bottom:12px;left:50%;transform:translateX(-50%);color:#fff;font:13px monospace;opacity:0.85;pointer-events:none;';
instr.textContent='WASD: Move  |  SPACE: Jump  |  Collect ALL coins to win!';
container.appendChild(instr);

const keys={{}};
window.addEventListener('keydown',e=>{{keys[e.key]=true;e.preventDefault();}});
window.addEventListener('keyup',e=>{{keys[e.key]=false;}});

let vy=0, onGround=false, coinsGot=0, gameOver=false;
const clock=new THREE.Clock();

function tick(){{
  requestAnimationFrame(tick);
  const dt=Math.min(clock.getDelta(), 0.05);
  if(!gameOver){{
    // Movement
    const spd=7;
    if(keys['a']||keys['ArrowLeft'])  hero.position.x-=spd*dt;
    if(keys['d']||keys['ArrowRight']) hero.position.x+=spd*dt;
    if(keys['w']||keys['ArrowUp'])    hero.position.z-=spd*dt;
    if(keys['s']||keys['ArrowDown'])  hero.position.z+=spd*dt;
    if((keys[' ']||keys['ArrowUp'])&&onGround){{vy=10;onGround=false;}}

    // Gravity
    vy-=25*dt;
    hero.position.y+=vy*dt;

    // Platform collision
    onGround=false;
    platforms.forEach(p=>{{
      const pb=new THREE.Box3().setFromObject(p);
      const hb=new THREE.Box3().setFromObject(hero);
      if(hb.intersectsBox(pb)&&vy<=0&&hero.position.y>p.position.y){{
        hero.position.y=p.position.y+p.geometry.parameters.height/2+0.5;
        vy=0; onGround=true;
      }}
    }});

    // Moving platform
    movPlat.position.x=4+Math.sin(Date.now()*0.001)*5;
    movPlat.userData.prevX=movPlat.position.x;

    if(hero.position.y<-15){{hero.position.set(0,0.5,0);vy=0;}}

    // Coins
    coins.forEach(c=>{{
      if(!c.userData.collected&&hero.position.distanceTo(c.position)<1){{
        c.userData.collected=true; scene.remove(c); coinsGot++;
      }}
      c.rotation.y+=dt*2;
    }});

    // Win
    if(coinsGot>=coins.length){{
      gameOver=true;
      const ov=document.createElement('div');
      ov.style.cssText='position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,0.88);color:#ffd700;padding:32px 48px;border-radius:16px;text-align:center;font:bold 30px monospace;border:2px solid #ffd700;';
      ov.innerHTML='YOU WIN! 🏆<br><span style="font-size:16px">All coins collected!</span><br><button onclick="location.reload()" style="margin-top:12px;padding:10px 24px;background:#ffd700;color:#000;border:none;border-radius:8px;font-size:16px;cursor:pointer;">Play Again</button>';
      container.appendChild(ov);
    }}

    // Camera follow from behind+above
    const ideal=new THREE.Vector3(hero.position.x,hero.position.y+6,hero.position.z+12);
    camera.position.lerp(ideal,0.08);
    camera.lookAt(hero.position);

    hud.textContent='🪙 Coins: '+coinsGot+' / '+coins.length;
  }}
  renderer.render(scene,camera);
}}
tick();
window.addEventListener('resize',()=>{{camera.aspect=container.clientWidth/container.clientHeight;camera.updateProjectionMatrix();renderer.setSize(container.clientWidth,container.clientHeight);}});
"""


def _space_shooter(cfg: dict) -> str:
    title = cfg.get("title", "Space Shooter")
    return f"""
// ── {title} ── Three.js 3D Space Shooter ───────────────────────────────────
const scene    = new THREE.Scene();
scene.background = new THREE.Color(0x000010);

const camera = new THREE.PerspectiveCamera(60, container.clientWidth/container.clientHeight, 0.1, 500);
camera.position.set(0, 5, 15);
camera.lookAt(0,0,0);

const renderer = new THREE.WebGLRenderer({{ antialias:true }});
renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
renderer.setSize(container.clientWidth,container.clientHeight);
container.appendChild(renderer.domElement);

scene.add(new THREE.AmbientLight(0x222266,1));
const starIsh=new THREE.DirectionalLight(0x8888ff,0.8);
starIsh.position.set(0,100,0); scene.add(starIsh);

// Stars
const starGeo=new THREE.BufferGeometry();
const starPos=new Float32Array(3000);
for(let i=0;i<3000;i++)starPos[i]=(Math.random()-0.5)*400;
starGeo.setAttribute('position',new THREE.BufferAttribute(starPos,3));
scene.add(new THREE.Points(starGeo,new THREE.PointsMaterial({{color:0xffffff,size:0.3}})));

// Player ship
const ship=new THREE.Group();
const hull=new THREE.Mesh(new THREE.ConeGeometry(0.6,3,8),new THREE.MeshLambertMaterial({{color:0x00aaff}}));
hull.rotation.x=Math.PI/2; ship.add(hull);
[[0.8,0],[−0.8,0]].forEach(([x])=>{{
  const wing=new THREE.Mesh(new THREE.BoxGeometry(2,0.1,1.5),new THREE.MeshLambertMaterial({{color:0x0066cc}}));
  wing.position.set(x,0,0.3); ship.add(wing);
}});
const engineGlow=new THREE.Mesh(new THREE.CylinderGeometry(0.2,0.2,0.5,8),new THREE.MeshLambertMaterial({{color:0xff6600,emissive:0xff4400}}));
engineGlow.rotation.x=Math.PI/2; engineGlow.position.z=1.8; ship.add(engineGlow);
ship.position.set(0,0,8); scene.add(ship);

// Enemies
const enemies=[];
function spawnEnemy(){{
  const g=new THREE.Group();
  const b=new THREE.Mesh(new THREE.SphereGeometry(0.8,8,8),new THREE.MeshLambertMaterial({{color:0xff2200}}));
  g.add(b);
  const sp=new THREE.Mesh(new THREE.RingGeometry(1,1.5,8),new THREE.MeshLambertMaterial({{color:0xff6600,side:THREE.DoubleSide}}));
  sp.rotation.x=Math.PI/2; g.add(sp);
  g.position.set((Math.random()-0.5)*20,-0,-60-Math.random()*20);
  g.userData={{hp:2,speed:0.06+Math.random()*0.05}};
  scene.add(g); enemies.push(g);
}}
for(let i=0;i<8;i++) spawnEnemy();

const bullets=[],eBullets=[];
const bMat=new THREE.MeshBasicMaterial({{color:0x00ffff}});
const eBMat=new THREE.MeshBasicMaterial({{color:0xff4400}});

container.style.position='relative';
const hud=document.createElement('div');
hud.style.cssText='position:absolute;top:12px;left:50%;transform:translateX(-50%);color:#0ff;font:bold 20px monospace;text-shadow:0 0 8px #0aa;pointer-events:none;';
container.appendChild(hud);
const instr=document.createElement('div');
instr.style.cssText='position:absolute;bottom:12px;left:50%;transform:translateX(-50%);color:#aaf;font:13px monospace;opacity:0.85;pointer-events:none;';
instr.textContent='Arrow Keys / WASD: Move  |  SPACE: Shoot';
container.appendChild(instr);

const keys={{}};
window.addEventListener('keydown',e=>{{keys[e.key]=true;e.preventDefault();}});
window.addEventListener('keyup',e=>{{keys[e.key]=false;}});

let score=0,hp=100,gameOver=false,fireTimer=0,enemySpawnTimer=0;
const clock=new THREE.Clock();

function tick(){{
  requestAnimationFrame(tick);
  const dt=Math.min(clock.getDelta(),0.05);
  if(!gameOver){{
    // Ship movement
    if((keys['ArrowLeft']||keys['a'])  &&ship.position.x>-9) ship.position.x-=10*dt;
    if((keys['ArrowRight']||keys['d']) &&ship.position.x<9)  ship.position.x+=10*dt;
    if((keys['ArrowUp']||keys['w'])    &&ship.position.z>2)  ship.position.z-=10*dt;
    if((keys['ArrowDown']||keys['s'])  &&ship.position.z<12) ship.position.z+=10*dt;
    ship.rotation.z+=(−ship.rotation.z)*0.1;
    if(keys['ArrowLeft']||keys['a']) ship.rotation.z=Math.min(ship.rotation.z+0.05,0.4);
    if(keys['ArrowRight']||keys['d']) ship.rotation.z=Math.max(ship.rotation.z-0.05,-0.4);

    // Shooting
    fireTimer-=dt;
    if((keys[' '])&&fireTimer<0){{
      fireTimer=0.15;
      [[-0.6,0],[0.6,0]].forEach(([ox])=>{{
        const b=new THREE.Mesh(new THREE.CylinderGeometry(0.08,0.08,0.8,6),bMat);
        b.rotation.x=Math.PI/2;
        b.position.copy(ship.position).add(new THREE.Vector3(ox,0,-1.5));
        b.userData={{vel:new THREE.Vector3(0,0,-0.7)}};
        scene.add(b); bullets.push(b);
      }});
    }}

    // Player bullets
    for(let i=bullets.length-1;i>=0;i--){{
      const b=bullets[i];
      b.position.add(b.userData.vel);
      if(b.position.z<-80){{scene.remove(b);bullets.splice(i,1);continue;}}
      for(let j=enemies.length-1;j>=0;j--){{
        const en=enemies[j];
        if(b.position.distanceTo(en.position)<1.4){{
          en.userData.hp--;
          scene.remove(b);bullets.splice(i,1);
          if(en.userData.hp<=0){{score+=100;scene.remove(en);enemies.splice(j,1);spawnEnemy();}}
          break;
        }}
      }}
    }}

    // Enemy movement + shoot
    enemies.forEach((en,i)=>{{
      en.position.z+=en.userData.speed;
      en.rotation.y+=dt;
      if(en.position.z>15){{en.position.z=-60;en.position.x=(Math.random()-0.5)*20;}}
      if(Math.random()<0.005){{
        const eb=new THREE.Mesh(new THREE.SphereGeometry(0.1,4,4),eBMat);
        eb.position.copy(en.position);
        const dir=new THREE.Vector3().subVectors(ship.position,en.position).normalize().multiplyScalar(0.3);
        eb.userData={{vel:dir}};
        scene.add(eb); eBullets.push(eb);
      }}
    }});

    // Enemy bullets
    for(let i=eBullets.length-1;i>=0;i--){{
      const eb=eBullets[i];
      eb.position.add(eb.userData.vel);
      if(eb.position.z>20){{scene.remove(eb);eBullets.splice(i,1);continue;}}
      if(eb.position.distanceTo(ship.position)<1){{
        hp=Math.max(0,hp-10);
        scene.remove(eb);eBullets.splice(i,1);
        if(hp<=0){{gameOver=true;showEnd('GAME OVER','#f00');}}
      }}
    }}

    // Enemy spawn wave
    enemySpawnTimer+=dt;
    if(enemySpawnTimer>15){{enemySpawnTimer=0;spawnEnemy();spawnEnemy();}}

    camera.position.set(ship.position.x*0.1,ship.position.y+5,15);
    camera.lookAt(ship.position.x*0.1,0,-5);
    hud.textContent='⭐ Score: '+score+'   ❤️ HP: '+Math.floor(hp)+'%';
  }}
  renderer.render(scene,camera);
}}

function showEnd(msg,color){{
  const ov=document.createElement('div');
  ov.style.cssText=`position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,16,0.92);color:${{color}};padding:32px 48px;border-radius:16px;text-align:center;font:bold 32px monospace;border:2px solid ${{color}};`;
  ov.innerHTML=msg+'<br><span style="font-size:18px">Score: '+score+'</span><br><button onclick="location.reload()" style="margin-top:12px;padding:10px 24px;background:'+color+';color:#fff;border:none;border-radius:8px;font-size:16px;cursor:pointer;">Play Again</button>';
  container.appendChild(ov);
}}
tick();
window.addEventListener('resize',()=>{{camera.aspect=container.clientWidth/container.clientHeight;camera.updateProjectionMatrix();renderer.setSize(container.clientWidth,container.clientHeight);}});
"""


def _soccer_game(cfg: dict) -> str:
    title = cfg.get("title", "Soccer / Football 3D")
    return f"""
// ── {title} ── Three.js 3D Soccer ────────────────────────────────────────────
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 120);

const camera = new THREE.PerspectiveCamera(65, container.clientWidth/container.clientHeight, 0.1, 200);
camera.position.set(0, 12, 22);
camera.lookAt(0, 0, 0);

const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.shadowMap.enabled = true;
renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
renderer.setSize(container.clientWidth, container.clientHeight);
container.appendChild(renderer.domElement);

scene.add(new THREE.AmbientLight(0xffffff, 0.7));
const sun = new THREE.DirectionalLight(0xffffff, 1.0);
sun.position.set(20,50,20); sun.castShadow=true; scene.add(sun);

// Field
const field = new THREE.Mesh(new THREE.PlaneGeometry(40,60), new THREE.MeshLambertMaterial({{color:0x2d8a2d}}));
field.rotation.x=-Math.PI/2; field.receiveShadow=true; scene.add(field);

// Field lines
[[0xffffff,40,0.1,0.1,0,0.05,0],[0xffffff,0.1,0.1,60,0,-0.05,0,0,-0.05,0]].forEach(()=>{{}});
[
  [0,0.05,0,40,0.1,0.1],
  [−19.5,0.05,0,0.1,0.1,60],
  [19.5,0.05,0,0.1,0.1,60],
].forEach(([x,y,z,w,h,d])=>{{
  const l=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),new THREE.MeshLambertMaterial({{color:0xffffff}}));
  l.position.set(x,y,z); scene.add(l);
}});

// Goals
function makeGoal(z){{
  const mat=new THREE.MeshLambertMaterial({{color:0xffffff}});
  [[0,1.5,z,0.1,3,0.1],[−3,1.5,z,0.1,3,0.1],[3,1.5,z,0.1,3,0.1],[0,3,z,6.1,0.1,0.1]].forEach(([x,y,gz,w,h,d])=>{{
    const p=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mat);
    p.position.set(x,y,gz); scene.add(p);
  }});
}}
makeGoal(-30); makeGoal(30);

// Ball
const ball=new THREE.Mesh(new THREE.SphereGeometry(0.5,16,16),new THREE.MeshLambertMaterial({{color:0xffffff}}));
ball.position.set(0,0.5,0); ball.castShadow=true; scene.add(ball);
let bVel=new THREE.Vector3(0,0,0);

// Player
const player=new THREE.Group();
const pBody=new THREE.Mesh(new THREE.CylinderGeometry(0.4,0.4,1.4,8),new THREE.MeshLambertMaterial({{color:0x1155ff}}));
pBody.position.y=0.7; player.add(pBody);
const pHead=new THREE.Mesh(new THREE.SphereGeometry(0.35,8,8),new THREE.MeshLambertMaterial({{color:0xffddaa}}));
pHead.position.y=1.7; player.add(pHead);
player.position.set(0,0,10); scene.add(player);

// AI opponents
const aiPlayers=[];
[[-4,0,-8],[4,0,-8],[0,0,-15]].forEach(([x,y,z])=>{{
  const ai=new THREE.Group();
  const aib=new THREE.Mesh(new THREE.CylinderGeometry(0.4,0.4,1.4,8),new THREE.MeshLambertMaterial({{color:0xff2200}}));
  aib.position.y=0.7; ai.add(aib);
  const aih=new THREE.Mesh(new THREE.SphereGeometry(0.35,8,8),new THREE.MeshLambertMaterial({{color:0xffddaa}}));
  aih.position.y=1.7; ai.add(aih);
  ai.position.set(x,0,z); scene.add(ai); aiPlayers.push(ai);
}});

container.style.position='relative';
const scoreDiv=document.createElement('div');
scoreDiv.style.cssText='position:absolute;top:12px;left:50%;transform:translateX(-50%);color:#fff;font:bold 24px monospace;text-shadow:0 2px 8px #000;pointer-events:none;';
container.appendChild(scoreDiv);
const instr=document.createElement('div');
instr.style.cssText='position:absolute;bottom:12px;left:50%;transform:translateX(-50%);color:#fff;font:13px monospace;opacity:0.85;pointer-events:none;';
instr.textContent='WASD: Move  |  SPACE: Kick ball  |  Score in the top goal!';
container.appendChild(instr);

const keys={{}};
window.addEventListener('keydown',e=>{{keys[e.key]=true;e.preventDefault();}});
window.addEventListener('keyup',e=>{{keys[e.key]=false;}});

let score=0, aiScore=0, gameOver=false;
const clock=new THREE.Clock();

function tick(){{
  requestAnimationFrame(tick);
  const dt=Math.min(clock.getDelta(),0.05);
  if(!gameOver){{
    const spd=8;
    if(keys['a']||keys['ArrowLeft'])  {{player.position.x-=spd*dt; player.position.x=Math.max(-19,player.position.x);}}
    if(keys['d']||keys['ArrowRight']) {{player.position.x+=spd*dt; player.position.x=Math.min(19,player.position.x);}}
    if(keys['w']||keys['ArrowUp'])    {{player.position.z-=spd*dt; player.position.z=Math.max(-29,player.position.z);}}
    if(keys['s']||keys['ArrowDown'])  {{player.position.z+=spd*dt; player.position.z=Math.min(29,player.position.z);}}

    // Kick ball
    if(keys[' ']){{
      const d=new THREE.Vector3().subVectors(ball.position,player.position);
      if(d.length()<2){{
        d.normalize();
        bVel.set(d.x*0.4,0.1,d.z*0.4);
      }}
    }}

    // Ball physics
    bVel.multiplyScalar(0.97);
    ball.position.add(bVel);
    ball.position.x=Math.max(-19.5,Math.min(19.5,ball.position.x));
    ball.position.z=Math.max(-29.5,Math.min(29.5,ball.position.z));
    if(ball.position.y<0.5){{ball.position.y=0.5;bVel.y=0;}}

    // Score detection
    if(ball.position.z<-29&&Math.abs(ball.position.x)<3){{
      score++;
      ball.position.set(0,0.5,0); bVel.set(0,0,0);
      if(score>=3){{gameOver=true;showEnd('YOU WIN! ⚽','#0f0',score,aiScore);}}
    }}
    if(ball.position.z>29&&Math.abs(ball.position.x)<3){{
      aiScore++;
      ball.position.set(0,0.5,0); bVel.set(0,0,0);
      if(aiScore>=3){{gameOver=true;showEnd('GAME OVER','#f00',score,aiScore);}}
    }}

    // AI logic - move toward ball and kick
    aiPlayers.forEach((ai,i)=>{{
      const target = i===2 ? ball.position : new THREE.Vector3(ball.position.x+(i==0?−2:2), 0, ball.position.z+3);
      const diff=new THREE.Vector3().subVectors(target,ai.position);
      diff.y=0; if(diff.length()>0.3) diff.normalize().multiplyScalar(4*dt);
      ai.position.add(diff);
      ai.position.x=Math.max(-19,Math.min(19,ai.position.x));
      ai.position.z=Math.max(-29,Math.min(10,ai.position.z));
      if(ai.position.distanceTo(ball.position)<1.5){{
        const kick=new THREE.Vector3().subVectors(ball.position,ai.position);
        kick.normalize().multiplyScalar(0.25); kick.y=0.05;
        bVel.add(kick);
      }}
    }});

    // Camera
    camera.position.set(player.position.x*0.15, 12, player.position.z+22);
    camera.lookAt(ball.position.x,0,ball.position.z);

    scoreDiv.textContent='⚽ YOU ' + score + ' : ' + aiScore + ' AI';
  }}
  renderer.render(scene,camera);
}}

function showEnd(msg,color,s,ai){{
  const ov=document.createElement('div');
  ov.style.cssText=`position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,0.88);color:${{color}};padding:32px 48px;border-radius:16px;text-align:center;font:bold 30px monospace;border:2px solid ${{color}};`;
  ov.innerHTML=msg+`<br><span style="font-size:18px">Final: You ${{s}} - ${{ai}} AI</span><br><button onclick="location.reload()" style="margin-top:12px;padding:10px 24px;background:${{color}};color:#000;border:none;border-radius:8px;font-size:16px;cursor:pointer;">Play Again</button>`;
  container.appendChild(ov);
}}
tick();
window.addEventListener('resize',()=>{{camera.aspect=container.clientWidth/container.clientHeight;camera.updateProjectionMatrix();renderer.setSize(container.clientWidth,container.clientHeight);}});
"""


# ─────────────────────────────────────────────────────────────────────────────
# Prompt → config parser
# ─────────────────────────────────────────────────────────────────────────────

def _parse_prompt(prompt: str) -> dict:
    """Pull colour / theme hints from the prompt."""
    p = prompt.lower()
    cfg = {"title": prompt.title()[:50]}

    color_map = {
        "red":    "0xff2200", "blue":  "0x0066ff", "green": "0x00aa33",
        "yellow": "0xffdd00", "purple":"0x8800cc", "orange":"0xff6600",
        "white":  "0xffffff", "black": "0x111111", "gold":  "0xffd700",
        "pink":   "0xff66aa", "cyan":  "0x00ccff",
    }
    sky_map = {
        "night":  "0x020210", "space":  "0x000010", "sunset": "0x331122",
        "desert": "0xddaa66", "forest": "0x1a2e1a", "snow":   "0xc0d8f0",
    }
    for kw, col in sky_map.items():
        if kw in p:
            cfg["sky"] = col
    for kw, col in color_map.items():
        if kw in p:
            cfg["car"] = col; cfg["hero"] = col; break
    return cfg


# ─────────────────────────────────────────────────────────────────────────────
# Main public function
# ─────────────────────────────────────────────────────────────────────────────

def generate_game_from_prompt(prompt: str) -> dict:
    """
    Given a free-text prompt, returns:
      {
        "status" : "ok",
        "title"  : str,
        "type"   : str,
        "code"   : str,          ← Three.js JS code; run in browser
        "description": str,
        "controls"   : str,
      }
    """
    p = prompt.lower()
    cfg = _parse_prompt(prompt)

    # Pick game template
    if any(w in p for w in ["race", "racing", "car", "drive", "road", "speed"]):
        game_type = "racing"
        code = _racing_game(cfg)
        description = f"🏎️ 3D Racing game — dodge obstacles, hit top speed!"
        controls = "← → Arrow Keys to steer. Avoid orange obstacles."

    elif any(w in p for w in ["fps", "shoot", "shooter", "gun", "first person", "soldier", "war", "army"]):
        game_type = "fps"
        code = _fps_game(cfg)
        description = "🔫 First-Person Shooter — click to lock mouse, aim and shoot enemies!"
        controls = "WASD to move • Mouse to aim • Click to shoot"

    elif any(w in p for w in ["platform", "jump", "mario", "side", "run"]):
        game_type = "platformer"
        code = _platformer_game(cfg)
        description = "🏃 3D Platformer — jump across platforms, collect all coins to win!"
        controls = "WASD / Arrow Keys: Move • SPACE: Jump"

    elif any(w in p for w in ["space", "spaceship", "alien", "star", "galaxy", "asteroid"]):
        game_type = "space_shooter"
        code = _space_shooter(cfg)
        description = "🚀 3D Space Shooter — defend the galaxy, shoot alien invaders!"
        controls = "Arrow Keys / WASD: Move • SPACE: Shoot"

    elif any(w in p for w in ["soccer", "football", "ball", "goal", "sport"]):
        game_type = "soccer"
        code = _soccer_game(cfg)
        description = "⚽ 3D Soccer — score 3 goals before the AI does!"
        controls = "WASD: Move • SPACE: Kick ball"

    else:
        # Default: platformer
        game_type = "platformer"
        code = _platformer_game(cfg)
        description = f"🎮 3D Platformer game based on: '{prompt}'"
        controls = "WASD / Arrow Keys: Move • SPACE: Jump"

    return {
        "status":      "ok",
        "title":       cfg["title"],
        "type":        game_type,
        "code":        code,
        "description": description,
        "controls":    controls,
    }
