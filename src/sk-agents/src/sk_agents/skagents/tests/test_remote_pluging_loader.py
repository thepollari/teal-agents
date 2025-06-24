
import pytest

from sk_agents.skagents.remote_plugin_loader import RemotePluginCatalog, RemotePlugins, RemotePlugin
from ska_utils import AppConfig
from unittest.mock import MagicMock, patch

def test_remote_plugin_catalog_init_success():
    # Mock the plugin path returned by AppConfig.get
    mock_app_config = MagicMock(spec=AppConfig)
    mock_plugin_path = "/fake/path/plugins.yaml"
    mock_app_config.get.return_value = mock_plugin_path

    # Mock the parsed YAML result
    mock_remote_plugins = RemotePlugins(remote_plugins=[
        RemotePlugin(
            plugin_name="pluginA",
            openapi_json_path="/fake/path/pluginA/openapi.json",
            server_url="http://localhost"
        )
    ])

    with patch("sk_agents.skagents.remote_plugin_loader.parse_yaml_file_as", return_value=mock_remote_plugins) as mock_parser:
        catalog = RemotePluginCatalog(mock_app_config)

        # Verify catalog is set correctly
        assert catalog.catalog is mock_remote_plugins
        mock_app_config.get.assert_called_once()
        mock_parser.assert_called_once_with(RemotePlugins, mock_plugin_path)

def test_remote_plugin_catalog_init_no_plugin_path():
    # Mock AppConfig to return None for the plugin path
    mock_app_config = MagicMock(spec=AppConfig)
    mock_app_config.get.return_value = None

    catalog = RemotePluginCatalog(mock_app_config)

    # Since plugin path is None, catalog should be None
    assert catalog.catalog is None
    mock_app_config.get.assert_called_once()