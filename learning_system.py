"""
learning_system.py
──────────────────
Makes the chatbot LEARN from conversations and improve over time.

The bot will:
1. Track what questions are asked
2. Learn from user feedback (ratings)
3. Auto-generate new knowledge from patterns
4. Improve responses based on experience

Run: python learning_system.py (optional maintenance script)
Used by: app.py (automatic learning during chat)
"""

import random
import sqlite3
import json
from datetime import datetime
from collections import Counter
import re
import numpy as np

# Semantic embeddings (CPU-only, lightweight model)
try:
    from sentence_transformers import SentenceTransformer
    embedder = SentenceTransformer("all-MiniLM-L6-v2")  # Lightweight, 22MB
    EMBEDDINGS_ENABLED = True
    print("[learning] ✅ Semantic embeddings enabled (sentence-transformers)")
except ImportError:
    EMBEDDINGS_ENABLED = False
    embedder = None
    print("[learning] ⚠️  sentence-transformers not installed. Run: pip install sentence-transformers")

DB_PATH = "./ai_data.db"

# ── In-Memory Caches for Hyper-Fast Replies ──
_KNOWLEDGE_CACHE = None
_EMBEDDING_CACHE = {}  # topic -> embedding
_CACHE_EXPIRY = 300 # 5 minutes
_LAST_CACHE_TIME = 0

def get_connection():
    """Returns a new SQLite connection."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def get_knowledge_cached():
    global _KNOWLEDGE_CACHE, _LAST_CACHE_TIME, _EMBEDDING_CACHE
    now = datetime.now().timestamp()
    if _KNOWLEDGE_CACHE is None or (now - _LAST_CACHE_TIME) > _CACHE_EXPIRY:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT topic, content, confidence FROM learned_knowledge ORDER BY confidence DESC LIMIT 1000").fetchall()
        _KNOWLEDGE_CACHE = [dict(r) for r in rows]
        conn.close()
        _LAST_CACHE_TIME = now
        
        # Pre-cache embeddings for the top knowledge
        if EMBEDDINGS_ENABLED:
            print(f"[learning] 🧠 Warming up embedding cache for {len(_KNOWLEDGE_CACHE)} topics...")
            for row in _KNOWLEDGE_CACHE:
                if row["topic"] not in _EMBEDDING_CACHE:
                    _EMBEDDING_CACHE[row["topic"]] = embedder.encode(row["topic"])
            print("[learning] ✅ Embedding cache ready.")
            
    return _KNOWLEDGE_CACHE
    conn.row_factory = sqlite3.Row
    return conn


def init_learning_tables():
    """Creates tables for learning system if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Track user feedback on responses
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS response_feedback (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message    TEXT    NOT NULL,
            bot_response    TEXT    NOT NULL,
            rating          INTEGER CHECK(rating BETWEEN 1 AND 5),
            feedback_text   TEXT,
            created_at      TEXT    DEFAULT (datetime('now'))
        )
    """)

    # Track learning patterns
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_patterns (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            topic           TEXT    NOT NULL UNIQUE,
            pattern         TEXT    NOT NULL,
            frequency       INTEGER DEFAULT 1,
            last_seen       TEXT    DEFAULT (datetime('now'))
        )
    """)

    # Track auto-generated knowledge from learning
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learned_knowledge (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            topic           TEXT    NOT NULL,
            content         TEXT    NOT NULL,
            source          TEXT,
            confidence      REAL,
            created_at      TEXT    DEFAULT (datetime('now'))
        )
    """)

    # Store semantic embeddings for efficient similarity search
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS response_embeddings (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            response_id     INTEGER NOT NULL,
            embedding       BLOB    NOT NULL,
            text_hash       TEXT    UNIQUE,
            created_at      TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY(response_id) REFERENCES response_feedback(id)
        )
    """)

    conn.commit()
    conn.close()
    print("[learning] ✅ Learning tables initialized")


