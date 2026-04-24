import requests

BASE_URL = "http://127.0.0.1:8001"


def fetch_json(method: str, path: str, **kwargs):
    response = requests.request(method, f"{BASE_URL}{path}", timeout=10, **kwargs)
    response.raise_for_status()
    return response.json()


def main():
    health = fetch_json("GET", "/health")
    print("Health:", health)
    assert health["status"] == "ok"
    assert health["model_loaded"] is True

    scenarios = [
        {
            "name": "valid floats",
            "message": "Predict 2.5 2.0 3.0",
            "expected_features": [2.5, 2.0, 3.0],
        },
        {
            "name": "valid ints",
            "message": "Predict 2 3 4",
            "expected_features": [2.0, 3.0, 4.0],
        },
        {
            "name": "negative ints",
            "message": "Predict -2 -3 -4",
            "expected_features": [-2.0, -3.0, -4.0],
        },
        {
            "name": "negative floats",
            "message": "Predict -2.5 -3.0 -4.75",
            "expected_features": [-2.5, -3.0, -4.75],
        },
    ]

    for scenario in scenarios:
        prediction = fetch_json("POST", "/chat", json={"message": scenario["message"]})
        print(f"{scenario['name']}:", prediction)

        if "prediction" not in prediction or "features" not in prediction:
            raise RuntimeError(
                f"Expected structured prediction fields were not returned for {scenario['name']}."
            )

        if prediction["features"] != scenario["expected_features"]:
            raise RuntimeError(
                f"Feature extraction failed for {scenario['name']}: "
                f"expected {scenario['expected_features']}, got {prediction['features']}"
            )

    greeting = fetch_json("POST", "/chat", json={"message": "hello"})
    print("greeting:", greeting)
    assert "Give me 3 numbers" in greeting["reply"]

    insufficient = fetch_json("POST", "/chat", json={"message": "Predict 2.5 3.0"})
    print("insufficient:", insufficient)
    assert "provide 3 numerical features" in insufficient["reply"]

    empty_response = requests.post(
        f"{BASE_URL}/chat",
        json={"message": "   "},
        timeout=10,
    )
    print("empty:", empty_response.status_code, empty_response.json())
    assert empty_response.status_code == 400
    assert empty_response.json()["error"] == "Empty message"


if __name__ == "__main__":
    main()
