import importlib.util
import sys
from pathlib import Path
from unittest.mock import Mock

repo_root = Path(__file__).parent.parent.parent.parent.parent
custom_plugins_path = (
    repo_root
    / "src"
    / "orchestrators"
    / "assistant-orchestrator"
    / "example"
    / "university"
    / "custom_plugins.py"
)

spec = importlib.util.spec_from_file_location("custom_plugins", custom_plugins_path)
custom_plugins = importlib.util.module_from_spec(spec)
sys.modules["custom_plugins"] = custom_plugins
spec.loader.exec_module(custom_plugins)

University = custom_plugins.University
UniversityPlugin = custom_plugins.UniversityPlugin
UniversitySearchResult = custom_plugins.UniversitySearchResult


class TestUniversityPluginSuccess:
    def test_search_universities_successful_response(
        self, mock_requests_get, university_search_responses
    ):
        plugin = UniversityPlugin()
        search_data = university_search_responses["search_by_name_mit"]

        mock_response = Mock()
        mock_response.json.return_value = search_data["results"]
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        result = plugin.search_universities("MIT")

        assert isinstance(result, UniversitySearchResult)
        assert result.error is None
        assert "Found 5 universities for query: MIT" == result.message
        assert len(result.universities) == 5

        first_uni = result.universities[0]
        assert isinstance(first_uni, University)
        assert first_uni.name == "Massachusetts Institute of Technology"
        assert first_uni.country == "United States"
        assert first_uni.state_province == "Massachusetts"
        assert first_uni.alpha_two_code == "US"
        assert first_uni.web_pages == ["http://web.mit.edu"]
        assert first_uni.domains == ["mit.edu"]

    def test_search_universities_respects_10_result_limit(
        self, mock_requests_get, university_search_responses
    ):
        plugin = UniversityPlugin()
        search_data = university_search_responses["search_exceeding_name_limit"]

        results_with_50_items = search_data["results"] * 5
        assert len(results_with_50_items) == 50

        mock_response = Mock()
        mock_response.json.return_value = results_with_50_items
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        result = plugin.search_universities("University")

        assert isinstance(result, UniversitySearchResult)
        assert result.error is None
        assert len(result.universities) == 10
        assert "Found 10 universities for query: University" == result.message

    def test_search_universities_single_result(
        self, mock_requests_get, university_search_responses
    ):
        plugin = UniversityPlugin()
        search_data = university_search_responses["search_by_name_stanford"]

        mock_response = Mock()
        mock_response.json.return_value = search_data["results"]
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        result = plugin.search_universities("Stanford")

        assert isinstance(result, UniversitySearchResult)
        assert result.error is None
        assert len(result.universities) == 1
        assert result.universities[0].name == "Stanford University"
        assert result.universities[0].country == "United States"
        assert result.universities[0].state_province == "California"

    def test_search_universities_empty_result(
        self, mock_requests_get, university_search_responses
    ):
        plugin = UniversityPlugin()
        search_data = university_search_responses["search_by_name_no_results"]

        mock_response = Mock()
        mock_response.json.return_value = search_data["results"]
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        result = plugin.search_universities("NonExistentUniversityXYZ123")

        assert isinstance(result, UniversitySearchResult)
        assert result.error is None
        assert len(result.universities) == 0
        assert (
            result.message
            == "No universities found for query: NonExistentUniversityXYZ123"
        )

    def test_get_universities_by_country_successful_response(
        self, mock_requests_get, university_search_responses
    ):
        plugin = UniversityPlugin()
        search_data = university_search_responses["search_by_country_us"]

        mock_response = Mock()
        mock_response.json.return_value = search_data["results"]
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        result = plugin.get_universities_by_country("United States")

        assert isinstance(result, UniversitySearchResult)
        assert result.error is None
        assert "Found 20 universities in United States" == result.message
        assert len(result.universities) == 20

        first_uni = result.universities[0]
        assert isinstance(first_uni, University)
        assert first_uni.name == "Massachusetts Institute of Technology"
        assert first_uni.country == "United States"
        assert first_uni.state_province == "Massachusetts"
        assert first_uni.alpha_two_code == "US"

    def test_get_universities_by_country_respects_20_result_limit(
        self, mock_requests_get, university_search_responses
    ):
        plugin = UniversityPlugin()
        search_data = university_search_responses["search_by_country_us"]

        results_with_40_items = search_data["results"] * 2
        assert len(results_with_40_items) == 40

        mock_response = Mock()
        mock_response.json.return_value = results_with_40_items
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        result = plugin.get_universities_by_country("United States")

        assert isinstance(result, UniversitySearchResult)
        assert result.error is None
        assert len(result.universities) == 20
        assert "Found 20 universities in United States" == result.message

    def test_get_universities_by_country_uk(
        self, mock_requests_get, university_search_responses
    ):
        plugin = UniversityPlugin()
        search_data = university_search_responses["search_by_country_uk"]

        mock_response = Mock()
        mock_response.json.return_value = search_data["results"]
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        result = plugin.get_universities_by_country("United Kingdom")

        assert isinstance(result, UniversitySearchResult)
        assert result.error is None
        assert len(result.universities) == 5
        assert "Found 5 universities in United Kingdom" == result.message

        first_uni = result.universities[0]
        assert first_uni.name == "University of Oxford"
        assert first_uni.state_province is None
        assert first_uni.alpha_two_code == "GB"

    def test_get_universities_by_country_empty_result(
        self, mock_requests_get, university_search_responses
    ):
        plugin = UniversityPlugin()
        search_data = university_search_responses["search_by_country_no_results"]

        mock_response = Mock()
        mock_response.json.return_value = search_data["results"]
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        result = plugin.get_universities_by_country("NonExistentCountryXYZ")

        assert isinstance(result, UniversitySearchResult)
        assert result.error is None
        assert len(result.universities) == 0
        assert result.message == "No universities found in country: NonExistentCountryXYZ"


