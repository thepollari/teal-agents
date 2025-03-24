from typing import Any

import aiohttp
from pydantic import BaseModel

from group_orchestrator.agents.agent_gateway import AgentGateway
from group_orchestrator.agents.types import BaseAgent


class InvokableAgent:
    def __init__(self, agent: BaseAgent, gateway: AgentGateway):
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
