"""
AAA Game Engine - Unity HDRP + CoD Warzone Style
Generates real, playable 3D games in the browser using Three.js
PBR rendering, Environment Maps, UnrealBloom, ACES tone mapping
Procedural textures, skybox, volumetric fog, real 3D models
"""

import re

# ---------------------------------------------------------------------------
# SHARED AAA RENDERER — CoD Warzone quality with environment mapping
# ---------------------------------------------------------------------------
AAA_RENDERER_SETUP = """
// ═══════════════════════════════════════════════════════
// AAA RENDERER — Real PBR with Environment Reflections
// ═══════════════════════════════════════════════════════
const renderer = new THREE.WebGLRenderer({
    antialias: true,
    powerPreference: 'high-performance',
    stencil: false,
    depth: true
});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2.0));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.getElementById('game-container').appendChild(renderer.domElement);

// ── Environment Map (generates HDR-like reflections) ──
const pmremGen = new THREE.PMREMGenerator(renderer);
pmremGen.compileEquirectangularShader();

function createEnvScene() {
    const envScene = new THREE.Scene();
    // Sky gradient
    const skyGeo = new THREE.SphereGeometry(500, 32, 16);
    const skyColors = [];
    const pos = skyGeo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
        const y = pos.getY(i);
        const t = (y + 500) / 1000;
        const r = 0.15 + t * 0.35;
        const g = 0.25 + t * 0.45;
        const b = 0.45 + t * 0.55;
        skyColors.push(r, g, b);
    }
    skyGeo.setAttribute('color', new THREE.Float32BufferAttribute(skyColors, 3));
    const skyMat = new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.BackSide });
    envScene.add(new THREE.Mesh(skyGeo, skyMat));
    return envScene;
}
const envScene = createEnvScene();
const envMap = pmremGen.fromScene(envScene, 0.04).texture;
scene.environment = envMap;

// Post-Processing (UnrealBloom + OutputPass)
const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
const bloomPass = new UnrealBloomPass(
    new THREE.Vector2(window.innerWidth, window.innerHeight),
    0.35, 0.5, 0.9
);
composer.addPass(bloomPass);
composer.addPass(new OutputPass());

// Quality presets
window.setQuality = function(level) {
    const presets = {
        low:    { pr: 0.75, bloom: false, shadows: false },
        medium: { pr: 1.0,  bloom: true,  shadows: true  },
        high:   { pr: 1.5,  bloom: true,  shadows: true  },
        ultra:  { pr: 2.0,  bloom: true,  shadows: true  }
    };
    const p = presets[level] || presets.high;
    renderer.setPixelRatio(Math.min(p.pr, window.devicePixelRatio));
    renderer.shadowMap.enabled = p.shadows;
    bloomPass.enabled = p.bloom;
    composer.setSize(window.innerWidth, window.innerHeight);
};

window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
    composer.setSize(window.innerWidth, window.innerHeight);
});
"""

# ---------------------------------------------------------------------------
# PROCEDURAL TEXTURE GENERATOR — real textures, not flat colors
# ---------------------------------------------------------------------------
TEXTURE_GEN = """
// ═══════════════════════════════════════════════════════
// PROCEDURAL TEXTURE GENERATOR — Real surface detail
// ═══════════════════════════════════════════════════════
function makeTexture(w, h, fn) {
    const c = document.createElement('canvas');
    c.width = w; c.height = h;
    const ctx = c.getContext('2d');
    fn(ctx, w, h);
    const tex = new THREE.CanvasTexture(c);
    tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
    return tex;
}

const grassTex = makeTexture(256, 256, (ctx, w, h) => {
    ctx.fillStyle = '#2a5e1a';
    ctx.fillRect(0, 0, w, h);
    for (let i = 0; i < 8000; i++) {
        const x = Math.random() * w, y = Math.random() * h;
        const shade = 20 + Math.random() * 40;
        ctx.fillStyle = `rgb(${30+Math.random()*30},${60+shade},${15+Math.random()*20})`;
        ctx.fillRect(x, y, 1 + Math.random()*2, 2 + Math.random()*4);
    }
});
grassTex.repeat.set(20, 20);

// ── BUMP MAPS (Normal/Depth simulation) ──
const bumpTex = makeTexture(128, 128, (ctx, w, h) => {
    ctx.fillStyle = '#8080ff'; // Flat normal
    ctx.fillRect(0, 0, w, h);
    for (let i = 0; i < 1000; i++) {
        ctx.fillStyle = `rgba(0,0,0,${Math.random()*0.1})`;
        ctx.fillRect(Math.random()*w, Math.random()*h, 2, 2);
    }
});
bumpTex.repeat.set(5, 5);

const concreteTex = makeTexture(256, 256, (ctx, w, h) => {
    ctx.fillStyle = '#8a8680';
    ctx.fillRect(0, 0, w, h);
    for (let i = 0; i < 3000; i++) {
        const x = Math.random() * w, y = Math.random() * h;
        const g = 100 + Math.random() * 80;
        ctx.fillStyle = `rgba(${g},${g-5},${g-10},0.3)`;
        ctx.fillRect(x, y, 1 + Math.random()*3, 1 + Math.random()*3);
    }
    // Cracks
    ctx.strokeStyle = 'rgba(60,55,50,0.3)';
    ctx.lineWidth = 0.5;
    for (let i = 0; i < 8; i++) {
        ctx.beginPath();
        ctx.moveTo(Math.random()*w, Math.random()*h);
        ctx.lineTo(Math.random()*w, Math.random()*h);
        ctx.stroke();
    }
});
concreteTex.repeat.set(4, 4);

const dirtTex = makeTexture(256, 256, (ctx, w, h) => {
    ctx.fillStyle = '#6b5b44';
    ctx.fillRect(0, 0, w, h);
    for (let i = 0; i < 5000; i++) {
        const x = Math.random() * w, y = Math.random() * h;
        const g = 70 + Math.random() * 50;
        ctx.fillStyle = `rgba(${g+20},${g},${g-20},0.4)`;
        ctx.fillRect(x, y, 1 + Math.random()*2, 1 + Math.random()*2);
    }
});
dirtTex.repeat.set(15, 15);

const brickTex = makeTexture(256, 128, (ctx, w, h) => {
    ctx.fillStyle = '#7a4a3a';
    ctx.fillRect(0, 0, w, h);
    const bw = 32, bh = 16;
    ctx.strokeStyle = '#5a3a2a';
    ctx.lineWidth = 2;
    for (let y = 0; y < h; y += bh) {
        const offset = (Math.floor(y / bh) % 2) * (bw / 2);
        for (let x = -bw; x < w + bw; x += bw) {
            const r = 100 + Math.random() * 40;
            ctx.fillStyle = `rgb(${r+30},${r-20},${r-40})`;
            ctx.fillRect(x + offset + 1, y + 1, bw - 2, bh - 2);
        }
    }
});
brickTex.repeat.set(3, 6);

const metalTex = makeTexture(128, 128, (ctx, w, h) => {
    const grad = ctx.createLinearGradient(0, 0, w, h);
    grad.addColorStop(0, '#3a3a3a');
    grad.addColorStop(0.5, '#555555');
    grad.addColorStop(1, '#2a2a2a');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, w, h);
    for (let i = 0; i < 500; i++) {
        const g = 40 + Math.random() * 60;
        ctx.fillStyle = `rgba(${g},${g},${g+10},0.15)`;
        ctx.fillRect(Math.random()*w, Math.random()*h, w, 1);
    }
});
"""

