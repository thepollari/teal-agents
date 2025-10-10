"""
LangChain Task Builder.

Builds LangChain tasks from configuration, replacing Semantic Kernel TaskBuilder.
"""

from sk_agents.extra_data_collector import ExtraDataCollector
from sk_agents.langchain_adapter.agent_builder import LangChainAgentBuilder
from sk_agents.langchain_adapter.langchain_agent import LangChainAgent
from sk_agents.langchain_skagents.v1.sequential.task import LangChainTask
from sk_agents.skagents.v1.sequential.config import AgentConfig, TaskConfig


class LangChainTaskBuilder:
    """
    Builds LangChain tasks from task configurations.
    
    Maintains the same interface as the original TaskBuilder while
    using LangChain components internally.
    """

    def __init__(self, agent_builder: LangChainAgentBuilder):
        """
        Initialize the task builder.
        
        Args:
            agent_builder: LangChainAgentBuilder for creating agents
        """
        self.agent_builder = agent_builder

    @staticmethod
    def _get_agent_config_by_name(
        agent_name: str,
        agent_configs: list[AgentConfig]
    ) -> AgentConfig:
        """
        Find agent configuration by name.
        
        Args:
            agent_name: Name of the agent
            agent_configs: List of agent configurations
            
        Returns:
            AgentConfig for the specified agent
            
        Raises:
            ValueError: If agent not found
        """
        for agent_config in agent_configs:
            if agent_config.name == agent_name:
                return agent_config
        raise ValueError(f"Agent {agent_name} not found")

    def _get_agent_for_task(
        self,
        task_config: TaskConfig,
        agent_configs: list[AgentConfig],
        extra_data_collector: ExtraDataCollector,
        output_type: str | None = None,
    ) -> LangChainAgent:
        """
        Create a LangChain agent for a task.
        
        Args:
            task_config: Task configuration
            agent_configs: List of agent configurations
            extra_data_collector: Collector for extra data
            output_type: Optional output type for structured output
            
        Returns:
            LangChainAgent configured for the task
        """
        agent_config = self._get_agent_config_by_name(
            task_config.agent,
            agent_configs
        )

        agent = self.agent_builder.build_agent(
            agent_config,
            extra_data_collector,
            output_type
        )
        return agent

    def build_task(
        self,
        task_config: TaskConfig,
        agent_configs: list[AgentConfig],
        output_type: str | None = None,
    ) -> LangChainTask:
        """
        Build a LangChain task from configuration.
        
        Args:
            task_config: Configuration for the task
            agent_configs: List of available agent configurations
            output_type: Optional output type for structured output
            
        Returns:
            LangChainTask ready to execute
        """
        extra_data_collector = ExtraDataCollector()
        agent = self._get_agent_for_task(
            task_config,
            agent_configs,
            extra_data_collector,
            output_type
        )
        
        return LangChainTask(
            name=task_config.name,
            description=task_config.description,
            instructions=task_config.instructions,
            agent=agent,
            extra_data_collector=extra_data_collector,
        )
