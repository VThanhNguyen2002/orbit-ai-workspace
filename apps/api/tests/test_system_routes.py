from fastapi.testclient import TestClient


def test_health_returns_success_envelope(client: TestClient) -> None:
    response = client.get("/v1/health")

    assert response.status_code == 200
    assert response.headers["x-request-id"].startswith("req_")
    assert response.json() == {
        "data": {
            "status": "ok",
            "service": "synapse-api",
        },
        "meta": {
            "request_id": response.headers["x-request-id"],
        },
    }


def test_version_returns_api_metadata(client: TestClient) -> None:
    response = client.get("/v1/version", headers={"x-request-id": "req_test"})

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "req_test"
    assert response.json() == {
        "data": {
            "service": "synapse-api",
            "version": "0.0.0",
            "api_version": "v1",
        },
        "meta": {
            "request_id": "req_test",
        },
    }


def test_not_found_uses_api_error_envelope(client: TestClient) -> None:
    response = client.get("/v1/missing", headers={"x-request-id": "req_missing"})

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "NOT_FOUND",
            "message": "Not Found",
        },
        "meta": {
            "request_id": "req_missing",
        },
    }
