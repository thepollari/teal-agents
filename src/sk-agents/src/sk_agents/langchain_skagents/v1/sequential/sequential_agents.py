"""
Simplified LangChain Sequential Agents handler.

Implements sequential task execution using LangChain, maintaining
compatibility with the existing API while validating the infrastructure.
"""

import json
import logging
import time
import uuid
from collections.abc import AsyncIterable
from contextlib import nullcontext
from copy import deepcopy
from typing import Any

from ska_utils import get_telemetry

from sk_agents.exceptions import AgentInvokeException, InvalidConfigException
from sk_agents.extra_data_collector import ExtraDataCollector, ExtraDataPartial
from sk_agents.langchain_adapter.agent_builder import LangChainAgentBuilder
from sk_agents.langchain_adapter.chain_builder import ChainBuilder
from sk_agents.langchain_adapter.utils import parse_chat_history_to_langchain
from sk_agents.langchain_skagents.v1.sequential.task_builder import LangChainTaskBuilder
from sk_agents.ska_types import (
    BaseConfig,
    BaseHandler,
    IntermediateTaskResponse,
    InvokeResponse,
    PartialResponse,
    TokenUsage,
)
from sk_agents.skagents.v1.sequential.config import Config
from sk_agents.type_loader import get_type_loader

logger = logging.getLogger(__name__)


