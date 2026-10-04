"""Favorite locations CRUD test cases."""

from app.models import FavoriteLocation


def test_create_location(auth_client):
    """Verify adding a favorite location returns 201 and stores record."""
    payload = {
        "city_name": "San Francisco",
        "country": "United States",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "temp_alert_threshold": 26.5,
        "notes": "Bay area monitoring station"
    }
    response = auth_client.post("/api/locations", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["location"]["city_name"] == "San Francisco"
    assert data["location"]["temp_alert_threshold"] == 26.5


def test_list_locations(auth_client):
    """Verify listing locations returns active items with enriched metrics."""
    # Add a location first
    auth_client.post("/api/locations", json={
        "city_name": "Zurich",
        "country": "Switzerland",
        "latitude": 47.3769,
        "longitude": 8.5417,
        "temp_alert_threshold": 22.0
    })

    response = auth_client.get("/api/locations")
    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] >= 1
    assert "current_weather" in data["locations"][0]


def test_update_location(auth_client):
    """Verify updating location notes and threshold."""
    create_resp = auth_client.post("/api/locations", json={
        "city_name": "Dublin",
        "country": "Ireland",
        "latitude": 53.3498,
        "longitude": -6.2603,
        "temp_alert_threshold": 20.0
    })
    loc_id = create_resp.get_json()["location"]["id"]

    update_resp = auth_client.put(f"/api/locations/{loc_id}", json={
        "temp_alert_threshold": 25.0,
        "notes": "Updated threshold after spring inspection"
    })
    assert update_resp.status_code == 200
    assert update_resp.get_json()["location"]["temp_alert_threshold"] == 25.0


def test_delete_location(auth_client):
    """Verify deleting a location removes it from storage."""
    create_resp = auth_client.post("/api/locations", json={
        "city_name": "Tokyo",
        "country": "Japan",
        "latitude": 35.6762,
        "longitude": 139.6503,
        "temp_alert_threshold": 28.0
    })
    loc_id = create_resp.get_json()["location"]["id"]

    del_resp = auth_client.delete(f"/api/locations/{loc_id}")
    assert del_resp.status_code == 200

    # Ensure not found
    get_resp = auth_client.get(f"/api/locations/{loc_id}")
    assert get_resp.status_code == 404


def test_unauthenticated_access_denied(client):
    """Verify unauthorized client cannot access locations API."""
    response = client.get("/api/locations")
    assert response.status_code == 401
