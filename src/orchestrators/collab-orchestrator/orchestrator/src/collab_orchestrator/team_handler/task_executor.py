from collections.abc import AsyncIterable
from contextlib import nullcontext

from httpx_sse import ServerSentEvent
from ska_utils import get_telemetry, KeepaliveMessage, execute_with_keepalive

from collab_orchestrator.agents import TaskAgent
from collab_orchestrator.co_types import (
    AgentRequestEvent,
    ErrorResponse,
    EventType,
    InvokeResponse,
    PartialResponse,
    new_event_response,
)
from collab_orchestrator.team_handler.conversation import Conversation


class TaskExecutor:
    def __init__(self, agents: list[TaskAgent]):
        self._logger = get_telemetry().get_logger(self.__class__.__name__)
        self.agents = {}
        for agent in agents:
            self.agents[f"{agent.agent.name}:{agent.agent.version}"] = agent
        self.t = get_telemetry()

    async def execute_task_sse(
        self,
        task_id: str,
        instructions: str,
        agent_name: str,
        conversation: Conversation,
        session_id: str | None = None,
        source: str | None = None,
        request_id: str | None = None,
    ) -> AsyncIterable[str]:
        with (
            self.t.tracer.start_as_current_span(
                name="execute-task",
                attributes={"instructions": instructions, "agent_name": agent_name},
            )
            if self.t.telemetry_enabled()
            else nullcontext()
        ):
            task_agent = self.agents[agent_name]
            if not task_agent:
                self._logger.error(f"Task agent {agent_name} not found.")
                raise ValueError(f"Task agent {agent_name} not found.")

            yield new_event_response(
                EventType.AGENT_REQUEST,
                AgentRequestEvent(
                    session_id=session_id,
                    source=source,
                    request_id=request_id,
                    task_id=task_id,
                    agent_name=agent_name,
                    task_goal=instructions,
                ),
            )

            task_result = ""
            pre_reqs = conversation.to_pre_requisites()
            try:
                self._logger.debug(
                    f"Starting task execution for {task_id} with agent {agent_name}"
                )
                async for content in task_agent.perform_task_sse(
                    session_id, instructions, pre_reqs
                ):
                    if isinstance(content, PartialResponse):
                        yield new_event_response(EventType.PARTIAL_RESPONSE, content)
                    elif isinstance(content, KeepaliveMessage):
                        yield new_event_response(EventType.KEEPALIVE_RESPONSE, content)
                    elif isinstance(content, InvokeResponse):
                        self._logger.debug("Received final response from agent")
                        task_result = content.output_raw
                        yield new_event_response(EventType.FINAL_RESPONSE, content)
                    elif isinstance(content, ServerSentEvent):
                        self._logger.warning(
                            f"Received unexpected ServerSentEvent: {content}"
                        )
                        yield f"event: {content.event}\ndata: {content.data}\n\n"
                    else:
                        self._logger.warning(
                            f"Received unknown response type: {type(content)} - {str(content)}"
                        )
                        yield new_event_response(
                            EventType.ERROR,
                            ErrorResponse(
                                session_id=session_id,
                                source=source,
                                request_id=request_id,
                                status_code=500,
                                detail=f"Unknown response type - {str(content)}",
                            ),
                        )
            except Exception as e:
                self._logger.error(f"Task execution failed: {e}")
                yield new_event_response(
                    EventType.ERROR,
                    ErrorResponse(
                        session_id=session_id,
                        source=source,
                        request_id=request_id,
                        status_code=500,
                        detail=f"Unexpected error occurred: {e}",
                    ),
                )
            conversation.add_item(task_id, agent_name, instructions, task_result)

    async def execute_task(
        self,
        task_id: str,
        instructions: str,
        agent_name: str,
        conversation: Conversation,
        session_id: str | None = None,
        source: str | None = None,
        request_id: str | None = None,
    ) -> AsyncIterable[str]:
        with (
            self.t.tracer.start_as_current_span(
                name="execute-task",
                attributes={"instructions": instructions, "agent_name": agent_name},
            )
            if self.t.telemetry_enabled()
            else nullcontext()
        ):
            task_agent = self.agents[agent_name]
            if not task_agent:
                raise ValueError(f"Task agent {agent_name} not found.")

            yield new_event_response(
                EventType.AGENT_REQUEST,
                AgentRequestEvent(
                    session_id=session_id,
                    source=source,
                    request_id=request_id,
                    task_id=task_id,
                    agent_name=agent_name,
                    task_goal=instructions,
                ),
            )

            try:
                pre_reqs = conversation.to_pre_requisites()
                task_response: InvokeResponse

                perform_task_coro = task_agent.perform_task(
                    session_id, instructions, pre_reqs
                )
                async for message in execute_with_keepalive(
                    perform_task_coro, logger=self._logger
                ):
                    if isinstance(message, KeepaliveMessage):
                        yield new_event_response(EventType.KEEPALIVE_RESPONSE, message)
                    else:
                        task_response = message
                        break

                conversation.add_item(
                    task_id, agent_name, instructions, task_response.output_raw
                )
                yield new_event_response(EventType.FINAL_RESPONSE, task_response)
            except Exception as e:
                yield new_event_response(
                    EventType.ERROR,
                    ErrorResponse(
                        session_id=session_id,
                        source=source,
                        request_id=request_id,
                        status_code=500,
                        detail=f"Unexpected error occurred: {e}",
                    ),
                )
