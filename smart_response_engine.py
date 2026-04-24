"""
smart_response_engine.py
────────────────────────
Uses the MASSIVE training database (8M examples) to give intelligent responses.

Instead of rule-based matching, it:
1. Embeds user query semantically
2. Searches millions of examples using FAISS (fast vector search)
3. Returns the best matching response
4. Learns from feedback continuously

This is how REAL AI models work - just scaled down for local use.
"""

import os
import sqlite3
import numpy as np
import pickle
from pathlib import Path

DB_PATH = "./ai_data.db"
INDEX_PATH = "./faiss_index.bin"
EMBEDDINGS_PATH = "./embeddings_cache.npy"
IDS_PATH = "./embeddings_ids.pkl"

# Lazy imports
_embedder = None
_faiss_index = None
_ids_map = None


def get_embedder():
    """Get the sentence transformer (lazy loaded)."""
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        print("⏳ Loading embedder...")
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder


def build_faiss_index(batch_size: int = 1000):
    """
    Build FAISS index from all training examples.
    This is FAST vector search across millions of examples.
    """
    try:
        import faiss
    except ImportError:
        print("❌ FAISS not installed. Run: pip install faiss-cpu")
        return False

    print("=" * 70)
    print("🔨 BUILDING FAISS INDEX FROM MASSIVE TRAINING DATA")
    print("=" * 70)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all training examples
    cursor.execute("SELECT id, user_message FROM massive_training")
    rows = cursor.fetchall()

    if not rows:
        print("❌ No training data found. Run massive_training_data.py first!")
        conn.close()
        return False

    print(f"\n📊 Processing {len(rows):,} training examples...")

    embedder = get_embedder()

    # Embed in batches
    all_embeddings = []
    all_ids = []

    total = len(rows)
    for i in range(0, total, batch_size):
        batch = rows[i:i + batch_size]
        texts = [row[1][:512] for row in batch]  # Truncate long texts
        ids = [row[0] for row in batch]

        embeddings = embedder.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        all_embeddings.append(embeddings)
        all_ids.extend(ids)

        if (i + batch_size) % 10000 == 0 or (i + batch_size) >= total:
            progress = min((i + batch_size) / total * 100, 100)
            print(f"  ⏳ {progress:.1f}% - {min(i + batch_size, total):,}/{total:,} embedded")

    # Combine all embeddings
    all_embeddings = np.vstack(all_embeddings).astype('float32')
    print(f"\n✅ Generated {len(all_embeddings):,} embeddings")
    print(f"📐 Embedding dimensions: {all_embeddings.shape}")

    # Build FAISS index (L2 distance - fast)
    dim = all_embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(all_embeddings)

    # Save index and IDs
    faiss.write_index(index, INDEX_PATH)
    np.save(EMBEDDINGS_PATH, all_embeddings)
    with open(IDS_PATH, 'wb') as f:
        pickle.dump(all_ids, f)

    conn.close()

    print(f"\n✅ Index built and saved to {INDEX_PATH}")
    print(f"💾 Size: {os.path.getsize(INDEX_PATH) / 1024 / 1024:.1f} MB")
    print("=" * 70)
    return True


def load_faiss_index():
    """Load the pre-built FAISS index."""
    global _faiss_index, _ids_map

    if _faiss_index is not None:
        return True

    try:
        import faiss
    except ImportError:
        return False

    if not os.path.exists(INDEX_PATH):
        print("⚠️  FAISS index not found. Build it first with build_faiss_index()")
        return False

    _faiss_index = faiss.read_index(INDEX_PATH)
    with open(IDS_PATH, 'rb') as f:
        _ids_map = pickle.load(f)

    return True


