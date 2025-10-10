"""
Test the university agent example end-to-end.

This validates that a real-world agent config works with LangChain.
"""
import asyncio
import os
from pathlib import Path
from pydantic_yaml import parse_yaml_file_as
from sk_agents.ska_types import BaseConfig
from sk_agents.langchain_handler import langchain_handle
from ska_utils import AppConfig, initialize_telemetry
from sk_agents.configs import configs


async def test_university_agent():
    print("=== Testing University/Complex Sequential Agent ===\n")
    
    # Setup
    AppConfig.add_configs(configs)
    app_config = AppConfig()
    initialize_telemetry('test-university', app_config)
    
    # Find and load the config
    config_path = Path("docs/demos/04_sequential_complex/config.yaml")
    
    if not config_path.exists():
        print(f"❌ Config not found at {config_path}")
        return
    
    print(f"Step 1: Loading config from {config_path}")
    config = parse_yaml_file_as(BaseConfig, str(config_path))
    
    print(f"✓ Config loaded")
    print(f"  API Version: {config.apiVersion}")
    print(f"  Kind: {config.kind}")
    print(f"  Description: {config.description}")
    print(f"  Service: {config.service_name}")
    
    # Check agents
    if hasattr(config, 'spec') and hasattr(config.spec, 'agents'):
        print(f"\n  Agents ({len(config.spec.agents)}):")
        for agent in config.spec.agents:
            print(f"    - {agent.name}: {agent.model}")
    
    # Check tasks
    if hasattr(config, 'spec') and hasattr(config.spec, 'tasks'):
        print(f"\n  Tasks ({len(config.spec.tasks)}):")
        for task in config.spec.tasks:
            print(f"    - Task {task.task_no}: {task.name}")
    
    print("\nStep 2: Creating handler...")
    try:
        handler = langchain_handle(config, app_config)
        print(f"✓ Handler created: {type(handler).__name__}")
    except Exception as e:
        print(f"❌ Failed to create handler: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Check handler attributes
    if hasattr(handler, 'tasks'):
        print(f"  Handler has {len(handler.tasks)} tasks")
    
    print("\nStep 3: Testing invoke with sample input...")
    
    # Create a sample input for the university agent
    inputs = {
        'chat_history': [
            {
                'role': 'user',
                'content': 'I want to learn about machine learning and artificial intelligence. What courses should I take?'
            }
        ]
    }
    
    try:
        print("  Invoking handler...")
        result = await handler.invoke(inputs)
        
        print("\n✓ Handler invoked successfully!")
        print(f"\nResponse Preview:")
        output = result.get('output', '')
        print(f"{output[:500]}...")
        
        if len(output) > 500:
            print(f"\n(Full response is {len(output)} characters)")
        
        # Check token usage
        if 'usage' in result:
            usage = result['usage']
            print(f"\nToken Usage:")
            print(f"  Prompt: {usage.get('prompt_tokens', 'N/A')}")
            print(f"  Completion: {usage.get('completion_tokens', 'N/A')}")
            print(f"  Total: {usage.get('total_tokens', 'N/A')}")
        
        print("\n✅ University agent test successful!")
        
    except Exception as e:
        print(f"\n❌ Error invoking handler: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_university_agent())
