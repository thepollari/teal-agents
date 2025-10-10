"""
Utility functions for LangChain adapter.

Provides conversion utilities between Semantic Kernel types
and LangChain types for compatibility during migration.
"""

from typing import Any

from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)

from sk_agents.ska_types import ModelType, TokenUsage


def parse_chat_history_to_langchain(
    inputs: dict[str, Any] | None
) -> list[BaseMessage]:
    """
    Parse chat history from inputs and convert to LangChain messages.
    
    Args:
        inputs: Dictionary containing chat_history and other inputs
        
    Returns:
        List of LangChain BaseMessage objects
    """
    messages = []
    
    if not inputs or "chat_history" not in inputs:
        return messages
    
    chat_history = inputs["chat_history"]
    
    if isinstance(chat_history, list):
        for message in chat_history:
            if isinstance(message, dict):
                role = message.get("role", "user")
                content = message.get("content", "")
                
                if role == "system":
                    messages.append(SystemMessage(content=content))
                elif role == "assistant" or role == "ai":
                    messages.append(AIMessage(content=content))
                else:  # user or default
                    messages.append(HumanMessage(content=content))
            elif isinstance(message, str):
                messages.append(HumanMessage(content=message))
    elif isinstance(chat_history, str):
        messages.append(HumanMessage(content=chat_history))
    
    if "input" in inputs:
        messages.append(HumanMessage(content=inputs["input"]))
    elif "user_input" in inputs:
        messages.append(HumanMessage(content=inputs["user_input"]))
    
    return messages


def get_token_usage_for_response(
    model_type: ModelType,
    message: AIMessage | AIMessageChunk
) -> TokenUsage:
    """
    Extract token usage information from a LangChain message.
    
    LangChain standardizes token usage across providers:
    - usage_metadata attribute (preferred, newer LangChain versions)
    - response_metadata['usage'] (fallback for older versions)
    
    Different providers use different field names:
    - OpenAI: prompt_tokens, completion_tokens, total_tokens
    - Anthropic/Gemini: input_tokens, output_tokens
    
    Args:
        model_type: Type of model (OPENAI, ANTHROPIC, GEMINI, AZURE_OPENAI)
        message: LangChain message with usage metadata
        
    Returns:
        TokenUsage object with token counts
    """
    if hasattr(message, 'usage_metadata') and message.usage_metadata:
        usage_metadata = message.usage_metadata
        
        # usage_metadata is typically a UsageMetadata object with attributes
        input_tokens = getattr(usage_metadata, 'input_tokens', 0)
        output_tokens = getattr(usage_metadata, 'output_tokens', 0)
        total_tokens = getattr(usage_metadata, 'total_tokens', input_tokens + output_tokens)
        
        return TokenUsage(
            prompt_tokens=input_tokens,
            completion_tokens=output_tokens,
            total_tokens=total_tokens,
        )
    
    if hasattr(message, 'response_metadata') and message.response_metadata:
        response_metadata = message.response_metadata
        
        if isinstance(response_metadata, dict):
            if 'usage' in response_metadata:
                usage = response_metadata['usage']
                
                if 'prompt_tokens' in usage:
                    return TokenUsage(
                        prompt_tokens=usage.get('prompt_tokens', 0),
                        completion_tokens=usage.get('completion_tokens', 0),
                        total_tokens=usage.get('total_tokens', 0),
                    )
                elif 'input_tokens' in usage:
                    input_tokens = usage.get('input_tokens', 0)
                    output_tokens = usage.get('output_tokens', 0)
                    return TokenUsage(
                        prompt_tokens=input_tokens,
                        completion_tokens=output_tokens,
                        total_tokens=usage.get('total_tokens', input_tokens + output_tokens),
                    )
            
            if 'token_usage' in response_metadata:
                token_usage = response_metadata['token_usage']
                return TokenUsage(
                    prompt_tokens=token_usage.get('prompt_tokens', 0),
                    completion_tokens=token_usage.get('completion_tokens', 0),
                    total_tokens=token_usage.get('total_tokens', 0),
                )
    
    return TokenUsage(
        prompt_tokens=0,
        completion_tokens=0,
        total_tokens=0,
    )


def convert_sk_message_to_langchain(sk_message: Any) -> BaseMessage:
    """
    Convert a Semantic Kernel message to LangChain message.
    
    Args:
        sk_message: Semantic Kernel message object
        
    Returns:
        LangChain BaseMessage
    """
    
    if hasattr(sk_message, 'role') and hasattr(sk_message, 'content'):
        role = sk_message.role.lower()
        content = sk_message.content
        
        if 'system' in role:
            return SystemMessage(content=content)
        elif 'assistant' in role or 'ai' in role:
            return AIMessage(content=content)
        else:
            return HumanMessage(content=content)
    
    return HumanMessage(content=str(sk_message))