class TestUniversityDataParsing:
    def test_university_model_parses_all_fields(
        self, mock_requests_get, university_api_responses
    ):
        plugin = UniversityPlugin()
        api_data = university_api_responses["universities_with_state"]

        mock_response = Mock()
        mock_response.json.return_value = api_data
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        result = plugin.search_universities("MIT")

        uni = result.universities[0]
        assert uni.name == "Massachusetts Institute of Technology"
        assert uni.country == "United States"
        assert uni.alpha_two_code == "US"
        assert uni.state_province == "Massachusetts"
        assert uni.domains == ["mit.edu"]
        assert uni.web_pages == ["http://web.mit.edu"]

    def test_university_model_handles_null_state_province(
        self, mock_requests_get, university_api_responses
    ):
        plugin = UniversityPlugin()
        api_data = university_api_responses["universities_without_state"]

        mock_response = Mock()
        mock_response.json.return_value = api_data
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        result = plugin.search_universities("Oxford")

        uni = result.universities[0]
        assert uni.name == "University of Oxford"
        assert uni.state_province is None
        assert uni.country == "United Kingdom"
        assert uni.alpha_two_code == "GB"

    def test_university_model_parses_multiple_domains_and_pages(
        self, mock_requests_get
    ):
        plugin = UniversityPlugin()

        api_data = [
            {
                "name": "Test University",
                "web_pages": ["http://www.test.edu", "http://test.edu"],
                "domains": ["test.edu", "test.com"],
                "country": "Test Country",
                "state-province": "Test State",
                "alpha_two_code": "TC",
            }
        ]

        mock_response = Mock()
        mock_response.json.return_value = api_data
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        result = plugin.search_universities("Test")

        uni = result.universities[0]
        assert len(uni.web_pages) == 2
        assert "http://www.test.edu" in uni.web_pages
        assert "http://test.edu" in uni.web_pages
        assert len(uni.domains) == 2
        assert "test.edu" in uni.domains
        assert "test.com" in uni.domains


class TestUniversitySearchResultFormat:
    def test_search_result_structure_valid(
        self, mock_requests_get, university_api_responses
    ):
        plugin = UniversityPlugin()
        api_data = university_api_responses["multiple_universities"]

        mock_response = Mock()
        mock_response.json.return_value = api_data
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        result = plugin.search_universities("University")

        assert hasattr(result, "message")
        assert hasattr(result, "universities")
        assert hasattr(result, "error")
        assert isinstance(result.message, str)
        assert isinstance(result.universities, list)
        assert result.error is None

    def test_search_result_universities_are_university_objects(
        self, mock_requests_get, university_api_responses
    ):
        plugin = UniversityPlugin()
        api_data = university_api_responses["multiple_universities"]

        mock_response = Mock()
        mock_response.json.return_value = api_data
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        result = plugin.search_universities("University")

        for uni in result.universities:
            assert isinstance(uni, University)
            assert hasattr(uni, "name")
            assert hasattr(uni, "country")
            assert hasattr(uni, "alpha_two_code")
            assert hasattr(uni, "state_province")
            assert hasattr(uni, "domains")
            assert hasattr(uni, "web_pages")

    def test_country_search_result_format_valid(
        self, mock_requests_get, university_search_responses
    ):
        plugin = UniversityPlugin()
        search_data = university_search_responses["search_by_country_uk"]

        mock_response = Mock()
        mock_response.json.return_value = search_data["results"]
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        result = plugin.get_universities_by_country("United Kingdom")

        assert isinstance(result, UniversitySearchResult)
        assert hasattr(result, "message")
        assert hasattr(result, "universities")
        assert hasattr(result, "error")
        assert isinstance(result.message, str)
        assert isinstance(result.universities, list)
        assert result.error is None

        for uni in result.universities:
            assert isinstance(uni, University)


