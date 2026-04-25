"""
add_expert_facts.py
───────────────────
Add curated expert knowledge: comparisons, code patterns,
complexity cheatsheet, system design facts.
"""
from mega_knowledge import get_knowledge
import time

COMPARISONS = [
    ("SQL vs NoSQL", "SQL: structured, ACID, vertical scaling, joins; NoSQL: flexible schema, horizontal scaling, eventual consistency, no joins"),
    ("REST vs GraphQL", "REST: multiple endpoints, over/under-fetching, simple; GraphQL: single endpoint, precise fetching, typed schema"),
    ("Monolith vs Microservices", "Monolith: simple deploy, tightly coupled, hard to scale parts; Microservices: independent deploy, loose coupling, network overhead"),
    ("Docker vs VMs", "Docker: shares OS kernel, MB size, seconds startup; VMs: full OS, GB size, minutes startup, stronger isolation"),
    ("TCP vs UDP", "TCP: reliable, ordered, connection-oriented, slower; UDP: unreliable, connectionless, faster, good for streaming/gaming"),
    ("Process vs Thread", "Process: own memory, more isolation, expensive context switch; Thread: shared memory, cheaper context switch"),
    ("Stack vs Heap memory", "Stack: LIFO, fast, limited size, automatic cleanup; Heap: dynamic size, slower, manual/GC cleanup, large allocations"),
    ("Mutex vs Semaphore", "Mutex: binary lock, owned by thread, exclusive; Semaphore: counting, not owned, multiple concurrent slots"),
    ("HTTP vs WebSocket", "HTTP: request-response, stateless, half-duplex; WebSocket: persistent, stateful, full-duplex, low-latency"),
    ("Kafka vs RabbitMQ", "Kafka: log-based, replay, high throughput, partitioned; RabbitMQ: queue-based, AMQP, complex routing, lower throughput"),
    ("Redis vs Memcached", "Redis: rich data types, persistence, pub/sub, Lua scripts; Memcached: simple strings, multi-threaded, simpler"),
    ("PostgreSQL vs MySQL", "PostgreSQL: JSONB, window functions, extensions; MySQL: wider hosting, simpler, faster for basic queries"),
    ("Git merge vs rebase", "Merge: preserves history, merge commit; Rebase: linear history, rewrites commits, cleaner log"),
    ("Abstract class vs Interface", "Abstract: can have state and implementation, single inheritance; Interface: contract only, multiple inheritance"),
    ("Strong vs Weak typing", "Strong: type errors caught, no implicit coercion; Weak: implicit coercion, more flexible, harder to debug"),
    ("Compiled vs Interpreted", "Compiled: fast runtime, platform-specific binary; Interpreted: portable, faster development cycle"),
    ("Synchronous vs Asynchronous", "Sync: blocks until complete, simple code; Async: non-blocking, concurrent, callback/promise/async-await"),
    ("Eager vs Lazy evaluation", "Eager: compute immediately; Lazy: compute on demand, avoids unnecessary work, enables infinite sequences"),
    ("Mutable vs Immutable", "Mutable: can change after creation; Immutable: cannot change, thread-safe, easier to reason about"),
    ("OLTP vs OLAP", "OLTP: many small transactions, row-oriented, normalized; OLAP: few complex queries, column-oriented, denormalized"),
    ("CAP: CP vs AP systems", "CP: consistent + partition tolerant (MongoDB, Zookeeper); AP: available + partition tolerant (Cassandra, DynamoDB)"),
    ("Blue-green vs Canary deploy", "Blue-green: instant full switch, parallel envs; Canary: gradual rollout, real traffic test, less resource use"),
    ("Forward vs Reverse proxy", "Forward: client-side, hides client; Reverse: server-side, load balancing, SSL termination, caching"),
    ("Symmetric vs Asymmetric crypto", "Symmetric: same key, fast; Asymmetric: key pair, slow, solves key distribution. TLS uses both"),
    ("Unit vs Integration test", "Unit: single function, fast, isolated, mocked; Integration: multiple components, slower, real dependencies"),
    ("Push vs Pull notifications", "Push: server initiates, WebSocket/SSE/FCM; Pull: client polls, simpler, wasted requests when no data"),
    ("Vertical vs Horizontal scaling", "Vertical: bigger machine, limit exists, simpler; Horizontal: more machines, no limit, needs distributed design"),
    ("Batch vs Stream processing", "Batch: high latency, high throughput, Spark; Stream: low latency, real-time, Kafka Streams/Flink"),
    ("Optimistic vs Pessimistic locking", "Optimistic: check version on write, no lock; Pessimistic: lock on read, prevents concurrent updates"),
    ("Row vs Column storage", "Row: fast for OLTP (get all columns per row); Column: fast for OLAP (aggregate one column across rows)"),
]

