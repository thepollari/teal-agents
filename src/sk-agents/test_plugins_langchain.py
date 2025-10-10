"""
Test plugin system with LangChain.
"""
import asyncio
from pydantic import BaseModel
from sk_agents.langchain_adapter.langchain_plugins import kernel_function
from sk_agents.langchain_adapter.plugin_converter import convert_sk_plugin_to_tools
from sk_agents.ska_types import BasePlugin


class TemperatureResponse(BaseModel):
    low: float
    high: float


class TestWeatherPlugin(BasePlugin):
    @kernel_function(description="Get temperature for a location")
    def get_temperature(self, lat: float, lng: float, timezone: str) -> TemperatureResponse:
        """Retrieve low and high temperatures for the day."""
        return TemperatureResponse(low=65.0, high=75.0)
    
    @kernel_function(description="Get coordinates for a location")
    def get_location(self, location: str) -> dict:
        """Get lat/lng for a location."""
        return {"lat": 37.7749, "lng": -122.4194, "timezone": "America/Los_Angeles"}


async def test():
    print("Testing plugin to tool conversion...")
    
    tools = convert_sk_plugin_to_tools(TestWeatherPlugin)
    
    print(f"✓ Converted {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    result = tools[0].invoke({"lat": 37.7, "lng": -122.4, "timezone": "America/Los_Angeles"})
    print(f"\n✓ Tool invocation result: {result}")
    
    print("\n✅ Plugin conversion working!")


if __name__ == "__main__":
    asyncio.run(test())
