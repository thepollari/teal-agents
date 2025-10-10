"""
Remote Tool Loader for OpenAPI-based tools.

Converts OpenAPI specifications to LangChain tools, replacing
Semantic Kernel's built-in OpenAPI plugin support.
"""

import logging
from typing import Any

import httpx
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, create_model, Field
from pydantic_yaml import parse_yaml_file_as
from ska_utils import AppConfig

from sk_agents.configs import TA_REMOTE_PLUGIN_PATH

logger = logging.getLogger(__name__)


class RemotePlugin(BaseModel):
    """Configuration for a remote OpenAPI plugin."""
    plugin_name: str
    openapi_json_path: str
    server_url: str | None = None


class RemotePlugins(BaseModel):
    """Collection of remote plugins."""
    remote_plugins: list[RemotePlugin]

    def get(self, plugin_name: str) -> RemotePlugin | None:
        """Get a remote plugin by name."""
        for remote_plugin in self.remote_plugins:
            if remote_plugin.plugin_name == plugin_name:
                return remote_plugin
        return None


class RemotePluginCatalog:
    """Catalog of available remote plugins."""
    
    def __init__(self, app_config: AppConfig) -> None:
        plugin_path = app_config.get(TA_REMOTE_PLUGIN_PATH.env_name)
        self.logger = logging.getLogger(__name__)
        if plugin_path is None:
            self.catalog = None
        else:
            self.catalog: RemotePlugins = parse_yaml_file_as(RemotePlugins, plugin_path)

    def get_remote_plugin(self, plugin_name: str) -> RemotePlugin | None:
        """Get a remote plugin configuration by name."""
        try:
            return self.catalog.get(plugin_name) if self.catalog else None
        except Exception as e:
            self.logger.exception(f"Could not get remote plugin {plugin_name}: {e}")
            raise


