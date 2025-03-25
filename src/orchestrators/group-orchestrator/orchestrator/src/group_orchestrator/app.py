from contextlib import nullcontext
from typing import List, AsyncIterable

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic_yaml import parse_yaml_file_as
from ska_utils import AppConfig, strtobool, initialize_telemetry, get_telemetry

from group_orchestrator.agents import (
    AgentGateway,
    BaseAgent,
    BaseAgentBuilder,
    PlanningAgent,
    TaskAgent,
)
from group_orchestrator.configs import (
    CONFIGS,
    TA_AGW_HOST,
    TA_AGW_SECURE,
    TA_AGW_KEY,
    TA_SERVICE_CONFIG,
)
from group_orchestrator.go_types import (
    Config,
    GroupOrchestratorRequest,
    new_event_response,
    EventType,
    PlanningFailedException,
    ErrorResponse,
)
from group_orchestrator.plan_manager import PlanManager
from group_orchestrator.step_executor import StepExecutor

AppConfig.add_configs(CONFIGS)
app_config = AppConfig()

config_file = app_config.get(TA_SERVICE_CONFIG.env_name)
config: Config = parse_yaml_file_as(Config, config_file)


async def run(overall_goal: str) -> AsyncIterable:
    initialize_telemetry(config.service_name, app_config)
    t = get_telemetry()

    with (
        t.tracer.start_as_current_span(
            name="invoke-sse", attributes={"goal": overall_goal}
        )
        if t.telemetry_enabled()
        else nullcontext()
    ):
        agent_gateway = AgentGateway(
            host=app_config.get(TA_AGW_HOST.env_name),
            secure=strtobool(app_config.get(TA_AGW_SECURE.env_name)),
            agw_key=app_config.get(TA_AGW_KEY.env_name),
        )
        base_agent_builder = BaseAgentBuilder(gateway=agent_gateway)
        planning_agent_base = await base_agent_builder.build_agent(
            config.spec.planning_agent
        )
        planning_agent = PlanningAgent(agent=planning_agent_base, gateway=agent_gateway)
        plan_manager = PlanManager(planning_agent)

        task_agents_bases: List[BaseAgent] = []
        task_agents: List[TaskAgent] = []
        for task_agent_name in config.spec.agents:
            task_agent_base = await base_agent_builder.build_agent(task_agent_name)
            task_agents_bases.append(task_agent_base)

            task_agent = TaskAgent(agent=task_agent_base, gateway=agent_gateway)
            task_agents.append(task_agent)

        with (
            t.tracer.start_as_current_span(name="build-plan")
            if t.telemetry_enabled()
            else nullcontext()
        ):
            try:
                plan = await plan_manager.generate_plan(
                    overall_goal=overall_goal, task_agents=task_agents_bases
                )
            except PlanningFailedException as e:
                yield new_event_response(
                    EventType.ERROR, ErrorResponse(status_code=400, detail=str(e))
                )
                return
            yield new_event_response(EventType.PLAN, plan)

        with (
            t.tracer.start_as_current_span(name="execute-plan")
            if t.telemetry_enabled()
            else nullcontext()
        ):
            step_executor = StepExecutor(task_agents)
            for step in plan.steps:
                try:
                    async for result in step_executor.execute_step_stream(step):
                        yield result
                except Exception as e:
                    yield new_event_response(
                        EventType.ERROR, ErrorResponse(status_code=500, detail=str(e))
                    )

        yield new_event_response(EventType.FINAL, plan.steps[-1].step_tasks[0])


app = FastAPI()


@app.post(f"/{config.service_name}/{config.version}/sse")
async def invoke_sse(go_request: GroupOrchestratorRequest):
    return StreamingResponse(
        run(go_request.overall_goal), media_type="text/event-stream"
    )
