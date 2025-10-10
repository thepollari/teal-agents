"""Quick test of LangChain handler with Gemini."""
import asyncio
from pydantic_yaml import parse_yaml_raw_as
from sk_agents.ska_types import BaseConfig
from sk_agents.langchain_handler import langchain_handle
from ska_utils import AppConfig, initialize_telemetry
from sk_agents.configs import configs

async def test():
    AppConfig.add_configs(configs)
    app_config = AppConfig()
    initialize_telemetry('test', app_config)
    
    config_yaml = """
apiVersion: skagents/v1
kind: Chat
description: Simple test
service_name: TestBot
version: 0.1
input_type: BaseInput
spec:
  agent:
    name: test
    role: Assistant
    model: gemini-2.0-flash
    system_prompt: You are helpful.
"""
    
    config = parse_yaml_raw_as(BaseConfig, config_yaml)
    handler = langchain_handle(config, app_config)
    
    print("✓ Handler created")
    
    inputs = {'chat_history': [{'role': 'user', 'content': 'Say hello!'}]}
    result = await handler.invoke(inputs)
    
    print(f"✓ Response: {result.get('output', '')[:100]}")
    print(f"✓ Tokens: {result.get('usage', {})}")
    print("\n✅ Test passed!")

asyncio.run(test())
