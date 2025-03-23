from typing import Any
from pydantic import BaseModel
from group_orchestrator.agents.agent_gateway import AgentGateway
from group_orchestrator.agents.types import BaseAgent


class InvokableAgent:
    def __init__(self, agent: BaseAgent, gateway: AgentGateway):
        self.agent = agent
        self.gateway = gateway

    def invoke(self, agent_input: BaseModel) -> Any:
        """
        Invokes the agent using the provided input.

        Args:
            agent_input (BaseModel): The input data for the agent.

        Returns:
            Any: The response from the agent.
        """
        return self.gateway.invoke_agent(
            agent_name=self.agent.name,
            agent_version=self.agent.version,
            agent_input=agent_input,
        )