# ---------------------------------------------------------------------------
# PBR MATERIALS with textures
# ---------------------------------------------------------------------------
PBR_MATERIALS = """
// ═══════════════════════════════════════════════════════
// PBR MATERIAL LIBRARY with Procedural Textures
// ═══════════════════════════════════════════════════════
function pbrMetal(color, roughness=0.2, metalness=0.95) {
    return new THREE.MeshStandardMaterial({
        color, roughness, metalness,
        envMapIntensity: 1.5
    });
}
function pbrGrass() {
    return new THREE.MeshStandardMaterial({
        map: grassTex, roughness: 0.95, metalness: 0.0,
        envMapIntensity: 0.2
    });
}
function pbrConcrete(color=0x999999) {
    return new THREE.MeshStandardMaterial({
        map: concreteTex, color, roughness: 0.85, metalness: 0.05,
        envMapIntensity: 0.3
    });
}
function pbrBrick() {
    return new THREE.MeshStandardMaterial({
        map: brickTex, roughness: 0.8, metalness: 0.1,
        normalMap: bumpTex, normalScale: new THREE.Vector2(0.5, 0.5),
        envMapIntensity: 0.5
    });
}
function pbrDirt() {
    return new THREE.MeshStandardMaterial({
        map: dirtTex, roughness: 1.0, metalness: 0.0,
        envMapIntensity: 0.1
    });
}
function pbrGlass() {
    return new THREE.MeshPhysicalMaterial({
        color: 0x88ccff, roughness: 0.05, metalness: 0.0,
        transmission: 0.9, thickness: 0.3,
        envMapIntensity: 2.5, transparent: true, opacity: 0.25
    });
}
function pbrSkin() {
    return new THREE.MeshStandardMaterial({
        color: 0xc68642, roughness: 0.7, metalness: 0.0,
        envMapIntensity: 0.6
    });
}
function pbrEmissive(color, emissive, intensity=2) {
    return new THREE.MeshStandardMaterial({
        color, emissive, emissiveIntensity: intensity,
        roughness: 0.2, metalness: 0.8
    });
}
"""

# ---------------------------------------------------------------------------
# LIGHTING with sky gradient
# ---------------------------------------------------------------------------
AAA_LIGHTING = """
// ═══════════════════════════════════════════════════════
// LIGHTING — Cinematic 3-point + Sky
// ═══════════════════════════════════════════════════════
// Sky gradient background
const skyCanvas = document.createElement('canvas');
skyCanvas.width = 1; skyCanvas.height = 512;
const skyCtx = skyCanvas.getContext('2d');
const skyGrad = skyCtx.createLinearGradient(0, 0, 0, 512);
skyGrad.addColorStop(0.0, '#1a2a4a');
skyGrad.addColorStop(0.3, '#4a6a8a');
skyGrad.addColorStop(0.5, '#7a9aba');
skyGrad.addColorStop(0.7, '#9ab0c8');
skyGrad.addColorStop(1.0, '#c8d8e8');
skyCtx.fillStyle = skyGrad;
skyCtx.fillRect(0, 0, 1, 512);
const skyTexture = new THREE.CanvasTexture(skyCanvas);
scene.background = skyTexture;

// Hemisphere (sky + ground bounce)
scene.add(new THREE.HemisphereLight(0x87ceeb, 0x4a3520, 0.7));

// Sun — key light with shadows
const sun = new THREE.DirectionalLight(0xffeedd, 2.5);
sun.position.set(60, 100, 40);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 0.5;
sun.shadow.camera.far = 250;
sun.shadow.camera.left = -80;
sun.shadow.camera.right = 80;
sun.shadow.camera.top = 80;
sun.shadow.camera.bottom = -80;
sun.shadow.bias = -0.0005;
sun.shadow.normalBias = 0.02;
scene.add(sun);

// Fill light
const fill = new THREE.DirectionalLight(0x6688bb, 0.5);
fill.position.set(-40, 30, -20);
scene.add(fill);

// Rim light
const rim = new THREE.DirectionalLight(0xffffff, 0.25);
rim.position.set(0, -5, -60);
scene.add(rim);
"""

# ---------------------------------------------------------------------------
# FPS COUNTER
# ---------------------------------------------------------------------------
FPS_COUNTER = """
let fpsClock = 0, fpsFrames = 0;
const fpsEl = document.getElementById('fps-counter');
function updateFPS(delta) {
    fpsClock += delta; fpsFrames++;
    if (fpsClock >= 0.5) {
        const fps = Math.round(fpsFrames / fpsClock);
        if (fpsEl) fpsEl.textContent = fps + ' FPS';
        if (fpsEl) fpsEl.style.color = fps >= 50 ? '#00ff88' : fps >= 30 ? '#ffaa00' : '#ff4444';
        fpsClock = 0; fpsFrames = 0;
    }
}
"""

