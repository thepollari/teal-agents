"""
LangChain Agent wrapper that maintains compatibility with SKAgent interface.

This wrapper allows LangChain chains/agents to be used in place of
Semantic Kernel's ChatCompletionAgent while preserving the same API.
"""

from collections.abc import AsyncIterable
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage, HumanMessage
from langchain_core.runnables import Runnable

from sk_agents.ska_types import ModelType


class LangChainAgent:
    """
    Wrapper for LangChain chains/agents that provides SKAgent-compatible interface.
    
    This allows seamless integration with existing teal-agents handlers
    while using LangChain under the hood.
    """

    def __init__(
        self,
        model_name: str,
        model_attributes: dict[str, Any],
        runnable: Runnable,
        chat_model: BaseChatModel,
    ):
        """
        Initialize LangChain agent wrapper.
        
        Args:
            model_name: Name of the LLM model
            model_attributes: Dict containing model_type and so_supported flags
            runnable: LangChain Runnable (chain/agent) to execute
            chat_model: Underlying chat model instance
        """
        self.model_name = model_name
        self.model_attributes = model_attributes
        self.runnable = runnable
        self.chat_model = chat_model
        self.tools = []

    def get_model_type(self) -> ModelType:
        """Get the model type (OPENAI, ANTHROPIC, GEMINI, AZURE_OPENAI)."""
        return self.model_attributes["model_type"]

    def so_supported(self) -> bool:
        """Check if model supports structured output."""
        return self.model_attributes["so_supported"]

    async def invoke_stream(
        self, history: list[BaseMessage]
    ) -> AsyncIterable[AIMessageChunk]:
        """
        Stream responses from the agent.
        
        Args:
            history: List of LangChain BaseMessage objects (chat history)
            
        Yields:
            AIMessageChunk: Streaming response chunks
        """
        input_data = {"messages": history}
        
        async for chunk in self.runnable.astream(input_data):
            if isinstance(chunk, AIMessageChunk):
                yield chunk
            elif isinstance(chunk, dict) and "content" in chunk:
                yield AIMessageChunk(content=chunk["content"])
            elif isinstance(chunk, str):
                yield AIMessageChunk(content=chunk)

    async def invoke(
        self, history: list[BaseMessage]
    ) -> AsyncIterable[AIMessage]:
        """
        Invoke agent and return complete response.
        
        Args:
            history: List of LangChain BaseMessage objects (chat history)
            
        Yields:
            AIMessage: Complete response messages
        """
        input_data = {"messages": history}
        
        result = await self.runnable.ainvoke(input_data)
        
        if isinstance(result, AIMessage):
            yield result
        elif isinstance(result, dict) and "content" in result:
            yield AIMessage(content=result["content"])
        elif isinstance(result, str):
            yield AIMessage(content=result)
        else:
            if hasattr(result, "get") and "messages" in result:
                messages = result["messages"]
                for msg in messages:
                    if isinstance(msg, AIMessage):
                        yield msg


class LangChainChatHistory:
    """
    Adapter to convert between Semantic Kernel ChatHistory and LangChain messages.
    
    This maintains compatibility with existing code that expects ChatHistory
    while using LangChain's message format internally.
    """

    def __init__(self):
        self.messages: list[BaseMessage] = []

    def add_user_message(self, content: str) -> None:
        """Add a user message to the history."""
        self.messages.append(HumanMessage(content=content))

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to the history."""
        self.messages.append(AIMessage(content=content))

    def add_message(self, message: BaseMessage) -> None:
        """Add a generic message to the history."""
        self.messages.append(message)

    def clear(self) -> None:
        """Clear all messages."""
        self.messages.clear()

    def __len__(self) -> int:
        """Get number of messages in history."""
        return len(self.messages)
