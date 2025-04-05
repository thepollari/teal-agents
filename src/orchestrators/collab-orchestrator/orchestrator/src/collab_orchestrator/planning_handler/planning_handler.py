from contextlib import nullcontext
from typing import List, AsyncIterable

from collab_orchestrator.agents import (
    AgentGateway,
    BaseAgentBuilder,
    BaseAgent,
    TaskAgent,
)
from collab_orchestrator.co_types import (
    BaseConfig,
    new_event_response,
    EventType,
    ErrorResponse,
)
from collab_orchestrator.co_types import KindHandler
from collab_orchestrator.planning_handler.plan_manager import (
    PlanManager,
    PlanningFailedException,
)
from collab_orchestrator.planning_handler.planning_agent import PlanningAgent
from collab_orchestrator.planning_handler.step_executor import StepExecutor
from collab_orchestrator.planning_handler.types import PlanningSpec
from ska_utils import Telemetry


class PlanningHandler(KindHandler):
    def __init__(
        self,
        t: Telemetry,
        config: BaseConfig,
        agent_gateway: AgentGateway,
        base_agent_builder: BaseAgentBuilder,
        task_agents_bases: List[BaseAgent],
        task_agents: List[TaskAgent],
    ):
        super().__init__(
            t, config, agent_gateway, base_agent_builder, task_agents_bases, task_agents
        )
        self.plan_manager = None
        self.planning_agent = None

    async def initialize(self):
        spec: PlanningSpec = PlanningSpec.model_validate(
            obj=self.config.spec.model_dump()
        )

        planning_agent_base = await self.base_agent_builder.build_agent(
            spec.planning_agent
        )
        self.planning_agent = PlanningAgent(
            agent=planning_agent_base, gateway=self.agent_gateway
        )
        self.plan_manager = PlanManager(self.planning_agent)

    async def invoke(self, request: str) -> AsyncIterable:
        with (
            self.t.tracer.start_as_current_span(
                name="invoke-sse", attributes={"goal": request}
            )
            if self.t.telemetry_enabled()
            else nullcontext()
        ):
            with (
                self.t.tracer.start_as_current_span(name="build-plan")
                if self.t.telemetry_enabled()
                else nullcontext()
            ):
                try:
                    plan = await self.plan_manager.generate_plan(
                        overall_goal=request, task_agents=self.task_agents_bases
                    )
                except PlanningFailedException as e:
                    yield new_event_response(
                        EventType.ERROR, ErrorResponse(status_code=400, detail=str(e))
                    )
                    return
                except Exception as e:
                    yield new_event_response(
                        EventType.ERROR, ErrorResponse(status_code=500, detail=str(e))
                    )
                    return
                yield new_event_response(EventType.PLAN, plan)

            with (
                self.t.tracer.start_as_current_span(name="execute-plan")
                if self.t.telemetry_enabled()
                else nullcontext()
            ):
                step_executor = StepExecutor(self.task_agents)
                for step in plan.steps:
                    try:
                        async for result in step_executor.execute_step(step):
                            yield result
                    except Exception as e:
                        yield new_event_response(
                            EventType.ERROR,
                            ErrorResponse(status_code=500, detail=str(e)),
                        )

            yield new_event_response(EventType.FINAL, plan.steps[-1].step_tasks[0])
