from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


def utcnow():
    """Return timezone-aware current UTC time."""
    return datetime.now(timezone.utc)


class User(db.Model):
    """Represents a registered user of the application."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)

    favorite_locations = db.relationship(
        "FavoriteLocation",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def set_password(self, password: str) -> None:
        """Hash and store the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class FavoriteLocation(db.Model):
    """A location a user has marked as a favorite for weather alerts."""

    __tablename__ = "favorite_locations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    city_name = db.Column(db.String(120), nullable=False)
    country = db.Column(db.String(80), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    temp_alert_threshold = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self) -> dict:
        """Serialize the location into a dictionary for API responses."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "city_name": self.city_name,
            "country": self.country,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "temp_alert_threshold": self.temp_alert_threshold,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<FavoriteLocation {self.city_name}, {self.country}>"
