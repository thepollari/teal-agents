import asyncio
from contextlib import nullcontext
from typing import AsyncIterable, List, Dict

import aiohttp
from collab_orchestrator.agents import TaskAgent
from collab_orchestrator.agents.task_agent import PreRequisite
from collab_orchestrator.co_types import (
    new_event_response,
    EventType,
    AgentResponseEvent,
    PartialAgentResponseEvent,
    AgentRequestEvent,
)
from collab_orchestrator.planning_handler.plan import ExecutableTask, TaskStatus, Step
from ska_utils import get_telemetry


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
                task_id=task.task_id,
                agent_name=task.task_agent,
                task_result=task_result,
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
                        task_id=task.task_id,
                        agent_name=task.task_agent,
                        partial_result=content,
                    ),
                )
                task_result = f"{task_result}{content}"
            task.result = task_result
            task.status = TaskStatus.DONE
            self.task_accumulator[task.task_id] = task
            yield new_event_response(
                EventType.AGENT_RESPONSE,
                AgentResponseEvent(
                    task_id=task.task_id,
                    agent_name=task.task_agent,
                    task_result=task_result,
                ),
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
                            task_id=task.task_id,
                            agent_name=task.task_agent,
                            task_goal=task.task_goal,
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

            async def process_task(task) -> AsyncIterable[str]:
                yield new_event_response(
                    EventType.AGENT_REQUEST,
                    AgentRequestEvent(
                        task_id=task.task_id,
                        agent_name=task.task_agent,
                        task_goal=task.task_goal,
                    ),
                )
                async for result in self._execute_task_stream(task):
                    yield result

            streams = [process_task(task) for task in step.step_tasks]
            async for result in self._merge_async_iterables(streams):
                yield result

    async def _merge_async_iterables(
        self, async_iterables: List[AsyncIterable[str]]
    ) -> AsyncIterable[str]:
        async def consume(iterable, queue):
            async for item in iterable:
                await queue.put(item)
            await queue.put(None)  # Signal the end of the iterable

        queue = asyncio.Queue()
        consumers = [
            asyncio.create_task(consume(iterable, queue))
            for iterable in async_iterables
        ]
        num_finished = 0
        while num_finished < len(async_iterables):
            result = await queue.get()
            if result is None:
                num_finished += 1
            else:
                yield result
        await asyncio.gather(*consumers)