# ---------------------------------------------------------------------------
# WARZONE FPS TEMPLATE — full 3D with textured environment
# ---------------------------------------------------------------------------
def _warzone_fps_template():
    return """
// ═══════════════════════════════════════════════
// WARZONE FPS — Textured 3D World
// ═══════════════════════════════════════════════
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x8899aa, 0.008);  // lighter fog

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 500);
camera.position.set(0, 1.7, 0);

""" + AAA_RENDERER_SETUP + TEXTURE_GEN + PBR_MATERIALS + AAA_LIGHTING + FPS_COUNTER + """

// ── TERRAIN with procedural grass texture ──
const terrainGeo = new THREE.PlaneGeometry(200, 200, 80, 80);
const terrainPos = terrainGeo.attributes.position;
for (let i = 0; i < terrainPos.count; i++) {
    const x = terrainPos.getX(i), z = terrainPos.getZ(i);
    terrainPos.setY(i, Math.sin(x*0.05)*1.2 + Math.cos(z*0.04)*0.8 + Math.random()*0.3);
}
terrainGeo.computeVertexNormals();
const terrain = new THREE.Mesh(terrainGeo, pbrGrass());
terrain.rotation.x = -Math.PI / 2;
terrain.receiveShadow = true;
scene.add(terrain);

// ── ROAD (dirt path) ──
const roadGeo = new THREE.PlaneGeometry(6, 120);
const road = new THREE.Mesh(roadGeo, pbrDirt());
road.rotation.x = -Math.PI / 2;
road.position.y = 0.02;
road.receiveShadow = true;
scene.add(road);

// ── BUILDINGS with brick/concrete textures ──
function addBuilding(x, z, w=8, h=14, d=8) {
    // Main structure
    const geo = new THREE.BoxGeometry(w, h, d);
    const mat = Math.random() > 0.5 ? pbrBrick() : pbrConcrete(0x8a8075);
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.set(x, h/2, z);
    mesh.castShadow = true; mesh.receiveShadow = true;
    scene.add(mesh);

    // Roof
    const roofGeo = new THREE.BoxGeometry(w + 0.4, 0.3, d + 0.4);
    const roof = new THREE.Mesh(roofGeo, pbrConcrete(0x666055));
    roof.position.set(x, h + 0.15, z);
    roof.castShadow = true;
    scene.add(roof);

    // Windows (glowing glass)
    const wSize = 1.2;
    for (let wy = 2.5; wy < h - 1; wy += 3) {
        for (let wx = -w/2+1.5; wx < w/2 - 0.5; wx += 2.5) {
            const wgeo = new THREE.BoxGeometry(wSize, wSize * 1.3, 0.08);
            const wm = new THREE.Mesh(wgeo, pbrGlass());
            wm.position.set(x + wx, wy, z + d/2 + 0.04);
            scene.add(wm);
            // Window frame
            const frame = new THREE.Mesh(
                new THREE.BoxGeometry(wSize+0.15, wSize*1.3+0.15, 0.04),
                pbrMetal(0x444444, 0.5, 0.3)
            );
            frame.position.copy(wm.position);
            frame.position.z -= 0.02;
            scene.add(frame);
        }
    }

    // Door
    const doorGeo = new THREE.BoxGeometry(1.4, 2.5, 0.1);
    const door = new THREE.Mesh(doorGeo, pbrMetal(0x3a2a1a, 0.7, 0.1));
    door.position.set(x, 1.25, z + d/2 + 0.05);
    scene.add(door);
}

// City layout
[[-20,-15],[20,-15],[-20,15],[20,15],[0,-35],[0,35],[-35,0],[35,0],
 [-15,0,5,8,5],[15,0,5,8,5],[-30,-25,6,10,6],[30,25,6,10,6]].forEach(b => addBuilding(...b));

// ── DEBRIS & COVER (sandbags, barriers) ──
function addCover() {
    // Sandbag walls
    [[-5,5],[5,-5],[-8,-2],[8,3],[12,12],[-12,-12]].forEach(([x,z]) => {
        const group = new THREE.Group();
        for (let i = 0; i < 4; i++) {
            for (let j = 0; j < 2; j++) {
                const bag = new THREE.Mesh(
                    new THREE.CapsuleGeometry(0.25, 0.6, 4, 8),
                    pbrDirt()
                );
                bag.rotation.z = Math.PI / 2;
                bag.position.set(i * 0.65 - 0.9, j * 0.45 + 0.25, 0);
                bag.castShadow = true;
                group.add(bag);
            }
        }
        group.position.set(x, 0, z);
        group.rotation.y = Math.random() * Math.PI;
        scene.add(group);
    });

    // Concrete barriers
    [[2,8],[-3,-8],[0,15]].forEach(([x,z]) => {
        const geo = new THREE.BoxGeometry(3, 1.2, 0.5);
        const mesh = new THREE.Mesh(geo, pbrConcrete(0x777770));
        mesh.position.set(x, 0.6, z);
        mesh.castShadow = true; mesh.receiveShadow = true;
        scene.add(mesh);
    });

    // Destroyed car
    const carBody = new THREE.Mesh(
        new THREE.BoxGeometry(2.2, 0.8, 4.5),
        pbrMetal(0x4a4035, 0.6, 0.3)
    );
    carBody.position.set(-10, 0.4, 8);
    carBody.rotation.y = 0.3;
    carBody.castShadow = true;
    scene.add(carBody);
    const carTop = new THREE.Mesh(
        new THREE.BoxGeometry(1.8, 0.6, 2.2),
        pbrMetal(0x3a3530, 0.7, 0.2)
    );
    carTop.position.set(-10, 1.1, 7.5);
    carTop.rotation.y = 0.3;
    carTop.castShadow = true;
    scene.add(carTop);
}
addCover();

// ── TREES / VEGETATION ──
function addTree(x, z) {
    // Trunk
    const trunk = new THREE.Mesh(
        new THREE.CylinderGeometry(0.15, 0.25, 3, 6),
        pbrMetal(0x5a3a1a, 0.9, 0.0)
    );
    trunk.position.set(x, 1.5, z);
    trunk.castShadow = true;
    scene.add(trunk);
    // Foliage (3 layers)
    for (let i = 0; i < 3; i++) {
        const leaves = new THREE.Mesh(
            new THREE.SphereGeometry(1.8 - i * 0.4, 8, 6),
            new THREE.MeshStandardMaterial({
                color: new THREE.Color().setHSL(0.28 + Math.random()*0.05, 0.6, 0.25 + i*0.05),
                roughness: 1.0, metalness: 0
            })
        );
        leaves.position.set(x + (Math.random()-0.5)*0.5, 3 + i * 1.2, z + (Math.random()-0.5)*0.5);
        leaves.castShadow = true;
        scene.add(leaves);
    }
}
[[-25,10],[25,-10],[-30,-20],[30,20],[-10,-25],[10,25],[-40,15],[40,-15]].forEach(([x,z]) => addTree(x,z));

// ── PLAYER WEAPON (detailed gun model) ──
const gunGroup = new THREE.Group();
// Receiver
const gunBody = new THREE.Mesh(
    new THREE.BoxGeometry(0.08, 0.12, 0.55),
    pbrMetal(0x1a1a1a, 0.25, 0.95)
);
// Barrel
const barrel = new THREE.Mesh(
    new THREE.CylinderGeometry(0.02, 0.025, 0.45, 8),
    pbrMetal(0x2a2a2a, 0.15, 1.0)
);
barrel.rotation.x = Math.PI / 2;
barrel.position.z = -0.5;
// Grip
const grip = new THREE.Mesh(
    new THREE.BoxGeometry(0.06, 0.15, 0.08),
    pbrMetal(0x2a2010, 0.7, 0.1)
);
grip.position.set(0, -0.12, 0.1);
grip.rotation.x = -0.2;
// Stock
const stock = new THREE.Mesh(
    new THREE.BoxGeometry(0.06, 0.08, 0.25),
    pbrMetal(0x2a2010, 0.8, 0.1)
);
stock.position.set(0, 0, 0.35);
// Scope (optional sight)
const scope = new THREE.Mesh(
    new THREE.BoxGeometry(0.04, 0.04, 0.12),
    pbrMetal(0x111111, 0.1, 0.9)
);
scope.position.set(0, 0.1, -0.1);
// Magazine
const mag = new THREE.Mesh(
    new THREE.BoxGeometry(0.05, 0.15, 0.08),
    pbrMetal(0x1a1a1a, 0.3, 0.8)
);
mag.position.set(0, -0.12, -0.05);

gunGroup.add(gunBody, barrel, grip, stock, scope, mag);
gunGroup.position.set(0.28, -0.22, -0.45);
camera.add(gunGroup);
scene.add(camera);

// ── ENEMIES (detailed soldiers) ──
const enemies = [];
function createSoldier(x, z) {
    const g = new THREE.Group();
    // Legs
    const legMat = pbrMetal(0x2a3a1a, 0.8, 0.0);
    const legL = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.75, 0.22), legMat);
    legL.position.set(-0.15, 0.375, 0); legL.castShadow = true;
    const legR = legL.clone(); legR.position.x = 0.15;
    // Body (camo)
    const body = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.85, 0.3),
        pbrMetal(0x3a4a2a, 0.7, 0.0));
    body.position.y = 1.15; body.castShadow = true;
    // Head + helmet
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.2, 8, 8), pbrSkin());
    head.position.y = 1.75; head.castShadow = true;
    const helmet = new THREE.Mesh(new THREE.SphereGeometry(0.23, 8, 6, 0, Math.PI*2, 0, Math.PI*0.6),
        pbrMetal(0x3a4a2a, 0.6, 0.1));
    helmet.position.y = 1.82;
    // Arms
    const armL = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.6, 0.18),
        pbrMetal(0x3a4a2a, 0.8, 0.0));
    armL.position.set(-0.38, 1.1, 0); armL.castShadow = true;
    const armR = armL.clone(); armR.position.x = 0.38;
    // Enemy weapon
    const eGun = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.06, 0.45),
        pbrMetal(0x222222, 0.3, 0.9));
    eGun.position.set(0.38, 0.95, -0.2);
    [legL, legR, body, head, helmet, armL, armR, eGun].forEach(m => g.add(m));
    g.position.set(x, 0, z);
    g.userData = { health: 100, t: Math.random() * Math.PI * 2, startX: x, startZ: z };
    scene.add(g);
    return g;
}
[[-12,12],[12,-12],[-25,5],[25,-5],[0,22],[-20,-22],[15,18],[-18,30]].forEach(([x,z]) =>
    enemies.push(createSoldier(x, z)));

// ── MUZZLE FLASH ──
const flashMat = pbrEmissive(0xffaa00, 0xffff00, 8);
const muzzleFlash = new THREE.Mesh(new THREE.SphereGeometry(0.04, 4, 4), flashMat);
muzzleFlash.visible = false;
muzzleFlash.position.set(0.28, -0.18, -0.9);
camera.add(muzzleFlash);

// ── BULLETS ──
const bullets = [];
function shoot() {
    const b = new THREE.Mesh(
        new THREE.SphereGeometry(0.025, 4, 4),
        pbrEmissive(0xffdd00, 0xffaa00, 4)
    );
    b.position.copy(camera.position);
    const dir = new THREE.Vector3();
    camera.getWorldDirection(dir);
    b.userData.velocity = dir.multiplyScalar(1.0);
    b.userData.life = 1.5;
    scene.add(b);
    bullets.push(b);
    muzzleFlash.visible = true;
    setTimeout(() => muzzleFlash.visible = false, 50);
    gunGroup.position.z = -0.38;
    setTimeout(() => gunGroup.position.z = -0.45, 70);
}

// ── DUST PARTICLES ──
const dustGeo = new THREE.BufferGeometry();
const dustCount = 200;
const dustPos = new Float32Array(dustCount * 3);
for (let i = 0; i < dustCount * 3; i++) dustPos[i] = (Math.random() - 0.5) * 80;
dustGeo.setAttribute('position', new THREE.BufferAttribute(dustPos, 3));
const dust = new THREE.Points(dustGeo, new THREE.PointsMaterial({
    color: 0xccbb99, size: 0.15, transparent: true, opacity: 0.3
}));
scene.add(dust);

// ── CONTROLS ──
const keys = {};
document.addEventListener('keydown', e => keys[e.code] = true);
document.addEventListener('keyup', e => keys[e.code] = false);
document.addEventListener('click', () => document.getElementById('game-container').requestPointerLock());
document.getElementById('game-container').addEventListener('click', shoot);

let yaw = 0, pitch = 0, score = 0;
document.addEventListener('mousemove', e => {
    if (!document.pointerLockElement) return;
    yaw -= e.movementX * 0.002;
    pitch -= e.movementY * 0.002;
    pitch = Math.max(-1.2, Math.min(1.2, pitch));
    camera.rotation.order = 'YXZ';
    camera.rotation.y = yaw;
    camera.rotation.x = pitch;
});

const clock = new THREE.Clock();
const velocity = new THREE.Vector3();

function animate() {
    requestAnimationFrame(animate);
    const delta = Math.min(clock.getDelta(), 0.05);
    updateFPS(delta);
    const t = clock.getElapsedTime();

    // Player
    const speed = 8;
    const dir = new THREE.Vector3();
    const fwd = new THREE.Vector3(-Math.sin(yaw), 0, -Math.cos(yaw));
    const rt = new THREE.Vector3(Math.cos(yaw), 0, -Math.sin(yaw));
    if (keys['KeyW']) dir.addScaledVector(fwd, 1);
    if (keys['KeyS']) dir.addScaledVector(fwd, -1);
    if (keys['KeyA']) dir.addScaledVector(rt, -1);
    if (keys['KeyD']) dir.addScaledVector(rt, 1);
    if (dir.lengthSq() > 0) dir.normalize();
    velocity.lerp(dir.multiplyScalar(speed), 0.15);
    camera.position.addScaledVector(velocity, delta);
    camera.position.y = 1.7;

    // Enemies patrol
    enemies.forEach(e => {
        if (!e.visible) return;
        e.userData.t += delta * 0.6;
        e.position.x = e.userData.startX + Math.sin(e.userData.t) * 5;
        e.position.z = e.userData.startZ + Math.cos(e.userData.t * 0.7) * 5;
        e.lookAt(camera.position.x, e.position.y, camera.position.z);
    });

    // Bullets
    for (let i = bullets.length - 1; i >= 0; i--) {
        const b = bullets[i];
        b.position.add(b.userData.velocity);
        b.userData.life -= delta;
        if (b.userData.life <= 0) { scene.remove(b); bullets.splice(i, 1); continue; }
        // Hit detection
        enemies.forEach(e => {
            if (e.visible && b.position.distanceTo(e.position) < 1.5) {
                e.userData.health -= 34;
                scene.remove(b); bullets.splice(i, 1);
                if (e.userData.health <= 0) {
                    e.visible = false; score++;
                    const el = document.getElementById('score-display');
                    if (el) el.textContent = 'KILLS: ' + score;
                    setTimeout(() => {
                        e.position.set((Math.random()-0.5)*60, 0, (Math.random()-0.5)*60);
                        e.userData.health = 100; e.visible = true;
                    }, 3000);
                }
            }
        });
    }

    // Gun sway
    gunGroup.position.y = -0.22 + Math.sin(t * 2.5) * 0.004;
    gunGroup.rotation.z = Math.sin(t * 1.8) * 0.003;

    // Dust particles drift
    dust.rotation.y += delta * 0.02;

    composer.render();
}
animate();
"""

