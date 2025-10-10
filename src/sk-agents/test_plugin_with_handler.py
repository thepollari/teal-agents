"""
Test plugin execution through full handler stack.

This is the ultimate validation - plugins working through the actual handler.
"""
import asyncio
import os
from pydantic import BaseModel, Field
from sk_agents.ska_types import BasePlugin
from sk_agents.langchain_handler import langchain_handle
from pydantic_yaml import parse_yaml_raw_as
from sk_agents.ska_types import BaseConfig
from ska_utils import AppConfig, initialize_telemetry
from sk_agents.configs import configs
from sk_agents.plugin_loader import get_plugin_loader
from semantic_kernel.functions.kernel_function_decorator import kernel_function


class WeatherData(BaseModel):
    """Weather data response."""
    temperature: float = Field(description="Temperature in Fahrenheit")
    conditions: str = Field(description="Weather conditions")


class SimpleWeatherPlugin(BasePlugin):
    """Simple weather plugin for testing."""
    
    @kernel_function(description="Get current weather for a city")
    def get_weather(self, city: str) -> WeatherData:
        """Get weather for a city."""
        # Simplified weather data
        weather_db = {
            "san francisco": WeatherData(temperature=65.0, conditions="foggy"),
            "new york": WeatherData(temperature=55.0, conditions="cloudy"),
            "miami": WeatherData(temperature=85.0, conditions="sunny"),
        }
        return weather_db.get(city.lower(), WeatherData(temperature=70.0, conditions="clear"))


async def test_plugin_with_handler():
    """Test plugins through the full handler."""
    
    print("=== Plugin + Handler Integration Test ===\n")
    
    # Setup
    AppConfig.add_configs(configs)
    app_config = AppConfig()
    initialize_telemetry('test-plugin-handler', app_config)
    
    # Set up plugin loader
    import types
    plugin_loader = get_plugin_loader()
    custom_module = types.ModuleType("weather_plugins")
    custom_module.SimpleWeatherPlugin = SimpleWeatherPlugin
    plugin_loader.custom_module = custom_module
    
    print("Step 1: Creating config with plugin...")
    
    config_yaml = """
apiVersion: skagents/v1
kind: Chat
description: Chat agent with weather plugin
service_name: WeatherBot
version: 0.1
input_type: BaseInput
plugin_module: weather_plugins.py
spec:
  agent:
    name: weather_agent
    role: Weather Assistant
    model: gemini-2.0-flash
    system_prompt: You are a weather assistant. Use the get_weather tool to provide weather information.
    plugins:
      - SimpleWeatherPlugin
"""
    
    config = parse_yaml_raw_as(BaseConfig, config_yaml)
    print(f"✓ Config created with plugin: {config.spec.agent.plugins}")
    
    print("\nStep 2: Creating handler with plugin...")
    handler = langchain_handle(config, app_config)
    print(f"✓ Handler created: {type(handler).__name__}")
    
    # Check if agent has tools
    if hasattr(handler, 'agent') and hasattr(handler.agent, 'tools'):
        print(f"✓ Agent has {len(handler.agent.tools)} tools bound")
        for tool in handler.agent.tools:
            print(f"  - {tool.name}")
    
    print("\nStep 3: Invoking handler with plugin-requiring query...")
    
    inputs = {
        'chat_history': [
            {'role': 'user', 'content': 'What is the weather in San Francisco?'}
        ]
    }
    
    try:
        result = await handler.invoke(inputs)
        print(f"\n✓ Handler invoked successfully")
        print(f"Response: {result.get('output', 'No output')[:200]}")
        
        # Check if the response mentions weather data
        output = result.get('output', '').lower()
        if 'weather' in output or 'temperature' in output or 'fog' in output or '65' in output:
            print("\n✅ Response appears to use weather data!")
        else:
            print(f"\n⚠️ Response may not have used plugin. Full response:\n{result.get('output', '')}")
        
        # Check token usage
        if 'usage' in result:
            print(f"\nToken usage: {result['usage']}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== Test Complete ===")


if __name__ == "__main__":
    asyncio.run(test_plugin_with_handler())
