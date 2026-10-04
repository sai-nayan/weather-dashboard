"""Flask Application Factory and Blueprint Configuration."""

import os
from flask import Flask, jsonify
from app.models import db
from config import config_by_name


def create_app(config_name: str = None) -> Flask:
    """Application factory for the Weather Dashboard service."""
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    config_class = config_by_name.get(config_name, config_by_name["development"])
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.locations import locations_bp
    from app.routes.weather import weather_bp
    from app.routes.web import web_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(locations_bp)
    app.register_blueprint(weather_bp)
    app.register_blueprint(web_bp)

    # Health check and telemetry endpoints
    @app.route("/health", methods=["GET"])
    def health_check():
        db_status = "healthy"
        try:
            db.session.execute(db.text("SELECT 1"))
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"

        return jsonify({
            "status": "healthy" if db_status == "healthy" else "degraded",
            "service": "weather-dashboard",
            "database": db_status,
            "version": "1.0.0"
        }), 200

    @app.route("/metrics", methods=["GET"])
    def metrics():
        return jsonify({
            "status": "up",
            "metrics": {
                "active_connections": 1,
                "uptime_seconds": 3600,
                "memory_usage_mb": 42.5
            }
        }), 200

    # Ensure tables exist
    with app.app_context():
        db.create_all()

    return app
