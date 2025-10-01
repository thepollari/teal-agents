from unittest.mock import MagicMock, patch

import pytest

from sk_agents.chat_completion.custom.gemini_chat_completion_factory import (
    GeminiChatCompletionFactory,
)
from sk_agents.ska_types import ModelType


class TestGeminiChatCompletionFactory:

    def test_init_with_valid_api_key(self, app_config_fixture):
        factory = GeminiChatCompletionFactory(app_config_fixture)

        assert factory.api_key == "test-api-key-123"
        assert factory.app_config is app_config_fixture

    def test_get_configs_returns_empty_list(self):
        configs_list = GeminiChatCompletionFactory.get_configs()

        assert isinstance(configs_list, list)
        assert len(configs_list) == 0

    @patch("sk_agents.chat_completion.custom.gemini_chat_completion_factory.GoogleAIChatCompletion")
    def test_get_chat_completion_for_supported_model(
        self, mock_google_completion, app_config_fixture
    ):
        mock_completion_instance = MagicMock()
        mock_google_completion.return_value = mock_completion_instance

        factory = GeminiChatCompletionFactory(app_config_fixture)
        result = factory.get_chat_completion_for_model_name("gemini-1.5-flash", "test-service")

        mock_google_completion.assert_called_once_with(
            service_id="test-service",
            gemini_model_id="gemini-1.5-flash",
            api_key="test-api-key-123"
        )
        assert result == mock_completion_instance

    @patch("sk_agents.chat_completion.custom.gemini_chat_completion_factory.GoogleAIChatCompletion")
    def test_get_chat_completion_for_all_supported_models(
        self, mock_google_completion, app_config_fixture
    ):
        factory = GeminiChatCompletionFactory(app_config_fixture)
        supported_models = [
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-1.0-pro",
            "gemini-2.0-flash-lite"
        ]

        for model_name in supported_models:
            result = factory.get_chat_completion_for_model_name(model_name, "test-service")
            assert result is not None

    def test_get_chat_completion_for_unsupported_model(self, app_config_fixture):
        factory = GeminiChatCompletionFactory(app_config_fixture)

        with pytest.raises(ValueError) as exc_info:
            factory.get_chat_completion_for_model_name("gpt-4", "test-service")

        assert "not supported by GeminiChatCompletionFactory" in str(exc_info.value)

    def test_get_chat_completion_for_empty_model_name(self, app_config_fixture):
        factory = GeminiChatCompletionFactory(app_config_fixture)

        with pytest.raises(ValueError):
            factory.get_chat_completion_for_model_name("", "test-service")

    def test_get_model_type_for_supported_model(self, app_config_fixture):
        factory = GeminiChatCompletionFactory(app_config_fixture)

        model_type = factory.get_model_type_for_name("gemini-1.5-flash")

        assert model_type == ModelType.GOOGLE

    def test_get_model_type_for_all_supported_models(self, app_config_fixture):
        factory = GeminiChatCompletionFactory(app_config_fixture)
        supported_models = [
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-1.0-pro",
            "gemini-2.0-flash-lite"
        ]

        for model_name in supported_models:
            model_type = factory.get_model_type_for_name(model_name)
            assert model_type == ModelType.GOOGLE

    def test_get_model_type_for_unsupported_model(self, app_config_fixture):
        factory = GeminiChatCompletionFactory(app_config_fixture)

        with pytest.raises(ValueError) as exc_info:
            factory.get_model_type_for_name("claude-3")

        assert "Unknown model name" in str(exc_info.value)

    def test_model_supports_structured_output_for_supported_model(self, app_config_fixture):
        factory = GeminiChatCompletionFactory(app_config_fixture)

        supports = factory.model_supports_structured_output("gemini-1.5-flash")

        assert supports is True

    def test_model_supports_structured_output_for_all_models(self, app_config_fixture):
        factory = GeminiChatCompletionFactory(app_config_fixture)
        supported_models = [
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-1.0-pro",
            "gemini-2.0-flash-lite"
        ]

        for model_name in supported_models:
            supports = factory.model_supports_structured_output(model_name)
            assert supports is True

    def test_model_supports_structured_output_for_unsupported_model(self, app_config_fixture):
        factory = GeminiChatCompletionFactory(app_config_fixture)

        with pytest.raises(ValueError) as exc_info:
            factory.model_supports_structured_output("gpt-4")

        assert "Unknown model name" in str(exc_info.value)

    @patch("sk_agents.chat_completion.custom.gemini_chat_completion_factory.GoogleAIChatCompletion")
    def test_create_chat_completion_with_defaults(self, mock_google_completion, app_config_fixture):
        mock_completion_instance = MagicMock()
        mock_google_completion.return_value = mock_completion_instance

        factory = GeminiChatCompletionFactory(app_config_fixture)
        result = factory.create_chat_completion()

        mock_google_completion.assert_called_once_with(
            service_id="gemini_service",
            gemini_model_id="gemini-2.0-flash-lite",
            api_key="test-api-key-123"
        )
        assert result == mock_completion_instance

    @patch("sk_agents.chat_completion.custom.gemini_chat_completion_factory.GoogleAIChatCompletion")
    def test_create_chat_completion_with_custom_params(
        self, mock_google_completion, app_config_fixture
    ):
        mock_completion_instance = MagicMock()
        mock_google_completion.return_value = mock_completion_instance

        factory = GeminiChatCompletionFactory(app_config_fixture)
        result = factory.create_chat_completion(
            model_name="gemini-1.5-pro",
            service_id="custom-service"
        )

        mock_google_completion.assert_called_once_with(
            service_id="custom-service",
            gemini_model_id="gemini-1.5-pro",
            api_key="test-api-key-123"
        )
        assert result == mock_completion_instance

    @patch("sk_agents.chat_completion.custom.gemini_chat_completion_factory.GoogleAIChatCompletion")
    def test_get_chat_completion_called_with_correct_api_key(
        self, mock_google_completion, app_config_fixture
    ):
        factory = GeminiChatCompletionFactory(app_config_fixture)
        factory.get_chat_completion_for_model_name("gemini-1.5-flash", "test-service")

        call_kwargs = mock_google_completion.call_args[1]
        assert call_kwargs["api_key"] == "test-api-key-123"

    def test_factory_inherits_from_chat_completion_factory(self, app_config_fixture):
        factory = GeminiChatCompletionFactory(app_config_fixture)

        assert hasattr(factory, "app_config")
        assert hasattr(factory, "get_chat_completion_for_model_name")
        assert hasattr(factory, "get_model_type_for_name")
        assert hasattr(factory, "model_supports_structured_output")

    @patch("sk_agents.chat_completion.custom.gemini_chat_completion_factory.GoogleAIChatCompletion")
    def test_get_chat_completion_with_none_service_id(
        self, mock_google_completion, app_config_fixture
    ):
        mock_completion_instance = MagicMock()
        mock_google_completion.return_value = mock_completion_instance

        factory = GeminiChatCompletionFactory(app_config_fixture)
        result = factory.get_chat_completion_for_model_name("gemini-1.5-flash", None)

        call_kwargs = mock_google_completion.call_args[1]
        assert call_kwargs["service_id"] is None
        assert result == mock_completion_instance

    def test_supported_models_list(self):
        expected_models = [
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-1.0-pro",
            "gemini-2.0-flash-lite",
        ]

        assert GeminiChatCompletionFactory._GEMINI_MODELS == expected_models
