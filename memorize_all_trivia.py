"""
memorize_all_trivia.py
──────────────────────
This script gives Gaman AI the physical storage capacity to memorize 
random trivia facts in existence! It fetches hundreds of random facts 
from public trivia APIs and permanently burns them into the local ai_data.db.
"""

import requests
import sqlite3
import time

DB_PATH = "ai_data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
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

def memorize_trivia(batch_size=5):
    """Fetches trivia from Open Trivia DB and saves to the local database."""
    print("🧠 Initiating Massive Trivia Memorization Protocol...")
    init_db()
    conn = sqlite3.connect(DB_PATH)
    
    total_memorized = 0
    
    try:
        for i in range(batch_size):
            # Fetch 50 trivia questions at a time
            print(f"📡 Downloading trivia chunk {i+1}/{batch_size}...")
            url = "https://opentdb.com/api.php?amount=50&type=multiple"
            resp = requests.get(url, timeout=10)
            
            if resp.status_code == 429:
                print("⏳ Rate limited. Waiting...")
                time.sleep(5)
                continue
                
            data = resp.json()
            if data.get("response_code") == 0:
                results = data.get("results", [])
                
                for item in results:
                    question = item['question']
                    answer = item['correct_answer']
                    category = item['category']
                    
                    # Clean up HTML entities common in this API
                    import html
                    question = html.unescape(question)
                    answer = html.unescape(answer)
                    
                    content = f"Q: {question}\nA: {answer}"
                    topic = f"Trivia: {category}"
                    
                    conn.execute("""
                        INSERT INTO learned_knowledge (topic, content, source, confidence)
                        VALUES (?, ?, ?, ?)
                    """, (topic, content, "opentdb_trivia", 0.99))
                    total_memorized += 1
            
            # Be polite to the API
            time.sleep(2)
            
        conn.commit()
        print(f"\n✅ SUCCESS: Successfully burned {total_memorized} random trivia facts into physical storage (ai_data.db)!")
        
    except Exception as e:
        print(f"\n❌ Error during memorization: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # Run 4 batches of 50 = 200 trivia facts immediately
    memorize_trivia(batch_size=4)