class RemoteToolLoader:
    """
    Loads OpenAPI specifications and converts them to LangChain tools.
    
    Replaces Semantic Kernel's kernel.add_plugin_from_openapi() with
    a custom implementation that creates LangChain StructuredTools.
    """

    def __init__(self, catalog: RemotePluginCatalog) -> None:
        self.catalog = catalog
        self.http_client = httpx.AsyncClient(timeout=httpx.Timeout(60.0))
        self.logger = logging.getLogger(__name__)

    def load_remote_tools(self, remote_plugin_names: list[str]) -> list[StructuredTool]:
        """
        Load remote plugins and convert to LangChain tools.
        
        Args:
            remote_plugin_names: List of remote plugin names to load
            
        Returns:
            List of LangChain StructuredTool instances
        """
        tools = []
        
        for plugin_name in remote_plugin_names:
            remote_plugin = self.catalog.get_remote_plugin(plugin_name)
            if not remote_plugin:
                raise ValueError(f"Remote plugin {plugin_name} not found in catalog")
            
            try:
                plugin_tools = self._create_tools_from_openapi(remote_plugin)
                tools.extend(plugin_tools)
            except Exception as e:
                self.logger.exception(
                    f"Error loading remote plugin {plugin_name}: {e}"
                )
                raise
        
        return tools

    def _create_tools_from_openapi(
        self,
        remote_plugin: RemotePlugin
    ) -> list[StructuredTool]:
        """
        Create LangChain tools from an OpenAPI specification.
        
        Args:
            remote_plugin: Remote plugin configuration
            
        Returns:
            List of StructuredTool instances, one per API operation
        """
        import json
        
        with open(remote_plugin.openapi_json_path, 'r') as f:
            spec = json.load(f)
        
        tools = []
        server_url = remote_plugin.server_url or spec.get("servers", [{}])[0].get("url", "")
        
        for path, path_item in spec.get("paths", {}).items():
            for method in ["get", "post", "put", "delete", "patch"]:
                if method not in path_item:
                    continue
                
                operation = path_item[method]
                tool = self._create_tool_for_operation(
                    path=path,
                    method=method,
                    operation=operation,
                    server_url=server_url,
                    plugin_name=remote_plugin.plugin_name
                )
                
                if tool:
                    tools.append(tool)
        
        return tools

    def _create_tool_for_operation(
        self,
        path: str,
        method: str,
        operation: dict,
        server_url: str,
        plugin_name: str
    ) -> StructuredTool | None:
        """
        Create a single LangChain tool from an OpenAPI operation.
        
        Args:
            path: API path (e.g., "/users/{id}")
            method: HTTP method (get, post, etc.)
            operation: OpenAPI operation object
            server_url: Base server URL
            plugin_name: Name of the plugin
            
        Returns:
            StructuredTool instance or None
        """
        operation_id = operation.get("operationId", f"{method}_{path.replace('/', '_')}")
        description = operation.get("summary") or operation.get("description", "")
        
        if not description:
            description = f"{method.upper()} {path}"
        
        parameters = operation.get("parameters", [])
        request_body = operation.get("requestBody", {})
        
        input_schema = self._build_input_schema(parameters, request_body, operation_id)
        
        async def execute_operation(**kwargs):
            """Execute the API operation."""
            url = server_url + path
            
            for key, value in kwargs.items():
                url = url.replace(f"{{{key}}}", str(value))
            
            query_params = {}
            body_params = {}
            
            for param in parameters:
                param_name = param.get("name")
                if param_name in kwargs:
                    if param.get("in") == "query":
                        query_params[param_name] = kwargs[param_name]
                    elif param.get("in") == "path":
                        pass
            
            if request_body and method in ["post", "put", "patch"]:
                body_params = {
                    k: v for k, v in kwargs.items()
                    if k not in query_params
                }
            
            try:
                response = await self.http_client.request(
                    method=method.upper(),
                    url=url,
                    params=query_params if query_params else None,
                    json=body_params if body_params else None,
                )
                response.raise_for_status()
                
                try:
                    return response.json()
                except Exception:
                    return response.text
                    
            except httpx.HTTPError as e:
                logger.error(f"HTTP error calling {operation_id}: {e}")
                return {"error": str(e)}
        
        tool_name = f"{plugin_name}_{operation_id}"
        
        return StructuredTool(
            name=tool_name,
            description=description,
            coroutine=execute_operation,
            args_schema=input_schema if input_schema else None,
        )

    def _build_input_schema(
        self,
        parameters: list[dict],
        request_body: dict,
        operation_id: str
    ) -> type[BaseModel] | None:
        """
        Build a Pydantic model for the operation's input parameters.
        
        Args:
            parameters: List of OpenAPI parameter objects
            request_body: OpenAPI requestBody object
            operation_id: Operation identifier
            
        Returns:
            Pydantic model class or None
        """
        fields = {}
        
        for param in parameters:
            param_name = param.get("name")
            param_description = param.get("description", "")
            required = param.get("required", False)
            
            schema = param.get("schema", {})
            param_type = self._get_python_type(schema)
            
            default = ... if required else None
            
            fields[param_name] = (
                param_type,
                Field(default=default, description=param_description)
            )
        
        if request_body:
            content = request_body.get("content", {})
            json_content = content.get("application/json", {})
            schema = json_content.get("schema", {})
            properties = schema.get("properties", {})
            
            for prop_name, prop_schema in properties.items():
                if prop_name not in fields:  # Don't override parameters
                    prop_type = self._get_python_type(prop_schema)
                    prop_description = prop_schema.get("description", "")
                    required = prop_name in schema.get("required", [])
                    
                    default = ... if required else None
                    fields[prop_name] = (
                        prop_type,
                        Field(default=default, description=prop_description)
                    )
        
        if not fields:
            return None
        
        model_name = f"{operation_id}_Input"
        return create_model(model_name, **fields)

    @staticmethod
    def _get_python_type(schema: dict) -> type:
        """
        Convert OpenAPI schema type to Python type.
        
        Args:
            schema: OpenAPI schema object
            
        Returns:
            Python type
        """
        type_mapping = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        
        schema_type = schema.get("type", "string")
        return type_mapping.get(schema_type, str)
