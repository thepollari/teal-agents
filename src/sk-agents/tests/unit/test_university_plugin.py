import sys
from unittest.mock import MagicMock, patch

import requests

sys.path.insert(
    0,
    "/home/ubuntu/repos/teal-agents/src/orchestrators/assistant-orchestrator/example/university",
)

from custom_plugins import University, UniversityPlugin, UniversitySearchResult


class TestUniversityPlugin:

    @patch("custom_plugins.requests.get")
    def test_search_universities_success(self, mock_get, mock_university_data):
        mock_response = MagicMock()
        mock_response.json.return_value = mock_university_data["success_response"]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        plugin = UniversityPlugin()
        result = plugin.search_universities("MIT")

        assert isinstance(result, UniversitySearchResult)
        assert len(result.universities) == 2
        assert result.universities[0].name == "Massachusetts Institute of Technology"
        assert result.message == "Found 2 universities for query: MIT"
        assert result.error is None
        mock_get.assert_called_once()

    @patch("custom_plugins.requests.get")
    def test_search_universities_empty_results(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        plugin = UniversityPlugin()
        result = plugin.search_universities("NonexistentUniversity")

        assert isinstance(result, UniversitySearchResult)
        assert len(result.universities) == 0
        assert result.message == "No universities found for query: NonexistentUniversity"
        assert result.error is None

    @patch("custom_plugins.requests.get")
    def test_search_universities_request_exception(self, mock_get):
        mock_get.side_effect = requests.RequestException("Network error")

        plugin = UniversityPlugin()
        result = plugin.search_universities("MIT")

        assert isinstance(result, UniversitySearchResult)
        assert len(result.universities) == 0
        assert result.message == "Failed to fetch universities"
        assert "Network error" in result.error

    @patch("custom_plugins.requests.get")
    def test_search_universities_timeout(self, mock_get):
        mock_get.side_effect = requests.Timeout("Request timeout")

        plugin = UniversityPlugin()
        result = plugin.search_universities("MIT")

        assert isinstance(result, UniversitySearchResult)
        assert len(result.universities) == 0
        assert result.error is not None
        assert "Request timeout" in result.error

    @patch("custom_plugins.requests.get")
    def test_search_universities_http_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        plugin = UniversityPlugin()
        result = plugin.search_universities("MIT")

        assert isinstance(result, UniversitySearchResult)
        assert len(result.universities) == 0
        assert result.error is not None

    @patch("custom_plugins.requests.get")
    def test_search_universities_generic_exception(self, mock_get):
        mock_get.side_effect = Exception("Unexpected error")

        plugin = UniversityPlugin()
        result = plugin.search_universities("MIT")

        assert isinstance(result, UniversitySearchResult)
        assert result.message == "Unexpected error occurred"
        assert "Unexpected error" in result.error

    @patch("custom_plugins.requests.get")
    def test_search_universities_limits_results(self, mock_get):
        mock_response = MagicMock()
        large_response = [
            {
                "name": f"University {i}",
                "web_pages": [f"http://uni{i}.edu"],
                "domains": [f"uni{i}.edu"],
                "country": "Country",
                "state-province": None,
                "alpha_two_code": "XX"
            }
            for i in range(15)
        ]
        mock_response.json.return_value = large_response
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        plugin = UniversityPlugin()
        result = plugin.search_universities("University")

        assert len(result.universities) == 10

    @patch("custom_plugins.requests.get")
    def test_get_universities_by_country_success(self, mock_get, mock_university_data):
        mock_response = MagicMock()
        mock_response.json.return_value = mock_university_data["country_response"]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        plugin = UniversityPlugin()
        result = plugin.get_universities_by_country("United Kingdom")

        assert isinstance(result, UniversitySearchResult)
        assert len(result.universities) == 1
        assert result.universities[0].name == "University of Oxford"
        assert result.universities[0].country == "United Kingdom"
        assert result.message == "Found 1 universities in United Kingdom"
        assert result.error is None

    @patch("custom_plugins.requests.get")
    def test_get_universities_by_country_empty_results(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        plugin = UniversityPlugin()
        result = plugin.get_universities_by_country("Atlantis")

        assert isinstance(result, UniversitySearchResult)
        assert len(result.universities) == 0
        assert result.message == "No universities found in country: Atlantis"
        assert result.error is None

    @patch("custom_plugins.requests.get")
    def test_get_universities_by_country_request_exception(self, mock_get):
        mock_get.side_effect = requests.RequestException("Connection failed")

        plugin = UniversityPlugin()
        result = plugin.get_universities_by_country("France")

        assert isinstance(result, UniversitySearchResult)
        assert len(result.universities) == 0
        assert result.message == "Failed to fetch universities"
        assert "Connection failed" in result.error

    @patch("custom_plugins.requests.get")
    def test_get_universities_by_country_generic_exception(self, mock_get):
        mock_get.side_effect = Exception("Unexpected error")

        plugin = UniversityPlugin()
        result = plugin.get_universities_by_country("France")

        assert isinstance(result, UniversitySearchResult)
        assert result.message == "Unexpected error occurred"
        assert "Unexpected error" in result.error

    @patch("custom_plugins.requests.get")
    def test_get_universities_by_country_limits_results(self, mock_get):
        mock_response = MagicMock()
        large_response = [
            {
                "name": f"University {i}",
                "web_pages": [f"http://uni{i}.edu"],
                "domains": [f"uni{i}.edu"],
                "country": "Country",
                "state-province": None,
                "alpha_two_code": "XX"
            }
            for i in range(25)
        ]
        mock_response.json.return_value = large_response
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        plugin = UniversityPlugin()
        result = plugin.get_universities_by_country("Country")

        assert len(result.universities) == 20

    def test_university_data_parsing(self, mock_university_data):
        uni_data = mock_university_data["success_response"][0]
        university = University(
            name=uni_data["name"],
            web_pages=uni_data["web_pages"],
            domains=uni_data["domains"],
            country=uni_data["country"],
            state_province=uni_data["state-province"],
            alpha_two_code=uni_data["alpha_two_code"]
        )

        assert university.name == "Massachusetts Institute of Technology"
        assert university.web_pages == ["http://web.mit.edu"]
        assert university.domains == ["mit.edu"]
        assert university.country == "United States"
        assert university.state_province == "Massachusetts"
        assert university.alpha_two_code == "US"

    def test_university_search_result_structure(self):
        universities = [
            University(
                name="Test University",
                web_pages=["http://test.edu"],
                domains=["test.edu"],
                country="Test Country",
                state_province="Test State",
                alpha_two_code="TC"
            )
        ]
        result = UniversitySearchResult(
            message="Test message",
            universities=universities,
            error=None
        )

        assert result.message == "Test message"
        assert len(result.universities) == 1
        assert result.error is None

    @patch("custom_plugins.requests.get")
    def test_search_universities_malformed_json_response(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        plugin = UniversityPlugin()
        result = plugin.search_universities("MIT")

        assert isinstance(result, UniversitySearchResult)
        assert len(result.universities) == 0
        assert result.error is not None

    def test_get_universities_url_with_name(self):
        url = UniversityPlugin._get_universities_url(name="MIT")
        assert url == "http://universities.hipolabs.com/search?name=MIT"

    def test_get_universities_url_with_country(self):
        url = UniversityPlugin._get_universities_url(country="United States")
        assert url == "http://universities.hipolabs.com/search?country=United States"

    def test_get_universities_url_with_both_params(self):
        url = UniversityPlugin._get_universities_url(name="MIT", country="United States")
        assert "name=MIT" in url
        assert "country=United States" in url

    def test_get_universities_url_without_params(self):
        url = UniversityPlugin._get_universities_url()
        assert url == "http://universities.hipolabs.com/search"

    @patch("custom_plugins.requests.get")
    def test_search_universities_with_special_characters(self, mock_get, mock_university_data):
        mock_response = MagicMock()
        mock_response.json.return_value = mock_university_data["success_response"]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        plugin = UniversityPlugin()
        result = plugin.search_universities("MIT & Harvard")

        assert isinstance(result, UniversitySearchResult)
        assert len(result.universities) == 2
        mock_get.assert_called_once()

    @patch("custom_plugins.requests.get")
    def test_search_universities_with_empty_string(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        plugin = UniversityPlugin()
        result = plugin.search_universities("")

        assert isinstance(result, UniversitySearchResult)
        assert len(result.universities) == 0

    @patch("custom_plugins.requests.get")
    def test_get_universities_by_country_with_empty_string(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        plugin = UniversityPlugin()
        result = plugin.get_universities_by_country("")

        assert isinstance(result, UniversitySearchResult)
        assert len(result.universities) == 0
