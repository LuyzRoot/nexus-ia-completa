"""
Weather lookup helper using Open-Meteo (public, no key).
- get_weather_forecast(city) -> dict with city, country, temperature_c, condition, humidity_percent, wind_kmh
"""
import httpx
import logging
from typing import Dict

logger = logging.getLogger("tools.weather")

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
    45: "fog", 48: "depositing rime fog", 51: "drizzle: light", 53: "drizzle: moderate", 55: "drizzle: dense",
    61: "rain: slight", 63: "rain: moderate", 65: "rain: heavy", 71: "snow: slight", 73: "snow: moderate",
    75: "snow: heavy", 80: "rain showers: slight", 81: "rain showers: moderate", 82: "rain showers: violent",
    95: "thunderstorm", 96: "thunderstorm with hail"
}

async def get_weather_forecast(city: str) -> Dict:
    if not city:
        return {"error": "City not provided"}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            geo = await client.get(GEOCODING_URL, params={"name": city, "count": 1, "language": "en"})
            geo.raise_for_status()
            geo_data = geo.json()
            results = geo_data.get("results") or []
            if not results:
                return {"error": f"City '{city}' not found"}
            place = results[0]
            lat, lon = place["latitude"], place["longitude"]

            weather = await client.get(FORECAST_URL, params={
                "latitude": lat,
                "longitude": lon,
                "current_weather": True,
                "timezone": "auto"
            })
            weather.raise_for_status()
            wdata = weather.json().get("current_weather") or weather.json().get("current", {})
            # Some Open-Meteo versions use different keys; try common ones
            temp = wdata.get("temperature") or wdata.get("temperature_2m")
            code = wdata.get("weathercode") or wdata.get("weather_code")
            wind = wdata.get("windspeed") or wdata.get("wind_speed_10m")
            return {
                "city": place.get("name"),
                "country": place.get("country"),
                "temperature_c": temp,
                "condition": WEATHER_CODES.get(code, "unknown"),
                "wind_kmh": wind,
            }
    except httpx.HTTPStatusError as exc:
        logger.warning("weather API returned error: %s", exc)
        return {"error": str(exc)}
    except Exception as exc:
        logger.exception("weather lookup failed: %s", exc)
        return {"error": str(exc)}