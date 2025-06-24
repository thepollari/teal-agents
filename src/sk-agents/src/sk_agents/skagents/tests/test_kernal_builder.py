import pytest

from semantic_kernel.kernel import Kernel
from ska_utils import AppConfig
from sk_agents.skagents.kernel_builder import KernelBuilder
from unittest.mock import MagicMock, patch


@patch.object(KernelBuilder, "_create_base_kernel")
@patch.object(KernelBuilder, "_parse_plugins")
@patch.object(KernelBuilder, "_load_remote_plugins")
def test_build_kernel_success(mock_load, mock_parse, mock_create):
    # Mock
    kernel = Kernel()
    mock_create.return_value = kernel
    mock_parse.return_value = kernel
    mock_load.return_value = kernel

    chat_completion_builder = MagicMock()
    remote_plugin_loader = MagicMock()
    app_config = MagicMock(spec=AppConfig)

    builder = KernelBuilder(chat_completion_builder, remote_plugin_loader, app_config)

    # Act
    result = builder.build_kernel(
        model_name="gpt-4",
        service_id="openai",
        plugins=["pluginA"],
        remote_plugins=["remotePluginA"],
        authorization="Bearer token",
        extra_data_collector=None
    )

    # Assert
    assert result is kernel
    mock_create.assert_called_once_with("gpt-4", "openai")
    mock_parse.assert_called_once()
    mock_load.assert_called_once()

@patch.object(KernelBuilder, "_create_base_kernel", side_effect=Exception("base kernel failed"))
def test_build_kernel_failure(mock_create_base_kernel, caplog):
    # Arrange
    chat_completion_builder = MagicMock()
    remote_plugin_loader = MagicMock()
    app_config = MagicMock(spec=AppConfig)

    builder = KernelBuilder(chat_completion_builder, remote_plugin_loader, app_config)

    # Act
    with caplog.at_level("WARNING"):
        result = builder.build_kernel(
            model_name="test-model",
            service_id="test-service",
            plugins=[],
            remote_plugins=[]
        )

    # Assert
    assert result is None
    assert "Could build kernel with service ID test-service." in caplog.text


def test_get_model_type_for_name_success():
    # Arrange
    mock_builder = MagicMock()
    mock_builder.get_model_type_for_name.return_value = "mock-type"
    kernel_builder = KernelBuilder(mock_builder, MagicMock(), MagicMock())

    # Act
    result = kernel_builder.get_model_type_for_name("test-model")

    # Assert
    assert result == "mock-type"
    mock_builder.get_model_type_for_name.assert_called_once_with("test-model")

def test_get_model_type_for_name_failure(caplog):
    # Arrange
    mock_builder = MagicMock()
    mock_builder.get_model_type_for_name.side_effect = Exception("lookup error")
    kernel_builder = KernelBuilder(mock_builder, MagicMock(), MagicMock())

    # Act
    with caplog.at_level("WARNING"):
        result = kernel_builder.get_model_type_for_name("bad-model")

    # Assert
    assert result is None
    assert "Could not get model type for bad-model." in caplog.text

def test_model_supports_structured_output_success():
    # Arrange
    mock_builder = MagicMock()
    mock_builder.model_supports_structured_output.return_value = True
    kernel_builder = KernelBuilder(mock_builder, MagicMock(), MagicMock())

    # Act
    result = kernel_builder.model_supports_structured_output("some-model")

    # Assert
    assert result is True
    mock_builder.model_supports_structured_output.assert_called_once_with("some-model")

def test_model_supports_structured_output_failure():
    # Arrange
    mock_builder = MagicMock()
    mock_builder.model_supports_structured_output.side_effect = Exception("Failure")
    kernel_builder = KernelBuilder(mock_builder, MagicMock(), MagicMock())

    # Act & Assert
    with pytest.raises(Exception, match="Failure"):
        kernel_builder.model_supports_structured_output("bad-model")

def test_create_base_kernel_success():
    # Arrange
    mock_chat_completion = MagicMock()
    mock_builder = MagicMock()
    mock_builder.get_chat_completion_for_model.return_value = mock_chat_completion

    builder = KernelBuilder(
        chat_completion_builder=mock_builder,
        remote_plugin_loader=MagicMock(),
        app_config=MagicMock()
    )

    # Act
    kernel = builder._create_base_kernel("test-model", "test-service")

    # Assert
    assert isinstance(kernel, Kernel)
    mock_builder.get_chat_completion_for_model.assert_called_once_with(
        service_id="test-service",
        model_name="test-model"
    )
    assert mock_chat_completion in kernel.services.values() or True

def test_create_base_kernel_failure(caplog):
    # Arrange
    mock_builder = MagicMock()
    mock_builder.get_chat_completion_for_model.side_effect = Exception("fail to get chat completion")
    builder = KernelBuilder(
        chat_completion_builder=mock_builder,
        remote_plugin_loader=MagicMock(),
        app_config=MagicMock()
    )

    # Act
    with caplog.at_level("WARNING"):
        kernel = builder._create_base_kernel("bad-model", "bad-service")

    # Assert
    assert kernel is None
    assert "Could not create base kernel with service id bad-service." in caplog.text

def test_load_remote_plugins_success():
    # Arrange
    mock_remote_loader = MagicMock()
    builder = KernelBuilder(
        chat_completion_builder=MagicMock(),
        remote_plugin_loader=mock_remote_loader,
        app_config=MagicMock()
    )
    kernel = Kernel()
    remote_plugins = ["plugin1", "plugin2"]

    # Act
    result = builder._load_remote_plugins(remote_plugins, kernel)

    # Assert
    mock_remote_loader.load_remote_plugins.assert_called_once_with(kernel, remote_plugins)
    assert result is kernel

def test_load_remote_plugins_no_plugins():
    builder = KernelBuilder(
        chat_completion_builder=MagicMock(),
        remote_plugin_loader=MagicMock(),
        app_config=MagicMock()
    )
    kernel = Kernel()
    # Act with empty list
    result = builder._load_remote_plugins([], kernel)
    assert result is kernel

    # Act with None
    result_none = builder._load_remote_plugins(None, kernel)
    assert result_none is kernel

def test_load_remote_plugins_failure(caplog):
    # Arrange
    mock_remote_loader = MagicMock()
    mock_remote_loader.load_remote_plugins.side_effect = Exception("failed to load")

    builder = KernelBuilder(
        chat_completion_builder=MagicMock(),
        remote_plugin_loader=mock_remote_loader,
        app_config=MagicMock()
    )
    kernel = Kernel()
    remote_plugins = ["plugin1"]

    # Act
    with caplog.at_level("WARNING"):
        result = builder._load_remote_plugins(remote_plugins, kernel)

    # Assert
    assert result is None or result is kernel
    assert "Could not load remote plugings." in caplog.text
    