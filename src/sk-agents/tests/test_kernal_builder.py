from unittest.mock import ANY, MagicMock, patch

import pytest

# from semantic_kernel.kernel import Kernel  # Removed - migrated to LangChain
from ska_utils import AppConfig

from sk_agents.skagents.kernel_builder import ChainBuilder


@patch.object(ChainBuilder, "_create_base_llm")
@patch.object(ChainBuilder, "_parse_plugins")
@patch.object(ChainBuilder, "_load_remote_plugins")
def test_build_kernel_success(mock_load, mock_parse, mock_create):
    # Mock
    kernel = MagicMock()  # Mock kernel for LangChain migration
    mock_create.return_value = kernel
    mock_parse.return_value = kernel
    mock_load.return_value = kernel

    chat_completion_builder = MagicMock()
    remote_plugin_loader = MagicMock()
    app_config = MagicMock(spec=AppConfig)

    builder = ChainBuilder(chat_completion_builder, remote_plugin_loader, app_config)

    # Act
    result = builder.build_chain(
        model_name="gpt-4",
        service_id="openai",
        system_prompt="test prompt",
        plugins=["pluginA"],
        remote_plugins=["remotePluginA"],
        authorization="Bearer token",
        extra_data_collector=None,
    )

    assert result is not None
    mock_create.assert_called_once_with("gpt-4", "openai")
    mock_parse.assert_called_once()
    mock_load.assert_called_once()


@patch.object(ChainBuilder, "_create_base_llm", side_effect=Exception("base llm failed"))
def test_build_kernel_failure(mock_create_base_llm, caplog):
    # Arrange
    chat_completion_builder = MagicMock()
    remote_plugin_loader = MagicMock()
    app_config = MagicMock(spec=AppConfig)

    builder = ChainBuilder(chat_completion_builder, remote_plugin_loader, app_config)

    # Act
    with caplog.at_level("WARNING"):
        with pytest.raises(Exception, match="base llm failed"):
            builder.build_chain(
                model_name="test-model",
                service_id="test-service",
                system_prompt="test",
                plugins=[],
                remote_plugins=[]
            )
    # Assert
    assert "Could build chain with service ID test-service." in caplog.text


def test_get_model_type_for_name_success():
    # Arrange
    mock_builder = MagicMock()
    mock_builder.get_model_type_for_name.return_value = "mock-type"
    kernel_builder = ChainBuilder(mock_builder, MagicMock(), MagicMock())

    # Act
    result = kernel_builder.get_model_type_for_name("test-model")

    # Assert
    assert result == "mock-type"
    mock_builder.get_model_type_for_name.assert_called_once_with("test-model")


def test_get_model_type_for_name_failure(caplog):
    # Arrange
    mock_builder = MagicMock()
    mock_builder.get_model_type_for_name.side_effect = Exception("lookup error")
    kernel_builder = ChainBuilder(mock_builder, MagicMock(), MagicMock())

    # Act
    with caplog.at_level("WARNING"):
        with pytest.raises(Exception, match="lookup error"):
            kernel_builder.get_model_type_for_name("bad-model")

    # Assert
    assert "Could not get model type for bad-model." in caplog.text


def test_model_supports_structured_output_success():
    # Arrange
    mock_builder = MagicMock()
    mock_builder.model_supports_structured_output.return_value = True
    kernel_builder = ChainBuilder(mock_builder, MagicMock(), MagicMock())

    # Act
    result = kernel_builder.model_supports_structured_output("some-model")

    # Assert
    assert result is True
    mock_builder.model_supports_structured_output.assert_called_once_with("some-model")


def test_model_supports_structured_output_failure():
    # Arrange
    mock_builder = MagicMock()
    mock_builder.model_supports_structured_output.side_effect = Exception("Failure")
    kernel_builder = ChainBuilder(mock_builder, MagicMock(), MagicMock())

    # Act & Assert
    with pytest.raises(Exception, match="Failure"):
        kernel_builder.model_supports_structured_output("bad-model")


def test_create_base_llm_success():
    # Arrange
    mock_chat_completion = MagicMock()
    mock_builder = MagicMock()
    mock_builder.get_chat_completion_for_model.return_value = mock_chat_completion

    builder = ChainBuilder(
        chat_completion_builder=mock_builder,
        remote_plugin_loader=MagicMock(),
        app_config=MagicMock(),
    )

    # Act
    llm = builder._create_base_llm("test-model", "test-service")

    # Assert
    assert llm is not None  # Updated for LangChain migration
    mock_builder.get_chat_completion_for_model.assert_called_once_with(
        service_id="test-service", model_name="test-model"
    )
    assert llm is not None


