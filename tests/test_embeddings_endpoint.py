from fastapi.testclient import TestClient

from app.main import create_app


def test_embeddings_success_single_test():
    app = create_app()
    client = TestClient(app)

    payload = {"input": "hello world", "model": "test-embed-model"}

    response = client.post("/v1/embeddings", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert "embeddings" in data
    assert isinstance(data["embeddings"], list)
    assert len(data["embeddings"]) == 1
    assert isinstance(data["embeddings"][0], list)
    assert "model" in data
    assert "latency_ms" in data
    assert "request_id" in data


def test_embeddings_success_batch_texts():
    app = create_app()
    client = TestClient(app)

    payload = {"input": ["a", "b", "c"], "model": "test-embed-model"}

    response = client.post("/v1/embeddings", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert len(data["embeddings"]) == 3