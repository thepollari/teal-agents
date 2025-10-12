import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from ska_utils import AppConfig


@pytest.fixture
def university_api_responses():
    """Load mock university API responses from fixtures."""
    fixture_path = Path(__file__).parent / "fixtures" / "university_api_responses.json"
    with open(fixture_path) as f:
        return json.load(f)


@pytest.fixture
def mock_app_config():
    """Mock AppConfig for GeminiChatCompletionFactory tests."""
    config = MagicMock(spec=AppConfig)
    config.get.return_value = "test_api_key_12345"
    return config


@pytest.fixture
def mock_requests_response():
    """Mock requests.Response object."""
    response = MagicMock()
    response.status_code = 200
    return response
