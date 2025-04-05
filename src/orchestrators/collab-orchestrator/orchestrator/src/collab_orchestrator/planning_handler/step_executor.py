import asyncio
from contextlib import nullcontext
from typing import AsyncIterable, List, Dict

import aiohttp
from collab_orchestrator.agents import TaskAgent
from collab_orchestrator.agents.task_agent import PreRequisite
from collab_orchestrator.co_types import new_event_response, EventType
from collab_orchestrator.planning_handler.plan import ExecutableTask, TaskStatus, Step
from pydantic import BaseModel
from ska_utils import get_telemetry


class AgentRequestEvent(BaseModel):
    agent_name: str
    task_goal: str


class AgentResponseEvent(BaseModel):
    agent_name: str
    task_result: str


class PartialAgentResponseEvent(BaseModel):
    agent_name: str
    partial_result: str


class StepExecutor:
    def __init__(self, task_agents: List[TaskAgent]):
        self.task_agents: Dict[str, TaskAgent] = {}
        for task_agent in task_agents:
            self.task_agents[f"{task_agent.agent.name}:{task_agent.agent.version}"] = (
                task_agent
            )
        self.task_accumulator: Dict[str, ExecutableTask] = {}
        self.t = get_telemetry()

    @staticmethod
    def _task_to_pre_requisite(task: ExecutableTask) -> PreRequisite:
        return PreRequisite(goal=task.task_goal, result=task.result)

    async def _execute_task(
        self, session: aiohttp.ClientSession, task: ExecutableTask
    ) -> AgentResponseEvent:
        with (
            self.t.tracer.start_as_current_span(
                name="execute-task",
                attributes={"task": task.task_id, "goal": task.task_goal},
            )
            if self.t
            else nullcontext()
        ):
            task_agent = self.task_agents[task.task_agent]
            if not task_agent:
                raise ValueError(f"Task agent {task.task_agent} not found.")
            pre_requisites: List[PreRequisite] = [
                StepExecutor._task_to_pre_requisite(
                    self.task_accumulator[pre_requisite]
                )
                for pre_requisite in task.prerequisite_tasks
            ]
            task_result = await task_agent.perform_task(
                session, task.task_goal, pre_requisites
            )
            task.result = task_result
            task.status = TaskStatus.DONE
            self.task_accumulator[task.task_id] = task
            return AgentResponseEvent(
                agent_name=task.task_agent, task_result=task_result
            )

    async def _execute_task_stream(self, task: ExecutableTask) -> AsyncIterable[str]:
        with (
            self.t.tracer.start_as_current_span(
                name="execute-task",
                attributes={"task": task.task_id, "goal": task.task_goal},
            )
            if self.t
            else nullcontext()
        ):
            task_agent = self.task_agents[task.task_agent]
            if not task_agent:
                raise ValueError(f"Task agent {task.task_agent} not found.")
            pre_requisites: List[PreRequisite] = [
                StepExecutor._task_to_pre_requisite(
                    self.task_accumulator[pre_requisite]
                )
                for pre_requisite in task.prerequisite_tasks
            ]
            task_result = ""
            async for content in task_agent.perform_task_stream(
                task.task_goal, pre_requisites
            ):
                yield new_event_response(
                    EventType.PARTIAL_AGENT_RESPONSE,
                    PartialAgentResponseEvent(
                        agent_name=task.task_agent, partial_result=content
                    ),
                )
                task_result = f"{task_result}{content}"
            task.result = task_result
            task.status = TaskStatus.DONE
            self.task_accumulator[task.task_id] = task
            yield new_event_response(
                EventType.AGENT_RESPONSE,
                AgentResponseEvent(agent_name=task.task_agent, task_result=task_result),
            )

    async def execute_step(self, step: Step) -> AsyncIterable[str]:
        with (
            self.t.tracer.start_as_current_span(
                name="execute-step", attributes={"step": str(step.step_number)}
            )
            if self.t
            else nullcontext()
        ):
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

    async def execute_step_stream(self, step: Step) -> AsyncIterable[str]:
        with (
            self.t.tracer.start_as_current_span(
                name="execute-step", attributes={"step": str(step.step_number)}
            )
            if self.t
            else nullcontext()
        ):
            aio_tasks = []
            for task in step.step_tasks:
                yield new_event_response(
                    EventType.AGENT_REQUEST,
                    AgentRequestEvent(
                        agent_name=task.task_agent, task_goal=task.task_goal
                    ),
                )
                aio_tasks.append(self._execute_task_stream(task))

            async def _iterate(
                async_iterable: AsyncIterable[str], queue: asyncio.Queue[str]
            ):
                async for item in async_iterable:
                    await queue.put(item)

            queue: asyncio.Queue[str] = asyncio.Queue()
            tasks = [
                asyncio.create_task(_iterate(iterable, queue)) for iterable in aio_tasks
            ]

            try:
                while tasks:
                    done, pending = await asyncio.wait(
                        tasks, return_when=asyncio.FIRST_COMPLETED
                    )
                    for task in done:
                        tasks.remove(task)
                    while not queue.empty():
                        yield queue.get_nowait()
            finally:
                for task in tasks:
                    task.cancel()  # ensure all tasks are cancelled, in case of early termination.
                await asyncio.gather(
                    *[task for task in tasks if not task.cancelled()],
                    return_exceptions=True,
                )  # gather cancellations to avoid errors.
