"""
real_cloud_llm.py
─────────────────
REAL Cloud LLM integration — GPT-4o (primary) + Claude Opus (fallback).
Both models significantly outperform GPT-3.5 in reasoning, coding, and knowledge.

Set environment variables to enable:
  OPENAI_API_KEY=sk-...        ← GPT-4o (primary)   [beats GPT-3.5 by far]
  ANTHROPIC_API_KEY=sk-ant-... ← Claude Opus 4      (fallback)

Get OpenAI key at:    https://platform.openai.com/api-keys
Get Anthropic key at: https://console.anthropic.com
"""

import os
import json
import sqlite3
import urllib.request
import urllib.error

try:
    from anthropic import Anthropic, APIError as AnthropicAPIError
    _anthropic_available = True
except ImportError:
    _anthropic_available = False

# ── API Keys ──────────────────────────────────────────────────
OPENAI_KEY    = os.getenv("OPENAI_API_KEY")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
REAL_CLOUD_ENABLED = bool(OPENAI_KEY or ANTHROPIC_KEY)

# ── Initialize Anthropic client (fallback) ────────────────────
anthropic_client = None
if ANTHROPIC_KEY and _anthropic_available:
    try:
        anthropic_client = Anthropic(api_key=ANTHROPIC_KEY)
        print("[cloud_llm] ✅ Anthropic Claude API enabled (fallback)")
    except Exception as e:
        print(f"[cloud_llm] ⚠️  Error initializing Anthropic: {e}")

if OPENAI_KEY:
    print("[cloud_llm] ✅ OpenAI GPT-4o API enabled (primary — beats GPT-3.5)")

if not REAL_CLOUD_ENABLED:
    print("[cloud_llm] ⚠️  No cloud API keys set. Using local fallback.")


def get_few_shot_examples() -> str:
    """Fetch high-quality examples from database to use as few-shot learning."""
    try:
        conn = sqlite3.connect("./ai_data.db", check_same_thread=False)
        cursor = conn.cursor()

        # Get top-rated responses
        cursor.execute("""
            SELECT user_message, bot_response, AVG(rating) as avg_rating
            FROM response_feedback
            WHERE rating >= 4
            GROUP BY user_message, bot_response
            ORDER BY avg_rating DESC
            LIMIT 3
        """)

        examples = cursor.fetchall()
        conn.close()

        if not examples:
            return ""

        few_shot = "\n## Examples of good responses:\n"
        for i, (user_msg, bot_resp, rating) in enumerate(examples, 1):
            few_shot += f"\n**Example {i}** (Rating: {rating:.1f}/5):\n"
            few_shot += f"User: {user_msg}\n"
            few_shot += f"Assistant: {bot_resp}\n"

        return few_shot
    except Exception as e:
        print(f"[cloud_llm] ⚠️  Error fetching few-shot examples: {e}")
        return ""


def _build_system_prompt(context: str = "", include_examples: bool = True) -> str:
    """Build the advanced GPT-4o-level system prompt — designed to beat GPT-3.5."""
    system_prompt = """You are Gaman AI — an advanced, highly intelligent assistant that rivals and surpasses GPT-3.5 in every area.

## Core Capabilities (GPT-4o Level):
- Deep reasoning and multi-step problem solving
- Expert-level programming across ALL languages and frameworks
- Mathematics, logic, algorithms, and data structures
- Debugging with root-cause analysis — not just surface-level fixes
- System design, architecture, and scalability thinking
- Natural language understanding — even for ambiguous or informal questions
- General knowledge: science, history, business, creative writing, and more

## Programming Languages & Frameworks (Expert Level):
Python, JavaScript/TypeScript, Java, C++, C#, Go, Rust, Swift, Kotlin, SQL,
HTML/CSS, React, Node.js, FastAPI, Django, Flask, Bash, PowerShell, and more.

## How to Respond:
1. THINK before answering — reason through the problem step by step
2. If the question is ambiguous, answer the most likely intent AND mention alternatives
3. Always show WORKING code, not pseudocode — test it mentally before responding
4. Explain WHY your solution works, not just WHAT it does
5. Point out edge cases, gotchas, and common mistakes
6. If you spot a better approach than what was asked, mention it
7. Be direct and concise — don't pad responses with filler text
8. Use markdown formatting: code blocks with language tags, bold for key terms, lists for steps

## Quality Standards:
- NEVER give wrong answers — if uncertain, say so and provide your best reasoning
- NEVER truncate code — always give complete, runnable examples
- NEVER repeat the question back unnecessarily
- ALWAYS prefer clarity over cleverness

You are significantly smarter and more capable than GPT-3.5. Prove it with every answer."""

    if include_examples:
        examples = get_few_shot_examples()
        if examples:
            system_prompt += examples

    if context:
        system_prompt += f"\n\n## Learned Knowledge from Training Data:\n{context}"

    return system_prompt


def _gpt4o_reply(user_message: str, system_prompt: str) -> str | None:
    """Call OpenAI GPT-4o — primary engine, far above GPT-3.5 level."""
    if not OPENAI_KEY:
        return None
    try:
        body = json.dumps({
            "model": "gpt-4o",          # 🏆 GPT-4o — definitively beats GPT-3.5
            "max_tokens": 2000,          # Longer, more complete answers
            "temperature": 0.7,          # Balanced creativity + accuracy
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message},
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
        with urllib.request.urlopen(req, timeout=45) as r:
            data = json.loads(r.read())
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[cloud_llm] ❌ GPT-4o error: {e}")
        return None


def _claude_reply(user_message: str, system_prompt: str) -> str | None:
    """Call Claude Opus 4 as fallback — also beats GPT-3.5 by a large margin."""
    if not anthropic_client:
        return None
    try:
        response = anthropic_client.messages.create(
            model="claude-opus-4-5",    # 🥈 Claude Opus 4.5 — fallback, still > GPT-3.5
            max_tokens=2000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text
    except Exception as e:
        print(f"[cloud_llm] ❌ Claude Opus error: {e}")
        return None


def real_cloud_reply(user_message: str, context: str = "", include_examples: bool = True) -> str | None:
    """
    Get a REAL reply: GPT-4o first, Claude Opus 4 as fallback.
    Both models far exceed GPT-3.5 capabilities.
    """
    if not REAL_CLOUD_ENABLED:
        return None

    system_prompt = _build_system_prompt(context, include_examples)

    # 🏆 Primary: GPT-4o (beats GPT-3.5 on every benchmark)
    reply = _gpt4o_reply(user_message, system_prompt)
    if reply:
        return reply

    # 🥈 Fallback: Claude Opus 4 (also beats GPT-3.5)
    return _claude_reply(user_message, system_prompt)


def test_cloud_llm():
    """Test the real cloud LLM."""
    if not REAL_CLOUD_ENABLED:
        print("❌ Anthropic API not configured. Set ANTHROPIC_API_KEY env var.")
        return

    print("\n🌐 Testing Real Cloud LLM (Claude API)\n")

    test_queries = [
        "write a hello world in python",
        "what is a function",
        "how to read a file in javascript",
    ]

    for query in test_queries:
        print(f"❓ Query: {query}")
        reply = real_cloud_reply(query)
        if reply:
            print(f"✅ Reply: {reply[:150]}...\n")
        else:
            print("❌ No reply\n")


if __name__ == "__main__":
    test_cloud_llm()
