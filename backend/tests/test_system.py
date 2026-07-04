def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["environment"] == "development"
    assert payload["database"] in {"healthy", "unhealthy"}


def test_version_endpoint(client):
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    payload = response.json()
    assert payload["api_version"] == "/api/v1"


def test_openapi_available(client):
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    payload = response.json()
    assert "/api/v1/health" in payload["paths"]