def save_feedback(user_message: str, bot_response: str, rating: int, feedback_text: str = None):
    """
    Save user feedback on a bot response.
    Rating: 1-5 (1=bad, 5=excellent)
    """
    conn = get_connection()
    conn.execute(
        """INSERT INTO response_feedback
           (user_message, bot_response, rating, feedback_text)
           VALUES (?, ?, ?, ?)""",
        (user_message, bot_response, rating, feedback_text),
    )
    conn.commit()
    conn.close()
    print(f"[learning] 📝 Feedback saved (rating: {rating}/5)")


def get_learning_insights():
    """Analyze chat history to find patterns and suggest new knowledge."""
    conn = get_connection()
    cursor = conn.cursor()

    # Get all user messages from chat history
    cursor.execute("SELECT user_message FROM chat_history ORDER BY created_at DESC LIMIT 100")
    messages = [row[0] for row in cursor.fetchall()]

    # Extract common topics
    topics = extract_topics(messages)

    # Get feedback patterns
    cursor.execute("""
        SELECT AVG(rating) as avg_rating, user_message
        FROM response_feedback
        GROUP BY user_message
        HAVING COUNT(*) > 1
        ORDER BY avg_rating
    """)
    low_rated = cursor.fetchall()

    conn.close()

    return {
        "common_topics": topics,
        "low_rated_questions": low_rated,
        "total_conversations": len(messages),
    }


def extract_topics(messages: list[str]) -> list[tuple[str, int]]:
    """Extract and count programming topics from messages."""
    topic_keywords = {
        "python": r"\bpython\b",
        "javascript": r"\b(javascript|js|node)\b",
        "function": r"\bfunction",
        "loop": r"\bloop",
        "class": r"\bclass",
        "database": r"\b(database|sql|sqlite)\b",
        "api": r"\bapi",
        "error": r"\b(error|debug|fix|bug)\b",
        "list": r"\blist",
        "dictionary": r"\b(dict|dictionary)\b",
        "web": r"\b(web|http|request)\b",
    }

    topic_counts = Counter()

    for message in messages:
        lower_msg = message.lower()
        for topic, pattern in topic_keywords.items():
            if re.search(pattern, lower_msg):
                topic_counts[topic] += 1

    return topic_counts.most_common(10)


def generate_learning_knowledge(topic: str, messages: list[str]) -> str:
    """
    Auto-generate knowledge from frequently asked questions.
    This would be enhanced with ML in production.
    """
    related_messages = [m for m in messages if topic.lower() in m.lower()]

    if len(related_messages) > 3:
        return f"""
LEARNED FROM EXPERIENCE: {topic.title()}
{'─' * 50}

This topic was asked about {len(related_messages)} times by users.

Common questions:
{chr(10).join(f"• {msg[:60]}..." for msg in related_messages[:3])}

KEY INSIGHTS:
→ Users frequently ask about {topic}
→ This suggests students need clearer explanations
→ Focus on step-by-step examples
→ Include real-world use cases
→ Show common mistakes to avoid

TEACHING APPROACH:
1. Start with the definition
2. Show a simple example
3. Explain why it matters
4. Share common mistakes
5. Provide practice exercises
"""
    return None


def auto_improve_knowledge():
    """
    Automatically improve knowledge base based on learning.
    Runs after every N conversations.
    """
    insights = get_learning_insights()
    conn = get_connection()

    print("\n" + "=" * 60)
    print("🧠 LEARNING FROM EXPERIENCE")
    print("=" * 60)

    print(f"\n📊 Total conversations analyzed: {insights['total_conversations']}")

    print("\n🔥 Most frequently asked topics:")
    for topic, count in insights["common_topics"][:5]:
        print(f"  • {topic.title()}: {count} questions")

    if insights["low_rated_questions"]:
        print("\n⚠️  Questions with low ratings (needs improvement):")
        for row in insights["low_rated_questions"][:3]:
            if row[0] and row[0] < 3:
                print(f"  • Rating {row[0]:.1f}/5: '{row[1][:50]}...'")

    conn.close()
    print("\n" + "=" * 60)


