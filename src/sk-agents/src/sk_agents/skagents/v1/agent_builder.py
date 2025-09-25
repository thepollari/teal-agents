from typing import Any

from sk_agents.extra_data_collector import ExtraDataCollector
from sk_agents.ska_types import ModelType
from sk_agents.skagents.kernel_builder import ChainBuilder
from sk_agents.skagents.v1.sequential.config import AgentConfig
from sk_agents.skagents.v1.sk_agent import SKAgent


class AgentBuilder:
    def __init__(self, chain_builder: ChainBuilder, authorization: str | None = None):
        self.chain_builder = chain_builder
        self.authorization = authorization

    def build_agent(
        self,
        agent_config: AgentConfig,
        extra_data_collector: ExtraDataCollector | None = None,
        output_type: str | None = None,
    ) -> SKAgent:
        chain = self.chain_builder.build_chain(
            agent_config.model,
            agent_config.name,
            agent_config.system_prompt,
            agent_config.plugins,
            agent_config.remote_plugins,
            self.authorization,
            extra_data_collector,
        )

        so_supported: bool = self.chain_builder.model_supports_structured_output(
            agent_config.model
        )

        model_type: ModelType = self.chain_builder.get_model_type_for_name(agent_config.model)

        model_attributes: dict[str, Any] = {
            "model_type": model_type,
            "so_supported": so_supported,
        }

        return SKAgent(
            model_name=agent_config.model,
            model_attributes=model_attributes,
            agent=chain,
        )