CODE_PATTERNS = [
    ("Python decorator pattern", "@functools.wraps preserves metadata. @lru_cache(maxsize=128) for memoization. @property for computed attributes. Stack decorators bottom-up."),
    ("Python generator pattern", "def gen(): yield item. Lazy evaluation, memory efficient for large data. next(g) or for loop. send() passes values back in."),
    ("Python context manager", "__enter__ returns resource, __exit__ handles cleanup. contextlib.contextmanager with yield. Ensures cleanup even on exception."),
    ("Python dataclass usage", "@dataclass auto-generates __init__, __repr__, __eq__. @dataclass(frozen=True) for immutable. field(default_factory=list) for mutable defaults."),
    ("Python async/await pattern", "async def with await. asyncio.gather() for parallel. asyncio.create_task() for background. aiohttp/httpx for async HTTP calls."),
    ("JavaScript Promise chaining", "Promise.all() for parallel, fails fast. Promise.allSettled() for all results. Promise.race() for first. Always handle .catch()."),
    ("JavaScript module exports", "CommonJS: module.exports = {}. ESM: export default / export {}. Tree-shakeable with ESM. Dynamic import() for code splitting."),
    ("React hooks best practices", "useState for UI state. useEffect with dependency array. useCallback for memoized callbacks. useMemo for expensive computations. Custom hooks for reuse."),
    ("Java streams API", "stream().filter().map().reduce(). Collectors.toList/toMap/groupingBy. parallelStream() for multi-core. flatMap for nested collections."),
    ("Go concurrency patterns", "goroutine: go func(){}(). channel for sync: ch := make(chan T). select for multiple channels. WaitGroup for fan-out/fan-in."),
    ("Rust ownership rules", "One owner at a time. Move transfers ownership. & borrows immutably. &mut borrows mutably. Lifetime ensures ref validity."),
    ("SQL window functions", "ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary). RANK(), DENSE_RANK(), LAG(n,1), LEAD(n,1), SUM() OVER (ROWS BETWEEN)."),
    ("SQL recursive CTE", "WITH RECURSIVE cte AS (base UNION ALL recursive). Used for trees, graphs, hierarchies. Termination condition required."),
    ("TypeScript generics", "function f<T>(arg: T): T. interface Box<T> { value: T }. Constraints: T extends Comparable. Utility types: Partial<T>, Required<T>, Pick<T,K>."),
    ("Event-driven patterns", "Emit events with EventEmitter. Subscribe to events. Decouple producers and consumers. Dead letter queue for failed events."),
]

COMPLEXITY_FACTS = [
    ("Array complexity cheatsheet", "Access O(1), Search O(n), Insert/Delete at end O(1) amortized, Insert/Delete at middle O(n). Cache-friendly due to contiguous memory."),
    ("Linked List complexity", "Access/Search O(n), Insert/Delete at head O(1), Insert after pointer O(1), Delete requires finding O(n). Not cache-friendly."),
    ("Hash Table complexity", "Average O(1) for all ops. Worst O(n) with collisions. Good hash function + load factor <0.75 avoids degradation."),
    ("Binary Search Tree complexity", "Balanced BST O(log n) search/insert/delete. Unbalanced degrades O(n). AVL tree guarantees O(log n) with rotations."),
    ("Sorting algorithms complexity", "Bubble/Selection/Insertion O(n²). Merge/Heap always O(n log n). Quicksort avg O(n log n) worst O(n²). Radix O(nk). Timsort O(n log n)."),
    ("Graph algorithms complexity", "BFS/DFS O(V+E). Dijkstra O((V+E)logV) with heap. Bellman-Ford O(VE). Floyd-Warshall O(V³). Prim/Kruskal O(ElogV)."),
    ("Dynamic programming patterns", "Memoization (top-down): recurse + cache. Tabulation (bottom-up): fill table. Requires overlapping subproblems + optimal substructure."),
    ("Space-time tradeoffs", "Caching: more memory = faster lookup. Compression: less space = more CPU. In-place algorithms: O(1) space but complex logic."),
]

