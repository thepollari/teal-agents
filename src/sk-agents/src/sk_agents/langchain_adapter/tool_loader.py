"""
Tool Loader for converting Semantic Kernel plugins to LangChain tools.

Handles loading and converting local Python-based plugins from the
@kernel_function format to LangChain @tool format.
"""

import inspect
import logging
from typing import Any, Callable

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, create_model

from sk_agents.extra_data_collector import ExtraDataCollector
from sk_agents.plugin_loader import get_plugin_loader

logger = logging.getLogger(__name__)


class ToolLoader:
    """
    Loads local plugins and converts them to LangChain tools.
    
    This handles the migration from Semantic Kernel's @kernel_function
    decorator pattern to LangChain's tool pattern.
    """

    @staticmethod
    def load_tools(
        plugin_names: list[str],
        authorization: str | None = None,
        extra_data_collector: ExtraDataCollector | None = None,
    ) -> list[StructuredTool]:
        """
        Load plugins and convert to LangChain tools.
        
        Args:
            plugin_names: List of plugin class names to load
            authorization: Optional authorization header
            extra_data_collector: Optional collector for extra data
            
        Returns:
            List of LangChain StructuredTool instances
        """
        if not plugin_names:
            return []
        
        tools = []
        plugin_loader = get_plugin_loader()
        plugins = plugin_loader.get_plugins(plugin_names)
        
        for plugin_name, plugin_class in plugins.items():
            plugin_instance = plugin_class(authorization, extra_data_collector)
            
            plugin_tools = ToolLoader._convert_plugin_to_tools(
                plugin_instance, plugin_name
            )
            tools.extend(plugin_tools)
        
        return tools

    @staticmethod
    def _convert_plugin_to_tools(
        plugin_instance: Any,
        plugin_name: str
    ) -> list[StructuredTool]:
        """
        Convert a plugin instance to LangChain tools.
        
        Finds all methods that were decorated with @kernel_function
        and converts them to LangChain StructuredTool instances.
        
        Args:
            plugin_instance: Instance of the plugin class
            plugin_name: Name of the plugin
            
        Returns:
            List of StructuredTool instances
        """
        tools = []
        
        for method_name in dir(plugin_instance):
            if method_name.startswith('_'):
                continue
            
            method = getattr(plugin_instance, method_name)
            
            if hasattr(method, '__kernel_function__') or callable(method):
                if not callable(method) or not hasattr(method, '__self__'):
                    continue
                
                try:
                    tool = ToolLoader._create_tool_from_method(
                        method,
                        method_name,
                        plugin_name
                    )
                    if tool:
                        tools.append(tool)
                except Exception as e:
                    logger.warning(
                        f"Could not convert {plugin_name}.{method_name} to tool: {e}"
                    )
        
        return tools

    @staticmethod
    def _create_tool_from_method(
        method: Callable,
        method_name: str,
        plugin_name: str
    ) -> StructuredTool | None:
        """
        Create a LangChain StructuredTool from a method.
        
        Args:
            method: The method to convert
            method_name: Name of the method
            plugin_name: Name of the plugin
            
        Returns:
            StructuredTool instance or None if conversion fails
        """
        sig = inspect.signature(method)
        
        description = ""
        if hasattr(method, '__kernel_function__'):
            kf_metadata = getattr(method, '__kernel_function__')
            description = kf_metadata.get('description', '')
        
        if not description and method.__doc__:
            description = method.__doc__.strip()
        
        if not description:
            description = f"Execute {method_name} from {plugin_name}"
        
        fields = {}
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            param_type = param.annotation
            if param_type == inspect.Parameter.empty:
                param_type = str  # Default to string if no annotation
            
            default = ... if param.default == inspect.Parameter.empty else param.default
            
            fields[param_name] = (param_type, default)
        
        if fields:
            args_schema = create_model(
                f"{plugin_name}_{method_name}_Input",
                **fields
            )
        else:
            args_schema = None
        
        tool_name = f"{plugin_name}_{method_name}"
        
        return StructuredTool(
            name=tool_name,
            description=description,
            func=method,
            coroutine=method if inspect.iscoroutinefunction(method) else None,
            args_schema=args_schema,
        )
