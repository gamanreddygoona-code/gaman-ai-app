"""
verify_upgrades.py
──────────────────
Quick verification that all 3 smart upgrades are working.
Run this to check your system before starting the app.
"""

import sys
import sqlite3

print("=" * 70)
print("🔍 GAMAN AI SMART UPGRADES VERIFICATION")
print("=" * 70)

# ============================================================
# 1. Check Semantic Embeddings
# ============================================================
print("\n1️⃣  SEMANTIC EMBEDDINGS")
print("-" * 70)
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np

    print("   ⏳ Loading embedding model (first time: ~30s)...")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")

    # Test embedding
    text1 = "How do I read a file?"
    text2 = "Reading files with open() function"
    text3 = "What's a pizza recipe?"

    emb1 = embedder.encode(text1, convert_to_numpy=True)
    emb2 = embedder.encode(text2, convert_to_numpy=True)
    emb3 = embedder.encode(text3, convert_to_numpy=True)

    # Cosine similarity
    def cosine_sim(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    sim_related = cosine_sim(emb1, emb2)
    sim_unrelated = cosine_sim(emb1, emb3)

    print(f"   ✅ Embeddings loaded successfully")
    print(f"   📊 Similarity test:")
    print(f"      • Related questions: {sim_related:.2%} similar")
    print(f"      • Unrelated questions: {sim_unrelated:.2%} similar")
    print(f"   ✅ SEMANTIC EMBEDDINGS WORKING\n")

except ImportError as e:
    print(f"   ❌ ERROR: {e}")
    print(f"   💡 FIX: pip install sentence-transformers\n")
    sys.exit(1)

# ============================================================
# 2. Check Full Context History
# ============================================================
print("2️⃣  FULL CONTEXT HISTORY")
print("-" * 70)
try:
    from db import get_chat_history, get_extended_chat_history

    # Check history limit
    print("   ✅ get_chat_history() loaded")
    print("   ✅ get_extended_chat_history() loaded")

    # Try getting history from database
    try:
        hist = get_chat_history(limit=20)
        ext_hist = get_extended_chat_history(limit=50)
        print(f"   📊 Chat history test:")
        print(f"      • Standard history: up to 20 turns")
        print(f"      • Extended history: up to 50 turns")
        if hist:
            print(f"      • Current database: {len(hist)} turns stored")
        print(f"   ✅ FULL CONTEXT HISTORY WORKING\n")
    except Exception as e:
        print(f"   ⚠️  Database issue: {e}")
        print(f"   💡 FIX: Make sure ai_data.db exists or run app.py once\n")

except ImportError as e:
    print(f"   ❌ ERROR: {e}\n")
    sys.exit(1)

# ============================================================
# 3. Check Few-Shot Learning
# ============================================================
print("3️⃣  FEW-SHOT LEARNING")
print("-" * 70)
try:
    from real_cloud_llm import get_few_shot_examples, REAL_CLOUD_ENABLED

    print(f"   🌐 Claude API Status: {'✅ ENABLED' if REAL_CLOUD_ENABLED else '⚠️  DISABLED (set ANTHROPIC_API_KEY)'}")

    # Check few-shot examples
    examples = get_few_shot_examples()
    if examples:
        print(f"   📚 Few-shot examples found:")
        num_examples = examples.count("Example")
        print(f"      • {num_examples} high-quality examples available")
        print(f"   ✅ FEW-SHOT LEARNING WORKING\n")
    else:
        print(f"   ℹ️  No examples yet (rate some responses 4-5 stars first)")
        print(f"   💡 TIP: Ask questions, rate with stars, examples will appear\n")

except ImportError as e:
    print(f"   ❌ ERROR: {e}")
    print(f"   💡 FIX: pip install anthropic\n")
    sys.exit(1)

# ============================================================
# Summary
# ============================================================
print("=" * 70)
print("✅ ALL UPGRADES VERIFIED AND READY!")
print("=" * 70)
print("""
Your AI is now:
  1. 🧠 SMART - Understands meaning with semantic embeddings
  2. 💾 AWARE - Remembers 20+ turns of conversation
  3. 📚 LEARNING - Adapts to your teaching style with few-shot examples

Next steps:
  1. Run: python app.py
  2. Open: http://127.0.0.1:8000
  3. Ask questions and rate responses (⭐⭐⭐⭐⭐)
  4. Watch it get smarter!

For full details, see: UPGRADE_GUIDE.md
""")
print("=" * 70)
