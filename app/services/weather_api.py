"""Open-Meteo Weather API Client with deterministic offline fallback."""

import math
from typing import Dict, Any
import requests

WMO_WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm"
}


class WeatherService:
    """Service to fetch real-time weather metrics from Open-Meteo API with fallback."""

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    @classmethod
    def get_weather(cls, latitude: float, longitude: float) -> Dict[str, Any]:
        """Fetch current weather for given latitude and longitude.

        Falls back to a simulated weather report if network is unavailable or request fails.
        """
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
                "timezone": "auto"
            }
            response = requests.get(cls.BASE_URL, params=params, timeout=3.0)
            if response.status_code == 200:
                data = response.json()
                current = data.get("current", {})
                code = current.get("weather_code", 0)
                return {
                    "source": "live",
                    "latitude": latitude,
                    "longitude": longitude,
                    "temperature": current.get("temperature_2m", 20.0),
                    "apparent_temperature": current.get("apparent_temperature", 20.0),
                    "humidity": current.get("relative_humidity_2m", 50),
                    "precipitation": current.get("precipitation", 0.0),
                    "wind_speed": current.get("wind_speed_10m", 5.0),
                    "weather_code": code,
                    "condition": WMO_WEATHER_CODES.get(code, "Clear sky"),
                    "time": current.get("time", "")
                }
        except Exception:
            # Deterministic offline fallback
            pass

        return cls._generate_fallback_weather(latitude, longitude)

    @classmethod
    def _generate_fallback_weather(cls, latitude: float, longitude: float) -> Dict[str, Any]:
        """Generate deterministic offline weather metrics based on geographic coordinates."""
        # Simulated seasonal baseline using coordinates
        norm_lat = max(min(latitude, 90.0), -90.0)
        base_temp = round(30.0 - (abs(norm_lat) * 0.45) + (math.sin(longitude) * 2.0), 1)
        humidity = int(45 + (abs(math.cos(latitude)) * 30))
        wind_speed = round(4.0 + (abs(math.sin(longitude)) * 12.0), 1)

        code = 1 if base_temp > 22 else (2 if base_temp > 15 else 3)
        return {
            "source": "simulated_fallback",
            "latitude": latitude,
            "longitude": longitude,
            "temperature": base_temp,
            "apparent_temperature": round(base_temp - 1.2, 1),
            "humidity": humidity,
            "precipitation": 0.0,
            "wind_speed": wind_speed,
            "weather_code": code,
            "condition": WMO_WEATHER_CODES.get(code, "Partly cloudy"),
            "time": "offline-cached"
        }