class TestUniversityPluginErrorHandling:
    def test_search_universities_network_failure(self, monkeypatch):
        import requests

        plugin = UniversityPlugin()

        mock_get = Mock()
        mock_get.side_effect = requests.RequestException("Connection timeout")
        monkeypatch.setattr(requests, "get", mock_get)

        result = plugin.search_universities("MIT")

        assert isinstance(result, UniversitySearchResult)
        assert result.message == "Failed to fetch universities"
        assert result.universities == []
        assert result.error is not None
        assert "Connection timeout" in result.error

    def test_search_universities_generic_exception(self, monkeypatch):
        import requests

        plugin = UniversityPlugin()

        mock_get = Mock()
        mock_get.side_effect = Exception("Unexpected error")
        monkeypatch.setattr(requests, "get", mock_get)

        result = plugin.search_universities("MIT")

        assert isinstance(result, UniversitySearchResult)
        assert result.message == "Unexpected error occurred"
        assert result.universities == []
        assert result.error is not None
        assert "Unexpected error" in result.error

    def test_get_universities_by_country_network_failure(self, monkeypatch):
        import requests

        plugin = UniversityPlugin()

        mock_get = Mock()
        mock_get.side_effect = requests.RequestException("Network unreachable")
        monkeypatch.setattr(requests, "get", mock_get)

        result = plugin.get_universities_by_country("United States")

        assert isinstance(result, UniversitySearchResult)
        assert result.message == "Failed to fetch universities"
        assert result.universities == []
        assert result.error is not None
        assert "Network unreachable" in result.error

    def test_get_universities_by_country_generic_exception(self, monkeypatch):
        import requests

        plugin = UniversityPlugin()

        mock_get = Mock()
        mock_get.side_effect = Exception("Generic failure")
        monkeypatch.setattr(requests, "get", mock_get)

        result = plugin.get_universities_by_country("United States")

        assert isinstance(result, UniversitySearchResult)
        assert result.message == "Unexpected error occurred"
        assert result.universities == []
        assert result.error is not None
        assert "Generic failure" in result.error

    def test_search_universities_timeout(self, monkeypatch):
        import requests

        plugin = UniversityPlugin()

        mock_get = Mock()
        mock_get.side_effect = requests.Timeout("Request timed out after 10 seconds")
        monkeypatch.setattr(requests, "get", mock_get)

        result = plugin.search_universities("MIT")

        assert isinstance(result, UniversitySearchResult)
        assert result.message == "Failed to fetch universities"
        assert result.universities == []
        assert result.error is not None
        assert "timed out" in result.error.lower()

    def test_get_universities_by_country_timeout(self, monkeypatch):
        import requests

        plugin = UniversityPlugin()

        mock_get = Mock()
        mock_get.side_effect = requests.Timeout("Request timed out after 10 seconds")
        monkeypatch.setattr(requests, "get", mock_get)

        result = plugin.get_universities_by_country("Canada")

        assert isinstance(result, UniversitySearchResult)
        assert result.message == "Failed to fetch universities"
        assert result.universities == []
        assert result.error is not None
        assert "timed out" in result.error.lower()

    def test_search_universities_http_error(self, monkeypatch):
        import requests

        plugin = UniversityPlugin()

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            "404 Not Found"
        )
        mock_get = Mock(return_value=mock_response)
        monkeypatch.setattr(requests, "get", mock_get)

        result = plugin.search_universities("MIT")

        assert isinstance(result, UniversitySearchResult)
        assert result.message == "Failed to fetch universities"
        assert result.universities == []
        assert result.error is not None

    def test_get_universities_by_country_http_error(self, monkeypatch):
        import requests

        plugin = UniversityPlugin()

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            "500 Internal Server Error"
        )
        mock_get = Mock(return_value=mock_response)
        monkeypatch.setattr(requests, "get", mock_get)

        result = plugin.get_universities_by_country("Japan")

        assert isinstance(result, UniversitySearchResult)
        assert result.message == "Failed to fetch universities"
        assert result.universities == []
        assert result.error is not None


