from contextlib import nullcontext
from typing import List, AsyncIterable

from collab_orchestrator.agents import TaskAgent
from collab_orchestrator.co_types import (
    new_event_response,
    EventType,
    AgentRequestEvent,
    PartialAgentResponseEvent,
    AgentResponseEvent,
)
from collab_orchestrator.team_handler.conversation import Conversation
from ska_utils import get_telemetry


class TaskExecutor:
    def __init__(self, agents: List[TaskAgent]):
        self.agents = {}
        for agent in agents:
            self.agents[f"{agent.agent.name}:{agent.agent.version}"] = agent
        self.t = get_telemetry()

    async def execute_task_stream(
        self,
        task_id: str,
        instructions: str,
        agent_name: str,
        conversation: Conversation,
    ) -> AsyncIterable[str]:
        with (
            self.t.tracer.start_as_current_span(
                name="execute-task",
                attributes={"instructions": instructions, "agent_name": agent_name},
            )
            if self.t
            else nullcontext()
        ):
            task_agent = self.agents[agent_name]
            if not task_agent:
                raise ValueError(f"Task agent {agent_name} not found.")

            yield new_event_response(
                EventType.AGENT_REQUEST,
                AgentRequestEvent(
                    task_id=task_id, agent_name=agent_name, task_goal=instructions
                ),
            )

            task_result = ""
            async for content in task_agent.perform_task_stream(
                instructions, conversation.to_pre_requisites()
            ):
                yield new_event_response(
                    EventType.PARTIAL_AGENT_RESPONSE,
                    PartialAgentResponseEvent(
                        task_id=task_id, agent_name=agent_name, partial_result=content
                    ),
                )
                task_result = f"{task_result}{content}"
            conversation.add_item(task_id, agent_name, instructions, task_result)
            yield new_event_response(
                EventType.AGENT_RESPONSE,
                AgentResponseEvent(
                    task_id=task_id, agent_name=agent_name, task_result=task_result
                ),
            )
