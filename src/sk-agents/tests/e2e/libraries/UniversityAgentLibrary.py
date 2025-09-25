"""Custom Robot Framework library for University Agent testing."""

import json
import os
import time
from typing import Any

import requests
from robot.api.deco import keyword


class UniversityAgentLibrary:
    """Custom library for University Agent E2E testing."""

    def __init__(self):
        self.agent_url = None
        self.ui_url = None

    @keyword
    def set_agent_urls(self, agent_url: str, ui_url: str):
        """Set the URLs for agent and UI services."""
        self.agent_url = agent_url
        self.ui_url = ui_url

    @keyword
    def wait_for_service_ready(self, url: str, timeout: int = 60):
        """Wait for a service to be ready by checking its health endpoint."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    return True
            except requests.RequestException:
                pass
            time.sleep(2)
        raise Exception(f"Service at {url} not ready within {timeout} seconds")

    @keyword
    def load_test_data(self, filename: str) -> dict[str, Any]:
        """Load test data from JSON file."""
        test_data_path = os.path.join(os.path.dirname(__file__), "..", "resources", filename)
        with open(test_data_path) as f:
            return json.load(f)

    @keyword
    def validate_university_response(self, response_text: str, expected_university: str) -> bool:
        """Validate that response contains expected university information."""
        return expected_university.lower() in response_text.lower()

    @keyword
    def extract_universities_from_response(self, response_text: str) -> list[str]:
        """Extract university names from response text."""
        universities = []
        lines = response_text.split("\n")
        for line in lines:
            if "university" in line.lower() and "**" in line:
                name = line.strip("*").strip()
                universities.append(name)
        return universities
