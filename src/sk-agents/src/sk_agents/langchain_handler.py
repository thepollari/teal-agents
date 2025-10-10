"""
LangChain handler factory.

Entry point for creating LangChain-based handlers that replace
Semantic Kernel handlers. This allows switching between SK and LC
implementations during the migration.
"""

import logging

from ska_utils import AppConfig

from sk_agents.langchain_adapter import (
    ChainBuilder,
    ChatModelFactory,
    LangChainAgentBuilder,
    RemotePluginCatalog,
    RemoteToolLoader,
)
from sk_agents.ska_types import BaseConfig, BaseHandler

logger = logging.getLogger(__name__)


def langchain_handle(
    config: BaseConfig,
    app_config: AppConfig,
    authorization: str | None = None,
) -> BaseHandler:
    """
    Create a LangChain-based handler from configuration.
    
    This is the LangChain equivalent of skagents_handle(), creating
    handlers that use LangChain instead of Semantic Kernel.
    
    Args:
        config: Agent configuration
        app_config: Application configuration
        authorization: Optional authorization header
        
    Returns:
        BaseHandler: LangChain-based handler (SequentialSkagents, ChatAgents, etc.)
    """
    api_version = config.apiVersion.lower()
    
    if "skagents" in api_version or "v1" in api_version:
        return _create_skagents_handler(config, app_config, authorization)
    elif "tealagents" in api_version:
        return _create_tealagents_handler(config, app_config, authorization)
    else:
        raise ValueError(f"Unknown apiVersion: {config.apiVersion}")


def _create_skagents_handler(
    config: BaseConfig,
    app_config: AppConfig,
    authorization: str | None = None,
) -> BaseHandler:
    """
    Create a LangChain-based handler for skagents/v1 API.
    
    Args:
        config: Agent configuration
        app_config: Application configuration
        authorization: Optional authorization header
        
    Returns:
        BaseHandler: Sequential or Chat agent handler using LangChain
    """
    from sk_agents.langchain_skagents.v1.sequential.sequential_skagents import (
        LangChainSequentialSkagents,
    )
    from sk_agents.langchain_skagents.v1.chat.chat_agents import LangChainChatAgents
    
    chat_model_factory = ChatModelFactory()
    remote_plugin_catalog = RemotePluginCatalog(app_config)
    remote_tool_loader = RemoteToolLoader(remote_plugin_catalog)
    
    chain_builder = ChainBuilder(
        chat_model_factory=chat_model_factory,
        remote_tool_loader=remote_tool_loader,
        app_config=app_config,
        authorization=authorization,
    )
    
    agent_builder = LangChainAgentBuilder(
        chain_builder=chain_builder,
        authorization=authorization,
    )
    
    if hasattr(config, 'kind'):
        kind = config.kind.lower()
        
        if kind == "sequential":
            return LangChainSequentialSkagents(
                config=config,
                chain_builder=chain_builder,
                agent_builder=agent_builder,
            )
        elif kind == "chat":
            return LangChainChatAgents(
                config=config,
                agent_builder=agent_builder,
            )
        else:
            raise ValueError(f"Unknown kind: {config.kind}")
    else:
        return LangChainSequentialSkagents(
            config=config,
            chain_builder=chain_builder,
            agent_builder=agent_builder,
        )


def _create_tealagents_handler(
    config: BaseConfig,
    app_config: AppConfig,
    authorization: str | None = None,
) -> BaseHandler:
    """
    Create a LangChain-based handler for tealagents API.
    
    Args:
        config: Agent configuration
        app_config: Application configuration
        authorization: Optional authorization header
        
    Returns:
        BaseHandler: TealAgents handler using LangChain
    """
    from sk_agents.langchain_tealagents.v1alpha1.agent.handler import (
        LangChainTealAgentsV1Alpha1Handler,
    )
    
    chat_model_factory = ChatModelFactory()
    remote_plugin_catalog = RemotePluginCatalog(app_config)
    remote_tool_loader = RemoteToolLoader(remote_plugin_catalog)
    
    chain_builder = ChainBuilder(
        chat_model_factory=chat_model_factory,
        remote_tool_loader=remote_tool_loader,
        app_config=app_config,
        authorization=authorization,
    )
    
    agent_builder = LangChainAgentBuilder(
        chain_builder=chain_builder,
        authorization=authorization,
    )
    
    return LangChainTealAgentsV1Alpha1Handler(
        config=config,
        agent_builder=agent_builder,
        app_config=app_config,
        authorization=authorization,
    )
