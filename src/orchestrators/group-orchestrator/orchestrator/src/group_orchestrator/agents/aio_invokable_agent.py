from typing import Any

import aiohttp
from pydantic import BaseModel

from group_orchestrator.agents.aio_agent_gateway import AioAgentGateway
from group_orchestrator.agents.types import BaseAgent


class AioInvokableAgent:
    def __init__(self, agent: BaseAgent, gateway: AioAgentGateway):
        self.agent = agent
        self.gateway = gateway

    async def invoke(
        self, session: aiohttp.ClientSession, agent_input: BaseModel
    ) -> Any:
        return await self.gateway.invoke_agent(
            session=session,
            agent_name=self.agent.name,
            agent_version=self.agent.version,
            agent_input=agent_input,
        )