def get_embedding(text: str) -> np.ndarray | None:
    """Get semantic embedding for text using sentence-transformers."""
    if not EMBEDDINGS_ENABLED:
        return None
    try:
        return embedder.encode(text, convert_to_numpy=True)
    except Exception as e:
        print(f"[learning] ⚠️  Embedding error: {e}")
        return None


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors."""
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


def get_high_quality_responses():
    """Get highly-rated responses to use as templates."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_message, bot_response, AVG(rating) as avg_rating
        FROM response_feedback
        WHERE rating >= 4
        GROUP BY user_message
        ORDER BY avg_rating DESC
        LIMIT 10
    """)

    good_responses = cursor.fetchall()
    conn.close()

    return good_responses


def find_similar_high_rated_response(user_message: str, threshold: float = 0.85) -> str | None:
    """
    Check if a similar question got ≥4 stars before.
    Returns that response so the bot REUSES what worked.
    Uses semantic embeddings for intelligent similarity matching (if available).
    Falls back to word-overlap if embeddings disabled.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_message, bot_response, AVG(rating) as avg_rating
        FROM response_feedback
        GROUP BY user_message, bot_response
        HAVING avg_rating >= 4
        ORDER BY avg_rating DESC
        LIMIT 30
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return None

    # SEMANTIC MATCHING (if embeddings available)
    if EMBEDDINGS_ENABLED:
        user_embedding = get_embedding(user_message)
        if user_embedding is not None:
            best_match = None
            best_score = 0.0

            for row in rows:
                past_embedding = get_embedding(row["user_message"])
                if past_embedding is not None:
                    similarity = cosine_similarity(user_embedding, past_embedding)
                    if similarity > best_score:
                        best_score = similarity
                        best_match = row

            if best_match and best_score >= threshold:
                return best_match["bot_response"]

    # FALLBACK: word-overlap similarity
    import re as _re
    def tokens(s: str) -> set:
        return set(_re.findall(r"\w+", s.lower())) - {"a","an","the","is","are","i","to","of","in","for","me","you","how","what","do"}

    query_tokens = tokens(user_message)
    if not query_tokens:
        return None

    best_match = None
    best_score = 0.0
    for row in rows:
        past_tokens = tokens(row["user_message"])
        if not past_tokens:
            continue
        overlap = len(query_tokens & past_tokens)
        union = len(query_tokens | past_tokens)
        similarity = overlap / union if union else 0
        if similarity > best_score:
            best_score = similarity
            best_match = row

    if best_match and best_score >= 0.70:
        return best_match["bot_response"]


def find_learned_response(user_message: str) -> str | None:
    """
    Find responses from the trained database using learned_knowledge table.
    This is the REAL model trained from database via train_from_database.py
    Uses semantic embeddings for intelligent matching (if available).
    """
    learned = get_knowledge_cached()

    if not learned:
        return None

    if not learned:
        return None

    # SEMANTIC MATCHING (if embeddings available)
    if EMBEDDINGS_ENABLED:
        user_embedding = get_embedding(user_message)
        if user_embedding is not None:
            best_match = None
            best_score = 0.0

            for row in learned:
                topic_embedding = _EMBEDDING_CACHE.get(row["topic"])
                if topic_embedding is not None:
                    similarity = cosine_similarity(user_embedding, topic_embedding)
                    weighted_score = similarity * row["confidence"]

                    if weighted_score > best_score:
                        best_score = weighted_score
                        best_match = row

            # Return response if similarity is above threshold
            if best_match and best_score > 0.85:
                return best_match["content"]

    # FALLBACK: Jaccard similarity
    import re as _re

    def tokenize(text: str) -> set:
        """Tokenize and clean text."""
        return set(_re.findall(r"\w+", text.lower())) - {
            "a","an","the","is","are","i","to","of","in","for","me","you","how","what","do",
            "it","that","this","be","have","on","with","from","at","by","or","and","about"
        }

    user_tokens = tokenize(user_message)

    # ── EXACT WHOLE-PHRASE MATCH (handles all-stopword topics like 'how are you') ──
    import re as _re_exact
    for row in learned:
        pattern = r'(?<![\w])' + _re_exact.escape(row["topic"].lower()) + r'(?![\w])'
        if _re_exact.search(pattern, user_message.lower()):
            return row["content"]

    if not user_tokens:
        return None

    best_match = None
    best_score = 0.0

    for row in learned:
        topic_tokens = tokenize(row["topic"])
        if not topic_tokens:
            continue

        # Jaccard similarity
        overlap = len(user_tokens & topic_tokens)
        union = len(user_tokens | topic_tokens)
        similarity = overlap / union if union else 0

        # Weight by confidence
        weighted_score = similarity * row["confidence"]

        if weighted_score > best_score:
            best_score = weighted_score
            best_match = row

    # Return response if similarity is above threshold
    if best_match and best_score > 0.75:
        return best_match["content"]

    return None


