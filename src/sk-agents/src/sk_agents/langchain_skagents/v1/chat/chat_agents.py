"""
Simplified LangChain Chat Agents handler.

Implements conversational agent using LangChain, maintaining
compatibility with the existing API.
"""

import time
import uuid
from collections.abc import AsyncIterable
from contextlib import nullcontext
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from ska_utils import get_telemetry

from sk_agents.extra_data_collector import ExtraDataCollector, ExtraDataPartial
from sk_agents.langchain_adapter.agent_builder import LangChainAgentBuilder
from sk_agents.langchain_adapter.utils import (
    get_token_usage_for_response,
    parse_chat_history_to_langchain,
)
from sk_agents.ska_types import (
    BaseConfig,
    BaseHandler,
    InvokeResponse,
    PartialResponse,
    TokenUsage,
)
from sk_agents.skagents.v1.chat.config import Config

import logging

logger = logging.getLogger(__name__)


class LangChainChatAgents(BaseHandler):
    """
    Chat agent handler using LangChain.
    
    Simplified version for testing the infrastructure.
    """

    def __init__(
        self,
        config: BaseConfig,
        agent_builder: LangChainAgentBuilder,
        is_v2: bool = False
    ):
        """
        Initialize the chat agents handler.
        
        Args:
            config: Agent configuration
            agent_builder: LangChainAgentBuilder for creating agents
            is_v2: Whether this is v2 API (affects naming)
        """
        self.version = config.version
        if not is_v2:
            self.name = config.service_name
            if config.input_type not in [
                "BaseInput",
                "BaseInputWithUserContext",
                "BaseMultiModalInput",
            ]:
                raise ValueError("Invalid input type")
        else:
            self.name = config.name

        if hasattr(config, "spec"):
            self.config = Config(config=config)
        else:
            raise ValueError("Invalid config")

        self.agent_builder = agent_builder

    @staticmethod
    def _augment_with_user_context(
        inputs: dict[str, Any] | None,
        messages: list
    ) -> None:
        """
        Add user context to message history if present.
        
        Args:
            inputs: Input dictionary
            messages: List of LangChain messages to augment
        """
        if not inputs or "user_context" not in inputs:
            return
        
        if inputs["user_context"]:
            content = "The following user context was provided:\n"
            for key, value in inputs["user_context"].items():
                content += f"  {key}: {value}\n"
            messages.append(HumanMessage(content=content))

    async def invoke_stream(
        self, inputs: dict[str, Any] | None = None
    ) -> AsyncIterable[PartialResponse | InvokeResponse]:
        """
        Execute chat agent with streaming.
        
        Args:
            inputs: Input dictionary with chat_history and user input
            
        Yields:
            PartialResponse or InvokeResponse
        """
        jt = get_telemetry()
        extra_data_collector = ExtraDataCollector()
        agent = self.agent_builder.build_agent(
            self.config.get_agent(),
            extra_data_collector
        )

        completion_tokens: int = 0
        prompt_tokens: int = 0
        total_tokens: int = 0
        final_response = []
        
        chat_history = parse_chat_history_to_langchain(inputs)
        self._augment_with_user_context(inputs, chat_history)

        session_id: str
        if inputs and "session_id" in inputs and inputs["session_id"]:
            session_id = inputs["session_id"]
        else:
            session_id = str(uuid.uuid4().hex)
        request_id = str(uuid.uuid4().hex)

        with (
            jt.tracer.start_as_current_span("handler-stream")
            if jt.telemetry_enabled()
            else nullcontext()
        ) as stream_span:
            first_token_received = False
            start_time = time.time()
            
            async for chunk in agent.invoke_stream(chat_history):
                if not first_token_received:
                    first_token_time = time.time()
                    ttft_ms = (first_token_time - start_time) * 1000
                    first_token_received = True
                
                if hasattr(chunk, 'content'):
                    content = chunk.content
                elif isinstance(chunk, str):
                    content = chunk
                else:
                    content = str(chunk)
                
                # Calculate usage metrics
                call_usage = get_token_usage_for_response(
                    agent.get_model_type(),
                    chunk
                )
                completion_tokens += call_usage.completion_tokens
                prompt_tokens += call_usage.prompt_tokens
                total_tokens += call_usage.total_tokens
                
                try:
                    # Attempt to parse as ExtraDataPartial
                    extra_data_partial: ExtraDataPartial = ExtraDataPartial.new_from_json(content)
                    extra_data_collector.add_extra_data_items(extra_data_partial.extra_data)
                except Exception:
                    if len(content) > 0:
                        # Handle and return partial response
                        final_response.append(content)
                        yield PartialResponse(
                            session_id=session_id,
                            source=f"{self.name}:{self.version}",
                            request_id=request_id,
                            output_partial=content,
                        )
            
            if stream_span:
                stream_span.set_attribute("completion_tokens", completion_tokens)
                stream_span.set_attribute("prompt_tokens", prompt_tokens)
                stream_span.set_attribute("total_tokens", total_tokens)
                if first_token_received:
                    stream_span.add_event(
                        "agent_time_to_first_token",
                        attributes={"first_token_time_ms": ttft_ms},
                    )
            
            final_response_str = "".join(final_response)
            response = InvokeResponse(
                session_id=session_id,
                source=f"{self.name}:{self.version}",
                request_id=request_id,
                token_usage=TokenUsage(
                    completion_tokens=completion_tokens,
                    prompt_tokens=prompt_tokens,
                    total_tokens=total_tokens,
                ),
                extra_data=extra_data_collector.get_extra_data(),
                output_raw=final_response_str,
            )
            yield response

    async def invoke(
        self,
        inputs: dict[str, Any] | None = None,
    ) -> InvokeResponse:
        """
        Execute chat agent without streaming.
        
        Args:
            inputs: Input dictionary with chat_history and user input
            
        Returns:
            InvokeResponse with output and token usage
        """
        extra_data_collector = ExtraDataCollector()
        agent = self.agent_builder.build_agent(
            self.config.get_agent(),
            extra_data_collector
        )
        
        chat_history = parse_chat_history_to_langchain(inputs)
        self._augment_with_user_context(inputs, chat_history)
        
        response_content = []
        completion_tokens: int = 0
        prompt_tokens: int = 0
        total_tokens: int = 0
        
        jt = get_telemetry()
        
        session_id: str
        if inputs and "session_id" in inputs and inputs["session_id"]:
            session_id = inputs["session_id"]
        else:
            session_id = str(uuid.uuid4().hex)
        request_id = str(uuid.uuid4().hex)
        
        with (
            jt.tracer.start_as_current_span("handler-invoke")
            if jt.telemetry_enabled()
            else nullcontext()
        ) as invoke_span:
            first_token_received = False
            start_time = time.time()
            
            async for content in agent.invoke(chat_history):
                if not first_token_received:
                    first_token_time = time.time()
                    ttft_ms = (first_token_time - start_time) * 1000
                    first_token_received = True
                
                response_content.append(content)
                call_usage = get_token_usage_for_response(
                    agent.get_model_type(),
                    content
                )
                completion_tokens += call_usage.completion_tokens
                prompt_tokens += call_usage.prompt_tokens
                total_tokens += call_usage.total_tokens
            
            if invoke_span:
                invoke_span.set_attribute("completion_tokens", completion_tokens)
                invoke_span.set_attribute("prompt_tokens", prompt_tokens)
                invoke_span.set_attribute("total_tokens", total_tokens)
                if first_token_received:
                    invoke_span.add_event(
                        "agent_response_time_ms",
                        attributes={"response_time_ms": ttft_ms},
                    )
            
            return InvokeResponse(
                session_id=session_id,
                source=f"{self.name}:{self.version}",
                request_id=request_id,
                token_usage=TokenUsage(
                    completion_tokens=completion_tokens,
                    prompt_tokens=prompt_tokens,
                    total_tokens=total_tokens,
                ),
                extra_data=extra_data_collector.get_extra_data(),
                output_raw=response_content[-1].content if response_content else "",
            )
