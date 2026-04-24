import requests

BASE_URL = "http://127.0.0.1:8000"


def fetch_json(method: str, path: str, **kwargs):
    response = requests.request(method, f"{BASE_URL}{path}", timeout=15, **kwargs)
    response.raise_for_status()
    return response.json()


def main():
    status = fetch_json("GET", "/status")
    print("status:", status)
    assert "model_mode" in status

    scenarios = [
        {
            "name": "greeting",
            "message": "hello",
            "must_include": "Supported languages include",
        },
        {
            "name": "python hello world",
            "message": "Write a Python hello world",
            "must_include": "```python",
        },
        {
            "name": "c++ add function",
            "message": "Show a C++ function to add two numbers",
            "must_include": "```cpp",
        },
        {
            "name": "javascript file read",
            "message": "How do I read a file in JavaScript?",
            "must_include": "readFileSync",
        },
        {
            "name": "api explanation",
            "message": "Explain what an API is",
            "must_include": "An API is a way for one program to talk to another",
        },
        {
            "name": "sql list tables",
            "message": "Show a SQL query to list all tables",
            "must_include": "sqlite_master",
        },
    ]

    for scenario in scenarios:
        response = fetch_json("POST", "/chat", json={"message": scenario["message"]})
        print(f"{scenario['name']}:", response)
        assert scenario["must_include"] in response["reply"]


if __name__ == "__main__":
    main()
