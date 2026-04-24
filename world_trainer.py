"""
world_trainer.py
────────────────
The 'Big Brain' autonomous learner. 
It picks topics, searches the real web, scrapes deep content, 
and trains the local AI knowledge base.

It implements 'Everything in the World' learning by:
1. Identifying knowledge gaps.
2. Scraping high-credibility sources (Wikipedia, MDN, Dev.to).
3. Extracting and structuring data for the AI.
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import random
import json
import re
from datetime import datetime

DB_PATH = "ai_data.db"

class WorldTrainer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        })
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS autonomous_learning (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT UNIQUE,
                status TEXT DEFAULT 'pending',
                source_count INTEGER DEFAULT 0,
                last_updated TEXT,
                quality_score REAL
            )
        """)
        # Ensure deep_research tables exist
        conn.execute("""
            CREATE TABLE IF NOT EXISTS learned_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT,
                content TEXT,
                source TEXT,
                confidence REAL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.commit()
        conn.close()

    def get_search_links(self, query):
        """Scrape DuckDuckGo Lite for real links using robust regex."""
        print(f"🌐 Searching the web for: {query}")
        # Use DDG Lite - faster and simpler HTML
        url = f"https://duckduckgo.com/lite/?q={query}"
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            
            # Simple but robust: find all 'a' tags with class 'result-link' or just links that aren't DDG internal
            soup = BeautifulSoup(resp.text, 'html.parser')
            links = []
            
            # DDG Lite uses 'a' tags with class 'result-link'
            for a in soup.find_all('a', href=True):
                href = a['href']
                # Filter out internal links and ads
                if 'http' in href and not any(x in href for x in ['duckduckgo.com', 'google.com/search', 'yandex.com']):
                    title = a.get_text(strip=True)
                    if len(title) > 5:
                        links.append({'title': title, 'url': href})
            
            print(f"🔎 Found {len(links)} potential links.")
            return links
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []

    def scrape_deep(self, url):
        """Extract high-quality text and code from a page."""
        try:
            print(f"📄 Reading source: {url}")
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Remove noise
            for s in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                s.decompose()
            
            # Extract main text
            paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'li'])
            content = "\n".join([p.get_text().strip() for p in paragraphs if len(p.get_text()) > 20])
            
            # Extract code
            code_blocks = []
            for pre in soup.find_all(['pre', 'code']):
                code = pre.get_text().strip()
                if len(code) > 20:
                    code_blocks.append(code)
            
            return {
                'text': content[:5000], # Cap at 5k chars per source
                'code': code_blocks[:5],
                'title': soup.title.string if soup.title else "Unknown Topic"
            }
        except Exception as e:
            print(f"⚠️ Scrape error for {url}: {e}")
            return None

    def get_wikipedia_content(self, query):
        """Search and scrape Wikipedia directly."""
        print(f"📖 Searching Wikipedia for: {query}")
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&format=json"
        try:
            resp = self.session.get(search_url, timeout=10)
            data = resp.json()
            if data['query']['search']:
                page_title = data['query']['search'][0]['title']
                print(f"✅ Found Wikipedia page: {page_title}")
                
                # Fetch page content
                content_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_title.replace(' ', '_')}"
                c_resp = self.session.get(content_url, timeout=10)
                c_data = c_resp.json()
                
                return {
                    'text': c_data.get('extract', ''),
                    'title': page_title,
                    'url': f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
                }
        except Exception as e:
            print(f"❌ Wikipedia search failed: {e}")
        return None

    def train_topic(self, topic):
        """The full autonomous learning loop for a single topic."""
        print(f"\n🧠 STARTING AUTONOMOUS TRAINING ON: {topic}")
        
        # Try Wikipedia first for high-quality general knowledge
        wiki_data = self.get_wikipedia_content(topic)
        if wiki_data and len(wiki_data['text']) > 100:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("""
                INSERT INTO learned_knowledge (topic, content, source, confidence)
                VALUES (?, ?, ?, ?)
            """, (topic, wiki_data['text'], wiki_data['url'], 0.99))
            conn.commit()
            conn.close()
            print(f"✅ Mastered via Wikipedia: {wiki_data['title']}")
            return True

        links = self.get_search_links(topic)
        if not links:
            return False
            
        conn = sqlite3.connect(DB_PATH)
        learned_count = 0
        
        # Learn from top 3 reliable sources
        for link in links[:3]:
            data = self.scrape_deep(link['url'])
            if not data or len(data['text']) < 200:
                continue
                
            # Clean text for the AI
            clean_text = re.sub(r'\n+', '\n', data['text'])
            
            # Save as learned knowledge
            conn.execute("""
                INSERT INTO learned_knowledge (topic, content, source, confidence)
                VALUES (?, ?, ?, ?)
            """, (topic, clean_text, link['url'], 0.95))
            
            # If code exists, save it as a separate fact
            for i, code in enumerate(data['code']):
                conn.execute("""
                    INSERT INTO learned_knowledge (topic, content, source, confidence)
                    VALUES (?, ?, ?, ?)
                """, (f"{topic} code example {i+1}", f"```\n{code}\n```", link['url'], 0.90))
                
            learned_count += 1
            print(f"✅ Ingested {len(clean_text)} chars from {link['title']}")
            time.sleep(1) # Be polite to servers

        # Mark as completed
        conn.execute("""
            INSERT OR REPLACE INTO autonomous_learning (topic, status, source_count, last_updated)
            VALUES (?, ?, ?, ?)
        """, (topic, 'completed', learned_count, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        return True

    def get_stats(self):
        conn = sqlite3.connect(DB_PATH)
        stats = conn.execute("SELECT COUNT(*) FROM learned_knowledge WHERE source LIKE 'http%'").fetchone()[0]
        topics = conn.execute("SELECT topic FROM autonomous_learning WHERE status='completed' ORDER BY last_updated DESC LIMIT 10").fetchall()
        conn.close()
        return {
            'total_web_facts': stats,
            'recent_topics': [t[0] for t in topics]
        }

if __name__ == "__main__":
    trainer = WorldTrainer()
    # Test on a complex topic
    trainer.train_topic("Quantum Computing Basics")
    print(trainer.get_stats())
