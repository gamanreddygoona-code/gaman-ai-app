"""
fast_facts.py
──────────────
Instant answers for common factual questions.
No web search needed — answers cached locally.
Auto-updates from web research when needed.
"""

import json
import time
from datetime import datetime, timedelta

# Cached facts (instant replies, no search needed)
FAST_FACTS = {
    "richest man in world": {
        "answer": "**Elon Musk** is currently the world's richest person with a net worth of ~$250+ billion (as of 2024-2025), primarily from Tesla and SpaceX ownership.",
        "details": "His wealth fluctuates with Tesla stock. Other top billionaires: Bernard Arnault (LVMH), Jeff Bezos (Amazon), Larry Ellison (Oracle).",
        "confidence": 0.9,
        "updated": "2025-04-20",
    },
    "who is the richest": {
        "answer": "**Elon Musk** (~$250B) — followed by Bernard Arnault, Jeff Bezos, Larry Ellison.",
        "confidence": 0.9,
    },
    "elon musk net worth": {
        "answer": "~$250+ billion (as of 2024-2025), primarily from Tesla (electric vehicles) and SpaceX (rockets/Starlink).",
        "confidence": 0.85,
    },
    "python list": {
        "answer": "Ordered, mutable collection. Create: `[1,2,3]`. Access: `lst[0]`. Add: `lst.append(4)`. Remove: `lst.pop()`. O(1) indexing, O(n) search.",
        "confidence": 1.0,
    },
    "python dict": {
        "answer": "Key-value hash map. Create: `{'a':1}`. Access: `d['a']`. Add: `d['b']=2`. O(1) lookup. Use for mapping, caching.",
        "confidence": 1.0,
    },
}

QUERY_CACHE = {}  # {query: (answer, timestamp)}
CACHE_TTL_SECONDS = 86400  # 24 hours


def _normalize_query(q: str) -> str:
    """Normalize query for matching."""
    return q.lower().strip()


def get_fast_answer(query: str) -> dict | None:
    """
    Get instant answer from cache.
    Returns: {"answer": str, "source": "fast_facts", "confidence": float}
    or None if not found.
    """
    norm_q = _normalize_query(query)

    # Check runtime cache first
    if norm_q in QUERY_CACHE:
        ans, ts = QUERY_CACHE[norm_q]
        if time.time() - ts < CACHE_TTL_SECONDS:
            return {
                "answer": ans,
                "source": "cached",
                "confidence": 0.95,
            }

    # Check built-in facts
    for key, fact in FAST_FACTS.items():
        if key in norm_q or norm_q in key or _similarity(norm_q, key) > 0.7:
            answer = fact.get("answer", "")
            if answer:
                # Cache it
                QUERY_CACHE[norm_q] = (answer, time.time())
                return {
                    "answer": answer,
                    "details": fact.get("details", ""),
                    "source": "fast_facts",
                    "confidence": fact.get("confidence", 0.85),
                }

    return None


def _similarity(a: str, b: str) -> float:
    """Simple word overlap similarity."""
    a_words = set(a.split())
    b_words = set(b.split())
    if not a_words or not b_words:
        return 0.0
    overlap = len(a_words & b_words)
    union = len(a_words | b_words)
    return overlap / union if union else 0.0


def add_fact(query: str, answer: str, confidence: float = 0.9):
    """Learn a new fact from web research."""
    norm_q = _normalize_query(query)
    FAST_FACTS[norm_q] = {
        "answer": answer,
        "confidence": confidence,
        "updated": datetime.now().strftime("%Y-%m-%d"),
    }
    QUERY_CACHE[norm_q] = (answer, time.time())


if __name__ == "__main__":
    tests = [
        "who is richest man in world",
        "elon musk net worth",
        "python list",
        "what is dict",
    ]
    for q in tests:
        ans = get_fast_answer(q)
        if ans:
            print(f"Q: {q}")
            print(f"A: {ans['answer']}\n")
