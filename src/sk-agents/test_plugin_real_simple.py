"""
Simple real plugin test without SK dependency.
"""
import asyncio
from pydantic import BaseModel, Field
from sk_agents.ska_types import BasePlugin
from sk_agents.langchain_adapter.langchain_plugins import kernel_function
from sk_agents.langchain_adapter.tool_loader import ToolLoader
from sk_agents.plugin_loader import PluginLoader


class WeatherData(BaseModel):
    temperature: float
    conditions: str


class TestPlugin(BasePlugin):
    """Test plugin using LangChain decorator."""
    
    @kernel_function(description="Get weather for a city")
    def get_weather(self, city: str) -> WeatherData:
        """Get weather."""
        return WeatherData(temperature=72.0, conditions="sunny")


async def test():
    print("=== Simple Plugin Test ===\n")
    
    # Create plugin loader
    import types
    plugin_loader = PluginLoader()
    custom_module = types.ModuleType("test_plugins")
    custom_module.TestPlugin = TestPlugin
    plugin_loader.custom_module = custom_module
    
    print("Step 1: Load and convert plugin...")
    tool_loader = ToolLoader()
    
    # Manually get the plugin and convert
    plugins_dict = plugin_loader.get_plugins(["TestPlugin"])
    print(f"✓ Got plugins: {list(plugins_dict.keys())}")
    
    # Convert to tools
    from sk_agents.langchain_adapter.tool_loader import ToolLoader
    tools = []
    for plugin_name, plugin_class in plugins_dict.items():
        plugin_instance = plugin_class(None, None)
        plugin_tools = ToolLoader._convert_plugin_to_tools(plugin_instance, plugin_name)
        tools.extend(plugin_tools)
    
    print(f"✓ Converted {len(tools)} tools")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    print("\nStep 2: Execute tool...")
    tool = tools[0]
    result = tool.invoke({"city": "San Francisco"})
    print(f"✓ Result: {result}")
    print(f"  Type: {type(result)}")
    
    if isinstance(result, WeatherData):
        print(f"  Temperature: {result.temperature}")
        print(f"  Conditions: {result.conditions}")
    
    print("\n✅ Real plugin execution working!")


if __name__ == "__main__":
    asyncio.run(test())
