"""
LangChain adapter module for teal-agents.

This module provides adapters and wrappers to integrate LangChain
with the existing teal-agents framework, maintaining API compatibility
while migrating from Semantic Kernel.
"""

from sk_agents.langchain_adapter.agent_builder import LangChainAgentBuilder
from sk_agents.langchain_adapter.chain_builder import ChainBuilder
from sk_agents.langchain_adapter.chat_model_factory import ChatModelFactory
from sk_agents.langchain_adapter.langchain_agent import LangChainAgent, LangChainChatHistory
from sk_agents.langchain_adapter.remote_tool_loader import (
    RemotePluginCatalog,
    RemoteToolLoader,
)
from sk_agents.langchain_adapter.tool_loader import ToolLoader
from sk_agents.langchain_adapter.utils import (
    get_token_usage_for_response,
    parse_chat_history_to_langchain,
)

__all__ = [
    "ChainBuilder",
    "ChatModelFactory",
    "LangChainAgent",
    "LangChainAgentBuilder",
    "LangChainChatHistory",
    "RemotePluginCatalog",
    "RemoteToolLoader",
    "ToolLoader",
    "get_token_usage_for_response",
    "parse_chat_history_to_langchain",
]
