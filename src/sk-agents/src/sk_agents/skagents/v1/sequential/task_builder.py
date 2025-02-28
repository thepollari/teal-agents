from typing import List

from sk_agents.extra_data_collector import ExtraDataCollector
from sk_agents.skagents.v1.sequential.agent_builder import AgentBuilder
from sk_agents.skagents.v1.sequential.config import AgentConfig, TaskConfig
from sk_agents.skagents.v1.sequential.sk_agent import SKAgent
from sk_agents.skagents.v1.sequential.task import Task


class TaskBuilder:
    def __init__(self, agent_builder: AgentBuilder, authorization: str | None = None):
        self.agent_builder = agent_builder
        self.authorization = authorization

    @staticmethod
    def _get_agent_config_by_name(
        agent_name: str, agent_configs: List[AgentConfig]
    ) -> AgentConfig:
        for agent_config in agent_configs:
            if agent_config.name == agent_name:
                return agent_config
        raise ValueError(f"Agent {agent_name} not found")

    def _get_agent_for_task(
        self,
        task_config: TaskConfig,
        agent_configs: List[AgentConfig],
        extra_data_collector: ExtraDataCollector,
    ) -> SKAgent:
        agent_config = TaskBuilder._get_agent_config_by_name(
            task_config.agent, agent_configs
        )

        agent = self.agent_builder.build_agent(
            agent_config, self.authorization, extra_data_collector
        )
        return agent

    def build_task(
        self, task_config: TaskConfig, agent_configs: List[AgentConfig]
    ) -> Task:
        extra_data_collector = ExtraDataCollector()
        agent = self._get_agent_for_task(
            task_config, agent_configs, extra_data_collector
        )
        return Task(
            name=task_config.name,
            description=task_config.description,
            instructions=task_config.instructions,
            agent=agent,
            extra_data_collector=extra_data_collector,
        )
