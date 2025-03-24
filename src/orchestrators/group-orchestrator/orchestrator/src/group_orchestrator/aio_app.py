from typing import List, AsyncIterable

import aiohttp
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic_yaml import parse_yaml_file_as
from ska_utils import AppConfig, strtobool, initialize_telemetry

from group_orchestrator.agents import BaseAgent
from group_orchestrator.agents.aio_agent_gateway import AioAgentGateway
from group_orchestrator.agents.aio_base_agent_builder import AioBaseAgentBuilder
from group_orchestrator.agents.aio_planning_agent import AioPlanningAgent
from group_orchestrator.agents.aio_task_agent import AioTaskAgent
from group_orchestrator.aio_plan_manager import AioPlanManager
from group_orchestrator.aio_step_executor import AioStepExecutor
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
)


async def run(overall_goal: str) -> AsyncIterable:
    initialize_telemetry(config.service_name, app_config)

    agent_gateway = AioAgentGateway(
        host=app_config.get(TA_AGW_HOST.env_name),
        secure=strtobool(app_config.get(TA_AGW_SECURE.env_name)),
        agw_key=app_config.get(TA_AGW_KEY.env_name),
    )
    base_agent_builder = AioBaseAgentBuilder(gateway=agent_gateway)
    planning_agent_base = await base_agent_builder.build_agent(
        config.spec.planning_agent
    )
    planning_agent = AioPlanningAgent(agent=planning_agent_base, gateway=agent_gateway)
    plan_manager = AioPlanManager(planning_agent)

    task_agents_bases: List[BaseAgent] = []
    task_agents: List[AioTaskAgent] = []
    for task_agent_name in config.spec.agents:
        task_agent_base = await base_agent_builder.build_agent(task_agent_name)
        task_agents_bases.append(task_agent_base)

        task_agent = AioTaskAgent(agent=task_agent_base, gateway=agent_gateway)
        task_agents.append(task_agent)

    plan = await plan_manager.generate_plan(
        overall_goal=overall_goal, task_agents=task_agents_bases
    )
    yield new_event_response(EventType.PLAN, plan)

    step_executor = AioStepExecutor(task_agents)
    for step in plan.steps:
        async for result in step_executor.execute_step(step):
            yield result
    yield new_event_response(EventType.FINAL, plan.steps[-1].step_tasks[0])


AppConfig.add_configs(CONFIGS)
app_config = AppConfig()

config_file = app_config.get(TA_SERVICE_CONFIG.env_name)
config: Config = parse_yaml_file_as(Config, config_file)

app = FastAPI()


@app.post(f"/{config.service_name}/{config.version}")
async def invoke_stream(go_request: GroupOrchestratorRequest):
    return StreamingResponse(
        run(go_request.overall_goal), media_type="text/event-stream"
    )
