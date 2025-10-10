"""
Plugin Converter for LangChain Tools.

Converts Semantic Kernel plugins (using @kernel_function) to LangChain tools.
"""
import inspect
from typing import Any, Callable

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, create_model


def convert_sk_plugin_to_tools(plugin_class: type) -> list[StructuredTool]:
    """
    Convert a Semantic Kernel plugin class to LangChain tools.
    
    Finds all methods decorated with @kernel_function and converts them
    to LangChain StructuredTool instances.
    
    Args:
        plugin_class: Plugin class (must inherit from BasePlugin)
        
    Returns:
        List of LangChain StructuredTool instances
    """
    tools = []
    plugin_instance = plugin_class()
    
    for name, method in inspect.getmembers(plugin_instance, predicate=inspect.ismethod):
        if hasattr(method, '__kernel_function__') or hasattr(method, '__wrapped__'):
            tool = _convert_method_to_tool(name, method, plugin_instance)
            if tool:
                tools.append(tool)
    
    return tools


def _convert_method_to_tool(
    name: str,
    method: Callable,
    plugin_instance: Any
) -> StructuredTool | None:
    """
    Convert a single SK plugin method to a LangChain tool.
    
    Args:
        name: Method name
        method: Method to convert
        plugin_instance: Instance of the plugin class
        
    Returns:
        StructuredTool or None if conversion fails
    """
    sig = inspect.signature(method)
    
    description = method.__doc__ or f"Tool: {name}"
    if hasattr(method, '__kernel_function_description__'):
        description = method.__kernel_function_description__
    
    args_schema = _create_args_schema(name, sig, method)
    
    def tool_func(**kwargs):
        return method(**kwargs)
    
    return StructuredTool(
        name=name,
        description=description,
        func=tool_func,
        args_schema=args_schema
    )


def _create_args_schema(name: str, sig: inspect.Signature, method: Callable) -> type[BaseModel]:
    """
    Create a Pydantic schema for tool arguments from method signature.
    
    Args:
        name: Tool name
        sig: Method signature
        method: Method to extract types from
        
    Returns:
        Pydantic BaseModel class for arguments
    """
    fields = {}
    
    for param_name, param in sig.parameters.items():
        if param_name == 'self':
            continue
            
        annotation = param.annotation if param.annotation != inspect.Parameter.empty else Any
        default = ... if param.default == inspect.Parameter.empty else param.default
        
        fields[param_name] = (annotation, default)
    
    schema_name = f"{name}_args"
    return create_model(schema_name, **fields)
