import requests
from typing import Any

from pydantic import BaseModel
from opentelemetry.propagate import inject


class AgentGateway(BaseModel):
    host: str
    secure: bool
    agw_key: str

    def _get_endpoint_for_agent(self, agent_name: str, agent_version: str) -> str:
        protocol = "https" if self.secure else "http"
        return f"{protocol}://{self.host}/{agent_name}/{agent_version}"

    def invoke_agent(
        self, agent_name: str, agent_version: str, agent_input: BaseModel
    ) -> Any:
        payload = agent_input.model_dump_json()

        headers = {
            "taAgwKey": self.agw_key,
            "Content-Type": "application/json",
        }
        inject(headers)
        response = requests.post(
            self._get_endpoint_for_agent(agent_name, agent_version),
            headers=headers,
            data=payload,
        )
        response_json = response.json()
        if response_json:
            return response_json
        else:
            raise Exception("Unable to invoke agent")
