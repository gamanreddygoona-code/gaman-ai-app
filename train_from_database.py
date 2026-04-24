"""
train_from_database.py
──────────────────────
Train the AI model from the existing database.
- Extract Q&A pairs from chat_history
- Extract knowledge from knowledge table
- Build a semantic model using TF-IDF + similarity matching
- Store learned patterns in learned_knowledge table
"""

import sqlite3
import json
import math
from collections import defaultdict
from datetime import datetime
import re

class DatabaseTrainer:
    def __init__(self, db_path='ai_data.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.vocabulary = defaultdict(int)
        self.documents = []
        self.tfidf_vectors = []

    def load_training_data(self):
        """Load chat history and knowledge from database."""
        print("[📚] Loading training data from database...")

        # Get chat history
        self.cursor.execute("""
            SELECT user_message, bot_response
            FROM chat_history
            WHERE user_message IS NOT NULL AND bot_response IS NOT NULL
            ORDER BY created_at DESC
            LIMIT 100
        """)
        qa_pairs = self.cursor.fetchall()
        print(f"  ✓ Loaded {len(qa_pairs)} Q&A pairs from chat history")

        # Get knowledge entries
        self.cursor.execute("SELECT topic, content FROM knowledge")
        knowledge = self.cursor.fetchall()
        print(f"  ✓ Loaded {len(knowledge)} knowledge entries")

        # Get feedback (highly-rated responses)
        self.cursor.execute("""
            SELECT user_message, bot_response, rating
            FROM response_feedback
            WHERE rating >= 4
        """)
        feedback = self.cursor.fetchall()
        print(f"  ✓ Loaded {len(feedback)} high-rated responses")

        return qa_pairs, knowledge, feedback

    def tokenize(self, text):
        """Simple tokenizer: lowercase, split, remove punctuation."""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        tokens = text.split()
        return [t for t in tokens if len(t) > 2]

    def build_vocabulary(self, qa_pairs, knowledge):
        """Build vocabulary from all text."""
        print("\n[📖] Building vocabulary...")

        for user, bot in qa_pairs:
            for token in self.tokenize(user + " " + bot):
                self.vocabulary[token] += 1

        for topic, content in knowledge:
            for token in self.tokenize(topic + " " + content):
                self.vocabulary[token] += 1

        # Keep only tokens that appear 2+ times
        self.vocabulary = {k: v for k, v in self.vocabulary.items() if v >= 2}
        print(f"  ✓ Vocabulary size: {len(self.vocabulary)}")
        return self.vocabulary

    def compute_tfidf(self, qa_pairs, knowledge):
        """Compute TF-IDF vectors for documents."""
        print("\n[🔢] Computing TF-IDF vectors...")

        # All documents
        all_docs = []

        for user, bot in qa_pairs:
            all_docs.append({
                'type': 'qa',
                'text': user + " " + bot,
                'user': user,
                'bot': bot
            })

        for topic, content in knowledge:
            all_docs.append({
                'type': 'knowledge',
                'text': topic + " " + content,
                'topic': topic,
                'content': content
            })

        self.documents = all_docs
        num_docs = len(all_docs)

        # IDF calculation - use all tokens in docs
        idf = {}
        all_tokens_in_docs = set()
        for doc in all_docs:
            all_tokens_in_docs.update(self.tokenize(doc['text']))

        for token in all_tokens_in_docs:
            count = sum(1 for doc in all_docs if token in self.tokenize(doc['text']))
            idf[token] = math.log(num_docs / (count + 1))

        # TF-IDF vectors
        vectors = []
        for doc in all_docs:
            tokens = self.tokenize(doc['text'])
            vector = {}

            # Term frequency
            for token in tokens:
                vector[token] = vector.get(token, 0) + 1

            # TF-IDF (only for tokens in idf)
            for token in list(vector.keys()):
                if token in idf:
                    tf = vector[token] / len(tokens) if tokens else 0
                    vector[token] = tf * idf[token]
                else:
                    del vector[token]

            vectors.append(vector)

        self.tfidf_vectors = vectors
        print(f"  ✓ Computed TF-IDF for {len(vectors)} documents")
        return vectors

    def cosine_similarity(self, vec1, vec2):
        """Compute cosine similarity between two TF-IDF vectors."""
        if not vec1 or not vec2:
            return 0.0

        # Dot product
        dot = sum(vec1.get(k, 0) * vec2.get(k, 0) for k in set(vec1) | set(vec2))

        # Magnitudes
        mag1 = math.sqrt(sum(v**2 for v in vec1.values()))
        mag2 = math.sqrt(sum(v**2 for v in vec2.values()))

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot / (mag1 * mag2)

    def find_similar_answers(self, query, top_k=3):
        """Find top-k similar Q&A pairs for a query."""
        query_vector = {}
        tokens = self.tokenize(query)

        for token in tokens:
            query_vector[token] = query_vector.get(token, 0) + 1

        # Normalize
        if tokens:
            for token in query_vector:
                query_vector[token] /= len(tokens)

        # Find similarities
        similarities = []
        for i, (doc, vec) in enumerate(zip(self.documents, self.tfidf_vectors)):
            sim = self.cosine_similarity(query_vector, vec)
            if sim > 0.1:  # Only consider relevant matches
                similarities.append((sim, doc))

        # Sort and return top-k
        similarities.sort(reverse=True, key=lambda x: x[0])
        return similarities[:top_k]

    def store_learned_patterns(self):
        """Store learned Q&A patterns in the database."""
        print("\n[💾] Storing learned patterns...")

        # Clear old learned knowledge
        self.cursor.execute("DELETE FROM learned_knowledge")

        # For each Q&A pair, store as learned knowledge
        patterns_added = 0
        for doc, vec in zip(self.documents, self.tfidf_vectors):
            if doc['type'] == 'qa':
                self.cursor.execute("""
                    INSERT INTO learned_knowledge
                    (topic, content, source, confidence, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    doc['user'][:100],  # Question as topic
                    doc['bot'],  # Answer as content
                    'trained_from_database',
                    0.85,  # High confidence
                    datetime.now().isoformat()
                ))
                patterns_added += 1

        self.conn.commit()
        print(f"  ✓ Stored {patterns_added} learned patterns")

    def generate_summary(self):
        """Generate a training summary."""
        print("\n" + "="*60)
        print("📊 TRAINING SUMMARY")
        print("="*60)

        self.cursor.execute("SELECT COUNT(*) FROM learned_knowledge")
        learned = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM chat_history")
        chats = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM knowledge")
        knowledge = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM response_feedback WHERE rating >= 4")
        high_rated = self.cursor.fetchone()[0]

        print(f"✓ Total chat history: {chats} conversations")
        print(f"✓ Knowledge base: {knowledge} topics")
        print(f"✓ High-rated responses: {high_rated}")
        print(f"✓ Learned patterns: {learned}")
        print(f"✓ Vocabulary size: {len(self.vocabulary)} words")
        print("="*60)
        print("✅ Training complete! Model is now ready to use.\n")

    def train(self):
        """Run the complete training pipeline."""
        print("\n🚀 Starting AI Model Training from Database\n")

        qa_pairs, knowledge, feedback = self.load_training_data()
        self.build_vocabulary(qa_pairs, knowledge)
        self.compute_tfidf(qa_pairs, knowledge)
        self.store_learned_patterns()
        self.generate_summary()

        self.conn.close()

    def test_similarity(self, query):
        """Test: find similar answers for a query."""
        results = self.find_similar_answers(query, top_k=3)
        print(f"\n🔍 Query: {query}")
        print(f"Found {len(results)} similar answers:\n")
        for sim, doc in results:
            if doc['type'] == 'qa':
                print(f"  Similarity: {sim:.2%}")
                print(f"  Q: {doc['user'][:60]}...")
                print(f"  A: {doc['bot'][:80]}...\n")


if __name__ == "__main__":
    trainer = DatabaseTrainer('ai_data.db')
    trainer.train()

    # Test with sample queries
    print("\n🧪 Testing learned model:\n")
    trainer.test_similarity("how do i write python")
    trainer.test_similarity("what is a function")
    trainer.test_similarity("how to read a file")
