"""
qa_corpus.py
────────────
Curated Q&A pairs to expand knowledge base.
Fast, no API rate limits.
"""

from mega_knowledge import get_knowledge

# Curated high-value Q&A pairs across domains
CURATED_QA = [
    # ===== Python Programming =====
    ("How do decorators work in Python?", "Decorators are functions that modify other functions or classes. They use the @syntax. Example: @property turns a method into an attribute. @lru_cache caches function results."),
    ("What's the difference between list and tuple in Python?", "Lists are mutable (changeable), tuples are immutable (fixed). Lists use [], tuples use (). Tuples are hashable and faster."),
    ("Explain list comprehensions in Python", "List comprehensions create lists concisely. [x*2 for x in range(5)] produces [0,2,4,6,8]. They're faster than for loops and more readable."),
    ("What's the GIL in Python?", "Global Interpreter Lock. It prevents multiple threads from executing Python bytecode simultaneously. Only one thread runs at a time. Use multiprocessing for true parallelism."),

    # ===== JavaScript =====
    ("What's the difference between var, let, const?", "var is function-scoped and hoisted. let is block-scoped. const is block-scoped and immutable. Use const by default, let when needed."),
    ("How does async/await work?", "async/await simplifies Promise handling. async functions return Promises. await pauses execution until a Promise resolves. Cleaner than .then() chains."),
    ("What is hoisting in JavaScript?", "Variable and function declarations are moved to the top of their scope before execution. var declarations hoist as undefined. Functions hoist completely."),

    # ===== Machine Learning =====
    ("What's the difference between supervised and unsupervised learning?", "Supervised learning uses labeled data (input-output pairs) to train. Unsupervised learning finds patterns in unlabeled data. Classification/regression are supervised. Clustering is unsupervised."),
    ("Explain gradient descent", "Gradient descent optimizes model weights by iteratively moving in the direction of steepest descent. Update: w = w - lr * gradient. Finds local minima."),
    ("What is overfitting?", "Overfitting occurs when a model learns noise in training data and performs poorly on new data. Signs: high training accuracy, low test accuracy. Fix: regularization, more data, simpler model."),
    ("Difference between training, validation, test sets?", "Training set: used to train. Validation set: tune hyperparameters. Test set: final evaluation. Split: ~60% train, 20% val, 20% test."),

    # ===== Data Structures =====
    ("What's the time complexity of hash table operations?", "O(1) average case for insert, delete, lookup. O(n) worst case if collisions occur. Space: O(n). Hash tables are fastest for lookups."),
    ("Explain binary search trees", "BST: left child < parent < right child. Search O(log n) if balanced. Insert/delete O(log n). In-order traversal gives sorted order."),
    ("What is a heap?", "Heap is a complete binary tree. Max heap: parent > children. Min heap: parent < children. Operations: insert O(log n), extract-min O(log n)."),

    # ===== Databases =====
    ("What's the difference between SQL and NoSQL?", "SQL: structured, relational, ACID. Schema required. NoSQL: flexible, document/key-value, BASE. Schema-less. SQL for transactions, NoSQL for scale."),
    ("Explain database normalization", "Normalization reduces data redundancy. 1NF: atomic values. 2NF: no partial dependencies. 3NF: no transitive dependencies. Higher forms trade performance for consistency."),
    ("What are database indexes?", "Indexes speed up queries by pre-sorting data. Create: CREATE INDEX idx ON table(column). Trade-off: faster reads, slower writes. Use on frequently queried columns."),

    # ===== Web Development =====
    ("What is REST?", "REST (Representational State Transfer) is an architecture for web APIs. Uses HTTP methods: GET (read), POST (create), PUT (update), DELETE (delete). Stateless, scalable."),
    ("Explain CORS", "Cross-Origin Resource Sharing controls requests between domains. Browser enforces it. Server sends Access-Control headers. Prevents malicious cross-site requests."),
    ("What's the difference between HTTP and HTTPS?", "HTTP is unencrypted. HTTPS adds TLS encryption for security. HTTPS is standard now. SEO favors HTTPS. Performance difference is negligible."),

    # ===== DevOps =====
    ("What is Docker?", "Docker containerizes applications with dependencies. Lightweight VMs. Build once, run everywhere. Images are templates, containers are instances. Faster than VMs."),
    ("Explain Kubernetes", "Kubernetes orchestrates containers at scale. Manages deployment, scaling, updates. Auto-restart failed containers. Load balances traffic. Replaces manual container management."),
    ("What's the difference between CI and CD?", "CI (Continuous Integration): automatically test code on every commit. CD (Continuous Deployment): automatically deploy to production. Together: fast, safe releases."),

    # ===== Algorithms =====
    ("What's the difference between BFS and DFS?", "BFS (Breadth-First): explores level by level. Uses queue. Shortest path in unweighted graphs. DFS (Depth-First): explores deep first. Uses stack. Good for topological sort."),
    ("Explain merge sort", "Merge sort: divide array, recursively sort halves, merge. Time: O(n log n) always. Space: O(n). Stable. Faster than quicksort for large datasets."),
    ("What is dynamic programming?", "DP solves overlapping subproblems by storing results (memoization). Optimal substructure required. Examples: Fibonacci, longest common subsequence, knapsack problem."),

    # ===== System Design =====
    ("How do you design a scalable cache?", "LRU (Least Recently Used) eviction. Hash map for O(1) lookups. Doubly-linked list for ordering. TTL (time-to-live) for expiration. Distributed cache: Redis, Memcached."),
    ("Explain load balancing", "Distributes traffic across servers. Algorithms: round-robin, least-loaded, consistent hashing. Prevents single point of failure. Hardware or software solutions."),
    ("What is a message queue?", "Async communication between services. Producer sends messages, consumer processes. Examples: RabbitMQ, Kafka. Decouples services, handles spikes, ensures durability."),

    # ===== Security =====
    ("What is SQL injection?", "Attacker inserts malicious SQL code via input. Bypasses authentication. Example: user = '1' OR '1'='1'. Fix: use parameterized queries, prepared statements."),
    ("Explain password hashing", "Hash password, don't store plaintext. Use bcrypt, scrypt, Argon2. Slow hashing prevents brute force. Use salt to prevent rainbow tables."),
    ("What's the difference between encryption and hashing?", "Encryption: reversible (decrypt). Hashing: irreversible (one-way). Use hashing for passwords, encryption for sensitive data."),
]

def ingest_qa_corpus():
    """Ingest curated Q&A pairs."""
    kb = get_knowledge()
    before = kb.stats()["total_facts"]

    print(f"📥 Ingesting {len(CURATED_QA)} Q&A pairs...")
    for q, a in CURATED_QA:
        kb.add_fact(
            topic=q,
            content=a,
            source="curated_qa",
            category="qa_pairs",
            confidence=0.92,
        )

    after = kb.stats()["total_facts"]
    print(f"✅ Ingested {after - before} Q&A pairs")
    print(f"📊 Total facts: {before} → {after}")
    return after - before


if __name__ == "__main__":
    ingest_qa_corpus()
