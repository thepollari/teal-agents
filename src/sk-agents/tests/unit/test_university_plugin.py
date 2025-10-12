import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

plugin_path = (
    Path(__file__).parent.parent.parent.parent.parent
    / "src"
    / "orchestrators"
    / "assistant-orchestrator"
    / "example"
    / "university"
)
sys.path.insert(0, str(plugin_path))

from custom_plugins import (  # noqa: E402
    University,
    UniversityPlugin,
    UniversitySearchResult,
)


class TestUniversityPlugin:
    """Isolated unit tests for UniversityPlugin component."""

    @pytest.fixture
    def plugin(self):
        """Create UniversityPlugin instance for testing."""
        return UniversityPlugin()

    @patch("custom_plugins.requests.get")
    def test_search_universities_success(self, mock_get, university_api_responses):
        """Test successful university search with valid query."""
        mock_response = MagicMock()
        mock_response.json.return_value = university_api_responses["successful_search"]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        plugin = UniversityPlugin()
        result = plugin.search_universities("Aalto")

        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "name=Aalto" in call_args[0][0]

        assert isinstance(result, UniversitySearchResult)
        assert len(result.universities) == 1
        assert result.universities[0].name == "Aalto University"
        assert result.error is None

    @patch("custom_plugins.requests.get")
    def test_search_universities_api_error(self, mock_get):
        """Test search_universities handles RequestException."""
        mock_get.side_effect = requests.RequestException("API timeout")

        plugin = UniversityPlugin()
        result = plugin.search_universities("test")

        assert isinstance(result, UniversitySearchResult)
        assert result.error is not None
        assert "API timeout" in result.error
        assert len(result.universities) == 0

    @patch("custom_plugins.requests.get")
    def test_search_universities_network_failure(self, mock_get):
        """Test search_universities handles network failures."""
        mock_get.side_effect = requests.ConnectionError("Network unreachable")

        plugin = UniversityPlugin()
        result = plugin.search_universities("test")

        assert result.error is not None
        assert "Network unreachable" in result.error

    @patch("custom_plugins.requests.get")
    def test_search_universities_generic_exception(self, mock_get):
        """Test search_universities handles unexpected exceptions."""
        mock_get.side_effect = Exception("Unexpected error")

        plugin = UniversityPlugin()
        result = plugin.search_universities("test")

        assert result.error is not None
        assert "Unexpected error" in result.error

    @patch("custom_plugins.requests.get")
    def test_search_universities_empty_query(self, mock_get, university_api_responses):
        """Test search with empty string query."""
        mock_response = MagicMock()
        mock_response.json.return_value = university_api_responses["empty_search"]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        plugin = UniversityPlugin()
        result = plugin.search_universities("")

        assert len(result.universities) == 0
        assert "No universities found" in result.message

    @patch("custom_plugins.requests.get")
    def test_search_universities_special_characters(self, mock_get, university_api_responses):
        """Test search with special characters in query."""
        mock_response = MagicMock()
        mock_response.json.return_value = university_api_responses["successful_search"]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        plugin = UniversityPlugin()
        result = plugin.search_universities("Aalto & University")

        mock_get.assert_called_once()
        assert result.error is None

    @patch("custom_plugins.requests.get")
    def test_get_universities_by_country_success(self, mock_get, university_api_responses):
        """Test successful country-based search."""
        mock_response = MagicMock()
        mock_response.json.return_value = university_api_responses["country_search_finland"]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        plugin = UniversityPlugin()
        result = plugin.get_universities_by_country("Finland")

        call_args = mock_get.call_args
        assert "country=Finland" in call_args[0][0]

        assert len(result.universities) >= 1
        assert result.universities[0].country == "Finland"

    @patch("custom_plugins.requests.get")
    def test_get_universities_by_country_not_found(self, mock_get, university_api_responses):
        """Test country search with no results."""
        mock_response = MagicMock()
        mock_response.json.return_value = university_api_responses["empty_search"]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        plugin = UniversityPlugin()
        result = plugin.get_universities_by_country("NonexistentCountry")

        assert len(result.universities) == 0
        assert "No universities found" in result.message

    @patch("custom_plugins.requests.get")
    def test_get_universities_by_country_malformed_response(self, mock_get):
        """Test handling of malformed JSON response."""
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        plugin = UniversityPlugin()
        result = plugin.get_universities_by_country("Finland")

        assert result.error is not None

    def test_university_data_parsing(self):
        """Test University Pydantic model parsing without external calls."""
        university_data = {
            "name": "Test University",
            "web_pages": ["https://test.edu"],
            "domains": ["test.edu"],
            "country": "Test Country",
            "state_province": "Test State",
            "alpha_two_code": "TC",
        }

        university = University(**university_data)

        assert university.name == "Test University"
        assert university.web_pages == ["https://test.edu"]
        assert university.country == "Test Country"

    def test_university_search_result_json_format(self):
        """Test UniversitySearchResult JSON serialization."""
        result = UniversitySearchResult(
            message="Test message", universities=[], error=None
        )

        json_data = result.model_dump_json()
        assert "message" in json_data
        assert "universities" in json_data

    @patch("custom_plugins.requests.get")
    def test_search_universities_limit_10_results(self, mock_get):
        """Test that search_universities limits results to 10."""
        many_universities = [
            {
                "name": f"University {i}",
                "web_pages": [f"https://uni{i}.edu"],
                "domains": [f"uni{i}.edu"],
                "country": "Test Country",
                "state-province": None,
                "alpha_two_code": "TC",
            }
            for i in range(15)
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = many_universities
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        plugin = UniversityPlugin()
        result = plugin.search_universities("University")

        assert len(result.universities) == 10

    @patch("custom_plugins.requests.get")
    def test_get_universities_by_country_limit_20_results(self, mock_get):
        """Test that get_universities_by_country limits results to 20."""
        many_universities = [
            {
                "name": f"University {i}",
                "web_pages": [f"https://uni{i}.edu"],
                "domains": [f"uni{i}.edu"],
                "country": "Test Country",
                "state-province": None,
                "alpha_two_code": "TC",
            }
            for i in range(25)
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = many_universities
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        plugin = UniversityPlugin()
        result = plugin.get_universities_by_country("Test Country")

        assert len(result.universities) == 20

    @patch("custom_plugins.requests.get")
    def test_get_universities_by_country_request_exception(self, mock_get):
        """Test get_universities_by_country handles RequestException."""
        mock_get.side_effect = requests.RequestException("Connection timeout")

        plugin = UniversityPlugin()
        result = plugin.get_universities_by_country("Finland")

        assert isinstance(result, UniversitySearchResult)
        assert result.error is not None
        assert "Connection timeout" in result.error
        assert len(result.universities) == 0

    @patch("custom_plugins.requests.get")
    def test_get_universities_by_country_generic_exception(self, mock_get):
        """Test get_universities_by_country handles unexpected exceptions."""
        mock_get.side_effect = Exception("Unexpected error")

        plugin = UniversityPlugin()
        result = plugin.get_universities_by_country("Finland")

        assert result.error is not None
        assert "Unexpected error" in result.error

    def test_get_universities_url_with_name(self):
        """Test URL construction with name parameter."""
        url = UniversityPlugin._get_universities_url(name="Stanford")
        assert url == "http://universities.hipolabs.com/search?name=Stanford"

    def test_get_universities_url_with_country(self):
        """Test URL construction with country parameter."""
        url = UniversityPlugin._get_universities_url(country="United States")
        assert url == "http://universities.hipolabs.com/search?country=United States"

    def test_get_universities_url_with_both_params(self):
        """Test URL construction with both name and country parameters."""
        url = UniversityPlugin._get_universities_url(name="Stanford", country="United States")
        assert url == "http://universities.hipolabs.com/search?name=Stanford&country=United States"

    def test_get_universities_url_no_params(self):
        """Test URL construction with no parameters."""
        url = UniversityPlugin._get_universities_url()
        assert url == "http://universities.hipolabs.com/search"
