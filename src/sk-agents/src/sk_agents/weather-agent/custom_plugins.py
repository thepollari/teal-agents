import json

import requests
from pydantic import BaseModel
from semantic_kernel.functions.kernel_function_decorator import kernel_function

from sk_agents.ska_types import BasePlugin


class WeatherData(BaseModel):
    temperature: float
    humidity: int
    wind_speed: float
    weather_code: int
    description: str


class CoordinatesData(BaseModel):
    latitude: float
    longitude: float
    name: str
    country: str


class WeatherPlugin(BasePlugin):
    def __init__(self, authorization: str | None = None, extra_data_collector=None):
        super().__init__(authorization, extra_data_collector)

    @kernel_function(description="Get current weather information for a city")
    def get_current_weather(self, city: str) -> str:
        try:
            coords_data = self._get_coordinates_data(city)
            if not coords_data:
                return json.dumps({"error": f"Could not find coordinates for {city}"})

            weather_url = (
                f"https://api.open-meteo.com/v1/current?"
                f"latitude={coords_data.latitude}&longitude={coords_data.longitude}"
                f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code"
                f"&temperature_unit=fahrenheit&wind_speed_unit=mph"
            )

            response = requests.get(weather_url, timeout=10)
            response.raise_for_status()
            weather_data = response.json()

            current = weather_data.get("current", {})
            weather_code = current.get("weather_code", 0)
            description = self._get_weather_description(weather_code)

            result = {
                "city": coords_data.name,
                "country": coords_data.country,
                "temperature": current.get("temperature_2m", 0),
                "humidity": current.get("relative_humidity_2m", 0),
                "wind_speed": current.get("wind_speed_10m", 0),
                "description": description,
                "units": {
                    "temperature": "°F",
                    "humidity": "%",
                    "wind_speed": "mph"
                }
            }

            return json.dumps(result)

        except Exception as e:
            return json.dumps({"error": f"Failed to get weather for {city}: {str(e)}"})

    @kernel_function(description="Get latitude and longitude coordinates for a city")
    def get_coordinates(self, city: str) -> str:
        try:
            coords_data = self._get_coordinates_data(city)
            if not coords_data:
                return json.dumps({"error": f"Could not find coordinates for {city}"})

            result = {
                "city": coords_data.name,
                "country": coords_data.country,
                "latitude": coords_data.latitude,
                "longitude": coords_data.longitude
            }

            return json.dumps(result)

        except Exception as e:
            return json.dumps({"error": f"Failed to get coordinates for {city}: {str(e)}"})

    def _get_coordinates_data(self, city: str) -> CoordinatesData | None:
        geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"

        response = requests.get(geocoding_url, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])
        if not results:
            return None

        result = results[0]
        return CoordinatesData(
            latitude=result.get("latitude", 0),
            longitude=result.get("longitude", 0),
            name=result.get("name", city),
            country=result.get("country", "Unknown")
        )

    def _get_weather_description(self, weather_code: int) -> str:
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        return weather_codes.get(weather_code, f"Unknown weather (code: {weather_code})")
