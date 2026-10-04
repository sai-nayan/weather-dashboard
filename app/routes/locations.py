"""Location CRUD endpoints for user favorite locations."""

from flask import Blueprint, request, jsonify, session, redirect, url_for
from app.models import db, FavoriteLocation
from app.routes.auth import login_required
from app.services.weather_api import WeatherService

locations_bp = Blueprint("locations", __name__, url_prefix="/api/locations")


@locations_bp.route("", methods=["GET"])
@login_required
def list_locations():
    """List all favorite locations for the logged in user."""
    user_id = session["user_id"]
    locations = FavoriteLocation.query.filter_by(user_id=user_id).order_by(FavoriteLocation.created_at.desc()).all()

    results = []
    for loc in locations:
        loc_data = loc.to_dict()
        # Optionally attach current weather summary
        weather = WeatherService.get_weather(loc.latitude, loc.longitude)
        loc_data["current_weather"] = weather
        loc_data["alert_triggered"] = weather["temperature"] >= loc.temp_alert_threshold
        results.append(loc_data)

    return jsonify({"status": "success", "count": len(results), "locations": results}), 200


@locations_bp.route("", methods=["POST"])
@login_required
def create_location():
    """Create a new favorite location for the current user."""
    data = request.get_json(silent=True) or request.form
    user_id = session["user_id"]

    city_name = data.get("city_name", "").strip()
    country = data.get("country", "").strip()
    lat_val = data.get("latitude")
    lon_val = data.get("longitude")
    threshold_val = data.get("temp_alert_threshold", 30.0)
    notes = data.get("notes", "").strip()

    if not city_name or not country or lat_val is None or lon_val is None:
        return jsonify({"error": "Bad Request", "message": "city_name, country, latitude, and longitude are required"}), 400

    try:
        latitude = float(lat_val)
        longitude = float(lon_val)
        temp_alert_threshold = float(threshold_val)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid format", "message": "latitude, longitude, and threshold must be numbers"}), 400

    if not (-90.0 <= latitude <= 90.0) or not (-180.0 <= longitude <= 180.0):
        return jsonify({"error": "Out of range", "message": "Latitude must be [-90, 90] and Longitude [-180, 180]"}), 400

    location = FavoriteLocation(
        user_id=user_id,
        city_name=city_name,
        country=country,
        latitude=latitude,
        longitude=longitude,
        temp_alert_threshold=temp_alert_threshold,
        notes=notes
    )
    db.session.add(location)
    db.session.commit()

    if not request.is_json and request.form:
        return redirect(url_for("web.dashboard_page"))

    return jsonify({
        "status": "success",
        "message": "Favorite location added",
        "location": location.to_dict()
    }), 201


@locations_bp.route("/<int:location_id>", methods=["GET"])
@login_required
def get_location(location_id: int):
    """Retrieve details for a single location."""
    user_id = session["user_id"]
    location = FavoriteLocation.query.filter_by(id=location_id, user_id=user_id).first()
    if not location:
        return jsonify({"error": "Not Found", "message": "Location not found"}), 404

    data = location.to_dict()
    data["current_weather"] = WeatherService.get_weather(location.latitude, location.longitude)
    return jsonify({"status": "success", "location": data}), 200


@locations_bp.route("/<int:location_id>", methods=["PUT", "PATCH"])
@login_required
def update_location(location_id: int):
    """Update an existing favorite location."""
    user_id = session["user_id"]
    location = FavoriteLocation.query.filter_by(id=location_id, user_id=user_id).first()
    if not location:
        return jsonify({"error": "Not Found", "message": "Location not found"}), 404

    data = request.get_json(silent=True) or request.form

    if "city_name" in data and data["city_name"]:
        location.city_name = str(data["city_name"]).strip()
    if "country" in data and data["country"]:
        location.country = str(data["country"]).strip()
    if "latitude" in data:
        try:
            val = float(data["latitude"])
            if -90.0 <= val <= 90.0:
                location.latitude = val
        except ValueError:
            pass
    if "longitude" in data:
        try:
            val = float(data["longitude"])
            if -180.0 <= val <= 180.0:
                location.longitude = val
        except ValueError:
            pass
    if "temp_alert_threshold" in data:
        try:
            location.temp_alert_threshold = float(data["temp_alert_threshold"])
        except ValueError:
            pass
    if "notes" in data:
        location.notes = str(data["notes"]).strip()

    db.session.commit()
    return jsonify({
        "status": "success",
        "message": "Location updated successfully",
        "location": location.to_dict()
    }), 200


@locations_bp.route("/<int:location_id>", methods=["DELETE"])
@login_required
def delete_location(location_id: int):
    """Delete a favorite location."""
    user_id = session["user_id"]
    location = FavoriteLocation.query.filter_by(id=location_id, user_id=user_id).first()
    if not location:
        return jsonify({"error": "Not Found", "message": "Location not found"}), 404

    db.session.delete(location)
    db.session.commit()
    return jsonify({"status": "success", "message": "Location deleted successfully"}), 200


@locations_bp.route("/delete/<int:location_id>", methods=["POST"])
@login_required
def delete_location_form(location_id: int):
    """HTML form handler for deleting a location."""
    user_id = session["user_id"]
    location = FavoriteLocation.query.filter_by(id=location_id, user_id=user_id).first()
    if location:
        db.session.delete(location)
        db.session.commit()
    return redirect(url_for("web.dashboard_page"))
