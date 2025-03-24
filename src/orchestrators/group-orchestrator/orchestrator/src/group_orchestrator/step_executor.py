import asyncio
from typing import AsyncIterable, List, Dict

import aiohttp
from pydantic import BaseModel

from group_orchestrator.agents.task_agent import TaskAgent, PreRequisite
from group_orchestrator.go_types import (
    Step,
    ExecutableTask,
    new_event_response,
    EventType,
    TaskStatus,
)


class AgentRequestEvent(BaseModel):
    agent_name: str
    task_goal: str


class AgentResponseEvent(BaseModel):
    agent_name: str
    task_result: str


class StepExecutor:
    def __init__(self, task_agents: List[TaskAgent]):
        self.task_agents: Dict[str, TaskAgent] = {}
        for task_agent in task_agents:
            self.task_agents[f"{task_agent.agent.name}:{task_agent.agent.version}"] = (
                task_agent
            )
        self.task_accumulator: Dict[str, ExecutableTask] = {}

    @staticmethod
    def _task_to_pre_requisite(task: ExecutableTask) -> PreRequisite:
        return PreRequisite(goal=task.task_goal, result=task.result)

    async def _execute_task(
        self, session: aiohttp.ClientSession, task: ExecutableTask
    ) -> AgentResponseEvent:
        task_agent = self.task_agents[task.task_agent]
        if not task_agent:
            raise ValueError(f"Task agent {task.task_agent} not found.")
        pre_requisites: List[PreRequisite] = [
            StepExecutor._task_to_pre_requisite(self.task_accumulator[pre_requisite])
            for pre_requisite in task.prerequisite_tasks
        ]
        task_result = await task_agent.perform_task(
            session, task.task_goal, pre_requisites
        )
        task.result = task_result
        task.status = TaskStatus.DONE
        self.task_accumulator[task.task_id] = task
        return AgentResponseEvent(agent_name=task.task_agent, task_result=task_result)

    async def execute_step(self, step: Step) -> AsyncIterable[str]:
        async with aiohttp.ClientSession() as session:
            aio_tasks = []
            for task in step.step_tasks:
                yield new_event_response(
                    EventType.AGENT_REQUEST,
                    AgentRequestEvent(
                        agent_name=task.task_agent, task_goal=task.task_goal
                    ),
                )
                aio_tasks.append(self._execute_task(session, task))
            for completed_task in asyncio.as_completed(aio_tasks):
                result = await completed_task
                yield new_event_response(EventType.AGENT_RESPONSE, result)