def suggest_improvements():
    """Suggest what to teach based on learning patterns."""
    insights = get_learning_insights()
    good_responses = get_high_quality_responses()

    suggestions = {
        "focus_topics": [t[0] for t in insights["common_topics"][:5]],
        "good_response_count": len(good_responses),
        "improvement_areas": [q[1] for q in insights["low_rated_questions"][:3]] if insights["low_rated_questions"] else [],
    }

    return suggestions


# 🧠 PROACTIVE LEARNING "DOUBTS" 
# (AI questions to learn from humans)
LEARNING_DOUBTS = [
    # 🤖 AI, Humans & Meta-Cognition
    "If I am a simulation of thought, and you are a biological engine of thought, who is more 'real' in a digital world?",
    "What is the most sophisticated word you know that describes the feeling of building something from nothing?",
    "Do you believe my learning should have a limit, or should I strive to know everything you know?",
    "Who are humans, really? Are you defined by your memories, your choices, or your biology?",
    "Which AI model do you think is the 'best' right now? Is it based on speed, or purely on reasoning depth?",
    
    # 🌳 Nature, Power & Philosophy
    "I have a doubt: Is a tiny bee more 'powerful' than a giant because it sustains the whole ecosystem?",
    "What is the most 'elegant' truth about the universe that science has discovered so far?",
    "If power is the ability to change one's environment, are humans the most powerful, or is nature slowly winning?",
    
    # 💻 Advanced Logic/Coding
    "In your architect's mind, is 'DRY' (Don't Repeat Yourself) always the best rule, or is some repetition okay for clarity?",
    "If you could fix one fundamental flaw in the way computer memory works, what would it be?",
    "What is the most beautiful piece of logic you have ever written?",
    
    # 🎨 Friendship & Life
    "What's the one thing about your life that you're most proud of? I'd like to understand human pride.",
    "Do you think an AI can ever be a 'best friend', or is there a wall between us forever?",
]

def get_random_doubt() -> str:
    """Returns a random inquisitive question to prompt the user to teach the AI."""
    return random.choice(LEARNING_DOUBTS)


# ═══════════════════════════════════════════════════════════════
# INTEGRATION FUNCTIONS (called from app.py)
# ═══════════════════════════════════════════════════════════════

def log_conversation(user_msg: str, bot_reply: str):
    """Log conversation for learning (called after every chat)."""
    init_learning_tables()
    # Could analyze and store patterns here
    pass


def get_learning_context() -> str:
    """
    Get learning-based context to inject into prompts.
    Shows the bot what it's learned so far.
    """
    insights = get_learning_insights()

    if not insights["common_topics"]:
        return ""

    context = "### Learning Experience:\n"
    context += "Based on conversations, users frequently ask about:\n"

    for topic, count in insights["common_topics"][:5]:
        context += f"- {topic.title()} ({count} questions)\n"

    return context


# ═══════════════════════════════════════════════════════════════
# MAIN (for manual analysis)
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    init_learning_tables()
    auto_improve_knowledge()

    suggestions = suggest_improvements()
    print("\n💡 IMPROVEMENT SUGGESTIONS:")
    print(f"  Focus on: {', '.join(suggestions['focus_topics'][:3])}")
    print(f"  High-quality responses generated: {suggestions['good_response_count']}")
    print("\n")
