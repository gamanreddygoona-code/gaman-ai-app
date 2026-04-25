"""
stackoverflow_corpus.py
──────────────────────
Fast Stack Overflow Q&A ingestion into mega_knowledge.
Fetches top-voted answers for programming topics.
"""

import requests
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import time

from mega_knowledge import get_knowledge

# Top programming topics to scrape from Stack Overflow API
SO_TOPICS = [
    "python", "javascript", "java", "c#", "php", "c++", "typescript",
    "go", "rust", "kotlin", "swift", "ruby", "sql", "html",
    "css", "react", "vue.js", "angular", "node.js", "django",
    "flask", "fastapi", "spring-boot", "docker", "kubernetes",
    "git", "github", "machine-learning", "deep-learning", "tensorflow",
    "pytorch", "data-science", "pandas", "numpy", "scikit-learn",
    "api", "rest", "graphql", "mongodb", "postgresql", "mysql",
    "linux", "bash", "git", "regex", "json", "xml",
]

def fetch_so_answers(tag: str, limit: int = 5) -> list:
    """Fetch top answers for a Stack Overflow tag."""
    try:
        url = "https://api.stackexchange.com/2.3/questions"
        params = {
            "order": "desc",
            "sort": "votes",
            "tagged": tag,
            "site": "stackoverflow",
            "pagesize": limit,
            "filter": "!9_bDE(fI5",  # Include body & title
        }
        r = requests.get(url, params=params, timeout=5)
        if r.status_code == 200:
            data = r.json()
            results = []
            for q in data.get("items", [])[:limit]:
                results.append({
                    "title": q.get("title", ""),
                    "body": q.get("body", "")[:500],
                    "score": q.get("score", 0),
                    "link": q.get("link", ""),
                    "tags": q.get("tags", []),
                })
            return results
    except Exception as e:
        print(f"[SO] Failed to fetch {tag}: {e}")
    return []


def ingest_stackoverflow(kb, limit_per_tag: int = 3):
    """Ingest Stack Overflow answers into mega_knowledge."""
    print(f"📥 Ingesting Stack Overflow answers for {len(SO_TOPICS)} tags...")

    count = 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(fetch_so_answers, tag, limit_per_tag): tag
                   for tag in SO_TOPICS}

        for future in futures:
            tag = futures[future]
            try:
                answers = future.result(timeout=10)
                for ans in answers:
                    if ans["title"] and ans["body"]:
                        kb.add_fact(
                            topic=f"StackOverflow: {ans['title'][:80]}",
                            content=ans["body"],
                            source="stackoverflow",
                            category="programming_qa",
                            confidence=0.85 + (min(ans["score"], 100) / 1000),
                        )
                        count += 1
            except Exception as e:
                print(f"[SO] Error processing {tag}: {e}")

            # Rate limit: Stack Exchange asks for 30 requests/sec max
            time.sleep(0.1)

    print(f"✅ Ingested {count} Stack Overflow answers")
    return count


if __name__ == "__main__":
    kb = get_knowledge()
    before = kb.stats()["total_facts"]
    ingest_stackoverflow(kb, limit_per_tag=3)
    after = kb.stats()["total_facts"]
    print(f"\n📊 Knowledge base: {before} → {after} facts")
