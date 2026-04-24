"""
fast_research.py
────────────────
Ultra-fast web research using DuckDuckGo API (no key needed).
Returns answers in <2 seconds, not seconds waiting for Google.

Used for: "who is richest man", "what is X", factual questions.
"""

import requests
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

TIMEOUT = 3  # seconds
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}


def search_duckduckgo(query: str) -> list[dict]:
    """
    Search using DuckDuckGo Instant Answer API (no key needed, instant).
    Returns: [{"title": str, "content": str, "url": str}, ...]
    """
    try:
        # DuckDuckGo API
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_redirect": 1,
        }
        r = requests.get(url, params=params, timeout=TIMEOUT, headers=HEADERS)
        data = r.json()

        results = []

        # Instant answer
        if data.get("AbstractText"):
            results.append({
                "title": data.get("Heading", "Answer"),
                "content": data.get("AbstractText"),
                "url": data.get("AbstractURL", ""),
                "score": 1.0,
            })

        # Related topics
        for topic in data.get("RelatedTopics", [])[:3]:
            if isinstance(topic, dict) and "Text" in topic:
                results.append({
                    "title": topic.get("FirstURL", "").split("/")[-1] or "Related",
                    "content": topic.get("Text"),
                    "url": topic.get("FirstURL", ""),
                    "score": 0.8,
                })

        return results[:3]  # Top 3 results

    except Exception as e:
        print(f"[fast_research] DuckDuckGo error: {e}")
        return []


def search_wikipedia(query: str) -> dict | None:
    """Quick Wikipedia search for definitions."""
    try:
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
        }
        r = requests.get(url, params=params, timeout=TIMEOUT, headers=HEADERS)
        data = r.json()

        results = data.get("query", {}).get("search", [])
        if results:
            first = results[0]
            return {
                "title": first["title"],
                "content": first["snippet"][:300],
                "url": f"https://en.wikipedia.org/wiki/{first['title'].replace(' ', '_')}",
                "score": 0.95,
            }
    except Exception as e:
        print(f"[fast_research] Wikipedia error: {e}")
    return None


def do_fast_research(query: str, timeout: float = 5.0) -> dict:
    """
    Fast parallel research — returns answer in <2 seconds.

    Returns:
        {
            "status": "success" | "timeout" | "error",
            "query": str,
            "answer": str,           # synthesized answer
            "sources": list,         # [{"title", "url", "content"}, ...]
        }
    """
    start = time.time()

    # Parallel search (Wikipedia + DuckDuckGo simultaneously)
    results = []

    with ThreadPoolExecutor(max_workers=2) as ex:
        wiki_future = ex.submit(search_wikipedia, query)
        ddg_future = ex.submit(search_duckduckgo, query)

        try:
            wiki_result = wiki_future.result(timeout=timeout)
            if wiki_result:
                results.append(wiki_result)
        except:
            pass

        try:
            ddg_results = ddg_future.result(timeout=timeout)
            results.extend(ddg_results)
        except:
            pass

    elapsed = time.time() - start

    if not results:
        return {
            "status": "no_results",
            "query": query,
            "answer": f"Could not find information about: {query}",
            "sources": [],
            "elapsed": elapsed,
        }

    # Synthesize answer from top result
    top = results[0]
    answer = f"{top['title']}\n\n{top['content']}"

    return {
        "status": "success",
        "query": query,
        "answer": answer,
        "source": top.get("title", "Web"),
        "url": top.get("url", ""),
        "sources": results,
        "elapsed": round(elapsed, 2),
    }


if __name__ == "__main__":
    tests = [
        "who is richest man in world",
        "what is python",
        "elon musk net worth",
    ]

    for q in tests:
        print(f"\nSearching: {q}")
        result = do_fast_research(q)
        print(f"Status: {result['status']} ({result['elapsed']}s)")
        print(f"Answer: {result['answer'][:200]}...")
