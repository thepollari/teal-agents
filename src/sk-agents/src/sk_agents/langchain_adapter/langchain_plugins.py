"""
LangChain-compatible plugin base and decorators.

Provides a compatibility layer for converting SK-style plugins to LangChain tools.
"""
from functools import wraps
from typing import Callable


def langchain_tool(description: str | None = None):
    """
    Decorator to mark a method as a LangChain tool.
    
    Compatible with Semantic Kernel's @kernel_function decorator.
    Can be used as a drop-in replacement.
    
    Args:
        description: Description of the tool
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        wrapper.__kernel_function__ = True
        if description:
            wrapper.__kernel_function_description__ = description
        
        return wrapper
    
    return decorator


kernel_function = langchain_tool
