from unittest.mock import MagicMock, patch

import pytest

from sk_agents.chat_completion.custom.gemini_chat_completion_factory import (
    GeminiChatCompletionFactory,
)
from sk_agents.configs import TA_API_KEY
from sk_agents.ska_types import ModelType


class TestGeminiChatCompletionFactoryInitialization:
    def test_init_with_valid_api_key(self, mock_app_config_with_api_key):
        """Test successful initialization when AppConfig provides a valid API key.

        This test verifies that GeminiChatCompletionFactory can be instantiated
        without errors when provided with a valid AppConfig containing an API key.
        """
        factory = GeminiChatCompletionFactory(mock_app_config_with_api_key)
        assert factory is not None
        assert isinstance(factory, GeminiChatCompletionFactory)

    def test_init_stores_api_key(self, mock_app_config):
        """Test that the API key is correctly stored in the self.api_key attribute.

        This test verifies that the factory retrieves the API key from AppConfig
        using the correct environment variable name and stores it in the api_key
        attribute.
        """
        expected_api_key = "test_api_key_123"
        mock_app_config.get.return_value = expected_api_key

        factory = GeminiChatCompletionFactory(mock_app_config)

        mock_app_config.get.assert_called_once_with(TA_API_KEY.env_name)
        assert factory.api_key == expected_api_key

    def test_init_with_missing_api_key(self, mock_app_config):
        """Test behavior when API key is None.

        This test verifies that the factory can be initialized even when the
        API key is None (the factory doesn't perform explicit validation in __init__).
        """
        mock_app_config.get.return_value = None

        factory = GeminiChatCompletionFactory(mock_app_config)

        assert factory.api_key is None

    def test_init_calls_parent_init(self, mock_app_config):
        """Test that the parent ChatCompletionFactory.__init__ is called with app_config.

        This test verifies that the factory properly calls its parent class's __init__
        method, which stores the app_config attribute.
        """
        mock_app_config.get.return_value = "test_api_key"

        factory = GeminiChatCompletionFactory(mock_app_config)

        assert hasattr(factory, 'app_config')
        assert factory.app_config == mock_app_config


class TestGeminiChatCompletionFactoryConfiguration:
    def test_get_configs_returns_empty_list(self):
        """Test that get_configs() returns an empty list.

        This test verifies that the static get_configs method returns an empty
        list, as the GeminiChatCompletionFactory doesn't define any additional
        configuration requirements beyond the standard TA_API_KEY.
        """
        configs = GeminiChatCompletionFactory.get_configs()

        assert configs == []
        assert isinstance(configs, list)
        assert len(configs) == 0


class TestGeminiChatCompletionFactoryValidModels:
    """Test GeminiChatCompletionFactory with all supported Gemini models."""

    @pytest.mark.parametrize(
        "model_name",
        [
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-1.0-pro",
            "gemini-2.0-flash-lite",
        ],
    )
    def test_get_chat_completion_for_valid_models(
        self,
        mock_app_config_with_api_key,
        model_name,
    ):
        """Test that get_chat_completion_for_model_name() works with all valid Gemini models.

        Verifies that each of the 4 supported Gemini models can be used to create
        a GoogleAIChatCompletion instance without raising errors.

        Args:
            mock_app_config_with_api_key: Fixture with pre-configured API key
            model_name: One of the supported Gemini model names (parametrized)
        """
        with patch(
            "sk_agents.chat_completion.custom.gemini_chat_completion_factory.GoogleAIChatCompletion"
        ) as mock_google_ai:
            mock_instance = MagicMock()
            mock_google_ai.return_value = mock_instance

            factory = GeminiChatCompletionFactory(mock_app_config_with_api_key)

            chat_completion = factory.get_chat_completion_for_model_name(
                model_name=model_name,
                service_id="test-service"
            )

            assert chat_completion is not None
            mock_google_ai.assert_called_once_with(
                service_id="test-service",
                gemini_model_id=model_name,
                api_key="test-api-key-12345"
            )


