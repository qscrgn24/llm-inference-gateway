from fastapi.testclient import TestClient

from app.main import create_app


def test_request_id_and_latency_headers_present():
    app = create_app()
    client = TestClient(app)

    response = client.get("v1/health")

    assert response.status_code == 200

    assert "X-Request-ID" in response.headers
    assert "X-Response-Time-ms" in response.headers

    latency = float(response.headers["X-Response-Time-ms"])
    assert latency >= 0.0


def test_upstream_request_id_is_preserved():
    app = create_app()
    client = TestClient(app)

    custom_id = "test-request-id-123"

    response = client.get("v1/health", headers={"X-Request-ID": custom_id})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == custom_id