def test_create_base_kernel_failure(caplog):
    # Arrange
    mock_builder = MagicMock()
    mock_builder.get_chat_completion_for_model.side_effect = Exception(
        "fail to get chat completion"
    )
    builder = ChainBuilder(
        chat_completion_builder=mock_builder,
        remote_plugin_loader=MagicMock(),
        app_config=MagicMock(),
    )

    # Act
    with pytest.raises(Exception, match="fail to get chat completion"):
        with caplog.at_level("WARNING"):
            llm = builder._create_base_llm("bad-model", "bad-service")

        # Assert
        assert llm is None
    assert "Could not create base LLM with service id bad-service." in caplog.text


def test_parse_plugins_empty_list():
    result = ChainBuilder._parse_plugins([])
    assert result == []


def test_parse_plugins_none():
    result = ChainBuilder._parse_plugins(None)
    assert result == []


def test_parse_plugins_with_valid_plugin():

    # Create a mock plugin instance with real-looking attributes
    mock_plugin_instance = MagicMock()
    mock_plugin_instance.name = "mock_plugin"
    mock_plugin_instance.description = "A mock plugin for testing"
    mock_plugin_instance.get_functions.return_value = {}

    mock_plugin_class = MagicMock(return_value=mock_plugin_instance)

    plugin_dict = {"mock_plugin": mock_plugin_class}

    with patch("sk_agents.skagents.kernel_builder.get_plugin_loader") as mock_loader:
        mock_loader.return_value.get_plugins.return_value = plugin_dict

        result = ChainBuilder._parse_plugins(
            plugin_names=["mock_plugin"],
            authorization="token",
            extra_data_collector=MagicMock(),
        )

        assert isinstance(result, list)
        mock_plugin_class.assert_called_once_with("token", ANY)


def test_parse_plugins_with_multiple_plugins():

    # Create realistic plugin instances
    plugin_instance_1 = MagicMock()
    plugin_instance_1.name = "plugin1"
    plugin_instance_1.description = "First plugin"
    plugin_instance_1.get_functions.return_value = {}

    plugin_instance_2 = MagicMock()
    plugin_instance_2.name = "plugin2"
    plugin_instance_2.description = "Second plugin"
    plugin_instance_2.get_functions.return_value = {}

    # Create mock constructors
    plugin_class_1 = MagicMock(return_value=plugin_instance_1)
    plugin_class_2 = MagicMock(return_value=plugin_instance_2)

    plugin_dict = {
        "plugin1": plugin_class_1,
        "plugin2": plugin_class_2,
    }

    with patch("sk_agents.skagents.kernel_builder.get_plugin_loader") as mock_loader:
        mock_loader.return_value.get_plugins.return_value = plugin_dict

        result = ChainBuilder._parse_plugins(plugin_names=["plugin1", "plugin2"])

        assert isinstance(result, list)
        plugin_class_1.assert_called_once()
        plugin_class_2.assert_called_once()


def test_parse_plugins_plugin_loader_failure():

    with patch("sk_agents.skagents.kernel_builder.get_plugin_loader") as mock_loader:
        # Simulate get_plugins raising an exception
        mock_loader.return_value.get_plugins.side_effect = RuntimeError("Failed to load plugins")

        with pytest.raises(RuntimeError, match="Failed to load plugins"):
            ChainBuilder._parse_plugins(
                plugin_names=["some_plugin"],
                authorization="token",
                extra_data_collector=MagicMock(),
            )


def test_load_remote_plugins_with_none_or_empty():
    kb = ChainBuilder(
        chat_completion_builder=MagicMock(),
        remote_plugin_loader=MagicMock(),
        app_config=MagicMock(),
    )

    # None input returns empty list
    result = kb._load_remote_plugins(None)
    assert result == []

    # Empty list input returns empty list
    result = kb._load_remote_plugins([])
    assert result == []


def test_load_remote_plugins_success():
    remote_loader = MagicMock()
    kb = ChainBuilder(
        chat_completion_builder=MagicMock(),
        remote_plugin_loader=remote_loader,
        app_config=MagicMock(),
    )
    remote_plugins = ["plugin1", "plugin2"]

    result = kb._load_remote_plugins(remote_plugins)

    assert isinstance(result, list)


def test_load_remote_plugins_failure():
    remote_loader = MagicMock()
    remote_loader.load_remote_plugins.side_effect = RuntimeError("Loading failed")

    kb = ChainBuilder(
        chat_completion_builder=MagicMock(),
        remote_plugin_loader=remote_loader,
        app_config=MagicMock(),
    )
    remote_plugins = ["plugin1"]

    result = kb._load_remote_plugins(remote_plugins)
    assert result == []