def smart_response(user_message: str, top_k: int = 5) -> dict:
    """
    Get smart response using semantic search over millions of examples.

    Returns:
        {
            'response': str,
            'confidence': float,
            'source': str,
            'alternatives': list  # Top-k similar matches
        }
    """
    if not load_faiss_index():
        return {"response": None, "confidence": 0, "error": "Index not built"}

    embedder = get_embedder()

    # Embed the query
    query_embedding = embedder.encode([user_message], convert_to_numpy=True).astype('float32')

    # Search FAISS index
    distances, indices = _faiss_index.search(query_embedding, top_k)

    # Get database IDs from index positions
    result_ids = [_ids_map[idx] for idx in indices[0]]

    # Fetch actual responses from database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    placeholders = ','.join('?' * len(result_ids))
    cursor.execute(f"""
        SELECT id, user_message, bot_response, source, quality_score
        FROM massive_training
        WHERE id IN ({placeholders})
    """, result_ids)

    # Sort by FAISS order
    id_to_row = {row[0]: row for row in cursor.fetchall()}
    ordered_results = [id_to_row[rid] for rid in result_ids if rid in id_to_row]

    conn.close()

    if not ordered_results:
        return {"response": None, "confidence": 0, "error": "No matches"}

    # Best match
    best = ordered_results[0]
    best_distance = float(distances[0][0])
    # Convert L2 distance to confidence (0-1)
    # Distance 0 = perfect match = confidence 1
    # Distance grows = confidence decreases
    confidence = max(0, 1 - (best_distance / 2))

    # Build alternatives
    alternatives = []
    for i, row in enumerate(ordered_results[:top_k]):
        dist = float(distances[0][i])
        conf = max(0, 1 - (dist / 2))
        alternatives.append({
            "user": row[1][:100],
            "bot": row[2][:200],
            "confidence": conf,
            "source": row[3]
        })

    return {
        "response": best[2],
        "confidence": confidence,
        "source": f"trained_{best[3]}",
        "matched_query": best[1],
        "quality_score": best[4],
        "alternatives": alternatives
    }


def test_smart_responses():
    """Test the smart response engine."""
    if not load_faiss_index():
        print("❌ Index not built yet. Run build_faiss_index() first")
        return

    test_queries = [
        "hello",
        "hi there",
        "how are you",
        "what is python",
        "write a function to sort a list",
        "explain machine learning",
        "I'm confused about loops",
        "yup",
        "tell me about yourself",
        "can you help me debug my code",
    ]

    print("\n" + "=" * 70)
    print("🧪 TESTING SMART RESPONSE ENGINE")
    print("=" * 70)

    for query in test_queries:
        print(f"\n❓ Query: '{query}'")
        result = smart_response(query, top_k=3)

        if result.get('response'):
            print(f"💡 Response: {result['response'][:200]}...")
            print(f"📊 Confidence: {result['confidence']:.1%}")
            print(f"🔗 Matched: '{result.get('matched_query', '')[:80]}...'")
            print(f"📦 Source: {result['source']}")
        else:
            print(f"❌ No response: {result.get('error', 'unknown')}")


def integrate_with_app():
    """Show how to use in app.py."""
    example = """
# Add to app.py:

from smart_response_engine import smart_response, load_faiss_index

# Load index at startup
@app.on_event("startup")
async def startup_event():
    init_db()
    init_learning_tables()
    load_faiss_index()  # ← Add this line
    print("[app] ✅ Smart response engine loaded")


# In /chat endpoint, add as first check:
@app.post("/chat")
async def chat(req: ChatRequest):
    user_msg = req.message.strip()

    # 🧠 Try smart response first (uses 8M training examples)
    smart = smart_response(user_msg)
    if smart.get('response') and smart['confidence'] > 0.6:
        save_chat(user_msg, smart['response'])
        return {
            "reply": smart['response'],
            "source": smart['source'],
            "confidence": smart['confidence']
        }

    # ... rest of existing logic
    """
    print(example)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Smart Response Engine')
    parser.add_argument('command', choices=['build', 'test', 'integrate'],
                       help='build=create index, test=test queries, integrate=show code')
    args = parser.parse_args()

    if args.command == 'build':
        build_faiss_index()
    elif args.command == 'test':
        test_smart_responses()
    elif args.command == 'integrate':
        integrate_with_app()
