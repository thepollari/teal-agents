import logging

from langchain_community.tools.openapi.utils.openapi_utils import OpenAPISpec
from pydantic import BaseModel
from pydantic_yaml import parse_yaml_file_as
from ska_utils import AppConfig

from sk_agents.configs import TA_REMOTE_PLUGIN_PATH


class RemotePlugin(BaseModel):
    plugin_name: str
    openapi_json_path: str
    server_url: str | None = None


class RemotePlugins(BaseModel):
    remote_plugins: list[RemotePlugin]

    def get(self, plugin_name: str) -> RemotePlugin | None:
        for remote_plugin in self.remote_plugins:
            if remote_plugin.plugin_name == plugin_name:
                return remote_plugin
        return None


class RemotePluginCatalog:
    def __init__(self, app_config: AppConfig) -> None:
        plugin_path = app_config.get(TA_REMOTE_PLUGIN_PATH.env_name)
        self.logger = logging.getLogger(__name__)
        if plugin_path is None:
            self.catalog = None
        else:
            self.catalog: RemotePlugins = parse_yaml_file_as(RemotePlugins, plugin_path)

    def get_remote_plugin(self, plugin_name: str) -> RemotePlugin | None:
        try:
            return self.catalog.get(plugin_name)
        except Exception as e:
            self.logger.exception(f"could not get remote pluging {plugin_name}. - {e}")
            raise


class RemotePluginLoader:
    def __init__(self, catalog: RemotePluginCatalog) -> None:
        self.catalog = catalog

    def load_remote_plugins(self, remote_plugins: list[str]) -> list:
        tools = []
        for remote_plugin_name in remote_plugins:
            remote_plugin = self.catalog.get_remote_plugin(remote_plugin_name)
            if remote_plugin:
                spec = OpenAPISpec.from_file(remote_plugin.openapi_json_path)
                for _operation in spec.operations:
                    pass
            else:
                raise ValueError(f"Remote plugin {remote_plugin_name} not found in catalog")
        return tools
