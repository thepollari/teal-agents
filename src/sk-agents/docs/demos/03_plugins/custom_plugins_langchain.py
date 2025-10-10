"""
Weather plugin example - LangChain compatible version.

This demonstrates how to write plugins that work with the LangChain migration.
Uses the langchain_plugins decorator which is compatible with both SK and LC.
"""
import requests
from pydantic import BaseModel

# Use LangChain-compatible decorator
from sk_agents.langchain_adapter.langchain_plugins import kernel_function
from sk_agents.ska_types import BasePlugin


class LocationCoordinates(BaseModel):
    latitude: float
    longitude: float
    timezone: str


class DailyUnits(BaseModel):
    time: str
    temperature_2m_max: str
    temperature_2m_min: str


class Daily(BaseModel):
    time: list[str]
    temperature_2m_max: list[float]
    temperature_2m_min: list[float]


class TemperatureResponseInt(BaseModel):
    latitude: float
    longitude: float
    generationtime_ms: float
    utc_offset_seconds: int
    timezone: str
    timezone_abbreviation: str
    elevation: float
    daily_units: DailyUnits
    daily: Daily


class WeatherPlugin(BasePlugin):
    """Plugin for getting weather information."""

    @kernel_function(description="Retrieve the latitude, longitude, and timezone for a given location search string")
    def get_location_coords(self, location_string: str) -> LocationCoordinates:
        """Get coordinates for a location."""
        # Simplified implementation
        locations = {
            "san francisco": LocationCoordinates(
                latitude=37.7749, longitude=-122.4194, timezone="America/Los_Angeles"
            ),
            "new york": LocationCoordinates(
                latitude=40.7128, longitude=-74.0060, timezone="America/New_York"
            ),
        }
        return locations.get(location_string.lower(), LocationCoordinates(
            latitude=0.0, longitude=0.0, timezone="UTC"
        ))

    @kernel_function(description="Retrieve low and high temperatures for the day for a given location")
    def get_temperature(
        self, lat: float, lng: float, timezone: str
    ) -> TemperatureResponseInt:
        """Get temperature for coordinates."""
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&daily=temperature_2m_max,temperature_2m_min&timezone={timezone}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return TemperatureResponseInt(**data)
        except Exception as e:
            # Return mock data on error
            return TemperatureResponseInt(
                latitude=lat,
                longitude=lng,
                generationtime_ms=0.0,
                utc_offset_seconds=0,
                timezone=timezone,
                timezone_abbreviation="UTC",
                elevation=0.0,
                daily_units=DailyUnits(
                    time="iso8601",
                    temperature_2m_max="°F",
                    temperature_2m_min="°F"
                ),
                daily=Daily(
                    time=["2024-01-01"],
                    temperature_2m_max=[75.0],
                    temperature_2m_min=[60.0]
                )
            )
