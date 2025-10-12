from unittest.mock import MagicMock, patch

import pytest
from ska_utils import AppConfig

from sk_agents.chat_completion.custom.gemini_chat_completion_factory import (
    GeminiChatCompletionFactory,
)
from sk_agents.ska_types import ModelType


class TestGeminiChatCompletionFactory:
    """Isolated unit tests for GeminiChatCompletionFactory."""

    def test_factory_initialization_valid_config(self, mock_app_config):
        """Test factory initialization with valid AppConfig."""
        factory = GeminiChatCompletionFactory(mock_app_config)

        assert factory.api_key == "test_api_key_12345"
        mock_app_config.get.assert_called_once_with("TA_API_KEY")

    def test_factory_initialization_missing_api_key(self):
        """Test factory initialization with missing API key."""
        mock_config = MagicMock(spec=AppConfig)
        mock_config.get.return_value = None

        factory = GeminiChatCompletionFactory(mock_config)
        assert factory.api_key is None

    @patch(
        "sk_agents.chat_completion.custom.gemini_chat_completion_factory.GoogleAIChatCompletion"
    )
    def test_get_chat_completion_for_supported_model(
        self, mock_google_ai, mock_app_config
    ):
        """Test service creation for supported Gemini models."""
        factory = GeminiChatCompletionFactory(mock_app_config)

        factory.get_chat_completion_for_model_name(
            "gemini-1.5-flash", "test_service"
        )

        mock_google_ai.assert_called_once_with(
            service_id="test_service",
            gemini_model_id="gemini-1.5-flash",
            api_key="test_api_key_12345",
        )

    @patch(
        "sk_agents.chat_completion.custom.gemini_chat_completion_factory.GoogleAIChatCompletion"
    )
    def test_get_chat_completion_for_all_supported_models(
        self, mock_google_ai, mock_app_config
    ):
        """Test service creation for all supported Gemini models."""
        factory = GeminiChatCompletionFactory(mock_app_config)

        supported_models = [
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-1.0-pro",
            "gemini-2.0-flash-lite",
        ]

        for model in supported_models:
            mock_google_ai.reset_mock()
            factory.get_chat_completion_for_model_name(model, "test_service")
            mock_google_ai.assert_called_once()

    def test_get_chat_completion_for_unsupported_model(self, mock_app_config):
        """Test service creation raises ValueError for unsupported models."""
        factory = GeminiChatCompletionFactory(mock_app_config)

        with pytest.raises(ValueError) as exc_info:
            factory.get_chat_completion_for_model_name(
                "unsupported-model", "test_service"
            )

        assert "not supported" in str(exc_info.value)

    def test_get_model_type_for_name_supported_model(self, mock_app_config):
        """Test get_model_type_for_name returns ModelType.GOOGLE for supported models."""
        factory = GeminiChatCompletionFactory(mock_app_config)

        model_type = factory.get_model_type_for_name("gemini-1.5-flash")
        assert model_type == ModelType.GOOGLE

    def test_get_model_type_for_name_all_supported_models(self, mock_app_config):
        """Test get_model_type_for_name returns ModelType.GOOGLE for all supported models."""
        factory = GeminiChatCompletionFactory(mock_app_config)

        supported_models = [
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-1.0-pro",
            "gemini-2.0-flash-lite",
        ]

        for model in supported_models:
            model_type = factory.get_model_type_for_name(model)
            assert model_type == ModelType.GOOGLE

    def test_get_model_type_for_name_unsupported_model(self, mock_app_config):
        """Test get_model_type_for_name raises ValueError for unsupported models."""
        factory = GeminiChatCompletionFactory(mock_app_config)

        with pytest.raises(ValueError) as exc_info:
            factory.get_model_type_for_name("unsupported-model")

        assert "Unknown model name" in str(exc_info.value)

    def test_model_supports_structured_output_supported_models(self, mock_app_config):
        """Test model_supports_structured_output returns True for all Gemini models."""
        factory = GeminiChatCompletionFactory(mock_app_config)

        supported_models = [
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-1.0-pro",
            "gemini-2.0-flash-lite",
        ]

        for model in supported_models:
            assert factory.model_supports_structured_output(model) is True

    def test_model_supports_structured_output_unsupported_model(self, mock_app_config):
        """Test model_supports_structured_output raises ValueError for unsupported models."""
        factory = GeminiChatCompletionFactory(mock_app_config)

        with pytest.raises(ValueError) as exc_info:
            factory.model_supports_structured_output("unsupported-model")

        assert "Unknown model name" in str(exc_info.value)

    @patch(
        "sk_agents.chat_completion.custom.gemini_chat_completion_factory.GoogleAIChatCompletion"
    )
    def test_create_chat_completion_with_default_model(
        self, mock_google_ai, mock_app_config
    ):
        """Test create_chat_completion uses default model when none specified."""
        factory = GeminiChatCompletionFactory(mock_app_config)

        factory.create_chat_completion()

        mock_google_ai.assert_called_once()
        call_args = mock_google_ai.call_args
        assert call_args[1]["gemini_model_id"] == "gemini-2.0-flash-lite"

    @patch(
        "sk_agents.chat_completion.custom.gemini_chat_completion_factory.GoogleAIChatCompletion"
    )
    def test_create_chat_completion_with_specified_model(
        self, mock_google_ai, mock_app_config
    ):
        """Test create_chat_completion with specified model name."""
        factory = GeminiChatCompletionFactory(mock_app_config)

        factory.create_chat_completion(model_name="gemini-1.5-pro")

        mock_google_ai.assert_called_once()
        call_args = mock_google_ai.call_args
        assert call_args[1]["gemini_model_id"] == "gemini-1.5-pro"

    @patch(
        "sk_agents.chat_completion.custom.gemini_chat_completion_factory.GoogleAIChatCompletion"
    )
    def test_create_chat_completion_with_custom_service_id(
        self, mock_google_ai, mock_app_config
    ):
        """Test create_chat_completion with custom service_id."""
        factory = GeminiChatCompletionFactory(mock_app_config)

        factory.create_chat_completion(service_id="custom_service")

        mock_google_ai.assert_called_once()
        call_args = mock_google_ai.call_args
        assert call_args[1]["service_id"] == "custom_service"

    def test_get_configs(self, mock_app_config):
        """Test get_configs returns empty list."""
        factory = GeminiChatCompletionFactory(mock_app_config)

        configs = factory.get_configs()
        assert configs == []

    def test_factory_inherits_from_chat_completion_factory(self, mock_app_config):
        """Test that GeminiChatCompletionFactory properly inherits from ChatCompletionFactory."""
        factory = GeminiChatCompletionFactory(mock_app_config)

        assert hasattr(factory, "app_config")
        assert factory.app_config == mock_app_config

    @patch(
        "sk_agents.chat_completion.custom.gemini_chat_completion_factory.GoogleAIChatCompletion"
    )
    def test_multiple_service_creations_use_same_api_key(
        self, mock_google_ai, mock_app_config
    ):
        """Test that multiple service creations use the same API key from config."""
        factory = GeminiChatCompletionFactory(mock_app_config)

        factory.get_chat_completion_for_model_name("gemini-1.5-flash", "service1")
        factory.get_chat_completion_for_model_name("gemini-1.5-pro", "service2")

        assert mock_google_ai.call_count == 2
        for call in mock_google_ai.call_args_list:
            assert call[1]["api_key"] == "test_api_key_12345"