# ---------------------------------------------------------------------------
# RACING TEMPLATE
# ---------------------------------------------------------------------------
def _racing_template():
    return """
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x111122, 0.008);

const camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.1, 800);
camera.position.set(0, 3, 8);

""" + AAA_RENDERER_SETUP + TEXTURE_GEN + PBR_MATERIALS + FPS_COUNTER + """

// Lighting
scene.add(new THREE.HemisphereLight(0x334466, 0x111111, 0.5));
const headlights = [];
[-0.6, 0.6].forEach(x => {
    const l = new THREE.SpotLight(0xffffee, 8, 60, 0.25, 0.5);
    l.position.set(x, 0.5, -1); l.castShadow = true;
    scene.add(l, l.target);
    headlights.push(l);
});
for (let i = -5; i <= 5; i++) {
    [-4.5, 4.5].forEach(x => {
        const l = new THREE.PointLight(0xff8833, 2, 15);
        l.position.set(x, 4, i * 30);
        scene.add(l);
        const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 4, 6), pbrMetal(0x333333));
        pole.position.copy(l.position); pole.position.y = 2;
        scene.add(pole);
    });
}

// Night sky
const skyC = document.createElement('canvas');
skyC.width = 1; skyC.height = 256;
const skyX = skyC.getContext('2d');
const skyG = skyX.createLinearGradient(0,0,0,256);
skyG.addColorStop(0,'#000011'); skyG.addColorStop(1,'#0a0a2a');
skyX.fillStyle = skyG; skyX.fillRect(0,0,1,256);
scene.background = new THREE.CanvasTexture(skyC);

// Track
const track = new THREE.Mesh(
    new THREE.PlaneGeometry(8, 600),
    new THREE.MeshStandardMaterial({ map: concreteTex, color: 0x333333, roughness: 0.85 })
);
track.rotation.x = -Math.PI / 2; track.receiveShadow = true;
scene.add(track);

// Lane markings
for (let i = -15; i <= 15; i++) {
    const m = new THREE.Mesh(
        new THREE.PlaneGeometry(0.15, 3),
        new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xffffff, emissiveIntensity: 0.5 })
    );
    m.rotation.x = -Math.PI / 2; m.position.set(0, 0.01, i * 10);
    scene.add(m);
}

// Barriers
[-4, 4].forEach(x => {
    for (let i = -15; i <= 15; i++) {
        const col = (i % 2 === 0) ? 0xff2200 : 0xffffff;
        const mesh = new THREE.Mesh(new THREE.BoxGeometry(0.3,0.5,2.5), pbrMetal(col, 0.4, 0.3));
        mesh.position.set(x, 0.25, i * 9); mesh.castShadow = true;
        scene.add(mesh);
    }
});

// Player car
const carGroup = new THREE.Group();
const carBody = new THREE.Mesh(new THREE.BoxGeometry(1.8,0.55,4.2), pbrMetal(0xff2200, 0.15, 0.95));
carBody.position.y = 0.4; carBody.castShadow = true;
const cabin = new THREE.Mesh(new THREE.BoxGeometry(1.4,0.45,2.0), pbrMetal(0xcc1100, 0.2, 0.9));
cabin.position.set(0, 0.85, -0.3); cabin.castShadow = true;
const windshield = new THREE.Mesh(new THREE.BoxGeometry(1.3,0.4,0.05), pbrGlass());
windshield.position.set(0, 0.9, 0.65); windshield.rotation.x = -0.2;
const wheelGeo = new THREE.CylinderGeometry(0.35,0.35,0.25,16);
const wheelMat = pbrMetal(0x111111, 0.9, 0.1);
const wheels = [[-0.95,0,1.4],[0.95,0,1.4],[-0.95,0,-1.4],[0.95,0,-1.4]].map(([x,y,z]) => {
    const w = new THREE.Mesh(wheelGeo, wheelMat);
    w.rotation.z = Math.PI/2; w.position.set(x,y,z); w.castShadow = true;
    carGroup.add(w); return w;
});
[-0.5, 0.5].forEach(x => {
    const glow = new THREE.Mesh(new THREE.SphereGeometry(0.12,8,8), pbrEmissive(0xffffee,0xffffff,4));
    glow.position.set(x, 0.4, 2.15); carGroup.add(glow);
});
carGroup.add(carBody, cabin, windshield);
carGroup.position.set(0, 0.35, 0);
scene.add(carGroup);

// Controls
const keys = {};
document.addEventListener('keydown', e => keys[e.code] = true);
document.addEventListener('keyup', e => keys[e.code] = false);
let speed = 0, steer = 0;
const clock = new THREE.Clock();

function animate() {
    requestAnimationFrame(animate);
    const delta = clock.getDelta();
    updateFPS(delta);
    if (keys['ArrowUp']||keys['KeyW']) speed = Math.min(speed+15*delta, 40);
    else if (keys['ArrowDown']||keys['KeyS']) speed = Math.max(speed-20*delta, -10);
    else speed *= 0.97;
    if (keys['ArrowLeft']||keys['KeyA']) steer = Math.min(steer+2*delta, 0.06);
    else if (keys['ArrowRight']||keys['KeyD']) steer = Math.max(steer-2*delta, -0.06);
    else steer *= 0.85;
    carGroup.rotation.y += steer*(speed/40);
    carGroup.position.x = Math.max(-3.2, Math.min(3.2, carGroup.position.x + steer*speed*delta*1.5));
    scene.children.forEach(obj => {
        if (obj !== carGroup && obj !== camera && obj.position) {
            obj.position.z += speed * delta;
            if (obj.position.z > 40) obj.position.z -= 300;
        }
    });
    wheels.forEach(w => w.rotation.y += speed*delta*1.5);
    camera.position.set(carGroup.position.x*0.5, 3+Math.abs(speed)*0.02, carGroup.position.z+8);
    camera.lookAt(carGroup.position.x, 1.5, carGroup.position.z-5);
    headlights.forEach(l => l.intensity = 4+speed*0.1);
    bloomPass.strength = 0.3+speed*0.005;
    composer.render();
}
animate();
"""