class TestUniversityPluginInputValidation:
    def test_search_universities_empty_string(self, mock_requests_get):
        plugin = UniversityPlugin()

        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        result = plugin.search_universities("")

        assert isinstance(result, UniversitySearchResult)
        assert result.error is None
        assert result.universities == []
        assert "No universities found" in result.message

    def test_get_universities_by_country_empty_string(self, mock_requests_get):
        plugin = UniversityPlugin()

        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        result = plugin.get_universities_by_country("")

        assert isinstance(result, UniversitySearchResult)
        assert result.error is None
        assert result.universities == []
        assert "No universities found" in result.message

    def test_search_universities_special_characters(self, mock_requests_get):
        plugin = UniversityPlugin()

        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        result = plugin.search_universities("@#$%^&*()")

        assert isinstance(result, UniversitySearchResult)
        assert result.error is None
        assert result.universities == []

    def test_get_universities_by_country_special_characters(self, mock_requests_get):
        plugin = UniversityPlugin()

        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        result = plugin.get_universities_by_country("!@#$%")

        assert isinstance(result, UniversitySearchResult)
        assert result.error is None
        assert result.universities == []

    def test_search_universities_very_long_string(self, mock_requests_get):
        plugin = UniversityPlugin()

        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        long_query = "x" * 1000
        result = plugin.search_universities(long_query)

        assert isinstance(result, UniversitySearchResult)
        assert result.error is None

    def test_search_universities_unicode_characters(self, mock_requests_get):
        plugin = UniversityPlugin()

        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        result = plugin.search_universities("北京大学")

        assert isinstance(result, UniversitySearchResult)
        assert result.error is None


class TestUniversityPluginMalformedResponses:
    def test_search_universities_invalid_json(self, monkeypatch):
        import requests

        plugin = UniversityPlugin()

        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status = Mock()
        mock_get = Mock(return_value=mock_response)
        monkeypatch.setattr(requests, "get", mock_get)

        result = plugin.search_universities("MIT")

        assert isinstance(result, UniversitySearchResult)
        assert result.message == "Unexpected error occurred"
        assert result.universities == []
        assert result.error is not None
        assert "Invalid JSON" in result.error

    def test_get_universities_by_country_invalid_json(self, monkeypatch):
        import requests

        plugin = UniversityPlugin()

        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Expecting value")
        mock_response.raise_for_status = Mock()
        mock_get = Mock(return_value=mock_response)
        monkeypatch.setattr(requests, "get", mock_get)

        result = plugin.get_universities_by_country("Canada")

        assert isinstance(result, UniversitySearchResult)
        assert result.message == "Unexpected error occurred"
        assert result.universities == []
        assert result.error is not None

    def test_search_universities_missing_required_fields(self, mock_requests_get):
        plugin = UniversityPlugin()

        api_data = [
            {
                "web_pages": ["http://example.edu"],
                "domains": ["example.edu"],
            }
        ]

        mock_response = Mock()
        mock_response.json.return_value = api_data
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        result = plugin.search_universities("Test")

        assert isinstance(result, UniversitySearchResult)
        assert len(result.universities) == 1
        uni = result.universities[0]
        assert uni.name == ""
        assert uni.country == ""
        assert uni.alpha_two_code == ""

    def test_search_universities_unexpected_data_types(self, mock_requests_get):
        plugin = UniversityPlugin()

        api_data = [
            {
                "name": "Test University",
                "web_pages": "not-a-list",
                "domains": "not-a-list",
                "country": "Test Country",
                "alpha_two_code": "TC",
            }
        ]

        mock_response = Mock()
        mock_response.json.return_value = api_data
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        result = plugin.search_universities("Test")

        assert isinstance(result, UniversitySearchResult)
        assert result.message == "Unexpected error occurred"
        assert result.universities == []
        assert result.error is not None

    def test_get_universities_by_country_non_list_response(self, mock_requests_get):
        plugin = UniversityPlugin()

        mock_response = Mock()
        mock_response.json.return_value = {"error": "Invalid request"}
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        result = plugin.get_universities_by_country("Invalid")

        assert isinstance(result, UniversitySearchResult)
        assert result.message == "Unexpected error occurred"
        assert result.universities == []
        assert result.error is not None

    def test_search_universities_null_response(self, mock_requests_get):
        plugin = UniversityPlugin()

        mock_response = Mock()
        mock_response.json.return_value = None
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        result = plugin.search_universities("Test")

        assert isinstance(result, UniversitySearchResult)
        assert "No universities found" in result.message
        assert result.universities == []
        assert result.error is None

    def test_get_universities_by_country_partial_data(self, mock_requests_get):
        plugin = UniversityPlugin()

        api_data = [
            {
                "name": "Partial University",
                "country": "Test Country",
                "alpha_two_code": "TC",
            }
        ]

        mock_response = Mock()
        mock_response.json.return_value = api_data
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        result = plugin.get_universities_by_country("Test")

        assert isinstance(result, UniversitySearchResult)
        assert len(result.universities) == 1
        uni = result.universities[0]
        assert uni.name == "Partial University"
        assert uni.web_pages == []
        assert uni.domains == []
