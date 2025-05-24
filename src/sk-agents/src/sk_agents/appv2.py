import os
from types import NoneType

from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill, AgentProvider
from fastapi import FastAPI
from ska_utils import AppConfig, strtobool

from sk_agents.a2a_agent_executor import A2AAgentExecutor
from sk_agents.configs import (
    TA_A2A_ENABLED,
    TA_SERVICE_CONFIG,
    TA_PROVIDER_ORG,
    TA_PROVIDER_URL,
    TA_AGENT_BASE_URL,
)
from sk_agents.routes import Routes
from sk_agents.ska_types import (
    BaseConfig,
    BaseMultiModalInput,
)
from sk_agents.utils import initialize_plugin_loader


class AppV2:
    @staticmethod
    def get_url(name: str, version: str, app_config: AppConfig) -> str:
        base_url = app_config.get(TA_AGENT_BASE_URL.env_name)
        if not base_url:
            raise ValueError("Base URL is not provided in the app config.")
        return f"{base_url}/{name}/{version}/a2a"

    @staticmethod
    def get_provider(app_config: AppConfig) -> AgentProvider:
        return AgentProvider(
            organization=app_config.get(TA_PROVIDER_ORG.env_name),
            url=app_config.get(TA_PROVIDER_URL.env_name),
        )

    @staticmethod
    def get_agent_card(config: BaseConfig, app_config: AppConfig) -> AgentCard:
        if config.metadata is None:
            raise ValueError("Agent card metadata is not provided in the config.")

        metadata = config.metadata
        skills = [
            AgentSkill(
                id=skill.id,
                name=skill.name,
                description=skill.description,
                tags=skill.tags,
                examples=skill.examples,
                inputModes=skill.input_modes,
                outputModes=skill.output_modes,
            )
            for skill in metadata.skills
        ]
        return AgentCard(
            name=config.name,
            version=str(config.version),
            description=metadata.description,
            url=AppV2.get_url(config.name, config.version, app_config),
            provider=AppV2.get_provider(app_config),
            documentationUrl=config.metadata.documentation_url,
            capabilities=AgentCapabilities(
                streaming=True, pushNotifications=False, stateTransitionHistory=True
            ),
            defaultInputModes=["text"],
            defaultOutputModes=["text"],
            skills=skills,
        )

    @staticmethod
    def get_request_handler() -> DefaultRequestHandler:
        return DefaultRequestHandler(
            agent_executor=A2AAgentExecutor(), task_store=InMemoryTaskStore()
        )

    @staticmethod
    def run(
        name: str, version: str, app_config: AppConfig, config: BaseConfig, app: FastAPI
    ):
        a2a_enabled = strtobool(app_config.get(TA_A2A_ENABLED.env_name))
        config_file = app_config.get(TA_SERVICE_CONFIG.env_name)
        agents_path = str(os.path.dirname(config_file))

        initialize_plugin_loader(agents_path=agents_path, app_config=app_config)

        root_handler = config.apiVersion.split("/")[0]

        if config.metadata is not None and config.metadata.description is not None:
            description = config.metadata.description
        else:
            description = f"{config.name} API"

        app.include_router(
            Routes.get_rest_routes(
                name=name,
                version=version,
                description=description,
                root_handler_name=root_handler,
                config=config,
                app_config=app_config,
                input_class=BaseMultiModalInput,
                output_class=NoneType,
            ),
            prefix=f"/{name}/{version}",
        )
        app.include_router(
            Routes.get_websocket_routes(
                name=name,
                version=version,
                root_handler_name=root_handler,
                config=config,
                app_config=app_config,
                input_class=BaseMultiModalInput,
            ),
            prefix=f"/{name}/{version}",
        )
        if a2a_enabled:
            app.include_router(
                Routes.get_a2a_routes(
                    name=name,
                    version=version,
                    description=description,
                    config=config,
                    app_config=app_config,
                ),
                prefix=f"/{name}/{version}/a2a",
            )
