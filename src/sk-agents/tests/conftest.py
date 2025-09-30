import json
import os
from pathlib import Path

import pytest
from ska_utils import AppConfig

from sk_agents.configs import configs


@pytest.fixture
def app_config_fixture():
    os.environ["TA_API_KEY"] = "test-api-key-123"
    AppConfig.add_configs(configs)
    return AppConfig()


@pytest.fixture
def mock_university_data():
    fixtures_path = Path(__file__).parent / "fixtures" / "university_api_responses.json"
    with open(fixtures_path) as f:
        return json.load(f)
