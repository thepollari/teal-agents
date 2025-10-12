import json
import os
from typing import Any
from unittest.mock import MagicMock

import pytest
from ska_utils import AppConfig

from src.sk_agents.configs import configs


@pytest.fixture()
def mock_app_config():
    """Mock AppConfig fixture for testing components that require configuration.

    This fixture creates a mock AppConfig instance with the ability to set and get
    configuration values, particularly useful for testing components that need API keys
    or other configuration settings.

    Usage:
        def test_example(mock_app_config):
            mock_app_config.get.return_value = "test-api-key"
    """
    AppConfig.add_configs(configs)
    mock_config = MagicMock(spec=AppConfig)
    return mock_config


@pytest.fixture()
def mock_app_config_with_api_key(mock_app_config):
    """Mock AppConfig fixture with API key pre-configured.

    This fixture extends mock_app_config by pre-configuring it with a test API key,
    useful for testing components like GeminiChatCompletionFactory.

    Usage:
        def test_gemini_factory(mock_app_config_with_api_key):
            factory = GeminiChatCompletionFactory(mock_app_config_with_api_key)
    """
    mock_app_config.get.return_value = "test-api-key-12345"
    return mock_app_config


@pytest.fixture()
def mock_requests_get(monkeypatch):
    """Mock requests.get() fixture for testing HTTP calls without actual network requests.

    This fixture mocks the requests.get function to return controlled responses based on
    test scenarios. It's particularly useful for testing UniversityPlugin methods.

    Usage:
        def test_api_call(mock_requests_get):
            mock_response = Mock()
            mock_response.json.return_value = [{"name": "MIT", ...}]
            mock_response.raise_for_status = Mock()
            mock_requests_get.return_value = mock_response

    Returns:
        MagicMock: A mock object that replaces requests.get
    """
    mock_get = MagicMock()

    import requests
    monkeypatch.setattr(requests, "get", mock_get)

    return mock_get


@pytest.fixture()
def university_api_responses() -> dict[str, Any]:
    """Load mock university API responses from fixtures file.

    This fixture loads the university_api_responses.json file containing various
    mock API response scenarios for testing UniversityPlugin.

    Usage:
        def test_with_mock_data(university_api_responses):
            multiple_unis = university_api_responses["multiple_universities"]
            empty_response = university_api_responses["empty_response"]

    Returns:
        Dict[str, Any]: Dictionary containing various mock API response scenarios
    """
    fixtures_path = os.path.join(
        os.path.dirname(__file__),
        "fixtures",
        "university_api_responses.json"
    )

    with open(fixtures_path) as f:
        return json.load(f)


@pytest.fixture()
def university_search_responses() -> dict[str, Any]:
    """Load mock university search response scenarios from fixtures file.

    This fixture loads the university_search_responses.json file containing various
    search scenarios including searches by name, by country, and edge cases.

    Usage:
        def test_search_scenarios(university_search_responses):
            mit_search = university_search_responses["search_by_name_mit"]
            us_universities = university_search_responses["search_by_country_us"]

    Returns:
        Dict[str, Any]: Dictionary containing various search response scenarios
    """
    fixtures_path = os.path.join(
        os.path.dirname(__file__),
        "fixtures",
        "university_search_responses.json"
    )

    with open(fixtures_path) as f:
        return json.load(f)


@pytest.fixture()
def mock_google_ai_chat_completion(monkeypatch):
    """Mock GoogleAIChatCompletion to prevent actual API calls to Google Gemini.

    This fixture mocks the GoogleAIChatCompletion class instantiation to avoid
    making real API calls during testing. It's used when testing GeminiChatCompletionFactory.

    Usage:
        def test_gemini_factory(mock_google_ai_chat_completion, mock_app_config_with_api_key):
            factory = GeminiChatCompletionFactory(mock_app_config_with_api_key)
            chat_completion = factory.get_chat_completion_for_model_name(
                "gemini-1.5-flash", "test-service"
            )

    Returns:
        MagicMock: A mock class that replaces GoogleAIChatCompletion
    """
    mock_chat_completion_class = MagicMock()
    mock_instance = MagicMock()
    mock_chat_completion_class.return_value = mock_instance

    from semantic_kernel.connectors.ai.google.google_ai.services import google_ai_chat_completion
    monkeypatch.setattr(
        google_ai_chat_completion,
        "GoogleAIChatCompletion",
        mock_chat_completion_class
    )

    return mock_chat_completion_class


@pytest.fixture()
def mock_requests_exception(monkeypatch):
    """Mock requests.get() to raise RequestException for error testing.

    This fixture configures requests.get to raise a RequestException, useful for
    testing error handling in UniversityPlugin methods.

    Usage:
        def test_api_error(mock_requests_exception):
            plugin = UniversityPlugin()
            result = plugin.search_universities("test")
    """
    import requests

    mock_get = MagicMock()
    mock_get.side_effect = requests.RequestException("Network error")
    monkeypatch.setattr(requests, "get", mock_get)

    return mock_get
