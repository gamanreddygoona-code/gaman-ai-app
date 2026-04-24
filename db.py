"""
db.py
─────
Handles all SQLite database operations:
  - chat_history  : stores every user message and bot reply
  - knowledge     : stores context facts the AI can reference
  - training_data : already exists (your AI training rows)
"""

import sqlite3
import os

DB_PATH = "./ai_data.db"
SHARDS = [f"./shard_worker_{i}.db" for i in range(10)]


def get_connection() -> sqlite3.Connection:
    """Returns a new SQLite connection."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row   # lets us access columns by name
    return conn


def init_db():
    """
    Creates required tables if they don't already exist.
    Safe to call every startup — will never overwrite existing data.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Chat history — every conversation turn
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message  TEXT    NOT NULL,
            bot_response  TEXT    NOT NULL,
            created_at    TEXT    DEFAULT (datetime('now'))
        )
    """)

    # Knowledge base — context facts injected into prompts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            topic     TEXT    NOT NULL,
            content   TEXT    NOT NULL,
            added_at  TEXT    DEFAULT (datetime('now'))
        )
    """)

    # Seed with a few starter knowledge entries (only if table is empty)
    cursor.execute("SELECT COUNT(*) FROM knowledge")
    if cursor.fetchone()[0] == 0:
        starter_knowledge = [
            ("identity",  "You are a helpful coding assistant powered by a fine-tuned CodeLlama model."),
            ("style",     "Always reply with clean, well-commented code. Prefer Python unless another language is asked for."),
            ("database",  "The local SQLite database (ai_data.db) stores training_data, chat_history, and knowledge tables."),
        ]
        cursor.executemany(
            "INSERT INTO knowledge (topic, content) VALUES (?, ?)",
            starter_knowledge
        )

    conn.commit()
    conn.close()
    print("[db] ✅ Database initialised.")


def save_chat(user_message: str, bot_response: str):
    """Saves one conversation turn to chat_history."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO chat_history (user_message, bot_response) VALUES (?, ?)",
        (user_message, bot_response),
    )
    conn.commit()
    conn.close()


def get_chat_history(limit: int = 20) -> list[dict]:
    """Returns the most recent `limit` conversation turns (oldest first).
    Default limit is 20 to maintain full context."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT user_message, bot_response FROM chat_history ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    # Reverse so oldest is first (natural conversation order)
    return [{"user": r["user_message"], "bot": r["bot_response"]} for r in reversed(rows)]


def get_extended_chat_history(limit: int = 50) -> list[dict]:
    """Returns extended conversation history for semantic analysis (oldest first)."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT user_message, bot_response FROM chat_history ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [{"user": r["user_message"], "bot": r["bot_response"]} for r in reversed(rows)]


def get_chat_history_count() -> int:
    """Returns the total number of conversation turns saved in history."""
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM chat_history").fetchone()[0]
    conn.close()
    return count


def get_knowledge_context(max_entries: int = 5) -> str:
    """
    Returns the newest knowledge entries joined into a single context string
    that can be prepended to the model prompt.
    """
    conn = get_connection()
    rows = conn.execute(
        "SELECT topic, content FROM knowledge ORDER BY id DESC LIMIT ?",
        (max_entries,),
    ).fetchall()
    conn.close()

    if not rows:
        return ""

    lines = ["### System Knowledge:"]
    for r in reversed(rows):
        lines.append(f"- [{r['topic']}] {r['content']}")
    return "\n".join(lines)


def add_knowledge(topic: str, content: str):
    """Inserts a new entry into the knowledge base."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO knowledge (topic, content) VALUES (?, ?)",
        (topic, content),
    )
    conn.commit()
    conn.close()


def add_or_update_knowledge(topic: str, content: str):
    """Updates a topic if it already exists, otherwise inserts a new one."""
    conn = get_connection()
    existing = conn.execute(
        "SELECT id FROM knowledge WHERE topic = ? ORDER BY id DESC LIMIT 1",
        (topic,),
    ).fetchone()

    if existing:
        conn.execute(
            "UPDATE knowledge SET content = ?, added_at = datetime('now') WHERE id = ?",
            (content, existing["id"]),
        )
    else:
        conn.execute(
            "INSERT INTO knowledge (topic, content) VALUES (?, ?)",
            (topic, content),
        )

    conn.commit()
    conn.close()


def search_massive_shards(query: str, limit_per_shard: int = 2) -> list[dict]:
    """
    Searches across all 100M examples in the 5 sharded databases (PARALLELIZED).
    Uses keyword matching for high-speed CPU performance.
    """
    from concurrent.futures import ThreadPoolExecutor
    
    results = []
    keywords = [w.lower() for w in query.split() if len(w) > 3]
    if not keywords:
        return []

    like_clause = " OR ".join([f"user_message LIKE ?" for _ in keywords])
    params = [f"%{k}%" for k in keywords]

    def search_shard(shard_path):
        shard_results = []
        if not os.path.exists(shard_path):
            return shard_results
        try:
            conn = sqlite3.connect(shard_path)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                f"SELECT user_message, bot_response FROM massive_training WHERE {like_clause} LIMIT ?",
                params + [limit_per_shard]
            ).fetchall()
            for r in rows:
                shard_results.append({"user": r["user_message"], "bot": r["bot_response"]})
            conn.close()
        except Exception as e:
            print(f"[db] Shard error ({shard_path}): {e}")
        return shard_results

    with ThreadPoolExecutor(max_workers=len(SHARDS)) as executor:
        futures = [executor.submit(search_shard, path) for path in SHARDS]
        for f in futures:
            results.extend(f.result())
            
    return results
