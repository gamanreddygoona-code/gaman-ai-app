"""
wiki_sections_fetcher.py
─────────────────────────
Extract MULTIPLE facts from each Wikipedia article by fetching
individual sections. One article → 5-20 facts.
Target: 50,000+ facts from 3,000 curated articles.
"""

from mega_knowledge import get_knowledge
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

HEADERS = {"User-Agent": "Gaman-AI-KnowledgeBot/2.0 (educational; local use)"}

# Curated list of articles to extract sections from (diverse, high-value)
HIGH_VALUE_ARTICLES = [
    # Programming Languages
    "Python (programming language)", "JavaScript", "TypeScript", "Java (programming language)",
    "C++ (programming language)", "C (programming language)", "Go (programming language)",
    "Rust (programming language)", "Swift (programming language)", "Kotlin (programming language)",
    "Ruby (programming language)", "PHP", "Scala (programming language)", "Haskell (programming language)",
    "Elixir (programming language)", "R (programming language)", "Julia (programming language)",

    # Web Frameworks
    "React (JavaScript library)", "Vue.js", "Angular (web framework)", "Django (web framework)",
    "Flask (web framework)", "FastAPI", "Spring Framework", "Express.js", "Next.js",
    "Ruby on Rails", "Laravel", "ASP.NET Core",

    # Databases
    "PostgreSQL", "MySQL", "MongoDB", "Redis (software)", "Cassandra (database)",
    "SQLite", "Elasticsearch", "DynamoDB", "Neo4j", "InfluxDB",

    # CS Fundamentals
    "Algorithm", "Data structure", "Sorting algorithm", "Searching algorithm",
    "Tree (data structure)", "Graph (discrete mathematics)", "Hash table",
    "Dynamic programming", "Greedy algorithm", "Divide-and-conquer algorithm",
    "Binary search algorithm", "Merge sort", "Quicksort", "Heapsort",
    "Breadth-first search", "Depth-first search", "Dijkstra's algorithm",

    # Machine Learning
    "Machine learning", "Deep learning", "Neural network", "Convolutional neural network",
    "Recurrent neural network", "Long short-term memory", "Transformer (machine learning model)",
    "Generative adversarial network", "Reinforcement learning", "Natural language processing",
    "Support vector machine", "Decision tree", "Random forest", "K-means clustering",
    "Principal component analysis", "Gradient descent", "Backpropagation",

    # Systems
    "Operating system", "Linux", "Process (computing)", "Thread (computing)",
    "Virtual memory", "File system", "Distributed computing", "Concurrent computing",
    "Computer network", "Internet protocol suite", "HTTP", "TCP", "DNS",
    "Cryptography", "Public-key cryptography", "Transport Layer Security",

    # Software Engineering
    "Software engineering", "Design pattern", "SOLID", "Agile software development",
    "Test-driven development", "Continuous integration", "DevOps", "Microservices",
    "Version control", "Git", "Software testing", "Debugging",

    # Mathematics
    "Linear algebra", "Calculus", "Probability theory", "Statistics",
    "Graph theory", "Number theory", "Combinatorics", "Set theory",
    "Matrix (mathematics)", "Eigenvalues and eigenvectors", "Fourier transform",

    # Cloud & DevOps
    "Cloud computing", "Amazon Web Services", "Docker (software)", "Kubernetes",
    "Serverless computing", "Infrastructure as code", "Continuous delivery",

    # AI/Tech Topics
    "Artificial intelligence", "Computer vision", "Speech recognition",
    "Recommendation system", "Blockchain", "Internet of Things",
    "Quantum computing", "Autonomous vehicle",
]


def get_article_sections(title: str) -> list[dict]:
    """Get section titles for a Wikipedia article."""
    try:
        r = requests.get("https://en.wikipedia.org/w/api.php",
            params={"action": "parse", "page": title, "prop": "sections", "format": "json"},
            headers=HEADERS, timeout=5)
        if r.status_code == 200:
            data = r.json()
            return data.get("parse", {}).get("sections", [])
    except Exception:
        pass
    return []


def get_section_text(title: str, section_idx: int) -> str:
    """Get plain text of a specific section."""
    try:
        r = requests.get("https://en.wikipedia.org/w/api.php",
            params={
                "action": "parse", "page": title, "prop": "wikitext",
                "section": section_idx, "format": "json",
            },
            headers=HEADERS, timeout=5)
        if r.status_code == 200:
            data = r.json()
            wikitext = data.get("parse", {}).get("wikitext", {}).get("*", "")
            # Clean up wikitext to plain text
            import re
            text = re.sub(r"\[\[([^\]|]+\|)?([^\]]+)\]\]", r"\2", wikitext)
            text = re.sub(r"\{\{[^}]+\}\}", "", text)
            text = re.sub(r"<[^>]+>", "", text)
            text = re.sub(r"'{2,3}", "", text)
            text = re.sub(r"\s+", " ", text).strip()
            return text[:600] if len(text) > 60 else ""
    except Exception:
        pass
    return ""


def fetch_article_facts(title: str) -> list[tuple[str, str]]:
    """Extract multiple facts from a Wikipedia article via its sections."""
    facts = []

    # First get the summary (already have these, but good as anchor)
    sections = get_article_sections(title)

    # Extract top-N most informative sections
    interesting_sections = [s for s in sections
                           if not any(skip in s["line"].lower()
                                    for skip in ["see also", "references", "external links",
                                                "notes", "bibliography", "further reading"])][:8]

    for section in interesting_sections:
        try:
            text = get_section_text(title, int(section["index"]))
            if text and len(text) > 60:
                facts.append((
                    f"{title} — {section['line']}",
                    text,
                ))
        except Exception:
            pass

    return facts


def run(max_articles=100, max_workers=8):
    kb = get_knowledge()
    start = time.time()
    before = kb.stats()["total_facts"]

    articles = HIGH_VALUE_ARTICLES[:max_articles]
    print(f"📖 Wikipedia Sections Fetcher")
    print(f"   Articles: {len(articles)}")
    print(f"   Expected facts: {len(articles) * 5}–{len(articles) * 8}")
    print(f"   Starting from: {before:,} facts\n")

    added = 0
    total_sections = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_article_facts, title): title
                   for title in articles}

        for i, future in enumerate(as_completed(futures)):
            facts = future.result()
            total_sections += len(facts)
            for topic, content in facts:
                if kb.add_fact(topic=topic, content=content,
                               source="wikipedia_sections", category="encyclopedic_deep",
                               confidence=0.90):
                    added += 1

            if (i + 1) % 20 == 0:
                elapsed = time.time() - start
                print(f"  [{i+1}/{len(articles)}] sections={total_sections}, added={added:,} | {elapsed:.0f}s")

    after = kb.stats()["total_facts"]
    elapsed = time.time() - start
    print(f"\n✅ Sections fetch complete")
    print(f"   Sections extracted: {total_sections}")
    print(f"   Facts added: {added}")
    print(f"   Total: {after:,} | Time: {elapsed:.0f}s")
    return after


if __name__ == "__main__":
    run(max_articles=len(HIGH_VALUE_ARTICLES))
