"""
Test multiple real-world example configs with LangChain.

This demonstrates testing various production-like agent configurations.
"""
import asyncio
import os
from pathlib import Path
from pydantic_yaml import parse_yaml_file_as
from sk_agents.ska_types import BaseConfig
from sk_agents.langchain_handler import langchain_handle
from ska_utils import AppConfig, initialize_telemetry
from sk_agents.configs import configs


async def test_config(config_path: Path, test_input: str):
    """Test a single config file."""
    print(f"\n{'=' * 70}")
    print(f"Testing: {config_path}")
    print('=' * 70)
    
    # Load config
    config = parse_yaml_file_as(BaseConfig, str(config_path))
    print(f"✓ Loaded config: {config.service_name} ({config.kind})")
    
    # Create handler  
    handler = langchain_handle(config, AppConfig())
    print(f"✓ Created handler: {type(handler).__name__}")
    
    # Invoke
    inputs = {'chat_history': [{'role': 'user', 'content': test_input}]}
    result = await handler.invoke(inputs)
    
    # Show results
    output = result.get('output', '')
    print(f"\nInput: {test_input}")
    print(f"Output: {output[:300]}...")
    
    if 'usage' in result:
        u = result['usage']
        print(f"Tokens: {u.get('prompt_tokens', 0)} + {u.get('completion_tokens', 0)} = {u.get('total_tokens', 0)}")
    
    return True


async def main():
    print("\n" + "=" * 70)
    print("REAL-WORLD AGENT EXAMPLES TEST")
    print("=" * 70)
    
    # Setup
    AppConfig.add_configs(configs)
    initialize_telemetry('test-examples', AppConfig())
    
    tests = [
        ("docs/demos/01_getting_started/config.yaml", "Hello! How can you help me?"),
        ("docs/demos/02_input_output/config.yaml", "Tell me about Python programming."),
        ("docs/demos/09_chat_simple/config.yaml", "What is machine learning?"),
    ]
    
    passed = 0
    failed = 0
    
    for config_path, test_input in tests:
        try:
            if not Path(config_path).exists():
                print(f"\n⚠️ Skipping {config_path} (not found)")
                continue
                
            await test_config(Path(config_path), test_input)
            passed += 1
            print("✅ PASSED")
            
        except Exception as e:
            print(f"❌ FAILED: {e}")
            failed += 1
    
    print(f"\n{'=' * 70}")
    print(f"SUMMARY: {passed} passed, {failed} failed")
    print('=' * 70)


if __name__ == "__main__":
    asyncio.run(main())
