"""Web UI frontend route handlers."""

from flask import Blueprint, render_template, session, redirect, url_for, request
from app.models import User, FavoriteLocation
from app.services.weather_api import WeatherService

web_bp = Blueprint("web", __name__)


@web_bp.route("/")
def dashboard_page():
    """Main dashboard page displaying user favorite locations and current conditions."""
    if "user_id" not in session:
        return redirect(url_for("web.login_page"))

    user = db.session.get(User, session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("web.login_page"))

    locations = FavoriteLocation.query.filter_by(user_id=user.id).order_by(FavoriteLocation.created_at.desc()).all()

    enriched_locations = []
    for loc in locations:
        weather = WeatherService.get_weather(loc.latitude, loc.longitude)
        alert = weather["temperature"] >= loc.temp_alert_threshold
        enriched_locations.append({
            "model": loc,
            "weather": weather,
            "alert": alert
        })

    return render_template(
        "dashboard.html",
        user=user,
        locations=enriched_locations,
        total_locations=len(enriched_locations)
    )


@web_bp.route("/login")
def login_page():
    """Render user login view."""
    if "user_id" in session:
        return redirect(url_for("web.dashboard_page"))
    error = request.args.get("error")
    return render_template("login.html", error=error)


@web_bp.route("/register")
def register_page():
    """Render user registration view."""
    if "user_id" in session:
        return redirect(url_for("web.dashboard_page"))
    return render_template("register.html")
