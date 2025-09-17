import requests
from pydantic import BaseModel
from semantic_kernel.functions.kernel_function_decorator import kernel_function

from sk_agents.ska_types import BasePlugin


class WeatherData(BaseModel):
    city: str
    temperature: float
    condition: str
    description: str
    humidity: int
    wind_speed: float


class WeatherPlugin(BasePlugin):
    @kernel_function(
        description="Get current weather information for a specified city"
    )
    def get_weather(self, city: str) -> WeatherData:
        """
        Get current weather information for a city using Open-Meteo API.
        
        Args:
            city: Name of the city to get weather for
            
        Returns:
            WeatherData object with current weather information
            
        Raises:
            ValueError: If city is not found or API request fails
        """
        try:
            geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
            
            geo_response = requests.get(geocoding_url, timeout=10)
            geo_response.raise_for_status()
            geo_data = geo_response.json()
            
            if not geo_data.get("results"):
                raise ValueError(f"City '{city}' not found. Please check the spelling and try again.")
            
            location = geo_data["results"][0]
            lat = location["latitude"]
            lon = location["longitude"]
            city_name = location["name"]
            
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m&temperature_unit=fahrenheit&wind_speed_unit=mph"
            
            weather_response = requests.get(weather_url, timeout=10)
            weather_response.raise_for_status()
            weather_data = weather_response.json()
            
            current = weather_data["current"]
            
            weather_code = current["weather_code"]
            condition, description = self._get_weather_description(weather_code)
            
            return WeatherData(
                city=city_name,
                temperature=round(current["temperature_2m"], 1),
                condition=condition,
                description=description,
                humidity=current["relative_humidity_2m"],
                wind_speed=round(current["wind_speed_10m"], 1)
            )
            
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch weather data: {str(e)}")
        except KeyError as e:
            raise ValueError(f"Unexpected response format from weather API: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error getting weather for '{city}': {str(e)}")
    
    def _get_weather_description(self, weather_code: int) -> tuple[str, str]:
        """
        Convert weather code to human-readable condition and description.
        
        Args:
            weather_code: WMO weather code
            
        Returns:
            Tuple of (condition, description)
        """
        weather_codes = {
            0: ("Clear", "Clear sky"),
            1: ("Mostly Clear", "Mainly clear"),
            2: ("Partly Cloudy", "Partly cloudy"),
            3: ("Overcast", "Overcast"),
            45: ("Foggy", "Fog"),
            48: ("Foggy", "Depositing rime fog"),
            51: ("Light Drizzle", "Light drizzle"),
            53: ("Moderate Drizzle", "Moderate drizzle"),
            55: ("Dense Drizzle", "Dense drizzle"),
            56: ("Light Freezing Drizzle", "Light freezing drizzle"),
            57: ("Dense Freezing Drizzle", "Dense freezing drizzle"),
            61: ("Light Rain", "Slight rain"),
            63: ("Moderate Rain", "Moderate rain"),
            65: ("Heavy Rain", "Heavy rain"),
            66: ("Light Freezing Rain", "Light freezing rain"),
            67: ("Heavy Freezing Rain", "Heavy freezing rain"),
            71: ("Light Snow", "Slight snow fall"),
            73: ("Moderate Snow", "Moderate snow fall"),
            75: ("Heavy Snow", "Heavy snow fall"),
            77: ("Snow Grains", "Snow grains"),
            80: ("Light Rain Showers", "Slight rain showers"),
            81: ("Moderate Rain Showers", "Moderate rain showers"),
            82: ("Violent Rain Showers", "Violent rain showers"),
            85: ("Light Snow Showers", "Slight snow showers"),
            86: ("Heavy Snow Showers", "Heavy snow showers"),
            95: ("Thunderstorm", "Thunderstorm"),
            96: ("Thunderstorm with Hail", "Thunderstorm with slight hail"),
            99: ("Thunderstorm with Hail", "Thunderstorm with heavy hail"),
        }
        
        return weather_codes.get(weather_code, ("Unknown", "Unknown weather condition"))
