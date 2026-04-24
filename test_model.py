"""
test_model.py
─────────────
Tests the AI model responses directly (no server needed).
Checks: DB connection, learned_knowledge table, find_learned_response matching.
Run: python test_model.py
"""

import sqlite3
import sys
import os

DB_PATH = "./ai_data.db"

# ── 1. DB EXISTS? ────────────────────────────────────────────
print("\n" + "=" * 60)
print("🧪  GAMANSAI MODEL TEST")
print("=" * 60)

if not os.path.exists(DB_PATH):
    print(f"❌  FAIL: Database not found at {DB_PATH}")
    sys.exit(1)
print(f"✅  DB found: {DB_PATH}  ({os.path.getsize(DB_PATH)//1024//1024} MB)")

# ── 2. TABLES EXIST? ────────────────────────────────────────
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print(f"✅  Tables: {', '.join(tables)}")

for required in ["chat_history", "knowledge", "learned_knowledge"]:
    if required not in tables:
        print(f"❌  FAIL: Missing table '{required}'")
        sys.exit(1)
print("✅  All required tables present")

# ── 3. HOW MANY TAUGHT RESPONSES? ───────────────────────────
count = conn.execute("SELECT COUNT(*) FROM learned_knowledge").fetchone()[0]
print(f"✅  learned_knowledge rows: {count}")
if count == 0:
    print("❌  FAIL: No teaching data. Run: python deep_teach.py")
    sys.exit(1)

# ── 4. SIMULATE find_learned_response ───────────────────────
def find_response(user_msg: str) -> tuple:
    """Mimic app.py's find_learned_response logic — keyword/Jaccard match."""
    import re
    STOP = {"a","an","the","is","are","i","to","of","in","for","me","you",
            "how","what","do","it","that","this","be","have","on","with",
            "from","at","by","or","and","about","my","can"}

    def tok(s):
        return set(re.findall(r"\w+", s.lower())) - STOP

    rows = conn.execute(
        "SELECT topic, content, confidence FROM learned_knowledge ORDER BY confidence DESC"
    ).fetchall()

    user_tok = tok(user_msg)
    if not user_tok:
        # still try exact phrase match
        for row in rows:
            if row["topic"].lower() in user_msg.lower():
                return row["content"], row["confidence"], row["topic"]
        return None, 0.0, ""

    # First: exact whole-phrase match (catches all-stopword topics like 'how are you')
    import re as _re2
    for row in rows:
        pattern = r'(?<![\w])' + _re2.escape(row["topic"].lower()) + r'(?![\w])'
        if _re2.search(pattern, user_msg.lower()):
            return row["content"], row["confidence"], row["topic"]

    best_reply, best_score, best_topic = None, 0.0, ""
    for row in rows:
        t_tok = tok(row["topic"])
        if not t_tok:
            continue
        overlap = len(user_tok & t_tok)
        union   = len(user_tok | t_tok)
        score   = (overlap / union) * row["confidence"] if union else 0
        if score > best_score:
            best_score  = score
            best_reply  = row["content"]
            best_topic  = row["topic"]

    if best_score > 0.3:
        return best_reply, best_score, best_topic
    return None, best_score, ""

# ── 5. TEST QUERIES ──────────────────────────────────────────
tests = [
    ("hello",                   True),
    ("hi there",                True),
    ("how are you",             True),
    ("who are you",             True),
    ("what is your name",       True),
    ("what can you do",         True),
    ("tell me a joke",          True),
    ("good morning",            True),
    ("bye",                     True),
    ("thank you",               True),
    ("motivate me",             True),
    ("i am stuck",              True),
    ("i don't understand",      True),
    ("what is python",          True),
    ("what is a function",      True),
    ("what is a loop",          True),
    ("what is machine learning",True),
    ("what is an api",          True),
    ("what is sql",             True),
    ("what is git",             True),
    ("explain databases",       True),
    ("how do i debug",          True),
    ("what is ai",              True),
    ("are you better than chatgpt", True),
    ("about gamansai",          True),
    ("remember this",           True),
]

print("\n── Response Matching Tests ─────────────────────────────")
passed, failed = 0, 0
for query, should_match in tests:
    reply, score, topic = find_response(query)
    if should_match and reply:
        preview = reply[:60].replace('\n', ' ')
        print(f"  ✅  '{query}'  →  '{topic}'  ({score:.2f}) | {preview}...")
        passed += 1
    elif should_match and not reply:
        print(f"  ❌  '{query}'  →  NO MATCH  (best score {score:.2f})")
        failed += 1
    else:
        print(f"  ✅  '{query}'  →  correctly returned nothing")
        passed += 1

# ── 6. CHAT HISTORY ─────────────────────────────────────────
history_count = conn.execute("SELECT COUNT(*) FROM chat_history").fetchone()[0]
print(f"\n✅  chat_history has {history_count} conversation turns stored")

# ── 7. KNOWLEDGE BASE ────────────────────────────────────────
knowledge_count = conn.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0]
print(f"✅  knowledge base has {knowledge_count} entries")

conn.close()

# ── SUMMARY ──────────────────────────────────────────────────
print("\n" + "=" * 60)
total = passed + failed
print(f"🏆  RESULT:  {passed}/{total} tests passed  |  {failed} failed")
if failed == 0:
    print("🎉  ALL TESTS PASSED — model is working correctly!")
else:
    print(f"⚠️   {failed} queries didn't match. Run: python deep_teach.py")
print("=" * 60 + "\n")
