"""
text_to_3d.py
─────────────
Optional text→3D model generation via Meshy AI.

Set env var to enable:
  MESHY_API_KEY=msy_...   (get free tier at https://meshy.ai)

If not set, the bot falls back to procedural Three.js primitives (no API).
"""

from __future__ import annotations
import os
import json
import time
import urllib.request
import urllib.error

MESHY_KEY = os.getenv("MESHY_API_KEY")
MESHY_ENABLED = bool(MESHY_KEY)

MESHY_BASE = "https://api.meshy.ai/openapi/v2/text-to-3d"


def _post(url: str, body: dict) -> dict | None:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={
            "Authorization": f"Bearer {MESHY_KEY}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except (urllib.error.URLError, json.JSONDecodeError) as e:
        print(f"[text_to_3d] POST failed: {e}")
        return None


def _get(url: str) -> dict | None:
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {MESHY_KEY}"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except (urllib.error.URLError, json.JSONDecodeError) as e:
        print(f"[text_to_3d] GET failed: {e}")
        return None


def generate_3d_model(prompt: str, poll_seconds: int = 120) -> dict | None:
    """
    Returns { "glb_url": <str>, "prompt": <str>, "status": "ok" }
    or None on failure.
    """
    if not MESHY_ENABLED:
        return None

    start = _post(MESHY_BASE, {"mode": "preview", "prompt": prompt, "art_style": "realistic"})
    if not start or "result" not in start:
        return None
    task_id = start["result"]

    deadline = time.time() + poll_seconds
    while time.time() < deadline:
        info = _get(f"{MESHY_BASE}/{task_id}")
        if not info:
            return None
        if info.get("status") == "SUCCEEDED":
            glb = info.get("model_urls", {}).get("glb")
            if glb:
                return {"glb_url": glb, "prompt": prompt, "status": "ok"}
            return None
        if info.get("status") == "FAILED":
            return None
        time.sleep(5)
    return None


if __name__ == "__main__":
    print(f"Meshy enabled: {MESHY_ENABLED}")
    if MESHY_ENABLED:
        print(generate_3d_model("a cute red dragon"))
