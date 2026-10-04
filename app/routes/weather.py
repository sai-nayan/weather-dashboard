"""Direct weather querying API routes."""

from flask import Blueprint, request, jsonify
from app.services.weather_api import WeatherService

weather_bp = Blueprint("weather", __name__, url_prefix="/api/weather")


@weather_bp.route("/current", methods=["GET"])
def get_current_weather():
    """Query current weather by coordinates."""
    lat_param = request.args.get("latitude") or request.args.get("lat")
    lon_param = request.args.get("longitude") or request.args.get("lon")

    if lat_param is None or lon_param is None:
        return jsonify({
            "error": "Missing parameters",
            "message": "Both latitude and longitude query parameters are required"
        }), 400

    try:
        latitude = float(lat_param)
        longitude = float(lon_param)
    except ValueError:
        return jsonify({
            "error": "Invalid format",
            "message": "Latitude and longitude must be valid floating point numbers"
        }), 400

    if not (-90.0 <= latitude <= 90.0) or not (-180.0 <= longitude <= 180.0):
        return jsonify({
            "error": "Out of range",
            "message": "Latitude must be between -90 and 90, Longitude between -180 and 180"
        }), 400

    weather_data = WeatherService.get_weather(latitude, longitude)
    return jsonify({
        "status": "success",
        "data": weather_data
    }), 200
