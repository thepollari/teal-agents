from sk_agents.chat_completion.custom.gemini_chat_completion_factory import (
    GeminiChatCompletionFactory,
)
from sk_agents.configs import TA_API_KEY


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
