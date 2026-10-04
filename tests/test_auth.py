"""Authentication and session management test cases."""

from app.models import User


def test_user_registration_success(client):
    """Verify new user registration creates database record and logs in."""
    payload = {
        "username": "newdeveloper",
        "email": "newdev@example.edu",
        "password": "strongPassword!2026"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["status"] == "success"
    assert data["user"]["username"] == "newdeveloper"


def test_user_registration_duplicate(client, test_user):
    """Verify duplicate username or email rejects registration."""
    payload = {
        "username": "testrunner",
        "email": "different@example.edu",
        "password": "password123"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 409


def test_user_login_success(client, test_user):
    """Verify valid credentials establish a user session."""
    payload = {
        "username": "testrunner",
        "password": "securepassword123"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"


def test_user_login_invalid_password(client, test_user):
    """Verify incorrect credentials return 401."""
    payload = {
        "username": "testrunner",
        "password": "wrongpassword"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401


def test_user_me_authenticated(auth_client, test_user):
    """Verify authenticated user can fetch profile details."""
    response = auth_client.get("/api/auth/me")
    assert response.status_code == 200
    data = response.get_json()
    assert data["user"]["username"] == test_user.username


def test_user_logout(auth_client):
    """Verify logout terminates user session."""
    response = auth_client.post("/api/auth/logout")
    assert response.status_code == 200

    # Next me check should fail
    me_resp = auth_client.get("/api/auth/me")
    assert me_resp.status_code == 401
