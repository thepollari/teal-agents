import logging

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from ska_utils import AppConfig

from sk_agents.extra_data_collector import ExtraDataCollector
from sk_agents.plugin_loader import get_plugin_loader
from sk_agents.ska_types import ModelType
from sk_agents.tealagents.chat_completion_builder import ChatCompletionBuilder
from sk_agents.tealagents.remote_plugin_loader import RemotePluginLoader


class ChainBuilder:
    def __init__(
        self,
        chat_completion_builder: ChatCompletionBuilder,
        remote_plugin_loader: RemotePluginLoader,
        app_config: AppConfig,
        authorization: str | None = None,
    ):
        self.chat_completion_builder: ChatCompletionBuilder = chat_completion_builder
        self.remote_plugin_loader = remote_plugin_loader
        self.app_config: AppConfig = app_config
        self.authorization = authorization
        self.logger = logging.getLogger(__name__)

    def build_chain(
        self,
        model_name: str,
        service_id: str,
        system_prompt: str,
        plugins: list[str],
        remote_plugins: list[str],
        authorization: str | None = None,
        extra_data_collector: ExtraDataCollector | None = None,
    ) -> Runnable:
        try:
            llm = self._create_base_llm(model_name, service_id)
            tools = []
            tools.extend(self._parse_plugins(plugins, authorization, extra_data_collector))
            tools.extend(self._load_remote_plugins(remote_plugins))

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])

            agent = create_agent(llm, tools, prompt)
            return agent
        except Exception as e:
            self.logger.exception(f"Could build chain with service ID {service_id}. - {e}")
            raise

    def get_model_type_for_name(self, model_name: str) -> ModelType:
        try:
            return self.chat_completion_builder.get_model_type_for_name(model_name)
        except Exception as e:
            self.logger.exception(f"Could not get model type for {model_name}. - {e}")
            raise

    def model_supports_structured_output(self, model_name: str) -> bool:
        return self.chat_completion_builder.model_supports_structured_output(model_name)

    def _create_base_llm(self, model_name: str, service_id: str) -> BaseChatModel:
        try:
            llm = self.chat_completion_builder.get_chat_completion_for_model(
                service_id=service_id,
                model_name=model_name,
            )
            return llm
        except Exception as e:
            self.logger.exception(f"Could not create base LLM with service id {service_id}.-{e}")
            raise

    def _load_remote_plugins(self, remote_plugins: list[str]) -> list[BaseTool]:
        if remote_plugins is None or len(remote_plugins) < 1:
            return []
        try:
            tools = []
            for plugin_name in remote_plugins:
                plugin = self.remote_plugin_loader.get_remote_plugin(plugin_name)
                for method_name in dir(plugin):
                    method = getattr(plugin, method_name)
                    if hasattr(method, '__langchain_tool__'):
                        tools.append(method)
            return tools
        except Exception as e:
            self.logger.exception(f"Could not load remote plugins. -{e}")
            raise

    @staticmethod
    def _parse_plugins(
        plugin_names: list[str],
        authorization: str | None = None,
        extra_data_collector: ExtraDataCollector | None = None,
    ) -> list[BaseTool]:
        if plugin_names is None or len(plugin_names) < 1:
            return []

        plugin_loader = get_plugin_loader()
        plugins = plugin_loader.get_plugins(plugin_names)
        tools = []
        for _k, v in plugins.items():
            plugin_instance = v(authorization, extra_data_collector)
            for method_name in dir(plugin_instance):
                method = getattr(plugin_instance, method_name)
                if hasattr(method, '__langchain_tool__'):
                    tools.append(method)
        return tools