class LangChainSequentialAgents(BaseHandler):
    """
    Sequential agent handler using LangChain.
    
    This is a simplified version that validates the infrastructure works
    before implementing all complex features like output transformation.
    """

    def __init__(
        self,
        config: BaseConfig,
        chain_builder: ChainBuilder,
        agent_builder: LangChainAgentBuilder,
    ):
        """
        Initialize the sequential agents handler.
        
        Args:
            config: Agent configuration
            chain_builder: ChainBuilder for creating chains
            agent_builder: LangChainAgentBuilder for creating agents
        """
        if hasattr(config, "spec"):
            self.config = Config(config=config)
        else:
            raise InvalidConfigException(
                f"Invalid config: Expected 'spec' attribute, got {config.__dict__}"
            )

        self.name = config.service_name
        self.version = config.version
        self.chain_builder = chain_builder

        task_configs = self.config.get_tasks()
        if not task_configs:
            raise InvalidConfigException(
                f"Invalid agent configuration: Expected 'spec.tasks', got {config.spec.tasks}"
            )
        
        sorted_configs = sorted(task_configs, key=lambda x: x.task_no)
        task_builder = LangChainTaskBuilder(agent_builder)
        
        self.tasks = []
        for i in range(len(sorted_configs) - 1):
            task_config = sorted_configs[i]
            self.tasks.append(
                task_builder.build_task(task_config, self.config.get_agents())
            )
        
        self.tasks.append(
            task_builder.build_task(
                sorted_configs[-1],
                self.config.get_agents(),
                self.config.config.output_type,
            )
        )

    @staticmethod
    def _parse_task_inputs(
        inputs: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """
        Parse inputs for tasks, removing chat_history.
        
        Args:
            inputs: Input dictionary
            
        Returns:
            Cleaned input dictionary for tasks
        """
        if inputs is not None:
            task_inputs = deepcopy(inputs)
            if "chat_history" in task_inputs:
                del task_inputs["chat_history"]
        else:
            task_inputs = None
        return task_inputs

    async def invoke_stream(
        self, inputs: dict[str, Any] | None = None
    ) -> AsyncIterable[PartialResponse | IntermediateTaskResponse | InvokeResponse]:
        """
        Execute tasks sequentially with streaming.
        
        Args:
            inputs: Input dictionary with chat_history and other params
            
        Yields:
            PartialResponse, IntermediateTaskResponse, or InvokeResponse
        """
        collector = ExtraDataCollector()
        jt = get_telemetry()
        
        task_no = 0
        completion_tokens: int = 0
        prompt_tokens: int = 0
        total_tokens: int = 0
        final_response = []
        
        chat_history = parse_chat_history_to_langchain(inputs)
        task_inputs = self._parse_task_inputs(inputs)
        
        session_id: str
        if inputs and "session_id" in inputs and inputs["session_id"]:
            session_id = inputs["session_id"]
        else:
            session_id = str(uuid.uuid4().hex)
        request_id = str(uuid.uuid4().hex)
        
        average_ttft_ms = []
        
        with (
            jt.tracer.start_as_current_span("handler-stream")
            if jt.telemetry_enabled()
            else nullcontext()
        ) as stream_span:
            for task in self.tasks[:-1]:
                try:
                    start_time = time.time()
                    i_response: InvokeResponse = await task.invoke(
                        history=chat_history,
                        inputs=task_inputs
                    )
                    
                    response_time = time.time()
                    ttft_ms = (response_time - start_time) * 1000
                    average_ttft_ms.append(ttft_ms)
                    
                    i_response.session_id = session_id
                    i_response.source = f"{self.name}:{self.version}"
                    i_response.request_id = request_id

                    if task_inputs is None:
                        task_inputs = {}
                    task_inputs[f"_{task.name}"] = i_response.output_raw
                    
                    completion_tokens += i_response.token_usage.completion_tokens
                    prompt_tokens += i_response.token_usage.prompt_tokens
                    total_tokens += i_response.token_usage.total_tokens
                    collector.add_extra_data_items(i_response.extra_data)
                    
                    task_no += 1
                    yield IntermediateTaskResponse(
                        task_no=task_no,
                        task_name=task.name,
                        response=i_response,
                    )
                except Exception as e:
                    raise AgentInvokeException(
                        f"Error invoking {self.name}:{self.version} "
                        f"for Session-id {session_id}, Request-id {request_id}, "
                        f"Task description {task.description}. Error: {str(e)}"
                    ) from e

            start_time = time.time()
            first_token_received = False
            
            async for chunk in self.tasks[-1].invoke_stream(
                history=chat_history,
                inputs=task_inputs
            ):
                if not first_token_received:
                    first_token_time = time.time()
                    ttft_ms = (first_token_time - start_time) * 1000
                    average_ttft_ms.append(ttft_ms)
                    first_token_received = True
                
                if hasattr(chunk, 'content'):
                    content = chunk.content
                elif isinstance(chunk, str):
                    content = chunk
                else:
                    content = str(chunk)
                
                try:
                    extra_data_partial: ExtraDataPartial = ExtraDataPartial.new_from_json(content)
                    collector.add_extra_data_items(extra_data_partial.extra_data)
                except Exception:
                    if len(content) > 0:
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
                if average_ttft_ms:
                    average_ttft = sum(average_ttft_ms) / len(average_ttft_ms)
                    stream_span.add_event(
                        "agent_time_to_first_token",
                        attributes={"first_token_time_ms": average_ttft},
                    )
            
            logger.info(
                f"{self.name}:{self.version} responded with {total_tokens} tokens. "
                f"Session-id {session_id}, Request-id {request_id}"
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
                extra_data=collector.get_extra_data(),
                output_raw=final_response_str,
            )
            
            yield response

    async def invoke(self, inputs: dict[str, Any] | None = None) -> InvokeResponse:
        """
        Execute tasks sequentially without streaming.
        
        Args:
            inputs: Input dictionary with chat_history and other params
            
        Returns:
            InvokeResponse with final output and token usage
        """
        jt = get_telemetry()
        task_no = 0
        
        completion_tokens: int = 0
        prompt_tokens: int = 0
        total_tokens: int = 0
        
        collector = ExtraDataCollector()
        
        chat_history = parse_chat_history_to_langchain(inputs)
        task_inputs = self._parse_task_inputs(inputs)
        
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
            average_ttft_ms = []
            last_output = ""
            
            for task in self.tasks:
                try:
                    start_time = time.time()
                    i_response = await task.invoke(
                        history=chat_history,
                        inputs=task_inputs
                    )
                    response_time = time.time()
                    ttft_ms = (response_time - start_time) * 1000
                    average_ttft_ms.append(ttft_ms)
                    
                    if task_inputs is None:
                        task_inputs = {}
                    task_inputs[f"_{task.name}"] = i_response.output_raw
                    
                    completion_tokens += i_response.token_usage.completion_tokens
                    prompt_tokens += i_response.token_usage.prompt_tokens
                    total_tokens += i_response.token_usage.total_tokens
                    collector.add_extra_data_items(i_response.extra_data)
                    
                    last_output = i_response.output_raw
                    task_no += 1
                    
                except Exception as e:
                    raise AgentInvokeException(
                        f"Error invoking {self.name}:{self.version} "
                        f"for Session-id {session_id}, Request-id {request_id}, "
                        f"Task description {task.description}. Error: {str(e)}"
                    ) from e
            
            if invoke_span:
                invoke_span.set_attribute("completion_tokens", completion_tokens)
                invoke_span.set_attribute("prompt_tokens", prompt_tokens)
                invoke_span.set_attribute("total_tokens", total_tokens)
                if average_ttft_ms:
                    average_response_time = sum(average_ttft_ms) / len(average_ttft_ms)
                    invoke_span.add_event(
                        "agent_response_time_ms",
                        attributes={"response_time_ms": average_response_time},
                    )
            
            logger.info(
                f"{self.name}:{self.version} responded with {total_tokens} tokens. "
                f"Session-id {session_id}, Request-id {request_id}"
            )
            
            response = InvokeResponse(
                session_id=session_id,
                source=f"{self.name}:{self.version}",
                request_id=request_id,
                token_usage=TokenUsage(
                    completion_tokens=completion_tokens,
                    prompt_tokens=prompt_tokens,
                    total_tokens=total_tokens,
                ),
                extra_data=collector.get_extra_data(),
                output_raw=last_output,
            )
            
            return response
