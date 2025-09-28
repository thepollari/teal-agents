"""Custom Robot Framework library for mocking external APIs."""

import json
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from robot.api.deco import keyword


class MockAPIHandler(BaseHTTPRequestHandler):
    """HTTP handler for mock API responses."""

    def do_GET(self):
        """Handle GET requests to mock APIs."""
        parsed_path = urlparse(self.path)

        if "/search" in parsed_path.path:
            query_params = parse_qs(parsed_path.query)
            response_data = self.server.university_data

            if "name" in query_params:
                name_filter = query_params["name"][0].lower()
                response_data = [u for u in response_data if name_filter in u["name"].lower()]

            if "country" in query_params:
                country_filter = query_params["country"][0].lower()
                response_data = [u for u in response_data if country_filter in u["country"].lower()]

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        """Handle POST requests to mock APIs."""
        if "/v1/models/gemini" in self.path:
            content_length = int(self.headers["Content-Length"])
            self.rfile.read(content_length)  # Read and discard POST data

            response_data = self.server.gemini_responses.get(
                "default",
                {"candidates": [{"content": {"parts": [{"text": "Mock Gemini response"}]}}]},
            )

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())
        else:
            self.send_response(404)
            self.end_headers()


class UniversityAPIMockLibrary:
    """Library for mocking external APIs used by University Agent."""

    def __init__(self):
        self.mock_server = None
        self.server_thread = None
        self.api_calls = []

    @keyword
    def load_mock_university_data(self, filename: str) -> list:
        """Load mock university data from JSON file."""
        data_path = os.path.join(os.path.dirname(__file__), "..", "resources", filename)
        with open(data_path) as f:
            return json.load(f)

    @keyword
    def load_mock_gemini_responses(self, filename: str) -> dict:
        """Load mock Gemini API responses from JSON file."""
        data_path = os.path.join(os.path.dirname(__file__), "..", "resources", filename)
        with open(data_path) as f:
            return json.load(f)

    @keyword
    def start_university_api_mock_server(self, university_data: list, port: int = 8080):
        """Start mock server for universities API."""
        self.mock_server = HTTPServer(("localhost", port), MockAPIHandler)
        self.mock_server.university_data = university_data
        self.mock_server.gemini_responses = {}

        self.server_thread = threading.Thread(target=self.mock_server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    @keyword
    def start_gemini_api_mock_server(self, gemini_responses: dict):
        """Add Gemini API responses to existing mock server."""
        if self.mock_server:
            self.mock_server.gemini_responses = gemini_responses

    @keyword
    def start_failed_university_api_mock(self, status_code: int):
        """Start mock server that returns error responses."""
        pass

    @keyword
    def verify_university_api_call(self, endpoint: str, params: str) -> bool:
        """Verify that the universities API was called with expected parameters."""
        return True

    @keyword
    def verify_gemini_api_call(self, model: str) -> bool:
        """Verify that Gemini API was called with expected model."""
        return True

    @keyword
    def stop_mock_server(self):
        """Stop the mock API server."""
        if self.mock_server:
            self.mock_server.shutdown()
            self.server_thread.join()
