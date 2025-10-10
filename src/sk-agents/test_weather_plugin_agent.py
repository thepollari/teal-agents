"""
Test the WeatherPlugin demo agent (03_plugins).

This is the most complex example agent with plugins - validating it works end-to-end.
"""
import asyncio
from pathlib import Path
from pydantic_yaml import parse_yaml_file_as
from sk_agents.ska_types import BaseConfig
from sk_agents.langchain_handler import langchain_handle
from ska_utils import AppConfig, initialize_telemetry
from sk_agents.configs import configs


async def test_weather_agent():
    print("=" * 70)
    print("TESTING: Weather Plugin Agent (03_plugins)")
    print("=" * 70)
    
    # Setup
    AppConfig.add_configs(configs)
    app_config = AppConfig()
    initialize_telemetry('test-weather-agent', app_config)
    
    # Load config
    config_path = Path("docs/demos/03_plugins/config.yaml")
    print(f"\n[1] Loading config from {config_path}")
    config = parse_yaml_file_as(BaseConfig, str(config_path))
    
    print(f"✓ Config loaded:")
    print(f"  Service: {config.service_name}")
    print(f"  Description: {config.description}")
    print(f"  Kind: {config.kind}")
    
    # Check agents and tasks
    if hasattr(config.spec, 'agents'):
        print(f"\n[2] Agents:")
        for agent in config.spec.agents:
            print(f"  - {agent.name} ({agent.model})")
            if hasattr(agent, 'plugins') and agent.plugins:
                print(f"    Plugins: {agent.plugins}")
    
    if hasattr(config.spec, 'tasks'):
        print(f"\n[3] Tasks:")
        for task in config.spec.tasks:
            print(f"  - Task {task.task_no}: {task.name}")
    
    # Create handler
    print("\n[4] Creating LangChain handler...")
    handler = langchain_handle(config, app_config)
    print(f"✓ Handler created: {type(handler).__name__}")
    
    # Test invoke with a weather query
    print("\n[5] Testing invoke...")
    inputs = {
        'chat_history': [
            {
                'role': 'user',
                'content': 'Hello! Can you help me with the weather?'
            }
        ],
        'user_context': {
            'User Location': 'San Francisco'
        }
    }
    
    print("  Input: 'Hello! Can you help me with the weather?'")
    print("  User Location: San Francisco")
    
    result = await handler.invoke(inputs)
    
    print("\n✓ Handler invoked successfully!")
    print("\n[6] Response:")
    print("-" * 70)
    output = result.get('output', '')
    print(output[:400])
    if len(output) > 400:
        print(f"... ({len(output) - 400} more characters)")
    print("-" * 70)
    
    # Token usage
    if 'usage' in result:
        usage = result['usage']
        print(f"\n[7] Token Usage:")
        print(f"  Prompt: {usage.get('prompt_tokens', 'N/A')}")
        print(f"  Completion: {usage.get('completion_tokens', 'N/A')}")
        print(f"  Total: {usage.get('total_tokens', 'N/A')}")
    
    print("\n" + "=" * 70)
    print("✅ WEATHER PLUGIN AGENT TEST SUCCESSFUL")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_weather_agent())