# ---------------------------------------------------------------------------
# PLATFORMER TEMPLATE
# ---------------------------------------------------------------------------
def _platformer_template():
    return """
const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0x87ceeb, 30, 150);

const camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.1, 300);
camera.position.set(0, 5, 12);

""" + AAA_RENDERER_SETUP + TEXTURE_GEN + PBR_MATERIALS + AAA_LIGHTING + FPS_COUNTER + """

// Platforms
const platformDefs = [
    {x:0,y:-1,z:0,w:12,d:12,col:0x4a8c3f},
    {x:8,y:0,z:-5,w:5,d:5,col:0x8B4513},
    {x:14,y:2,z:-10,w:5,d:5,col:0x8B4513},
    {x:6,y:4,z:-18,w:6,d:4,col:0x7a6040},
    {x:-2,y:6,z:-25,w:5,d:5,col:0x4a8c3f},
    {x:-10,y:8,z:-20,w:5,d:5,col:0x8B4513},
    {x:-14,y:10,z:-12,w:6,d:4,col:0x7a6040},
    {x:0,y:12,z:-8,w:8,d:8,col:0xffd700},
];
const platforms = platformDefs.map(p => {
    const mat = p.col === 0x4a8c3f ? pbrGrass() :
        new THREE.MeshStandardMaterial({ color: p.col, roughness: 0.85, metalness: 0.1 });
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(p.w, 1, p.d), mat);
    mesh.position.set(p.x, p.y, p.z);
    mesh.receiveShadow = true; mesh.castShadow = true; mesh.userData = p;
    scene.add(mesh); return mesh;
});

// Coins
const coins = [];
platformDefs.slice(1).forEach(p => {
    const mesh = new THREE.Mesh(new THREE.TorusGeometry(0.3,0.08,8,20), pbrMetal(0xffd700,0.1,1.0));
    mesh.position.set(p.x, p.y+1.5, p.z); mesh.castShadow = true;
    scene.add(mesh); coins.push(mesh);
});

// Hero
const hero = new THREE.Group();
const hBody = new THREE.Mesh(new THREE.BoxGeometry(0.6,0.8,0.4), pbrMetal(0x3388ff,0.3,0.1));
hBody.position.y = 0.4; hBody.castShadow = true;
const hHead = new THREE.Mesh(new THREE.SphereGeometry(0.3,12,12), pbrSkin());
hHead.position.y = 1.05; hHead.castShadow = true;
const hLegL = new THREE.Mesh(new THREE.BoxGeometry(0.22,0.5,0.22), pbrMetal(0x224488,0.5,0.1));
hLegL.position.set(-0.18,-0.05,0); hLegL.castShadow = true;
const hLegR = hLegL.clone(); hLegR.position.x = 0.18;
hero.add(hBody, hHead, hLegL, hLegR);
hero.position.set(0, 0, 0);
scene.add(hero);

const keys = {};
document.addEventListener('keydown', e => { keys[e.code] = true; e.preventDefault(); });
document.addEventListener('keyup', e => keys[e.code] = false);
let velY = 0, onGround = false, score = 0;
const clock = new THREE.Clock();

function animate() {
    requestAnimationFrame(animate);
    const delta = Math.min(clock.getDelta(), 0.05);
    updateFPS(delta);
    const t = clock.getElapsedTime();
    const speed = 6;
    if (keys['ArrowLeft']||keys['KeyA']) hero.position.x -= speed*delta;
    if (keys['ArrowRight']||keys['KeyD']) hero.position.x += speed*delta;
    if (keys['ArrowUp']||keys['KeyW']) hero.position.z -= speed*delta;
    if (keys['ArrowDown']||keys['KeyS']) hero.position.z += speed*delta;
    if ((keys['Space']||keys['ArrowUp']) && onGround) { velY = 8; onGround = false; }
    velY -= 20*delta; hero.position.y += velY*delta;
    onGround = false;
    platforms.forEach(p => {
        const pd = p.userData;
        if (Math.abs(hero.position.x-pd.x)<pd.w/2+0.3 && Math.abs(hero.position.z-pd.z)<pd.d/2+0.3
            && hero.position.y>=pd.y && hero.position.y<=pd.y+1.5 && velY<=0) {
            hero.position.y = pd.y+0.5; velY = 0; onGround = true;
        }
    });
    if (hero.position.y < -20) { hero.position.set(0,1,0); velY = 0; }
    hLegL.rotation.x = Math.sin(t*8)*0.4;
    hLegR.rotation.x = -Math.sin(t*8)*0.4;
    coins.forEach(c => {
        c.rotation.y += delta*2;
        if (c.visible && c.position.distanceTo(hero.position) < 1.2) {
            c.visible = false; score++;
            const el = document.getElementById('score-display');
            if (el) el.textContent = 'Score: ' + score;
        }
    });
    const target = hero.position.clone().add(new THREE.Vector3(0,4,10));
    camera.position.lerp(target, 5*delta);
    camera.lookAt(hero.position.x, hero.position.y+1, hero.position.z);
    composer.render();
}
animate();
"""

