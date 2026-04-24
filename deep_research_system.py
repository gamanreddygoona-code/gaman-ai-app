"""
deep_research_system.py
──────────────────────
Real deep research from Google and online platforms.
Learns from tutorials, documentation, Stack Overflow, etc.
Saves all learned knowledge to database for future use.

Features:
- Google search for current information
- Web scraping from tutorials
- Save learning to database
- Retrieve saved knowledge for similar queries
- Track source of information
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import json
import re
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

DB_PATH = "ai_data.db"
TIMEOUT = 5  # seconds — fast timeout


class DeepResearchSystem:
    """Fast web research with parallel requests."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.session.timeout = TIMEOUT
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()
        self.executor = ThreadPoolExecutor(max_workers=3)  # Parallel requests

    def _create_tables(self):
        """Create tables for storing research data."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS web_research (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                source_url TEXT,
                source_title TEXT,
                content TEXT,
                content_summary TEXT,
                source_type TEXT,
                learned_at TEXT DEFAULT CURRENT_TIMESTAMP,
                confidence REAL DEFAULT 0.8,
                UNIQUE(query, source_url)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_url TEXT UNIQUE,
                source_name TEXT,
                source_type TEXT,
                last_crawled TEXT,
                credibility_score REAL DEFAULT 0.8
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_from_web (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                key_points TEXT,
                code_examples TEXT,
                resources TEXT,
                learned_from TEXT,
                learned_at TEXT DEFAULT CURRENT_TIMESTAMP,
                confidence REAL DEFAULT 0.85
            )
        """)

        self.conn.commit()

    def google_search(self, query: str, num_results: int = 5) -> list:
        """Search Wikipedia (as a highly reliable proxy for factual internet search)."""
        print(f"\n🔍 Searching Wikipedia for: '{query}'")

        try:
            import urllib.parse
            import re
            
            # Basic keyword extraction: remove common stop words and question markers
            stop_words = ["who", "what", "where", "when", "why", "how", "is", "are", "was", "were", "do", "does", "did", "can", "could", "would", "should", "the", "a", "an", "of", "in", "on", "at", "to", "for", "with", "about", "explain", "tell", "me"]
            words = re.findall(r'\b\w+\b', query.lower())
            keywords = [w for w in words if w not in stop_words]
            search_term = " ".join(keywords) if keywords else query
            
            # Wikipedia API search
            safe_query = urllib.parse.quote(search_term)
            search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={safe_query}&limit={num_results}&namespace=0&format=json"
            response = self.session.get(search_url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                results = []
                if len(data) == 4 and len(data[1]) > 0:
                    titles = data[1]
                    urls = data[3]
                    for i in range(len(titles)):
                        results.append({
                            "title": titles[i],
                            "url": urls[i],
                            "snippet": f"Wikipedia article about {titles[i]}"
                        })
                return results
        except Exception as e:
            print(f"⚠️  Search error: {e}")

        return []

    def scrape_webpage(self, url: str) -> dict:
        """Scrape content from webpage (specifically tuned for Wikipedia or clean articles)."""
        print(f"📄 Scraping: {url}")

        try:
            # If it's wikipedia, use the exact extract API for clean text
            if "wikipedia.org" in url:
                import urllib.parse
                page_title = url.split("/")[-1]
                api_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=true&explaintext=true&titles={page_title}&format=json"
                response = self.session.get(api_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    pages = data.get("query", {}).get("pages", {})
                    for page_id in pages:
                        extract = pages[page_id].get("extract", "")
                        title = pages[page_id].get("title", "Unknown")
                        if extract:
                            return {
                                "url": url,
                                "title": title,
                                "content": extract,
                                "status": "success"
                            }
            
            # Fallback to normal scraping
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()

                text = soup.get_text(separator='\n', strip=True)
                title = soup.find('title')
                title_text = title.get_text(strip=True) if title else "Unknown"

                return {
                    "url": url,
                    "title": title_text,
                    "content": text[:3000],  # Give model more context (3000 chars)
                    "status": "success"
                }
        except Exception as e:
            print(f"⚠️  Scraping error: {e}")

        return {"url": url, "status": "failed", "error": str(e)}

    def extract_code_examples(self, content: str) -> list:
        """Extract code examples from content."""
        code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', content, re.DOTALL)
        return code_blocks

    def summarize_content(self, content: str) -> str:
        """Create summary of content."""
        sentences = content.split('.')
        # Take first 3 sentences as summary
        summary = '.'.join(sentences[:3]) + '.'
        return summary[:500]

    def save_learning(self, query: str, source_url: str, content: dict) -> bool:
        """Save learned information to database."""
        try:
            summary = self.summarize_content(content.get('content', ''))

            self.cursor.execute("""
                INSERT OR REPLACE INTO web_research
                (query, source_url, source_title, content, content_summary, source_type, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                query,
                source_url,
                content.get('title', 'Unknown'),
                content.get('content', ''),
                summary,
                'web_scraped',
                0.85
            ))

            # Also save as topic knowledge
            code_examples = self.extract_code_examples(content.get('content', ''))
            self.cursor.execute("""
                INSERT INTO knowledge_from_web
                (topic, key_points, code_examples, resources, learned_from, confidence)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                query,
                summary,
                json.dumps(code_examples),
                source_url,
                source_url,
                0.85
            ))

            self.conn.commit()
            print(f"✅ Saved learning: {query}")
            return True
        except Exception as e:
            print(f"⚠️  Save error: {e}")
            return False

    def get_saved_learning(self, query: str) -> dict:
        """Retrieve previously learned information."""
        try:
            self.cursor.execute("""
                SELECT content_summary, source_url, source_title, learned_at
                FROM web_research
                WHERE query LIKE ?
                ORDER BY learned_at DESC
                LIMIT 1
            """, (f"%{query}%",))

            result = self.cursor.fetchone()
            if result:
                return {
                    "summary": result[0],
                    "source_url": result[1],
                    "source_title": result[2],
                    "learned_at": result[3],
                    "found": True
                }
        except Exception as e:
            print(f"⚠️  Retrieval error: {e}")

        return {"found": False}

    def deep_research(self, query: str) -> dict:
        """Perform deep research: search, scrape, save."""
        print(f"\n" + "="*70)
        print(f"🧠 DEEP RESEARCH: {query}")
        print("="*70)

        # 1. Check if already learned
        saved = self.get_saved_learning(query)
        if saved['found']:
            print(f"\n✅ Found in memory (learned {saved['learned_at']})")
            return {
                "status": "found_in_memory",
                "query": query,
                "content": saved['summary'],
                "source": saved['source_title'],
                "source_url": saved['source_url']
            }

        # 2. Search Google
        search_results = self.google_search(query, num_results=3)
        if not search_results:
            return {
                "status": "no_results",
                "query": query,
                "message": "Could not find information online"
            }

        # 3. Scrape and save first result
        best_result = None
        for result in search_results:
            print(f"\n📍 Processing: {result['title']}")
            scraped = self.scrape_webpage(result['url'])

            if scraped['status'] == 'success':
                # Save to database
                self.save_learning(query, scraped['url'], scraped)
                best_result = scraped
                break

        if best_result:
            return {
                "status": "success",
                "query": query,
                "content": best_result['content'][:1000],
                "source": best_result['title'],
                "source_url": best_result['url'],
                "message": f"✅ Learned from web and saved to memory!",
                "saved": True
            }

        return {
            "status": "failed",
            "query": query,
            "message": "Could not extract information from sources"
        }

    def get_learning_stats(self) -> dict:
        """Get statistics about learned information."""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM web_research")
            research_count = self.cursor.fetchone()[0]

            self.cursor.execute("SELECT COUNT(*) FROM knowledge_from_web")
            knowledge_count = self.cursor.fetchone()[0]

            self.cursor.execute("SELECT DISTINCT query FROM web_research")
            unique_topics = len(self.cursor.fetchall())

            return {
                "web_research_entries": research_count,
                "knowledge_entries": knowledge_count,
                "unique_topics_learned": unique_topics
            }
        except Exception as e:
            return {"error": str(e)}


# Singleton instance
_research_system = None

def get_research_system():
    global _research_system
    if _research_system is None:
        _research_system = DeepResearchSystem()
    return _research_system


if __name__ == "__main__":
    system = DeepResearchSystem()

    print("\n🔬 DEEP RESEARCH SYSTEM TEST\n")

    # Test research
    result = system.deep_research("how to learn python programming")
    print(f"\n📊 Result: {result['status']}")
    if result['status'] == 'success':
        print(f"Source: {result['source']}")
        print(f"Content: {result['content'][:200]}...")
    elif result['status'] == 'found_in_memory':
        print(f"Previously learned from: {result['source']}")

    # Stats
    print("\n" + "="*70)
    print("📈 LEARNING STATISTICS")
    print("="*70)
    stats = system.get_learning_stats()
    print(f"Web research entries: {stats.get('web_research_entries', 0)}")
    print(f"Knowledge entries: {stats.get('knowledge_entries', 0)}")
    print(f"Unique topics learned: {stats.get('unique_topics_learned', 0)}")
