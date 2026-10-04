"""Weather service and query endpoint test cases."""

from app.services.weather_api import WeatherService


def test_weather_service_deterministic():
    """Verify WeatherService returns valid structured weather dictionary."""
    weather = WeatherService.get_weather(40.7128, -74.0060)
    assert "temperature" in weather
    assert "humidity" in weather
    assert "wind_speed" in weather
    assert "condition" in weather
    assert isinstance(weather["temperature"], (int, float))


def test_weather_endpoint_success(client):
    """Verify GET /api/weather/current returns 200 with coordinates."""
    response = client.get("/api/weather/current?latitude=51.5074&longitude=-0.1278")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert "data" in data
    assert data["data"]["latitude"] == 51.5074


def test_weather_endpoint_missing_params(client):
    """Verify missing coordinates return 400."""
    response = client.get("/api/weather/current")
    assert response.status_code == 400


def test_weather_endpoint_invalid_range(client):
    """Verify out-of-range coordinates return 400."""
    response = client.get("/api/weather/current?latitude=120.0&longitude=0.0")
    assert response.status_code == 400
