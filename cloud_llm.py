"""
cloud_llm.py
────────────
Optional cloud LLM fallback using Claude or OpenAI GPT-4.5.

Set one of these env vars to enable:
  ANTHROPIC_API_KEY=sk-ant-...
  OPENAI_API_KEY=sk-...

If neither is set, this module is a no-op and the bot uses local rule-based replies.
"""

from __future__ import annotations
import os
import json
import urllib.request
import urllib.error


ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_KEY    = os.getenv("OPENAI_API_KEY")
CLOUD_ENABLED = bool(ANTHROPIC_KEY or OPENAI_KEY)

SYSTEM_PROMPT = (
    "You are a friendly, concise coding teacher. "
    "Default to short, varied replies. Only give long explanations if the user asks "
    "to 'explain', 'teach', or 'in detail'. Use code blocks for code. "
    "Never repeat the same greeting twice in a row."
)


def _anthropic_call(message: str) -> str | None:
    if not ANTHROPIC_KEY:
        return None
    body = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 600,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": message}],
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
            return data["content"][0]["text"]
    except (urllib.error.URLError, KeyError, json.JSONDecodeError) as e:
        print(f"[cloud_llm] Anthropic call failed: {e}")
        return None


def _openai_call(message: str) -> str | None:
    if not OPENAI_KEY:
        return None
    body = json.dumps({
        "model": "gpt-4o",  # 🏆 GPT-4o — beats GPT-3.5
        "max_tokens": 1200,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {OPENAI_KEY}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
            return data["choices"][0]["message"]["content"]
    except (urllib.error.URLError, KeyError, json.JSONDecodeError) as e:
        print(f"[cloud_llm] OpenAI GPT-4.5 call failed: {e}")
        return None


def cloud_reply(message: str) -> str | None:
    """Try GPT-4.5 first, then Claude as fallback. Returns None if none configured/all fail."""
    if not CLOUD_ENABLED:
        return None
    # GPT-4.5 is now primary; Claude is fallback
    return _openai_call(message) or _anthropic_call(message)


if __name__ == "__main__":
    print(f"Anthropic: {'✓' if ANTHROPIC_KEY else '✗'}")
    print(f"OpenAI: {'✓' if OPENAI_KEY else '✗'}")
    if CLOUD_ENABLED:
        print("\nTest reply:", cloud_reply("Say hi in 5 words"))
    else:
        print("\nNo cloud LLM configured. Set ANTHROPIC_API_KEY or OPENAI_API_KEY.")