# ---------------------------------------------------------------------------
# SPACE SHOOTER
# ---------------------------------------------------------------------------
def _space_shooter_template():
    return """
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x000008);
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 2000);
camera.position.set(0, 0, 20);

""" + AAA_RENDERER_SETUP + TEXTURE_GEN + PBR_MATERIALS + FPS_COUNTER + """

// Stars
const starGeo = new THREE.BufferGeometry();
const starPos = new Float32Array(5000 * 3);
for (let i = 0; i < 15000; i++) starPos[i] = (Math.random()-0.5)*1000;
starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
scene.add(new THREE.Points(starGeo, new THREE.PointsMaterial({ color: 0xffffff, size: 0.3 })));

// Nebula
[{x:0,y:0,z:-200,c:0x220066},{x:-80,y:30,z:-150,c:0x004422},{x:80,y:-30,z:-180,c:0x440022}].forEach(n => {
    const m = new THREE.Mesh(new THREE.SphereGeometry(30,8,8),
        new THREE.MeshBasicMaterial({color:n.c, transparent:true, opacity:0.04, side:THREE.BackSide}));
    m.position.set(n.x,n.y,n.z); scene.add(m);
});

scene.add(new THREE.AmbientLight(0x111133, 2));
const engineGlow = new THREE.PointLight(0x4488ff, 3, 20);
scene.add(engineGlow);
bloomPass.strength = 1.2; bloomPass.radius = 0.8; bloomPass.threshold = 0.1;

// Ship
const ship = new THREE.Group();
const shipBody = new THREE.Mesh(new THREE.ConeGeometry(0.6,3,6), pbrMetal(0x4488ff,0.2,0.9));
shipBody.rotation.x = Math.PI/2;
const wingL = new THREE.Mesh(new THREE.BoxGeometry(3,0.1,1.5), pbrMetal(0x2255aa,0.3,0.8));
wingL.position.set(-1.2,0,0.4);
const wingR = wingL.clone(); wingR.position.x = 1.2;
const thruster = new THREE.Mesh(new THREE.SphereGeometry(0.3,8,8), pbrEmissive(0x4488ff,0x2244ff,6));
thruster.position.z = 1.8;
ship.add(shipBody, wingL, wingR, thruster);
scene.add(ship);

// Enemies
function spawnEnemy() {
    const g = new THREE.Group();
    g.add(new THREE.Mesh(new THREE.OctahedronGeometry(1.2), pbrMetal(0xff2200,0.3,0.7)));
    g.add(new THREE.Mesh(new THREE.SphereGeometry(1.5,8,8),
        new THREE.MeshBasicMaterial({color:0xff2200, transparent:true, opacity:0.1})));
    g.position.set((Math.random()-0.5)*40, (Math.random()-0.5)*20, -100-Math.random()*100);
    g.userData = { speed: 0.1+Math.random()*0.15, health: 3 };
    scene.add(g); return g;
}
const enemies = Array.from({length:8}, spawnEnemy);

// Lasers
const lasers = [];
function fireLaser() {
    const l = new THREE.Mesh(new THREE.CapsuleGeometry(0.05,1.5,4,4), pbrEmissive(0x00ffff,0x00ffff,8));
    l.position.copy(ship.position); l.rotation.z = Math.PI/2;
    l.userData = { vz: -0.8, life: 80 };
    scene.add(l); lasers.push(l);
}

const keys = {};
document.addEventListener('keydown', e => keys[e.code] = true);
document.addEventListener('keyup', e => keys[e.code] = false);
let lastFire = 0, score = 0;
const clock = new THREE.Clock();

function animate() {
    requestAnimationFrame(animate);
    const delta = clock.getDelta();
    updateFPS(delta);
    const t = clock.getElapsedTime();
    if (keys['ArrowLeft']||keys['KeyA']) ship.position.x = Math.max(-18, ship.position.x-12*delta);
    if (keys['ArrowRight']||keys['KeyD']) ship.position.x = Math.min(18, ship.position.x+12*delta);
    if (keys['ArrowUp']||keys['KeyW']) ship.position.y = Math.min(10, ship.position.y+8*delta);
    if (keys['ArrowDown']||keys['KeyS']) ship.position.y = Math.max(-10, ship.position.y-8*delta);
    if ((keys['Space']||keys['KeyZ']) && t-lastFire > 0.15) { fireLaser(); lastFire = t; }
    ship.rotation.z = -ship.position.x*0.04;
    engineGlow.position.set(ship.position.x, ship.position.y, ship.position.z+2);
    engineGlow.intensity = 3+Math.sin(t*10)*0.5;

    for (let i = lasers.length-1; i >= 0; i--) {
        const l = lasers[i];
        l.position.z += l.userData.vz; l.userData.life--;
        if (l.userData.life <= 0) { scene.remove(l); lasers.splice(i,1); continue; }
        enemies.forEach(e => {
            if (e.visible && l.position.distanceTo(e.position) < 2) {
                e.userData.health--; scene.remove(l); lasers.splice(i,1);
                if (e.userData.health <= 0) {
                    e.visible = false; score++;
                    const el = document.getElementById('score-display');
                    if (el) el.textContent = 'Score: ' + score;
                    setTimeout(() => { Object.assign(e.position, spawnEnemy().position); e.visible=true; e.userData.health=3; }, 1000);
                }
            }
        });
    }
    enemies.forEach(e => {
        if (!e.visible) return;
        e.position.z += e.userData.speed; e.rotation.x += 0.02; e.rotation.y += 0.015;
        if (e.position.z > 25) { e.position.z = -100-Math.random()*100; e.position.x = (Math.random()-0.5)*40; }
    });
    composer.render();
}
animate();
"""

