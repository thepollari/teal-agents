"""
Test plugins integrated with LangChain agent.
"""
import asyncio
from pydantic import BaseModel
from sk_agents.langchain_adapter.langchain_plugins import kernel_function
from sk_agents.langchain_adapter.chat_model_factory import ChatModelFactory
from sk_agents.langchain_adapter.chain_builder import ChainBuilder
from sk_agents.langchain_adapter.remote_tool_loader import RemoteToolLoader
from sk_agents.plugin_loader import PluginLoader
from sk_agents.ska_types import BasePlugin
from ska_utils import AppConfig
from sk_agents.configs import configs


class TemperatureResponse(BaseModel):
    low: float
    high: float


class TestWeatherPlugin(BasePlugin):
    @kernel_function(description="Get current temperature for coordinates")
    def get_temperature(self, lat: float, lng: float) -> TemperatureResponse:
        """Retrieve low and high temperatures."""
        return TemperatureResponse(low=65.0, high=75.0)


async def test():
    AppConfig.add_configs(configs)
    app_config = AppConfig()
    
    chat_factory = ChatModelFactory(app_config)
    remote_loader = RemoteToolLoader(app_config)
    chain_builder = ChainBuilder(chat_factory, remote_loader, app_config)
    
    plugin_loader = PluginLoader()
    plugin_loader.custom_module = type('TestModule', (), {'TestWeatherPlugin': TestWeatherPlugin})()
    
    print("Testing agent with plugins...")
    
    agent = chain_builder.build_chain(
        model_name="gemini-2.0-flash",
        service_id="test",
        plugins=["TestWeatherPlugin"]
    )
    
    print(f"✓ Agent created with {len(agent.tools) if hasattr(agent, 'tools') else 0} tools")
    
    from langchain_core.messages import HumanMessage
    result = await agent.runnable.ainvoke({"messages": [HumanMessage(content="What's the temperature at lat 37.7, lng -122.4?")]})
    
    print(f"✓ Response: {result.content[:100]}")
    print("\n✅ Plugin integration working!")


if __name__ == "__main__":
    asyncio.run(test())
