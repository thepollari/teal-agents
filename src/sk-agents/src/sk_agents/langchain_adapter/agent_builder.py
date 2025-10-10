"""
LangChain Agent Builder.

Replaces the Semantic Kernel AgentBuilder with LangChain equivalent,
building agents using LCEL (LangChain Expression Language) with .bind_tools().
"""

from typing import Any

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable

from sk_agents.extra_data_collector import ExtraDataCollector
from sk_agents.langchain_adapter.chain_builder import ChainBuilder
from sk_agents.langchain_adapter.langchain_agent import LangChainAgent
from sk_agents.skagents.v1.sequential.config import AgentConfig
from sk_agents.type_loader import get_type_loader


class LangChainAgentBuilder:
    """
    Builds LangChain agents from configuration.
    
    Replaces the Semantic Kernel AgentBuilder while maintaining
    the same interface for compatibility.
    """

    def __init__(
        self,
        chain_builder: ChainBuilder,
        authorization: str | None = None
    ):
        """
        Initialize the LangChain agent builder.
        
        Args:
            chain_builder: ChainBuilder instance for creating chains
            authorization: Optional authorization header
        """
        self.chain_builder = chain_builder
        self.authorization = authorization

    def build_agent(
        self,
        agent_config: AgentConfig,
        extra_data_collector: ExtraDataCollector | None = None,
        output_type: str | None = None,
    ) -> LangChainAgent:
        """
        Build a LangChain agent from configuration.
        
        This creates an agent using LCEL with .bind_tools() for maximum flexibility,
        optionally wrapped in a ReAct agent pattern for tool calling.
        
        Args:
            agent_config: Configuration for the agent
            extra_data_collector: Optional collector for extra data/telemetry
            output_type: Optional output type for structured output
            
        Returns:
            LangChainAgent: Configured agent ready to use
        """
        langchain_agent = self.chain_builder.build_chain(
            model_name=agent_config.model,
            service_id=agent_config.name,
            plugins=agent_config.plugins or [],
            remote_plugins=agent_config.remote_plugins or [],
            authorization=self.authorization,
            extra_data_collector=extra_data_collector,
        )
        
        chat_model = langchain_agent.chat_model
        so_supported = self.chain_builder.model_supports_structured_output(
            agent_config.model
        )
        
        if agent_config.temperature is not None:
            chat_model = chat_model.bind(temperature=agent_config.temperature)
        
        if so_supported and output_type:
            type_loader = get_type_loader()
            output_schema = type_loader.get_type(output_type)
            chat_model = chat_model.with_structured_output(output_schema)
        
        prompt = self._create_prompt_template(agent_config.system_prompt)
        
        if agent_config.plugins or agent_config.remote_plugins:
            runnable = langchain_agent.runnable
            
            agent_runnable = self._create_react_agent(
                chat_model=chat_model,
                tools=runnable,
                prompt=prompt
            )
        else:
            agent_runnable = prompt | chat_model
        
        langchain_agent.runnable = agent_runnable
        langchain_agent.chat_model = chat_model
        
        return langchain_agent

    def _create_prompt_template(self, system_prompt: str) -> ChatPromptTemplate:
        """
        Create a prompt template with system instructions.
        
        Args:
            system_prompt: System instructions for the agent
            
        Returns:
            ChatPromptTemplate configured with system prompt
        """
        
        template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad", optional=True),
        ])
        
        return template

    def _create_react_agent(
        self,
        chat_model,
        tools,
        prompt: ChatPromptTemplate
    ) -> Runnable:
        """
        Create a ReAct agent for tool calling.
        
        Uses LangChain's create_react_agent which implements the ReAct
        (Reasoning + Acting) pattern using LCEL under the hood.
        
        Args:
            chat_model: The LangChain chat model
            tools: List of tools or a model with tools bound
            prompt: Prompt template
            
        Returns:
            Runnable agent that can be invoked
        """
        
        
        return prompt | chat_model
