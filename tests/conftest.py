"""Pytest fixtures and test environment configuration."""

import pytest
from app import create_app
from app.models import db, User


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    application = create_app("testing")

    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client for issuing HTTP requests."""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Create a default user in the test database."""
    with app.app_context():
        user = User(username="testrunner", email="testrunner@example.edu")
        user.set_password("securepassword123")
        db.session.add(user)
        db.session.commit()
        # Keep user attributes populated
        db.session.refresh(user)
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
        # Create an object wrapper that behaves like user
        class UserProxy:
            id = user_data["id"]
            username = user_data["username"]
            email = user_data["email"]

        yield UserProxy()


@pytest.fixture
def auth_client(client, test_user):
    """Authenticated client fixture with test_user in session."""
    with client.session_transaction() as sess:
        sess["user_id"] = test_user.id
        sess["username"] = test_user.username
    return client
