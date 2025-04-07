import uuid
from contextlib import nullcontext
from copy import deepcopy
from typing import List, Dict

from collab_orchestrator.agents import (
    AgentGateway,
    BaseAgentBuilder,
    BaseAgent,
    TaskAgent,
)
from collab_orchestrator.co_types import BaseConfig, ChatHistory, KindHandler
from collab_orchestrator.configs import (
    CONFIGS,
    TA_SERVICE_CONFIG,
    TA_AGW_HOST,
    TA_AGW_SECURE,
    TA_AGW_KEY,
)
from collab_orchestrator.handler_factory import HandlerFactory
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic_yaml import parse_yaml_file_as
from ska_utils import AppConfig, strtobool, initialize_telemetry, get_telemetry


def docstring_parameter(*sub):
    def dec(obj):
        obj.__doc__ = obj.__doc__.format(*sub)
        return obj

    return dec


AppConfig.add_configs(CONFIGS)
app_config = AppConfig()

config_file = app_config.get(TA_SERVICE_CONFIG.env_name)
config: BaseConfig = parse_yaml_file_as(BaseConfig, config_file)

if config.apiVersion != "skagents/v1":
    raise ValueError(f"Unknown apiVersion: {config.apiVersion}")

if config.description:
    description = config.description
else:
    description = f"{config.service_name} {config.version}"

initialize_telemetry(config.service_name, app_config)
t = get_telemetry()

agent_gateway: AgentGateway
base_agent_builder: BaseAgentBuilder
task_agents_bases: List[BaseAgent] = []
task_agents: List[TaskAgent] = []
handler: KindHandler


async def initialize():
    global agent_gateway, base_agent_builder, task_agents_bases, task_agents, handler

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

        for task_agent_name in config.spec.agents:
            task_agent_base = await base_agent_builder.build_agent(task_agent_name)
            task_agents_bases.append(task_agent_base)

            task_agent = TaskAgent(agent=task_agent_base, gateway=agent_gateway)
            task_agents.append(task_agent)

        handler_factory = HandlerFactory(
            t,
            config,
            agent_gateway,
            base_agent_builder,
            task_agents_bases,
            task_agents,
        )
        if not handler_factory.is_valid_handler(config.kind):
            raise ValueError(f"Unknown kind: {config.kind}")

        handler = handler_factory.get_handler(config.kind)
        await handler.initialize()


app = FastAPI()
app.add_event_handler("startup", initialize)

session_cache: Dict[str, ChatHistory] = {}


@app.post(f"/{config.service_name}/{config.version}/sse")
@docstring_parameter(description)
async def invoke_sse(chat_history: ChatHistory):
    """
    {0}

    SSE Handler
    """

    if not chat_history:
        raise HTTPException(status_code=400, detail="Chat history is required")
    if chat_history.chat_history[-1].role != "user":
        raise HTTPException(status_code=400, detail="First message must be from user")

    session_id = str(uuid.uuid4())
    session_cache[session_id] = chat_history

    return {"session_id": session_id}


@app.get(f"/{config.service_name}/{config.version}/sse/{{session_id}}")
async def get_sse_response(session_id: str):
    """
    SSE Handler
    """

    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID is required")
    if session_id not in session_cache:
        raise HTTPException(status_code=400, detail="Session ID not found")

    chat_history = deepcopy(session_cache[session_id])
    request = chat_history.chat_history.pop()

    return StreamingResponse(
        handler.invoke(chat_history, request.content),
        media_type="text/event-stream",
    )
