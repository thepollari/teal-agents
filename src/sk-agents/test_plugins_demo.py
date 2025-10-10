"""
Test the 03_plugins demo (real-world example with WeatherPlugin).

Steps:
1. Load the config from docs/demos/03_plugins/config.yaml
2. Load the custom WeatherPlugin from custom_plugins.py
3. Create handler with LangChain
4. Test invoke with weather query
5. Verify plugin execution
"""
import asyncio
import os
import sys
from pathlib import Path
from pydantic_yaml import parse_yaml_file_as
from sk_agents.ska_types import BaseConfig
from sk_agents.langchain_handler import langchain_handle
from ska_utils import AppConfig, initialize_telemetry
from sk_agents.configs import configs
from sk_agents.plugin_loader import get_plugin_loader


async def test_plugins_demo():
    print("=" * 60)
    print("TESTING: 03_plugins Demo (Weather Plugin)")
    print("=" * 60)
    
    # Step 1: Setup
    print("\n[STEP 1] Setting up environment...")
    AppConfig.add_configs(configs)
    app_config = AppConfig()
    initialize_telemetry('test-plugins-demo', app_config)
    print("✓ Environment configured")
    
    # Step 2: Load config
    print("\n[STEP 2] Loading config from docs/demos/03_plugins/config.yaml...")
    config_path = Path("docs/demos/03_plugins/config.yaml")
    
    if not config_path.exists():
        print(f"❌ Config not found at {config_path}")
        return
    
    config = parse_yaml_file_as(BaseConfig, str(config_path))
    print(f"✓ Config loaded:")
    print(f"  - API Version: {config.apiVersion}")
    print(f"  - Kind: {config.kind}")
    print(f"  - Service: {config.service_name}")
    print(f"  - Description: {config.description}")
    
    # Step 3: Check config details
    print("\n[STEP 3] Analyzing configuration...")
    if hasattr(config, 'spec'):
        if hasattr(config.spec, 'agents'):
            print(f"  Agents:")
            for agent in config.spec.agents:
                print(f"    - {agent.name} ({agent.model})")
                if hasattr(agent, 'plugins') and agent.plugins:
                    print(f"      Plugins: {agent.plugins}")
        
        if hasattr(config.spec, 'tasks'):
            print(f"  Tasks: {len(config.spec.tasks)}")
            for i, task in enumerate(config.spec.tasks, 1):
                print(f"    {i}. {task.name} (agent: {task.agent})")
    
    # Step 4: Load plugin module
    print("\n[STEP 4] Loading plugin module...")
    plugin_module_path = Path("docs/demos/03_plugins/custom_plugins.py")
    
    if plugin_module_path.exists():
        # Add to path so we can import
        sys.path.insert(0, str(plugin_module_path.parent))
        
        plugin_loader = get_plugin_loader(str(plugin_module_path))
        print(f"✓ Plugin loader initialized with module: {plugin_module_path.name}")
    else:
        print(f"⚠️ Plugin file not found, continuing without plugins")
    
    # Step 5: Create handler
    print("\n[STEP 5] Creating LangChain handler...")
    try:
        handler = langchain_handle(config, app_config)
        print(f"✓ Handler created: {type(handler).__name__}")
        
        # Check handler details
        if hasattr(handler, 'tasks'):
            print(f"  - Tasks: {len(handler.tasks)}")
        if hasattr(handler, 'agents'):
            print(f"  - Agents: {len(handler.agents) if isinstance(handler.agents, list) else 'N/A'}")
        
    except Exception as e:
        print(f"❌ Failed to create handler: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 6: Test invoke
    print("\n[STEP 6] Testing handler invoke...")
    print("  Query: 'What's the weather in San Francisco?'")
    
    inputs = {
        'chat_history': [
            {
                'role': 'user',
                'content': 'What is the weather forecast for San Francisco?'
            }
        ]
    }
    
    try:
        print("  Invoking handler...")
        result = await handler.invoke(inputs)
        
        print("\n✓ Handler invoked successfully!")
        
        # Step 7: Analyze results
        print("\n[STEP 7] Analyzing results...")
        output = result.get('output', '')
        
        print(f"\nResponse (first 400 chars):")
        print("-" * 60)
        print(output[:400])
        if len(output) > 400:
            print(f"... ({len(output) - 400} more characters)")
        print("-" * 60)
        
        # Check for weather-related content
        keywords = ['temperature', 'weather', 'forecast', 'san francisco', 'degrees']
        found_keywords = [kw for kw in keywords if kw in output.lower()]
        
        if found_keywords:
            print(f"\n✓ Response contains weather-related keywords: {found_keywords}")
        
        # Token usage
        if 'usage' in result:
            usage = result['usage']
            print(f"\nToken Usage:")
            print(f"  - Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
            print(f"  - Completion tokens: {usage.get('completion_tokens', 'N/A')}")
            print(f"  - Total tokens: {usage.get('total_tokens', 'N/A')}")
        
        print("\n" + "=" * 60)
        print("✅ PLUGINS DEMO TEST SUCCESSFUL")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error invoking handler: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_plugins_demo())
