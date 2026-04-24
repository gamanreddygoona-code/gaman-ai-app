"""
teach_model.py
──────────────
Adds a few curated knowledge entries gathered from official web docs
into the local SQLite knowledge base so the chatbot can use them.
"""

from db import add_or_update_knowledge, get_knowledge_context, init_db


WEB_FACTS = [
    {
        "topic": "fastapi_basics",
        "content": (
            "FastAPI is a modern, high-performance Python web framework based on "
            "standard type hints, and it provides automatic interactive API docs "
            "at /docs plus alternative docs at /redoc. "
            "Source: https://fastapi.tiangolo.com/"
        ),
    },
    {
        "topic": "linear_regression_basics",
        "content": (
            "In scikit-learn, LinearRegression uses ordinary least squares to fit "
            "coefficients that minimize residual error between predicted and observed values. "
            "Source: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html"
        ),
    },
    {
        "topic": "sqlite_basics",
        "content": (
            "SQLite is a self-contained, serverless, zero-configuration, transactional "
            "SQL database engine with ACID transactions. "
            "Source: https://www.sqlite.org/about.html"
        ),
    },
    {
        "topic": "fastapi_testing",
        "content": (
            "FastAPI relies on the optional httpx dependency when using the TestClient, "
            "which is useful for local API testing and smoke tests. "
            "Source: https://fastapi.tiangolo.com/"
        ),
    },
    {
        "topic": "python_best_practices",
        "content": (
            "Always use type hints, docstrings for functions, and virtual environments for projects. "
            "Follow PEP 8 style guidelines. Use context managers (with statements) for file/resource handling. "
            "Avoid mutable default arguments in functions."
        ),
    },
    {
        "topic": "debugging_tips",
        "content": (
            "Use print() or logging to trace execution. Use debugger breakpoints. Read error messages carefully - "
            "they often point to the exact line and problem. Check variable values at suspicious points. "
            "Isolate the problem by testing small code chunks separately."
        ),
    },
    {
        "topic": "code_optimization",
        "content": (
            "Use list comprehensions instead of loops for better performance. Use generators for large datasets. "
            "Cache expensive operations with memoization. Profile code to find bottlenecks before optimizing. "
            "Choose appropriate data structures (dict for lookups, set for membership checks)."
        ),
    },
    {
        "topic": "api_security",
        "content": (
            "Always validate user input. Use HTTPS for sensitive data. Implement rate limiting. "
            "Use authentication (JWT, OAuth2) for protected endpoints. Never expose error details to users. "
            "Keep dependencies updated for security patches."
        ),
    },
    {
        "topic": "database_performance",
        "content": (
            "Add indexes to frequently queried columns. Use prepared statements to prevent SQL injection. "
            "Batch operations when possible. Normalize database schema to avoid redundancy. "
            "Use EXPLAIN QUERY PLAN to analyze query performance."
        ),
    },
    {
        "topic": "javascript_tips",
        "content": (
            "Use const by default, let when needed, avoid var. Always use strict equality (===). "
            "Use async/await instead of callbacks. Handle promise rejections. Use optional chaining (?.) "
            "and nullish coalescing (??) for safe property access."
        ),
    },
]


def main():
    init_db()

    print("Adding curated web knowledge to SQLite...")
    for fact in WEB_FACTS:
        add_or_update_knowledge(fact["topic"], fact["content"])
        print(f"  - saved topic: {fact['topic']}")

    print("\nLatest knowledge context preview:\n")
    print(get_knowledge_context(max_entries=8))


if __name__ == "__main__":
    main()