# ---------------------------------------------------------------------------
# SOCCER TEMPLATE
# ---------------------------------------------------------------------------
def _soccer_template():
    return """
const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0x111111, 50, 200);

const camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.1, 300);
camera.position.set(0, 15, 35); camera.lookAt(0,0,0);

""" + AAA_RENDERER_SETUP + TEXTURE_GEN + PBR_MATERIALS + FPS_COUNTER + """

// Stadium lights
[[-25,18,-30],[25,18,-30],[-25,18,30],[25,18,30]].forEach(([x,y,z]) => {
    const l = new THREE.SpotLight(0xfff5e0, 12, 120, Math.PI/5, 0.3);
    l.position.set(x,y,z); l.castShadow = true;
    l.shadow.mapSize.set(1024,1024); l.target.position.set(0,0,0);
    scene.add(l, l.target);
    const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.2,0.2,y,6), pbrMetal(0x888888,0.5,0.6));
    pole.position.set(x,y/2,z); scene.add(pole);
});

// Pitch
const pitch = new THREE.Mesh(new THREE.PlaneGeometry(70,100,10,14), pbrGrass());
pitch.rotation.x = -Math.PI/2; pitch.receiveShadow = true;
scene.add(pitch);

// Markings
function addLine(x,z,w,d) {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w,d),
        new THREE.MeshStandardMaterial({color:0xffffff, roughness:0.8}));
    m.rotation.x = -Math.PI/2; m.position.set(x, 0.01, z); scene.add(m);
}
addLine(0,0,70,0.2); addLine(0,0,0.2,100);
scene.add(new THREE.Mesh(new THREE.RingGeometry(9.15,9.35,48),
    new THREE.MeshStandardMaterial({color:0xffffff, side:THREE.DoubleSide}))
    .rotateX(-Math.PI/2).translateY(0.01));

// Goals
function buildGoal(z) {
    const mat = pbrMetal(0xffffff,0.2,0.8);
    [-3.66, 3.66].forEach(x => {
        const post = new THREE.Mesh(new THREE.CylinderGeometry(0.08,0.08,2.5,8), mat);
        post.position.set(x,1.25,z); post.castShadow = true; scene.add(post);
    });
    const bar = new THREE.Mesh(new THREE.CylinderGeometry(0.08,0.08,7.32,8), mat);
    bar.rotation.z = Math.PI/2; bar.position.set(0,2.5,z); scene.add(bar);
}
buildGoal(-49); buildGoal(49);

// Ball
const ball = new THREE.Mesh(new THREE.SphereGeometry(0.7,24,24), pbrMetal(0xffffff,0.6,0.0));
ball.castShadow = true; ball.position.set(0,0.7,0); scene.add(ball);

// Player
const player = new THREE.Group();
const pb = new THREE.Mesh(new THREE.BoxGeometry(0.7,1.2,0.4), pbrMetal(0xff2200,0.5,0.1));
pb.position.y = 0.6; pb.castShadow = true;
const ph = new THREE.Mesh(new THREE.SphereGeometry(0.35,12,12), pbrSkin());
ph.position.y = 1.55; ph.castShadow = true;
const pl = new THREE.Mesh(new THREE.BoxGeometry(0.28,0.7,0.28), pbrMetal(0xffffff,0.7,0.0));
pl.position.set(-0.2,-0.15,0); const pr = pl.clone(); pr.position.x = 0.2;
player.add(pb,ph,pl,pr);
player.position.set(0,0,10); scene.add(player);

const keys = {};
document.addEventListener('keydown', e => keys[e.code] = true);
document.addEventListener('keyup', e => keys[e.code] = false);
let ballVel = new THREE.Vector3(), scored = 0;
const clock = new THREE.Clock();

function animate() {
    requestAnimationFrame(animate);
    const delta = Math.min(clock.getDelta(), 0.05);
    updateFPS(delta);
    const t = clock.getElapsedTime();
    const spd = 10;
    if (keys['ArrowLeft']||keys['KeyA']) player.position.x = Math.max(-33, player.position.x-spd*delta);
    if (keys['ArrowRight']||keys['KeyD']) player.position.x = Math.min(33, player.position.x+spd*delta);
    if (keys['ArrowUp']||keys['KeyW']) player.position.z = Math.max(-48, player.position.z-spd*delta);
    if (keys['ArrowDown']||keys['KeyS']) player.position.z = Math.min(48, player.position.z+spd*delta);
    if (keys['Space']) {
        const dir = ball.position.clone().sub(player.position).normalize();
        if (ball.position.distanceTo(player.position) < 2) ballVel.set(dir.x*18, 4, dir.z*18);
    }
    ballVel.y -= 15*delta;
    ball.position.addScaledVector(ballVel, delta);
    ball.rotation.x += ballVel.z*delta; ball.rotation.z -= ballVel.x*delta;
    if (ball.position.y <= 0.7) { ball.position.y=0.7; ballVel.y=Math.abs(ballVel.y)*0.55; ballVel.x*=0.85; ballVel.z*=0.85; }
    if (Math.abs(ball.position.x) > 35) ballVel.x *= -0.7;
    if (Math.abs(ball.position.z) > 50) { ballVel.set(0,0,0); ball.position.set(0,0.7,0); }
    if (ball.position.z < -48 && Math.abs(ball.position.x) < 3.66 && ball.position.y < 2.6) {
        scored++;
        const el = document.getElementById('score-display');
        if (el) el.textContent = 'Goals: ' + scored;
        ballVel.set(0,0,0); ball.position.set(0,0.7,0);
    }
    camera.position.x += (player.position.x*0.3-camera.position.x)*3*delta;
    camera.position.z = player.position.z+18;
    camera.lookAt(player.position.x, 0, player.position.z);
    pl.rotation.x = Math.sin(t*8)*0.4; pr.rotation.x = -Math.sin(t*8)*0.4;
    composer.render();
}
animate();
"""

