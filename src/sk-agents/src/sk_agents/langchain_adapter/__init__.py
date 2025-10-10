"""
LangChain adapter module for teal-agents.

This module provides adapters and wrappers to integrate LangChain
with the existing teal-agents framework, maintaining API compatibility
while migrating from Semantic Kernel.
"""

from sk_agents.langchain_adapter.chain_builder import ChainBuilder
from sk_agents.langchain_adapter.langchain_agent import LangChainAgent
from sk_agents.langchain_adapter.chat_model_factory import ChatModelFactory

__all__ = [
    "ChainBuilder",
    "LangChainAgent",
    "ChatModelFactory",
]
