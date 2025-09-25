from unittest.mock import Mock, patch

import pytest
from ska_utils import AppConfig

from sk_agents.skagents.remote_plugin_loader import (
    RemotePlugin,
    RemotePluginCatalog,
    RemotePluginLoader,
    RemotePlugins,
)


@pytest.fixture
def remote_plugin():
    return RemotePlugin(
        plugin_name="test_plugin",
        openapi_json_path="path/to/openapi.json",
        server_url="http://localhost",
    )


@pytest.fixture
def app_config():
    mock_config = Mock(spec=AppConfig)
    mock_config.get.return_value = "dummy_plugin_path.yaml"
    return mock_config


def test_get_plugin_found(remote_plugin):
    catalog = RemotePlugins(remote_plugins=[remote_plugin])
    result = catalog.get("test_plugin")
    assert result == remote_plugin


def test_get_plugin_not_found(remote_plugin):
    catalog = RemotePlugins(remote_plugins=[remote_plugin])
    result = catalog.get("unknown_plugin")
    assert result is None


@patch("sk_agents.skagents.remote_plugin_loader.parse_yaml_file_as")
def test_catalog_initialization_with_path(mock_parse_yaml, app_config):
    mock_catalog = Mock(spec=RemotePlugins)
    mock_parse_yaml.return_value = mock_catalog
    catalog = RemotePluginCatalog(app_config)
    assert catalog.catalog == mock_catalog


def test_catalog_initialization_without_path():
    mock_config = Mock(spec=AppConfig)
    mock_config.get.return_value = None
    catalog = RemotePluginCatalog(mock_config)
    assert catalog.catalog is None


@patch("sk_agents.skagents.remote_plugin_loader.parse_yaml_file_as")
def test_get_remote_plugin_success(mock_parse_yaml, remote_plugin):
    # Provide a realistic RemotePlugins instance to the catalog
    mock_parse_yaml.return_value = RemotePlugins(remote_plugins=[remote_plugin])

    mock_app_config = Mock()
    mock_app_config.get.return_value = "dummy_plugin_path.yaml"
    catalog_wrapper = RemotePluginCatalog(mock_app_config)

    result = catalog_wrapper.get_remote_plugin("test_plugin")
    assert result == remote_plugin


@patch("sk_agents.skagents.remote_plugin_loader.parse_yaml_file_as")
def test_get_remote_plugin_exception(mock_parse_yaml):
    # Mock the catalog with a broken `.get` to simulate exception
    broken_catalog = Mock(spec=RemotePlugins)
    broken_catalog.get.side_effect = Exception("simulated failure")

    # Mock parse_yaml_file_as to return the broken catalog
    mock_parse_yaml.return_value = broken_catalog

    mock_app_config = Mock()
    mock_app_config.get.return_value = "dummy_plugin_path.yaml"
    catalog_wrapper = RemotePluginCatalog(mock_app_config)

    with patch.object(catalog_wrapper.logger, "exception") as mock_warn:
        with pytest.raises(Exception, match="simulated failure"):
            result = catalog_wrapper.get_remote_plugin("test_plugin")
            assert result is None
        mock_warn.assert_called_once_with(
            "could not get remote pluging test_plugin. - simulated failure"
        )


@patch("sk_agents.skagents.remote_plugin_loader.OpenAPISpec.from_file")
def test_load_remote_plugin_success(mock_openapi_spec, remote_plugin):
    mock_spec = Mock()
    mock_spec.operations = []
    mock_openapi_spec.return_value = mock_spec

    catalog = Mock()
    catalog.get_remote_plugin.return_value = remote_plugin

    loader = RemotePluginLoader(catalog)
    result = loader.load_remote_plugins(["test_plugin"])

    mock_openapi_spec.assert_called_once_with(remote_plugin.openapi_json_path)
    assert result == []


def test_load_remote_plugin_not_found():
    catalog = Mock()
    catalog.get_remote_plugin.return_value = None
    loader = RemotePluginLoader(catalog)

    with pytest.raises(ValueError, match="Remote plugin test_plugin not found in catalog"):
        loader.load_remote_plugins(["test_plugin"])
