"""Gets the weather at a certain location.

This tool retrieves the weather information for a specified location using Open-Meteo API.
"""


import requests
from pydantic import BaseModel


class Input(BaseModel):
    location: str


class Output(BaseModel):
    weather: str


def get_coordinates(location: str) -> tuple[float, float] | None:
    """Get latitude and longitude for a location using Open-Meteo geocoding API."""
    try:
        geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {"name": location, "count": 1, "language": "en", "format": "json"}
        response = requests.get(geocoding_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("results"):
            result = data["results"][0]
            return result["latitude"], result["longitude"]
        return None
    except Exception as e:
        raise Exception(f"Failed to geocode location: {str(e)}")


def get_weather(location: str) -> str:
    """Get current weather for a location using Open-Meteo API."""
    # Get coordinates first
    coords = get_coordinates(location)
    if not coords:
        return f"Could not find location: {location}"

    latitude, longitude = coords

    # Get weather data
    try:
        weather_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
            "temperature_unit": "celsius",
            "wind_speed_unit": "kmh",
            "precipitation_unit": "mm",
        }
        response = requests.get(weather_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        current = data["current"]

        # Weather code interpretation (WMO codes)
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            95: "Thunderstorm",
        }

        weather_desc = weather_codes.get(
            current.get("weather_code", 0), "Unknown conditions"
        )

        weather_info = f"""Weather in {location}:
- Condition: {weather_desc}
- Temperature: {current['temperature_2m']}°C (feels like {current['apparent_temperature']}°C)
- Humidity: {current['relative_humidity_2m']}%
- Wind Speed: {current['wind_speed_10m']} km/h
- Precipitation: {current['precipitation']} mm
"""
        return weather_info

    except Exception as e:
        return f"Failed to retrieve weather data: {str(e)}"


def execute(input_data: Input) -> Output:
    return Output(weather=get_weather(input_data.location))
