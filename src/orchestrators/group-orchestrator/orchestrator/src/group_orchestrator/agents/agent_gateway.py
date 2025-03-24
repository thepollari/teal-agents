from typing import Any

import aiohttp
from opentelemetry.propagate import inject
from pydantic import BaseModel


class AgentGateway(BaseModel):
    host: str
    secure: bool
    agw_key: str

    def _get_endpoint_for_agent(self, agent_name: str, agent_version: str) -> str:
        protocol = "https" if self.secure else "http"
        return f"{protocol}://{self.host}/{agent_name}/{agent_version}"

    async def invoke_agent(
        self,
        session: aiohttp.ClientSession,
        agent_name: str,
        agent_version: str,
        agent_input: BaseModel,
    ) -> Any:
        payload = agent_input.model_dump_json()

        headers = {
            "taAgwKey": self.agw_key,
            "Content-Type": "application/json",
        }
        inject(headers)
        async with session.post(
            self._get_endpoint_for_agent(agent_name, agent_version),
            data=payload,
            headers=headers,
        ) as response:
            response.raise_for_status()
            return await response.json()