class TestGeminiChatCompletionFactoryInvalidModel:
    """Test GeminiChatCompletionFactory error handling for invalid models."""

    def test_get_chat_completion_for_invalid_model(
        self,
        mock_app_config_with_api_key,
    ):
        """Test that get_chat_completion_for_model_name() raises ValueError for unsupported models.

        Verifies that attempting to create a chat completion with an unsupported
        model name raises a ValueError with an appropriate error message.

        Args:
            mock_app_config_with_api_key: Fixture with pre-configured API key
        """
        factory = GeminiChatCompletionFactory(mock_app_config_with_api_key)

        with pytest.raises(ValueError) as excinfo:
            factory.get_chat_completion_for_model_name(
                model_name="unsupported-model",
                service_id="test-service"
            )

        assert "Model unsupported-model not supported by GeminiChatCompletionFactory" in str(
            excinfo.value
        )

    def test_get_model_type_for_invalid_model(
        self,
        mock_app_config_with_api_key,
    ):
        """Test that get_model_type_for_name() raises ValueError for unsupported models.

        Verifies that attempting to get the model type for an unsupported
        model name raises a ValueError.

        Args:
            mock_app_config_with_api_key: Fixture with pre-configured API key
        """
        factory = GeminiChatCompletionFactory(mock_app_config_with_api_key)

        with pytest.raises(ValueError) as excinfo:
            factory.get_model_type_for_name("unsupported-model")

        assert "Unknown model name unsupported-model" in str(excinfo.value)

    def test_model_supports_structured_output_invalid_model(
        self,
        mock_app_config_with_api_key,
    ):
        """Test that model_supports_structured_output() raises ValueError for unsupported models.

        Verifies that attempting to check structured output support for an
        unsupported model name raises a ValueError.

        Args:
            mock_app_config_with_api_key: Fixture with pre-configured API key
        """
        factory = GeminiChatCompletionFactory(mock_app_config_with_api_key)

        with pytest.raises(ValueError) as excinfo:
            factory.model_supports_structured_output("unsupported-model")

        assert "Unknown model name unsupported-model" in str(excinfo.value)


class TestGeminiChatCompletionFactoryModelType:
    """Test GeminiChatCompletionFactory model type identification."""

    @pytest.mark.parametrize(
        "model_name",
        [
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-1.0-pro",
            "gemini-2.0-flash-lite",
        ],
    )
    def test_get_model_type_returns_google(
        self,
        mock_app_config_with_api_key,
        model_name,
    ):
        """Test that get_model_type_for_name() returns ModelType.GOOGLE for all Gemini models.

        Verifies that the factory correctly identifies all supported Gemini models
        as Google model types.

        Args:
            mock_app_config_with_api_key: Fixture with pre-configured API key
            model_name: One of the supported Gemini model names (parametrized)
        """
        factory = GeminiChatCompletionFactory(mock_app_config_with_api_key)

        model_type = factory.get_model_type_for_name(model_name)

        assert model_type == ModelType.GOOGLE


class TestGeminiChatCompletionFactoryStructuredOutput:
    """Test GeminiChatCompletionFactory structured output support."""

    @pytest.mark.parametrize(
        "model_name",
        [
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-1.0-pro",
            "gemini-2.0-flash-lite",
        ],
    )
    def test_model_supports_structured_output_returns_true(
        self,
        mock_app_config_with_api_key,
        model_name,
    ):
        """Test that model_supports_structured_output() returns True for all Gemini models.

        Verifies that all supported Gemini models are marked as supporting
        structured output.

        Args:
            mock_app_config_with_api_key: Fixture with pre-configured API key
            model_name: One of the supported Gemini model names (parametrized)
        """
        factory = GeminiChatCompletionFactory(mock_app_config_with_api_key)

        supports_structured_output = factory.model_supports_structured_output(model_name)

        assert supports_structured_output is True


class TestGeminiChatCompletionFactoryCreateMethod:
    """Test GeminiChatCompletionFactory factory method."""

    def test_create_chat_completion_with_default_model(
        self,
        mock_app_config_with_api_key,
    ):
        """Test that create_chat_completion() works with default model and service_id.

        Verifies that the factory method creates a chat completion using the
        default model (gemini-2.0-flash-lite) and service_id (gemini_service)
        when no parameters are provided.

        Args:
            mock_app_config_with_api_key: Fixture with pre-configured API key
        """
        with patch(
            "sk_agents.chat_completion.custom.gemini_chat_completion_factory.GoogleAIChatCompletion"
        ) as mock_google_ai:
            mock_instance = MagicMock()
            mock_google_ai.return_value = mock_instance

            factory = GeminiChatCompletionFactory(mock_app_config_with_api_key)

            chat_completion = factory.create_chat_completion()

            assert chat_completion is not None
            mock_google_ai.assert_called_once_with(
                service_id="gemini_service",
                gemini_model_id="gemini-2.0-flash-lite",
                api_key="test-api-key-12345"
            )

    def test_create_chat_completion_with_custom_parameters(
        self,
        mock_app_config_with_api_key,
    ):
        """Test that create_chat_completion() works with custom model_name and service_id.

        Verifies that the factory method correctly uses provided model_name
        and service_id parameters when creating a chat completion.

        Args:
            mock_app_config_with_api_key: Fixture with pre-configured API key
        """
        with patch(
            "sk_agents.chat_completion.custom.gemini_chat_completion_factory.GoogleAIChatCompletion"
        ) as mock_google_ai:
            mock_instance = MagicMock()
            mock_google_ai.return_value = mock_instance

            factory = GeminiChatCompletionFactory(mock_app_config_with_api_key)

            chat_completion = factory.create_chat_completion(
                model_name="gemini-1.5-pro",
                service_id="custom-service"
            )

            assert chat_completion is not None
            mock_google_ai.assert_called_once_with(
                service_id="custom-service",
                gemini_model_id="gemini-1.5-pro",
                api_key="test-api-key-12345"
            )
