"""
End-to-end plugin test with handler and real API.
"""
import asyncio
import os
from pydantic import BaseModel
from sk_agents.ska_types import BasePlugin
from sk_agents.langchain_adapter.langchain_plugins import kernel_function
from sk_agents.langchain_handler import langchain_handle
from pydantic_yaml import parse_yaml_raw_as
from sk_agents.ska_types import BaseConfig
from ska_utils import AppConfig, initialize_telemetry
from sk_agents.configs import configs
from sk_agents.plugin_loader import get_plugin_loader


class CityWeather(BaseModel):
    city: str
    temperature: float
    conditions: str


class SimpleWeatherPlugin(BasePlugin):
    """Simple weather plugin."""
    
    @kernel_function(description="Get current weather for a city")
    def get_weather(self, city: str) -> CityWeather:
        """Get weather for a city."""
        weather_data = {
            "san francisco": CityWeather(city="San Francisco", temperature=65.0, conditions="foggy"),
            "seattle": CityWeather(city="Seattle", temperature=55.0, conditions="rainy"),
            "miami": CityWeather(city="Miami", temperature=85.0, conditions="sunny"),
        }
        return weather_data.get(city.lower(), CityWeather(city=city, temperature=70.0, conditions="clear"))


async def test():
    print("=== End-to-End Plugin Test ===\n")
    
    # Setup
    AppConfig.add_configs(configs)
    app_config = AppConfig()
    initialize_telemetry('test-e2e', app_config)
    
    # Load plugin
    import types
    plugin_loader = get_plugin_loader()
    custom_module = types.ModuleType("weather_plugin")
    custom_module.SimpleWeatherPlugin = SimpleWeatherPlugin
    plugin_loader.custom_module = custom_module
    
    # Create config
    config_yaml = """
apiVersion: skagents/v1
kind: Chat
description: Weather bot
service_name: WeatherBot
version: 0.1
input_type: BaseInput
plugin_module: weather_plugin.py
spec:
  agent:
    name: weather
    role: Weather Assistant
    model: gemini-2.0-flash
    system_prompt: You are a weather assistant. Use the get_weather tool when asked about weather. Always call the tool to get accurate data.
    plugins:
      - SimpleWeatherPlugin
"""
    
    config = parse_yaml_raw_as(BaseConfig, config_yaml)
    handler = langchain_handle(config, app_config)
    
    print(f"✓ Handler created: {type(handler).__name__}")
    
    # Check tools
    if hasattr(handler, 'agent') and hasattr(handler.agent, 'tools'):
        print(f"✓ Agent has {len(handler.agent.tools)} tools")
        for tool in handler.agent.tools:
            print(f"  - {tool.name}")
    
    # Test invoke
    print("\nTesting handler with weather query...")
    inputs = {
        'chat_history': [
            {'role': 'user', 'content': 'What is the weather in Seattle? Please use the get_weather tool.'}
        ]
    }
    
    result = await handler.invoke(inputs)
    print(f"\n✓ Response received")
    print(f"Output: {result.get('output', '')[:300]}")
    
    # Check if response mentions weather data
    output_lower = result.get('output', '').lower()
    if 'rain' in output_lower or '55' in result.get('output', '') or 'seattle' in output_lower:
        print("\n✅ Response contains weather data - tool was likely used!")
    else:
        print(f"\n⚠️ Unclear if tool was used. Full output:\n{result.get('output', '')}")
    
    if 'usage' in result:
        print(f"\nToken usage: {result['usage']}")


if __name__ == "__main__":
    asyncio.run(test())
