from contextlib import nullcontext
from typing import List, AsyncIterable

from fastapi import FastAPI, HTTPException
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
    new_event_response,
    EventType,
    PlanningFailedException,
    ErrorResponse,
)
from group_orchestrator.go_types.requests import ChatHistory
from group_orchestrator.plan_manager import PlanManager
from group_orchestrator.step_executor import StepExecutor

AppConfig.add_configs(CONFIGS)
app_config = AppConfig()

config_file = app_config.get(TA_SERVICE_CONFIG.env_name)
config: Config = parse_yaml_file_as(Config, config_file)

initialize_telemetry(config.service_name, app_config)
t = get_telemetry()

agent_gateway: AgentGateway
base_agent_builder: BaseAgentBuilder
plan_manager: PlanManager
task_agents_bases: List[BaseAgent] = []
task_agents: List[TaskAgent] = []


async def initialize():
    global agent_gateway, base_agent_builder, plan_manager, task_agents_bases, task_agents

    with (
        t.tracer.start_as_current_span("initialization")
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

        for task_agent_name in config.spec.agents:
            task_agent_base = await base_agent_builder.build_agent(task_agent_name)
            task_agents_bases.append(task_agent_base)

            task_agent = TaskAgent(agent=task_agent_base, gateway=agent_gateway)
            task_agents.append(task_agent)


async def run(overall_goal: str) -> AsyncIterable:
    with (
        t.tracer.start_as_current_span(
            name="invoke-sse", attributes={"goal": overall_goal}
        )
        if t.telemetry_enabled()
        else nullcontext()
    ):
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
            except Exception as e:
                yield new_event_response(
                    EventType.ERROR, ErrorResponse(status_code=500, detail=str(e))
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
app.add_event_handler("startup", initialize)


@app.post(f"/{config.service_name}/{config.version}/sse")
async def invoke_sse(chat_history: ChatHistory):
    if not chat_history:
        raise HTTPException(status_code=400, detail="Chat history is required")

    if chat_history.chat_history[0].role != "user":
        raise HTTPException(status_code=400, detail="First message must be from user")

    return StreamingResponse(
        run(chat_history.chat_history[0].content), media_type="text/event-stream"
    )
