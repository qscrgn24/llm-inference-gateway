from fastapi.testclient import TestClient

from app.main import create_app


def test_chat_success():
    app = create_app()
    client = TestClient(app)

    payload = {
        "messages": [
            {"role": "user", "content": "hello"}
        ],
        "model": "test-model",
        "temperature": 0.7,
        "max_output_tokens": 50,
    }

    response = client.post("v1/chat", json=payload)

    assert response.status_code == 200

    data = response.json

    assert "text" in data
    assert "model" in data
    assert "latency_ms" in data
    assert "request_id" in data