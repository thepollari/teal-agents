"""
Test if plugins work with LangChain migration.

Plugins in SK use @kernel_function decorator from Semantic Kernel.
We need to check if these can work with LangChain's tool system.
"""
import asyncio
from langchain_core.tools import tool
from pydantic import BaseModel, Field

# Example: Converting SK plugin to LangChain tool
class TemperatureResponse(BaseModel):
    low: float = Field(description="Low temperature in Fahrenheit")
    high: float = Field(description="High temperature in Fahrenheit")

@tool
def get_temperature(lat: float, lng: float, timezone: str) -> TemperatureResponse:
    """Retrieve low and high temperatures for the day for a given location."""
    # Mock implementation
    return TemperatureResponse(low=65.0, high=75.0)

@tool  
def get_location_coords(location_string: str) -> dict:
    """Retrieve the latitude, longitude, and timezone for a given location search string."""
    # Mock implementation
    return {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "timezone": "America/Los_Angeles"
    }

async def test_langchain_tools():
    """Test that LangChain tools can be created."""
    tools = [get_temperature, get_location_coords]
    
    print("LangChain Tools Created:")
    for t in tools:
        print(f"  - {t.name}: {t.description}")
    
    # Test invocation
    result = get_temperature.invoke({
        "lat": 37.7749,
        "lng": -122.4194,
        "timezone": "America/Los_Angeles"
    })
    print(f"\nTest invocation result: {result}")
    print("\n✅ LangChain tools working!")

if __name__ == "__main__":
    asyncio.run(test_langchain_tools())
