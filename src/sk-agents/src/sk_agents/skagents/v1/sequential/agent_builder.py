from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.function_choice_behavior import (
    FunctionChoiceBehavior,
)
from semantic_kernel.functions.kernel_arguments import KernelArguments

from sk_agents.extra_data_collector import ExtraDataCollector
from sk_agents.ska_types import ModelType
from sk_agents.skagents.kernel_builder import KernelBuilder
from sk_agents.skagents.v1.sequential.config import AgentConfig
from sk_agents.skagents.v1.sequential.sk_agent import SKAgent


class AgentBuilder:
    def __init__(self, kernel_builder: KernelBuilder):
        self.kernel_builder = kernel_builder

    def build_agent(
        self,
        agent_config: AgentConfig,
        authorization: str | None = None,
        extra_data_collector: ExtraDataCollector | None = None,
    ) -> SKAgent:
        kernel = self.kernel_builder.build_kernel(
            agent_config.model,
            agent_config.name,
            agent_config.plugins,
            agent_config.remote_plugins,
            authorization,
            extra_data_collector,
        )
        settings = kernel.get_prompt_execution_settings_from_service_id(
            agent_config.name
        )
        settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

        model_type: ModelType = self.kernel_builder.get_model_type_for_name(
            agent_config.model
        )

        return SKAgent(
            model_name=agent_config.model,
            model_type=model_type,
            agent=ChatCompletionAgent(
                kernel=kernel,
                name=agent_config.name,
                instructions=agent_config.system_prompt,
                arguments=KernelArguments(settings=settings),
            ),
        )
