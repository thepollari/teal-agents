"""
Chain Builder for constructing LangChain chains/agents.

Replaces Semantic Kernel's KernelBuilder with LangChain equivalent,
maintaining the same interface for compatibility.
"""

import logging
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import Runnable
from ska_utils import AppConfig

from sk_agents.extra_data_collector import ExtraDataCollector
from sk_agents.langchain_adapter.chat_model_factory import ChatModelFactory
from sk_agents.langchain_adapter.langchain_agent import LangChainAgent
from sk_agents.langchain_adapter.tool_loader import ToolLoader
from sk_agents.langchain_adapter.remote_tool_loader import RemoteToolLoader
from sk_agents.ska_types import ModelType

logger = logging.getLogger(__name__)


class ChainBuilder:
    """
    Builder for creating LangChain chains/agents with tools.
    
    Replaces KernelBuilder while maintaining the same interface pattern
    used throughout the teal-agents framework.
    """

    def __init__(
        self,
        chat_model_factory: ChatModelFactory,
        remote_tool_loader: RemoteToolLoader,
        app_config: AppConfig,
        authorization: str | None = None,
    ):
        """
        Initialize ChainBuilder.
        
        Args:
            chat_model_factory: Factory for creating chat models
            remote_tool_loader: Loader for remote (OpenAPI) tools
            app_config: Application configuration
            authorization: Optional authorization header
        """
        self.chat_model_factory = chat_model_factory
        self.remote_tool_loader = remote_tool_loader
        self.app_config = app_config
        self.authorization = authorization
        self.logger = logging.getLogger(__name__)

    def build_chain(
        self,
        model_name: str,
        service_id: str,
        plugins: list[str],
        remote_plugins: list[str],
        authorization: str | None = None,
        extra_data_collector: ExtraDataCollector | None = None,
    ) -> LangChainAgent:
        """
        Build a LangChain agent with tools.
        
        This is the equivalent of KernelBuilder.build_kernel() but returns
        a LangChainAgent instead.
        
        Args:
            model_name: Name of the LLM model
            service_id: Service identifier (used for logging/tracking)
            plugins: List of local plugin names to load
            remote_plugins: List of remote (OpenAPI) plugin names to load
            authorization: Optional authorization header
            extra_data_collector: Optional collector for extra data/telemetry
            
        Returns:
            LangChainAgent: Configured agent ready to use
        """
        try:
            chat_model = self._create_base_model(model_name, service_id)
            
            tools = []
            if plugins:
                local_tools = self._load_local_tools(
                    plugins, authorization, extra_data_collector
                )
                tools.extend(local_tools)
            
            if remote_plugins:
                remote_tools = self._load_remote_tools(remote_plugins)
                tools.extend(remote_tools)
            
            if tools:
                runnable = chat_model.bind_tools(tools)
            else:
                runnable = chat_model
            
            model_type = self.chat_model_factory.get_model_type_for_name(model_name)
            so_supported = self.chat_model_factory.model_supports_structured_output(
                model_name
            )
            
            model_attributes = {
                "model_type": model_type,
                "so_supported": so_supported,
            }
            
            return LangChainAgent(
                model_name=model_name,
                model_attributes=model_attributes,
                runnable=runnable,
                chat_model=chat_model,
            )
            
        except Exception as e:
            self.logger.exception(f"Could not build chain with service ID {service_id}: {e}")
            raise

    def get_model_type_for_name(self, model_name: str) -> ModelType:
        """
        Get the model type for a given model name.
        
        Args:
            model_name: Name of the model
            
        Returns:
            ModelType enum value
        """
        try:
            return self.chat_model_factory.get_model_type_for_name(model_name)
        except Exception as e:
            self.logger.exception(f"Could not get model type for {model_name}: {e}")
            raise

    def model_supports_structured_output(self, model_name: str) -> bool:
        """
        Check if a model supports structured output.
        
        Args:
            model_name: Name of the model
            
        Returns:
            True if model supports structured output
        """
        return self.chat_model_factory.model_supports_structured_output(model_name)

    def _create_base_model(
        self,
        model_name: str,
        service_id: str
    ) -> BaseChatModel:
        """
        Create the base chat model without tools.
        
        Args:
            model_name: Name of the model
            service_id: Service identifier
            
        Returns:
            BaseChatModel instance
        """
        try:
            return self.chat_model_factory.create_chat_model(model_name)
        except Exception as e:
            self.logger.exception(
                f"Could not create base model with service id {service_id}: {e}"
            )
            raise

    def _load_local_tools(
        self,
        plugin_names: list[str],
        authorization: str | None = None,
        extra_data_collector: ExtraDataCollector | None = None,
    ) -> list:
        """
        Load local (Python-based) tools/plugins.
        
        Args:
            plugin_names: List of plugin names to load
            authorization: Optional authorization header
            extra_data_collector: Optional collector for extra data
            
        Returns:
            List of LangChain tools
        """
        if not plugin_names:
            return []
        
        tool_loader = ToolLoader()
        return tool_loader.load_tools(
            plugin_names,
            authorization=authorization,
            extra_data_collector=extra_data_collector
        )

    def _load_remote_tools(self, remote_plugin_names: list[str]) -> list:
        """
        Load remote (OpenAPI) tools/plugins.
        
        Args:
            remote_plugin_names: List of remote plugin names to load
            
        Returns:
            List of LangChain tools created from OpenAPI specs
        """
        if not remote_plugin_names:
            return []
        
        try:
            return self.remote_tool_loader.load_remote_tools(remote_plugin_names)
        except Exception as e:
            self.logger.exception(f"Could not load remote tools: {e}")
            raise