SYSTEM_DESIGN_FACTS = [
    ("Scaling to 1M users", "Single server -> CDN -> DB read replicas -> Cache layer -> Message queue -> Horizontal scaling -> Multi-region. Each step handles 10x more load."),
    ("Database capacity planning", "1KB/row x 1M rows = 1GB. Add 3x buffer for indexes. 10x for 5-year growth. Separate read replicas at 100K+ QPS."),
    ("API rate limiting design", "Token bucket: N tokens/sec. Sliding window: count in rolling time. Redis for distributed counter. Return HTTP 429 + Retry-After header."),
    ("Cache invalidation strategies", "Write-through: update cache+DB atomically. Write-behind: async DB write. Cache-aside: app manages cache. TTL: automatic expiry."),
    ("Database sharding strategies", "Range sharding: partition by value range. Hash sharding: consistent hashing for even distribution. Directory: lookup table for location."),
    ("Message queue use cases", "Task queues: decouple work from producers. Event streaming: audit log, replay. Pub/sub: fan-out to multiple consumers. Priority queues."),
    ("Idempotency key design", "Client generates UUID per request. Server stores processed IDs with result. Safe to retry. Expire old IDs after 24 hours."),
    ("Circuit breaker states", "CLOSED: all requests pass. OPEN: fast-fail after N failures in window. HALF-OPEN: test probe after timeout. Library: Resilience4j, Polly."),
    ("Service discovery patterns", "Client-side (Eureka): client queries registry. Server-side (Nginx): LB queries. DNS-based (Route53): SRV records. Health checks critical."),
    ("Read-heavy optimization", "Add cache layer (Redis). Read replicas. CDN for static. Denormalize hot data. Pre-compute aggregations. Index query patterns."),
    ("Write-heavy optimization", "Message queue to buffer writes. Batch writes. Write-behind cache. Async replication. Event sourcing for append-only. SSD storage."),
    ("Observability three pillars", "Metrics (what): Prometheus/Grafana. Logs (why): ELK stack. Traces (where): Jaeger/Zipkin. OpenTelemetry as standard."),
    ("Database connection pooling", "Pool size = CPU cores x 2 + disk spindles. PgBouncer for PostgreSQL. HikariCP for Java. Idle timeout 10min. Validate on borrow."),
    ("Zero-downtime deployment", "Blue-green: parallel environments, instant switch. Canary: gradual traffic shift. Rolling: replace instances one by one. Feature flags."),
    ("Data consistency patterns", "2PC for distributed transactions (slow). Saga for long-running (choreography or orchestration). Eventual consistency + compensation."),
]


def run():
    kb = get_knowledge()
    start = time.time()
    before = kb.stats()["total_facts"]
    added = 0

    print(f"📚 Adding expert facts ({before:,} currently)...")

    for topic, content in COMPARISONS:
        if kb.add_fact(f"Comparison: {topic}", content, "expert", "comparison", 0.95):
            added += 1

    for topic, content in CODE_PATTERNS:
        if kb.add_fact(topic, content, "expert", "code_patterns", 0.95):
            added += 1

    for topic, content in COMPLEXITY_FACTS:
        if kb.add_fact(topic, content, "expert", "algorithms", 0.95):
            added += 1

    for topic, content in SYSTEM_DESIGN_FACTS:
        if kb.add_fact(topic, content, "expert", "system_design", 0.95):
            added += 1

    after = kb.stats()["total_facts"]
    print(f"✅ Added {added} facts | Total: {after:,} | {time.time()-start:.2f}s")
    return after


if __name__ == "__main__":
    run()