# ---------------------------------------------------------------------------
# HTML WRAPPER
# ---------------------------------------------------------------------------
def _build_html(game_code: str, title: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>{title} — AAA 3D Game</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#000; overflow:hidden; font-family:'Segoe UI',sans-serif; }}
  #game-container {{ width:100vw; height:100vh; display:block; }}
  #game-container canvas {{ display:block; width:100% !important; height:100% !important; }}
  #hud {{
    position:fixed; top:0; left:0; right:0; bottom:0;
    pointer-events:none; z-index:10;
  }}
  #fps-counter {{
    position:absolute; top:12px; right:16px;
    color:#00ff88; font-size:14px; font-weight:700;
    text-shadow:0 0 8px #00ff88;
    font-family:'Courier New',monospace;
  }}
  #score-display {{
    position:absolute; top:12px; left:50%; transform:translateX(-50%);
    color:#fff; font-size:20px; font-weight:800;
    text-shadow:0 0 12px #fff, 0 2px 4px rgba(0,0,0,0.8);
  }}
  #quality-panel {{
    position:absolute; bottom:16px; right:16px;
    display:flex; gap:6px; pointer-events:all;
  }}
  .q-btn {{
    padding:6px 12px; border:1px solid rgba(255,255,255,0.3);
    background:rgba(0,0,0,0.6); color:#fff; cursor:pointer;
    border-radius:4px; font-size:12px; font-weight:600;
    transition:all 0.2s; backdrop-filter:blur(8px);
  }}
  .q-btn:hover {{ background:rgba(255,255,255,0.2); border-color:#fff; }}
  .q-btn.active {{ background:rgba(0,200,100,0.3); border-color:#00ff88; color:#00ff88; }}
  #controls-hint {{
    position:absolute; bottom:16px; left:16px;
    color:rgba(255,255,255,0.6); font-size:12px;
    line-height:1.6; pointer-events:none;
  }}
  #crosshair {{
    position:absolute; top:50%; left:50%;
    transform:translate(-50%,-50%);
    width:20px; height:20px; pointer-events:none;
  }}
  #crosshair::before, #crosshair::after {{
    content:''; position:absolute; background:rgba(255,255,255,0.8);
  }}
  #crosshair::before {{ width:2px; height:100%; left:50%; transform:translateX(-50%); }}
  #crosshair::after  {{ height:2px; width:100%; top:50%;  transform:translateY(-50%); }}
  #loading-overlay {{
    position:fixed; inset:0; background:#000;
    display:flex; align-items:center; justify-content:center;
    flex-direction:column; gap:16px; z-index:100;
    transition:opacity 0.5s;
  }}
  #loading-overlay.hidden {{ opacity:0; pointer-events:none; }}
  .loading-bar-wrap {{ width:300px; height:4px; background:rgba(255,255,255,0.1); border-radius:2px; overflow:hidden; }}
  .loading-bar {{ height:100%; width:0; background:linear-gradient(90deg,#00ff88,#0088ff); border-radius:2px; animation:load 1.5s ease-out forwards; }}
  @keyframes load {{ to {{ width:100%; }} }}
  .loading-title {{ color:#fff; font-size:28px; font-weight:900; letter-spacing:3px; }}
  .loading-sub   {{ color:rgba(255,255,255,0.5); font-size:13px; }}
</style>
</head>
<body>
<div id="loading-overlay">
  <div class="loading-title">⚡ {title.upper()}</div>
  <div class="loading-bar-wrap"><div class="loading-bar"></div></div>
  <div class="loading-sub">Initializing AAA renderer · PBR · Bloom · ACES</div>
</div>
<div id="game-container"></div>
<div id="hud">
  <div id="fps-counter">-- FPS</div>
  <div id="score-display"></div>
  <div id="crosshair"></div>
  <div id="quality-panel">
    <button class="q-btn" onclick="setQuality('low')">Low</button>
    <button class="q-btn" onclick="setQuality('high')">High</button>
    <button class="q-btn active" onclick="setQuality('ultra')">Ultra 4K</button>
  </div>
  <div id="controls-hint">
    WASD / Arrows — Move<br>
    Space — Jump / Action<br>
    Mouse — Look<br>
    Click — Interact
  </div>
</div>
<!-- Use only Module Import to avoid duplicate Three.js instances -->
<script type="importmap">
{{
  "imports": {{
    "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
  }}
}}
</script>
<script type="module">
import {{ EffectComposer }} from 'three/addons/postprocessing/EffectComposer.js';
import {{ RenderPass }}     from 'three/addons/postprocessing/RenderPass.js';
import {{ UnrealBloomPass }} from 'three/addons/postprocessing/UnrealBloomPass.js';
import {{ OutputPass }}     from 'three/addons/postprocessing/OutputPass.js';

{game_code}

setTimeout(() => {{
  const overlay = document.getElementById('loading-overlay');
  if (overlay) overlay.classList.add('hidden');
}}, 1800);
</script>
</body>
</html>"""

# ---------------------------------------------------------------------------
# MAIN ENTRY
# ---------------------------------------------------------------------------
GAME_KEYWORDS = {
    'warzone': _warzone_fps_template, 'fps': _warzone_fps_template,
    'shooter': _warzone_fps_template, 'soldier': _warzone_fps_template,
    'gun': _warzone_fps_template, 'combat': _warzone_fps_template,
    'military': _warzone_fps_template, 'sniper': _warzone_fps_template,
    'race': _racing_template, 'racing': _racing_template,
    'car': _racing_template, 'drive': _racing_template,
    'speed': _racing_template, 'drift': _racing_template,
    'platformer': _platformer_template, 'platform': _platformer_template,
    'jump': _platformer_template, 'mario': _platformer_template,
    'collect': _platformer_template,
    'space': _space_shooter_template, 'spaceship': _space_shooter_template,
    'alien': _space_shooter_template, 'galaxy': _space_shooter_template,
    'star': _space_shooter_template, 'laser': _space_shooter_template,
    'soccer': _soccer_template, 'football': _soccer_template,
    'sport': _soccer_template, 'goal': _soccer_template,
    'ball': _soccer_template,
}

def generate_aaa_game(prompt: str) -> dict:
    """Generate a real AAA-quality 3D game from a text prompt."""
    prompt_lower = prompt.lower()
    game_fn = None
    titles = {
        _warzone_fps_template:    ('Warzone FPS', 'fps'),
        _racing_template:         ('Night Racing', 'racing'),
        _platformer_template:     ('3D Platformer', 'platformer'),
        _space_shooter_template:  ('Space Shooter', 'space'),
        _soccer_template:         ('Soccer Stadium', 'soccer'),
    }
    for kw, fn in GAME_KEYWORDS.items():
        if kw in prompt_lower:
            game_fn = fn
            break
    if game_fn is None:
        game_fn = _warzone_fps_template
    title, game_type = titles[game_fn]
    game_code = game_fn()
    html = _build_html(game_code, title)
    return {
        'html': html,
        'title': title,
        'type': game_type,
        'engine': 'Three.js r160 + PBR + EnvMap + Bloom + ACES',
        'quality': '4K Ultra (pixelRatio 2.0, 2048 shadows)'
    }
