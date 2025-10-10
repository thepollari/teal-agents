"""
LangChain Task implementation.

Replaces Semantic Kernel Task with LangChain equivalent,
maintaining the same interface for sequential task execution.
"""

from collections.abc import AsyncIterable
from typing import Any

from jinja2 import Template
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage, HumanMessage

from sk_agents.extra_data_collector import ExtraDataCollector, ExtraDataPartial
from sk_agents.langchain_adapter.langchain_agent import LangChainAgent
from sk_agents.langchain_adapter.utils import get_token_usage_for_response
from sk_agents.ska_types import EmbeddedImage, InvokeResponse, TokenUsage


class LangChainTask:
    """
    Task for sequential execution using LangChain agents.
    
    Maintains compatibility with the original Task interface while
    using LangChain messages and agents internally.
    """

    def __init__(
        self,
        name: str,
        description: str,
        instructions: str,
        agent: LangChainAgent,
        extra_data_collector: ExtraDataCollector | None = None,
    ):
        """
        Initialize a LangChain task.
        
        Args:
            name: Task name
            description: Task description
            instructions: Jinja2 template for task instructions
            agent: LangChainAgent to execute the task
            extra_data_collector: Optional collector for extra data
        """
        self.name = name
        self.description = description
        self.instructions = instructions
        self.agent = agent
        if extra_data_collector:
            self.extra_data_collector = extra_data_collector
        else:
            self.extra_data_collector = ExtraDataCollector()

    def _get_user_message_with_inputs(
        self,
        inputs: dict[str, Any] | None = None
    ) -> str:
        """
        Render task instructions with input variables.
        
        Args:
            inputs: Dictionary of variables for template rendering
            
        Returns:
            Rendered instruction string
        """
        if inputs is None:
            return self.instructions
        return Template(self.instructions).render(inputs)

    @staticmethod
    def _parse_image_input(
        inputs: dict[str, Any] | None = None,
    ) -> EmbeddedImage | None:
        """
        Extract embedded image from inputs.
        
        Args:
            inputs: Input dictionary
            
        Returns:
            EmbeddedImage if present, None otherwise
        """
        if not inputs:
            return None

        if "embedded_image" in inputs:
            return inputs.pop("embedded_image")
        return None

    def _get_message(
        self,
        inputs: dict[str, Any] | None = None
    ) -> HumanMessage:
        """
        Create a HumanMessage from task instructions and inputs.
        
        For now, this handles text content. Multi-modal support (images)
        can be added later if needed.
        
        Args:
            inputs: Input variables for template rendering
            
        Returns:
            HumanMessage with rendered content
        """
        content = self._get_user_message_with_inputs(inputs)
        
        
        return HumanMessage(content=content)

    async def invoke_stream(
        self,
        history: list[BaseMessage],
        inputs: dict[str, Any] | None = None,
    ) -> AsyncIterable[AIMessageChunk | str]:
        """
        Execute task with streaming.
        
        Args:
            history: List of previous messages
            inputs: Input variables for task
            
        Yields:
            AIMessageChunk or string chunks from the agent
        """
        message = self._get_message(inputs)
        history.append(message)
        
        contents = []
        
        async for chunk in self.agent.invoke_stream(history):
            contents.append(chunk)
            yield chunk
        
        if not self.extra_data_collector.is_empty():
            yield ExtraDataPartial(
                extra_data=self.extra_data_collector.get_extra_data()
            ).model_dump_json()
        
        message_content = "".join([
            chunk.content if hasattr(chunk, 'content') else str(chunk)
            for chunk in contents
        ])
        history.append(AIMessage(content=message_content))

    async def invoke(
        self,
        history: list[BaseMessage],
        inputs: dict[str, Any] | None = None,
    ) -> InvokeResponse:
        """
        Execute task without streaming.
        
        Args:
            history: List of previous messages
            inputs: Input variables for task
            
        Returns:
            InvokeResponse with task output and token usage
        """
        message = self._get_message(inputs)
        history.append(message)
        
        response_content = []
        completion_tokens: int = 0
        prompt_tokens: int = 0
        total_tokens: int = 0
        
        async for content in self.agent.invoke(history):
            response_content.append(content)
            history.append(content)
            
            call_usage = get_token_usage_for_response(
                self.agent.get_model_type(),
                content
            )
            completion_tokens += call_usage.completion_tokens
            prompt_tokens += call_usage.prompt_tokens
            total_tokens += call_usage.total_tokens
        
        return InvokeResponse(
            token_usage=TokenUsage(
                completion_tokens=completion_tokens,
                prompt_tokens=prompt_tokens,
                total_tokens=total_tokens,
            ),
            extra_data=self.extra_data_collector.get_extra_data(),
            output_raw=response_content[-1].content if response_content else "",
        )
