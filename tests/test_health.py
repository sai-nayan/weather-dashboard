"""Health check and telemetry endpoint test cases."""


def test_health_endpoint(client):
    """Verify /health endpoint returns 200 with service details."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "weather-dashboard"
    assert "version" in data


def test_metrics_endpoint(client):
    """Verify /metrics telemetry endpoint returns operational counters."""
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "up"
    assert "active_connections" in data["metrics"]
