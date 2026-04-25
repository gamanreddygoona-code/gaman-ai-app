"""
expert_knowledge.py
───────────────────
Deep, expert-level knowledge for top technology topics.
Each topic has 6 dimensions: definition, how it works, use cases,
advantages, challenges, best practices.
"""

from mega_knowledge import get_knowledge
import time

EXPERT_TOPICS = {
    "REST API": {
        "definition": "a stateless client-server architectural style using HTTP verbs (GET/POST/PUT/DELETE) on resources identified by URLs",
        "how it works": "clients send HTTP requests to endpoints; servers respond with JSON/XML; stateless means no session stored server-side; each request is self-contained",
        "use cases": "web services, mobile backends, microservice communication, third-party integrations, public APIs",
        "advantages": "simple, widely understood, cacheable, scalable, language-agnostic, great tooling ecosystem",
        "challenges": "over-fetching and under-fetching data, versioning strategies, rate limiting, statelessness can be limiting",
        "best practices": "use nouns not verbs in URLs, return proper HTTP status codes, version the API (v1/v2), document with OpenAPI/Swagger",
    },
    "GraphQL": {
        "definition": "a query language for APIs and runtime for executing queries, developed by Facebook in 2012 and open-sourced in 2015",
        "how it works": "clients specify exactly what data they need; resolvers fetch data from sources; single endpoint /graphql; strongly typed schema",
        "use cases": "complex UI data requirements, mobile apps needing bandwidth efficiency, aggregating multiple data sources",
        "advantages": "no over/under-fetching, strongly typed schema, introspection, single endpoint, real-time with subscriptions",
        "challenges": "N+1 query problem (use DataLoader), complex caching, learning curve, file uploads need multipart",
        "best practices": "use DataLoader for batching, paginate large results, implement depth limiting to prevent abuse, rate limit by complexity",
    },
    "Microservices Architecture": {
        "definition": "an architectural pattern where applications are built as small, independently deployable services each running its own process and communicating via APIs",
        "how it works": "each service owns its data store, communicates via REST/gRPC/message queues, deployed independently, scales independently",
        "use cases": "large engineering teams, independent scaling of components, polyglot tech stacks, high availability requirements",
        "advantages": "independent deployment, technology flexibility per service, fault isolation, team autonomy, fine-grained scaling",
        "challenges": "distributed system complexity, network latency, data consistency across services, service discovery, debugging across services",
        "best practices": "single responsibility per service, database per service, use async messaging, implement circuit breakers, centralized logging and tracing",
    },
    "Docker Containers": {
        "definition": "an open platform for developing, shipping, and running applications in containers — isolated environments sharing the OS kernel, more lightweight than VMs",
        "how it works": "Dockerfile defines image layers; docker build creates image; docker run starts container from image; images stored in registries like Docker Hub",
        "use cases": "consistent dev/prod environments, microservices packaging, CI/CD pipelines, application isolation, rapid deployment",
        "advantages": "consistent environments, fast startup (seconds vs minutes), lightweight vs VMs, easy distribution, version-controlled images",
        "challenges": "persistent storage complexity, networking configuration, security (container escape, privileged containers), image bloat",
        "best practices": "minimal base images (Alpine/distroless), multi-stage builds, non-root user, .dockerignore, pin image versions",
    },
    "Kubernetes Orchestration": {
        "definition": "an open-source container orchestration platform for automating deployment, scaling, and management of containerized applications at scale",
        "how it works": "control plane (API server, scheduler, etcd) manages desired state; kubelet on nodes runs pods; controllers reconcile actual vs desired state",
        "use cases": "large-scale container deployments, auto-scaling applications, rolling deployments, self-healing infrastructure, multi-cloud",
        "advantages": "auto-healing (restarts failed pods), horizontal auto-scaling, service discovery built-in, rolling updates, declarative config",
        "challenges": "steep learning curve, complex networking (CNI plugins), storage management (CSI), resource overhead, debugging difficulty",
        "best practices": "use namespaces for isolation, always set resource requests/limits, configure liveness/readiness probes, RBAC for security, GitOps",
    },
    "Redis Cache": {
        "definition": "an open-source, in-memory data structure store used as a database, cache, message broker, and streaming engine with sub-millisecond latency",
        "how it works": "all data in RAM for near-instant access; persistence via RDB snapshots or AOF append-only file; primary-replica replication; cluster mode for horizontal scaling",
        "use cases": "session storage, API response caching, real-time leaderboards, pub/sub messaging, rate limiting, distributed locks",
        "advantages": "extremely fast (microsecond latency), rich data structures (strings/lists/sets/hashes/sorted sets/streams), multiple persistence options",
        "challenges": "memory bounded by RAM, single-threaded command processing, no complex relational queries, cluster shard key design is critical",
        "best practices": "set TTL on cached data, choose appropriate data structure, monitor memory with INFO memory, use pipeline for batching commands",
    },
    "Git Version Control": {
        "definition": "a distributed version control system tracking changes in source code files, created by Linus Torvalds in 2005 for Linux kernel development",
        "how it works": "every clone is a full repository with complete history; commits form a DAG; branches are lightweight pointers; merging/rebasing integrates histories",
        "use cases": "source code versioning, team collaboration, code review via pull requests, release management, maintaining audit trail",
        "advantages": "offline work, cheap branching, distributed (no single point of failure), complete history, cryptographic integrity via SHA-1/SHA-256",
        "challenges": "merge conflicts, complex rebasing (interactive rebase), large binary files (use Git LFS), learning curve for advanced operations",
        "best practices": "atomic commits, meaningful commit messages (imperative mood, explain why), feature branches, PR reviews, protect main/master branch",
    },
    "PostgreSQL Database": {
        "definition": "an open-source object-relational database with 35+ years of development, known for reliability, data integrity, and rich feature set",
        "how it works": "MVCC (Multi-Version Concurrency Control) for concurrent access; WAL for crash recovery; cost-based query planner; B-tree indexes by default",
        "use cases": "OLTP transactional apps, geospatial data (PostGIS), JSON document storage (JSONB), analytics, time-series (TimescaleDB extension)",
        "advantages": "full ACID compliance, rich types (JSONB, arrays, UUID, ranges), window functions, CTEs, stored procedures, massive extensions ecosystem",
        "challenges": "table bloat from MVCC requires VACUUM, performance tuning needed for large workloads, connection overhead (use PgBouncer)",
        "best practices": "use EXPLAIN ANALYZE for query tuning, index foreign keys, configure autovacuum, use connection pooling, prefer JSONB over JSON",
    },
    "Transformer Architecture": {
        "definition": "a deep learning model architecture relying on self-attention mechanisms, introduced in Attention Is All You Need (2017), foundational to GPT/BERT/LLMs",
        "how it works": "input tokens become embeddings + positional encoding; multi-head self-attention computes Q/K/V; feed-forward layers; residual connections + layer norm throughout",
        "use cases": "text generation, machine translation, summarization, Q&A, code generation, image recognition (ViT), audio (Whisper), multimodal",
        "advantages": "fully parallelizable training (unlike RNNs), captures long-range dependencies, scales with compute and data, excellent for transfer learning",
        "challenges": "quadratic attention complexity O(n^2) with sequence length, enormous compute for pretraining, hallucination, prompt sensitivity",
        "best practices": "use Flash Attention for memory efficiency, quantize (INT8/INT4) for deployment, tune temperature and top-p sampling, use structured system prompts",
    },
    "Apache Kafka": {
        "definition": "a distributed event streaming platform designed for high-throughput, fault-tolerant, publish-subscribe messaging and stream processing",
        "how it works": "producers write messages to topics; topics are partitioned across brokers for parallelism; consumer groups read from partitions; messages retained on disk",
        "use cases": "event streaming, log aggregation, metrics pipeline, activity tracking, CDC (Change Data Capture), stream processing",
        "advantages": "high throughput (millions msg/s), fault tolerant, durable (configurable retention), decouples producers/consumers, message replay capability",
        "challenges": "complex initial setup, at-least-once delivery requires idempotent consumers, partition rebalancing overhead, ZooKeeper dependency (pre-KRaft)",
        "best practices": "choose partition count carefully (cannot reduce), use consumer group for parallelism, monitor consumer lag, compress messages (LZ4/Zstd)",
    },
    "Nginx Web Server": {
        "definition": "a high-performance open-source web server, reverse proxy, load balancer, and HTTP cache known for low memory footprint and high concurrency",
        "how it works": "event-driven, asynchronous architecture with master process and worker processes; each worker handles thousands of simultaneous connections via epoll/kqueue",
        "use cases": "serving static files, reverse proxy to application servers, SSL/TLS termination, load balancing, rate limiting, HTTP caching",
        "advantages": "extremely fast for static content, very low memory usage, handles C10K+ connections, battle-tested, HTTP/2 and gRPC support",
        "challenges": "configuration syntax complexity, no dynamic config reload for all changes, limited dynamic module loading",
        "best practices": "set worker_processes to auto, configure keepalive_timeout, enable gzip compression, use upstream blocks with health checks for load balancing",
    },
    "Load Balancing": {
        "definition": "distribution of network or application traffic across multiple servers to ensure reliability, scalability, and optimal resource utilization",
        "how it works": "load balancer receives all incoming requests; routing algorithm selects backend; health checks remove unhealthy backends; session persistence optional",
        "use cases": "web traffic distribution, microservice routing, database read replicas, zero-downtime deployments, geographic distribution",
        "advantages": "eliminates single point of failure, improves throughput and response time, enables horizontal scaling, transparent maintenance windows",
        "challenges": "session affinity complicates stateless design, SSL termination adds overhead, health check configuration critical, cost of dedicated hardware",
        "best practices": "configure meaningful health checks with appropriate intervals, use connection draining for graceful scale-in, prefer stateless backends for simplicity",
    },
    "CI/CD Pipeline": {
        "definition": "Continuous Integration and Continuous Delivery — automation practices for frequent, reliable software delivery through automated testing and deployment",
        "how it works": "code commit triggers pipeline; automated build; unit/integration tests; security scanning; staging deployment; acceptance tests; production deployment",
        "use cases": "automated testing on every commit, frequent safe deployments, rollback capability, environment consistency, compliance and audit trails",
        "advantages": "faster feedback loops, reduced manual errors, always-deployable main branch, team confidence to deploy frequently, earlier bug detection",
        "challenges": "test suite maintenance, flaky tests erode trust, pipeline duration (aim for under 10 min), secrets management, environment parity",
        "best practices": "fail fast (static analysis and unit tests first), parallelize test stages, cache dependencies, keep pipelines under 10 minutes, blue-green or canary deploys",
    },
    "Neural Network Training": {
        "definition": "the process of adjusting model weights to minimize a loss function on training data using gradient-based optimization algorithms",
        "how it works": "forward pass computes predictions; loss calculated vs ground truth; backpropagation computes gradients via chain rule; optimizer updates weights",
        "use cases": "image classification, object detection, NLP, speech recognition, game playing, recommendation systems, generative models",
        "advantages": "can learn complex nonlinear patterns, generalizes well with sufficient data, composable (transfer learning), handles raw inputs (images/text/audio)",
        "challenges": "vanishing/exploding gradients, overfitting on small datasets, hyperparameter sensitivity, compute requirements, black-box interpretability",
        "best practices": "normalize inputs, use batch normalization, apply dropout for regularization, use learning rate warmup, monitor validation loss, early stopping",
    },
    "Cloud Auto-Scaling": {
        "definition": "automatic adjustment of compute resources based on load — adding capacity when demand rises and removing it when demand falls to optimize cost and performance",
        "how it works": "CloudWatch/metrics monitor resource utilization; scaling policies define thresholds; scale-out adds instances; scale-in removes; cooldown prevents thrashing",
        "use cases": "handling traffic spikes, cost optimization for variable workloads, gaming/streaming events, e-commerce sales, batch processing",
        "advantages": "cost efficiency (pay for what you use), handles unpredictable load, eliminates over-provisioning, improved availability",
        "challenges": "cold start latency (containers/VMs need time), stateful applications need careful design, premature scale-in risks, cost unpredictability",
        "best practices": "use target tracking policies over step scaling, set appropriate cooldown periods, pre-warm for known events, design stateless applications",
    },
    "OAuth 2.0": {
        "definition": "an authorization framework enabling third-party applications to obtain limited access to user accounts on another service, without exposing passwords",
        "how it works": "client redirects user to auth server; user grants permission; auth server returns auth code; client exchanges for access token; token used for API calls",
        "use cases": "social login (Sign in with Google), third-party app integration, API authorization, mobile app authentication, service-to-service auth",
        "advantages": "users never share passwords with third parties, limited scope access, tokens expire, revocable, industry standard",
        "challenges": "complex flow with multiple actors, token storage security (never in localStorage), PKCE required for SPAs/mobile, refresh token rotation",
        "best practices": "always use PKCE for public clients, store tokens in httpOnly cookies, implement refresh token rotation, validate state parameter to prevent CSRF",
    },
    "Database Indexing": {
        "definition": "a data structure technique to speed up retrieval of rows from a table, similar to a book index — trades write overhead and storage for read speed",
        "how it works": "B-tree index stores sorted key values with pointers to rows; database optimizer chooses index based on query plan; covering index includes all queried columns",
        "use cases": "speeding up WHERE clause queries, JOIN operations on foreign keys, ORDER BY without sort, GROUP BY, UNIQUE constraints",
        "advantages": "dramatically faster reads (O(log n) vs O(n) table scan), enables efficient sorting, enforces uniqueness, supports range queries",
        "challenges": "every index slows INSERT/UPDATE/DELETE, uses additional storage, outdated statistics mislead optimizer, index maintenance overhead",
        "best practices": "index foreign keys, use composite indexes matching query patterns, analyze slow queries with EXPLAIN, remove unused indexes, consider partial indexes",
    },
    "Event-Driven Architecture": {
        "definition": "a software design pattern where components communicate through events — asynchronous messages describing things that happened — enabling loose coupling",
        "how it works": "producers emit events to event bus/stream; consumers subscribe to event types; each consumer processes independently; events stored for replay",
        "use cases": "microservice decoupling, audit logging, CQRS, real-time notifications, saga orchestration, data pipeline processing",
        "advantages": "loose coupling (producers/consumers evolve independently), scalability, resilience, event sourcing enables audit trail and replay",
        "challenges": "eventual consistency (not immediate), event schema evolution (versioning), debugging complex event chains, ordering guarantees",
        "best practices": "include event timestamp and ID, design idempotent consumers, version event schemas, implement dead letter queues for failed events",
    },
    "SOLID Principles": {
        "definition": "five object-oriented design principles for writing maintainable, flexible, and robust software: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion",
        "how it works": "SRP: one reason to change per class; OCP: extend not modify; LSP: subtypes replaceable; ISP: small focused interfaces; DIP: depend on abstractions",
        "use cases": "class and module design, refactoring legacy code, designing testable systems, building maintainable frameworks",
        "advantages": "easier to maintain and extend, better testability (inject dependencies), reduces coupling, clearer responsibilities",
        "challenges": "can lead to over-engineering if applied dogmatically, more files/classes, learning curve, sometimes pragmatism overrides",
        "best practices": "apply as guidelines not strict rules, focus on SRP and DIP first, use interfaces for external dependencies, code to interfaces not implementations",
    },
    "Rate Limiting": {
        "definition": "a technique to control the rate of requests a user or service can make to an API, protecting against abuse, DoS attacks, and ensuring fair resource distribution",
        "how it works": "token bucket: tokens replenish at rate R, each request consumes one; sliding window: count requests in rolling time window; Redis stores counters for distributed setup",
        "use cases": "API abuse prevention, DDoS mitigation, fair usage enforcement, cost control for expensive operations, preventing cascade failures",
        "advantages": "protects backend services, ensures fair usage, prevents accidental and malicious abuse, improves overall system stability",
        "challenges": "distributed rate limiting needs shared state (Redis), choosing appropriate limits, handling limit exceeded gracefully, authenticated vs anonymous users",
        "best practices": "use token bucket or sliding window algorithm, return 429 with Retry-After header, rate limit by authenticated user not just IP, implement exponential backoff in clients",
    },
}


def ingest_expert_knowledge():
    kb = get_knowledge()
    start = time.time()
    before = kb.stats()["total_facts"]
    added = 0

    print(f"🧠 Ingesting expert knowledge ({len(EXPERT_TOPICS)} topics × 6 dimensions)...")

    for topic, dims in EXPERT_TOPICS.items():
        for dim_name, content in dims.items():
            ok = kb.add_fact(
                topic=f"{topic} — {dim_name}",
                content=content,
                source="expert_knowledge",
                category="technical_deep",
                confidence=0.95,
            )
            if ok:
                added += 1

    after = kb.stats()["total_facts"]
    print(f"  ✅ Added {added} expert facts")
    print(f"  📊 Total: {after} (was {before})")
    print(f"  ⏱️  Time: {time.time()-start:.2f}s")
    return after


if __name__ == "__main__":
    ingest_expert_knowledge()
