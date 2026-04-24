"""
real_3d_generator.py
────────────────────
Generate REAL 3D models as .glb/.obj files.
Uses trimesh library to create actual 3D geometry.

Supported shapes:
- cube, sphere, cylinder, cone, torus, pyramid
- dragon, robot, spaceship, alien, etc (procedural)
"""

import os
import trimesh
import numpy as np
from datetime import datetime
import json


class RealModelGenerator:
    """Generate real 3D models."""

    def __init__(self):
        # Use platform-independent path
        self.output_dir = os.path.join(os.path.dirname(__file__), "static", "models")
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"[3D] Output directory: {self.output_dir}")

    def create_cube(self, size=1.0, color=None):
        """Create a cube."""
        mesh = trimesh.creation.box(extents=[size, size, size])
        if color:
            mesh.visual.vertex_colors = color
        return mesh

    def create_sphere(self, radius=1.0, color=None):
        """Create a sphere."""
        mesh = trimesh.creation.icosphere(radius=radius, subdivisions=3)
        if color:
            mesh.visual.vertex_colors = color
        return mesh

    def create_cylinder(self, radius=1.0, height=2.0, color=None):
        """Create a cylinder."""
        mesh = trimesh.creation.cylinder(radius=radius, height=height)
        if color:
            mesh.visual.vertex_colors = color
        return mesh

    def create_cone(self, radius=1.0, height=2.0, color=None):
        """Create a cone."""
        mesh = trimesh.creation.cone(radius=radius, height=height)
        if color:
            mesh.visual.vertex_colors = color
        return mesh

    def create_torus(self, major_radius=2.0, minor_radius=0.5, color=None):
        """Create a torus."""
        mesh = trimesh.creation.torus(major_radius=major_radius, minor_radius=minor_radius)
        if color:
            mesh.visual.vertex_colors = color
        return mesh

    def create_dragon(self):
        """Create a procedural dragon."""
        # Body
        body = trimesh.creation.cylinder(radius=0.8, height=3.0)
        body.apply_translation([0, 0, 0])

        # Head
        head = trimesh.creation.icosphere(radius=0.6, subdivisions=2)
        head.apply_translation([0, 0, 2])

        # Wings
        wing_geom = trimesh.creation.box(extents=[0.2, 2.0, 3.0])
        wing_left = wing_geom.copy()
        wing_left.apply_translation([-1.5, 0, 1])

        wing_right = wing_geom.copy()
        wing_right.apply_translation([1.5, 0, 1])

        # Combine
        combined = trimesh.util.concatenate([body, head, wing_left, wing_right])
        combined.fill_holes()
        return combined

    def create_robot(self):
        """Create a procedural robot."""
        meshes = []

        # Body
        body = trimesh.creation.box(extents=[1.0, 2.0, 1.5])
        body.apply_translation([0, 0, 0])
        meshes.append(body)

        # Head
        head = trimesh.creation.box(extents=[0.8, 0.8, 0.8])
        head.apply_translation([0, 0, 2.5])
        meshes.append(head)

        # Arms
        arm = trimesh.creation.cylinder(radius=0.3, height=2.0)
        arm_left = arm.copy()
        arm_left.apply_translation([-1.5, 0, 1.5])
        meshes.append(arm_left)

        arm_right = arm.copy()
        arm_right.apply_translation([1.5, 0, 1.5])
        meshes.append(arm_right)

        # Legs
        leg = trimesh.creation.cylinder(radius=0.3, height=2.0)
        leg_left = leg.copy()
        leg_left.apply_translation([-0.5, 0, -1.5])
        meshes.append(leg_left)

        leg_right = leg.copy()
        leg_right.apply_translation([0.5, 0, -1.5])
        meshes.append(leg_right)

        # Combine
        combined = trimesh.util.concatenate(meshes)
        return combined

    def create_spaceship(self):
        """Create a procedural spaceship."""
        meshes = []

        # Main fuselage
        fuselage = trimesh.creation.cylinder(radius=0.6, height=3.0)
        fuselage.apply_translation([0, 0, 0])
        meshes.append(fuselage)

        # Cone nose
        nose = trimesh.creation.cone(radius=0.6, height=1.0)
        nose.apply_translation([0, 0, 2.5])
        meshes.append(nose)

        # Wings
        wing = trimesh.creation.box(extents=[0.3, 3.0, 0.5])
        wing_top = wing.copy()
        wing_top.apply_translation([0, 0, 0.8])
        meshes.append(wing_top)

        wing_bottom = wing.copy()
        wing_bottom.apply_translation([0, 0, -0.8])
        meshes.append(wing_bottom)

        # Engines
        engine = trimesh.creation.cylinder(radius=0.2, height=1.0)
        engine_left = engine.copy()
        engine_left.apply_translation([-0.8, 0, -1.5])
        meshes.append(engine_left)

        engine_right = engine.copy()
        engine_right.apply_translation([0.8, 0, -1.5])
        meshes.append(engine_right)

        # Combine
        combined = trimesh.util.concatenate(meshes)
        return combined

    def parse_prompt(self, prompt: str):
        """Parse prompt to determine what to create."""
        prompt_lower = prompt.lower()

        # Check for shapes
        if "sphere" in prompt_lower or "ball" in prompt_lower:
            return self.create_sphere(radius=1.5)
        elif "cube" in prompt_lower or "box" in prompt_lower:
            return self.create_cube(size=2.0)
        elif "cylinder" in prompt_lower:
            return self.create_cylinder(radius=1.0, height=2.5)
        elif "cone" in prompt_lower:
            return self.create_cone(radius=1.0, height=2.5)
        elif "torus" in prompt_lower or "donut" in prompt_lower:
            return self.create_torus()

        # Check for creatures
        if "dragon" in prompt_lower or "reptile" in prompt_lower:
            return self.create_dragon()
        elif "robot" in prompt_lower or "android" in prompt_lower or "droid" in prompt_lower:
            return self.create_robot()
        elif "spaceship" in prompt_lower or "ship" in prompt_lower or "aircraft" in prompt_lower:
            return self.create_spaceship()

        # Default
        return self.create_sphere(radius=1.5)

    def generate_and_save(self, prompt: str) -> dict:
        """Generate a 3D model from prompt and save it."""
        try:
            mesh = self.parse_prompt(prompt)

            # Create unique filename with random component
            import random
            timestamp = int(datetime.now().timestamp())
            random_id = random.randint(1000, 9999)
            filename = f"model_{timestamp}_{random_id}.glb"
            filepath = os.path.join(self.output_dir, filename)

            # Export as GLB (binary format, smaller file size)
            mesh.export(filepath, file_type='glb')

            # Also export OBJ for compatibility
            obj_filename = filename.replace('.glb', '.obj')
            obj_path = os.path.join(self.output_dir, obj_filename)
            mesh.export(obj_path, file_type='obj')

            file_size = os.path.getsize(filepath) / 1024  # KB

            return {
                "status": "ok",
                "glb_url": f"/static/models/{filename}",
                "obj_url": f"/static/models/{obj_filename}",
                "file_size_kb": round(file_size, 2),
                "vertices": len(mesh.vertices),
                "faces": len(mesh.faces),
                "prompt": prompt,
                "message": f"✅ Real 3D model generated! {len(mesh.vertices)} vertices, {len(mesh.faces)} faces"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to generate model: {str(e)}"
            }

    def list_models(self) -> list:
        """List all generated models."""
        models = []
        for f in os.listdir(self.output_dir):
            if f.endswith('.glb'):
                path = os.path.join(self.output_dir, f)
                size = os.path.getsize(path) / 1024
                models.append({
                    "filename": f,
                    "url": f"/static/models/{f}",
                    "size_kb": round(size, 2),
                    "created": datetime.fromtimestamp(os.path.getctime(path)).isoformat()
                })
        return sorted(models, key=lambda x: x["created"], reverse=True)


# Singleton
_generator = None

def get_generator():
    global _generator
    if _generator is None:
        _generator = RealModelGenerator()
    return _generator


if __name__ == "__main__":
    gen = RealModelGenerator()

    print("\n🎨 Generating Real 3D Models\n")

    # Test
    result = gen.generate_and_save("create a dragon")
    print(f"Dragon: {result}")

    result = gen.generate_and_save("robot")
    print(f"Robot: {result}")

    result = gen.generate_and_save("spaceship")
    print(f"Spaceship: {result}")

    print("\n✅ Models saved to /c/Gamansai/ai/static/models/")
