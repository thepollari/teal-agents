# Testing Guide - Teal Agents Framework

This guide provides comprehensive testing strategies, patterns, and best practices for the Teal Agents Framework, covering unit tests, integration tests, performance testing, and validation procedures.

## Table of Contents

- [Testing Philosophy](#testing-philosophy)
- [Testing Environment Setup](#testing-environment-setup)
- [Unit Testing](#unit-testing)
- [Integration Testing](#integration-testing)
- [Configuration Testing](#configuration-testing)
- [Plugin Testing](#plugin-testing)
- [Performance Testing](#performance-testing)
- [End-to-End Testing](#end-to-end-testing)
- [Mocking Strategies](#mocking-strategies)
- [Continuous Integration](#continuous-integration)
- [Testing Best Practices](#testing-best-practices)

## Testing Philosophy

### Testing Pyramid for Teal Agents

The Teal Agents Framework follows a testing pyramid approach:

```
    /\
   /  \     E2E Tests (Few)
  /____\    - Full agent workflows
 /      \   - UI integration tests
/________\  - Production-like scenarios

Integration Tests (Some)
- Plugin integration
- API endpoint testing
- Configuration loading
- External service mocking

Unit Tests (Many)
- Plugin functions
- Utility functions
- Configuration validation
- Data model testing
```

### Testing Principles

1. **Fast Feedback**: Unit tests should run quickly and provide immediate feedback
2. **Isolation**: Tests should not depend on external services or other tests
3. **Repeatability**: Tests should produce consistent results across environments
4. **Clarity**: Test names and structure should clearly indicate what is being tested
5. **Coverage**: Aim for high test coverage while focusing on critical paths

## Testing Environment Setup

### Prerequisites

```bash
# Ensure testing dependencies are installed
cd src/sk-agents
uv sync --dev

# Verify pytest installation
uv run pytest --version

# Install additional testing tools
uv add --dev pytest-asyncio pytest-mock pytest-cov httpx
```

### Test Directory Structure

```
src/sk-agents/
├── tests/
│   ├── unit/
│   │   ├── test_plugins.py
│   │   ├── test_config.py
│   │   ├── test_utils.py
│   │   └── test_models.py
│   ├── integration/
│   │   ├── test_agent_endpoints.py
│   │   ├── test_plugin_integration.py
│   │   └── test_completion_factories.py
│   ├── e2e/
│   │   ├── test_agent_workflows.py
│   │   └── test_ui_integration.py
│   ├── fixtures/
│   │   ├── sample_configs/
│   │   ├── mock_responses/
│   │   └── test_data/
│   └── conftest.py  # Shared fixtures and configuration
```

### Test Configuration

```python
# conftest.py
import pytest
import tempfile
import os
from pathlib import Path
from ska_utils import AppConfig
from sk_agents.configs import TA_API_KEY, TA_SERVICE_CONFIG

@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration"""
    return {
        "api_key": "test_api_key",
        "base_url": "http://localhost:8000",
        "timeout": 30
    }

@pytest.fixture
def temp_config_file():
    """Create temporary configuration file for testing"""
    config_content = """
apiVersion: skagents/v1
kind: Sequential
description: Test agent
service_name: TestAgent
version: 0.1
input_type: BaseInput
spec:
  agents:
    - name: default
      role: Test Agent
      model: gpt-4o
      system_prompt: You are a test agent.
  tasks:
    - name: test_task
      description: Test task
      instructions: Perform test operations.
      agent: default
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    os.unlink(temp_path)

@pytest.fixture
def mock_app_config():
    """Mock AppConfig for testing"""
    AppConfig.reset()
    AppConfig.add_config(TA_API_KEY)
    AppConfig.add_config(TA_SERVICE_CONFIG)
    
    # Set test environment variables
    os.environ[TA_API_KEY.env_name] = "test_api_key"
    
    yield AppConfig()
    
    # Cleanup
    AppConfig.reset()
```

## Unit Testing

### Testing Plugin Functions

```python
# tests/unit/test_plugins.py
import pytest
import json
from unittest.mock import Mock, patch
from custom_plugins import YourCustomPlugin, YourDataModel

class TestYourCustomPlugin:
    """Test suite for YourCustomPlugin"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.plugin = YourCustomPlugin()
    
    def test_primary_function_success(self):
        """Test successful plugin function execution"""
        # Mock external API call
        with patch.object(self.plugin, '_call_external_api') as mock_api:
            mock_api.return_value = [
                {"id": "1", "name": "Test Item 1", "description": "Test description"},
                {"id": "2", "name": "Test Item 2", "description": "Another test"}
            ]
            
            result = self.plugin.primary_function("test query", limit=2)
            data = json.loads(result)
            
            # Assertions
            assert isinstance(data, list)
            assert len(data) == 2
            assert data[0]["id"] == "1"
            assert data[0]["name"] == "Test Item 1"
            
            # Verify API was called with correct parameters
            mock_api.assert_called_once_with("test query", 2, "all")
    
    def test_primary_function_empty_query(self):
        """Test plugin function with empty query"""
        result = self.plugin.primary_function("")
        data = json.loads(result)
        
        # Should handle empty query gracefully
        assert isinstance(data, (list, dict))
    
    def test_primary_function_api_error(self):
        """Test plugin function when API call fails"""
        with patch.object(self.plugin, '_call_external_api') as mock_api:
            mock_api.side_effect = Exception("API connection failed")
            
            result = self.plugin.primary_function("test query")
            data = json.loads(result)
            
            # Should return error information
            assert "error" in data
            assert "API connection failed" in data["error"]
            assert data["query"] == "test query"
    
    def test_secondary_function(self):
        """Test secondary plugin function"""
        with patch.object(self.plugin, '_process_input') as mock_process:
            mock_process.return_value = "processed_result"
            
            result = self.plugin.secondary_function("test input")
            data = json.loads(result)
            
            assert data["result"] == "processed_result"
            assert data["input"] == "test input"
    
    @pytest.mark.parametrize("query,limit,filter_type", [
        ("test", 5, "all"),
        ("another test", 10, "specific"),
        ("", 1, "all"),
    ])
    def test_primary_function_parameters(self, query, limit, filter_type):
        """Test plugin function with various parameter combinations"""
        with patch.object(self.plugin, '_call_external_api') as mock_api:
            mock_api.return_value = []
            
            self.plugin.primary_function(query, limit, filter_type)
            
            mock_api.assert_called_once_with(query, limit, filter_type)

class TestYourDataModel:
    """Test suite for Pydantic data models"""
    
    def test_valid_model_creation(self):
        """Test creating model with valid data"""
        data = {
            "id": "123",
            "name": "Test Name",
            "description": "Test description"
        }
        
        model = YourDataModel(**data)
        
        assert model.id == "123"
        assert model.name == "Test Name"
        assert model.description == "Test description"
    
    def test_model_with_optional_fields(self):
        """Test model creation with optional fields"""
        data = {"id": "123", "name": "Test Name"}
        
        model = YourDataModel(**data)
        
        assert model.id == "123"
        assert model.name == "Test Name"
        assert model.description is None
    
    def test_model_validation_error(self):
        """Test model validation with invalid data"""
        with pytest.raises(ValueError):
            YourDataModel(id="", name="")  # Empty required fields
    
    def test_model_serialization(self):
        """Test model serialization to dict"""
        data = {"id": "123", "name": "Test Name"}
        model = YourDataModel(**data)
        
        serialized = model.dict()
        
        assert serialized["id"] == "123"
        assert serialized["name"] == "Test Name"
        assert "description" in serialized
```

### Testing Utility Functions

```python
# tests/unit/test_utils.py
import pytest
from sk_agents.utils import docstring_parameter, get_sse_event_for_response
from sk_agents.ska_types import InvokeResponse, PartialResponse

class TestUtilityFunctions:
    """Test suite for utility functions"""
    
    def test_docstring_parameter(self):
        """Test docstring parameter replacement"""
        @docstring_parameter("Test Description")
        def test_function():
            """
            {0}
            
            This is a test function.
            """
            pass
        
        expected_docstring = "Test Description\n\nThis is a test function."
        assert test_function.__doc__.strip() == expected_docstring.strip()
    
    def test_get_sse_event_for_invoke_response(self):
        """Test SSE event generation for InvokeResponse"""
        response = InvokeResponse(
            output_raw="Test response",
            token_usage={"total_tokens": 10}
        )
        
        sse_event = get_sse_event_for_response(response)
        
        assert "data: " in sse_event
        assert "Test response" in sse_event
    
    def test_get_sse_event_for_partial_response(self):
        """Test SSE event generation for PartialResponse"""
        response = PartialResponse(output_partial="Partial response")
        
        sse_event = get_sse_event_for_response(response)
        
        assert "data: " in sse_event
        assert "Partial response" in sse_event
```

### Testing Configuration Loading

```python
# tests/unit/test_config.py
import pytest
import yaml
import tempfile
import os
from sk_agents.skagents import load_config
from sk_agents.ska_types import BaseConfig

class TestConfigurationLoading:
    """Test suite for configuration loading and validation"""
    
    def test_load_valid_config(self, temp_config_file):
        """Test loading a valid configuration file"""
        config = load_config(temp_config_file)
        
        assert isinstance(config, BaseConfig)
        assert config.apiVersion == "skagents/v1"
        assert config.kind == "Sequential"
        assert config.service_name == "TestAgent"
        assert len(config.spec.agents) == 1
        assert len(config.spec.tasks) == 1
    
    def test_load_invalid_yaml(self):
        """Test loading invalid YAML file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            invalid_file = f.name
        
        try:
            with pytest.raises(yaml.YAMLError):
                load_config(invalid_file)
        finally:
            os.unlink(invalid_file)
    
    def test_load_missing_required_fields(self):
        """Test loading config with missing required fields"""
        config_content = """
apiVersion: skagents/v1
# Missing kind, service_name, etc.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            invalid_file = f.name
        
        try:
            with pytest.raises(ValueError):
                load_config(invalid_file)
        finally:
            os.unlink(invalid_file)
    
    def test_config_validation(self):
        """Test configuration validation logic"""
        # Test with valid configuration data
        valid_config_data = {
            "apiVersion": "skagents/v1",
            "kind": "Sequential",
            "service_name": "TestAgent",
            "version": "0.1",
            "spec": {
                "agents": [
                    {
                        "name": "default",
                        "role": "Test Agent",
                        "model": "gpt-4o"
                    }
                ],
                "tasks": [
                    {
                        "name": "test_task",
                        "description": "Test task",
                        "agent": "default"
                    }
                ]
            }
        }
        
        config = BaseConfig(**valid_config_data)
        assert config.service_name == "TestAgent"
        assert len(config.spec.agents) == 1
```

## Integration Testing

### Testing API Endpoints

```python
# tests/integration/test_agent_endpoints.py
import pytest
import httpx
import asyncio
from fastapi.testclient import TestClient
from sk_agents.app import create_app

class TestAgentEndpoints:
    """Integration tests for agent API endpoints"""
    
    @pytest.fixture
    def client(self, temp_config_file, mock_app_config):
        """Create test client with mocked configuration"""
        os.environ["TA_SERVICE_CONFIG"] = temp_config_file
        app = create_app()
        return TestClient(app)
    
    def test_agent_card_endpoint(self, client):
        """Test agent card endpoint"""
        response = client.get("/.well-known/agent.json")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "description" in data
        assert "capabilities" in data
    
    def test_invoke_endpoint(self, client):
        """Test synchronous invoke endpoint"""
        payload = {
            "chat_history": [
                {"role": "user", "content": "Hello, test agent!"}
            ]
        }
        
        with patch('sk_agents.skagents.handle') as mock_handle:
            mock_response = InvokeResponse(
                output_raw="Hello! I'm a test agent.",
                token_usage={"total_tokens": 10}
            )
            mock_handle.return_value.invoke.return_value = mock_response
            
            response = client.post("/invoke", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert "output_raw" in data
            assert data["output_raw"] == "Hello! I'm a test agent."
    
    def test_sse_endpoint(self, client):
        """Test Server-Sent Events endpoint"""
        payload = {
            "chat_history": [
                {"role": "user", "content": "Stream a response"}
            ]
        }
        
        response = client.post("/sse", json=payload)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream"
    
    def test_websocket_endpoint(self, client):
        """Test WebSocket endpoint"""
        with client.websocket_connect("/stream") as websocket:
            # Send test data
            test_data = {
                "chat_history": [
                    {"role": "user", "content": "WebSocket test"}
                ]
            }
            websocket.send_json(test_data)
            
            # Should receive response (mocked)
            # Note: This requires proper mocking of the handler
    
    def test_invalid_payload(self, client):
        """Test endpoints with invalid payloads"""
        invalid_payload = {"invalid": "payload"}
        
        response = client.post("/invoke", json=invalid_payload)
        
        assert response.status_code == 422  # Validation error
    
    def test_endpoint_error_handling(self, client):
        """Test endpoint error handling"""
        payload = {
            "chat_history": [
                {"role": "user", "content": "Trigger error"}
            ]
        }
        
        with patch('sk_agents.skagents.handle') as mock_handle:
            mock_handle.side_effect = Exception("Test error")
            
            response = client.post("/invoke", json=payload)
            
            assert response.status_code == 500
```

## Performance Testing

### Load Testing

```python
# tests/performance/test_load.py
import asyncio
import aiohttp
import time
import pytest
from concurrent.futures import ThreadPoolExecutor

class TestAgentPerformance:
    """Performance tests for agent endpoints"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test agent performance under concurrent load"""
        
        test_payload = {
            "chat_history": [
                {"role": "user", "content": "Performance test query"}
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            # Test concurrent requests
            tasks = []
            start_time = time.time()
            
            for i in range(10):  # 10 concurrent requests
                task = asyncio.create_task(
                    self.make_request(session, test_payload)
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            # Analyze results
            successful = sum(1 for r in results if not isinstance(r, Exception))
            failed = len(results) - successful
            
            assert successful > 0, "No successful requests"
            assert failed < len(results) * 0.1, "Too many failed requests"
            
            total_time = end_time - start_time
            avg_time = total_time / len(results)
            
            # Performance assertions
            assert total_time < 30, "Total time too high"
            assert avg_time < 5, "Average response time too high"
    
    async def make_request(self, session, payload):
        """Make a single request to the agent"""
        async with session.post(
            "http://localhost:8000/invoke",
            json=payload,
            headers={"Content-Type": "application/json"}
        ) as response:
            return await response.json()
    
    def test_memory_usage(self):
        """Test memory usage during agent operations"""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Perform operations that might cause memory leaks
        for i in range(100):
            # Simulate agent operations
            pass
        
        gc.collect()  # Force garbage collection
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Assert memory increase is reasonable
        assert memory_increase < 100 * 1024 * 1024, "Memory usage increased too much"
```

## Mocking Strategies

### External API Mocking

```python
# tests/mocks/api_mocks.py
import json
from unittest.mock import Mock, patch
import httpx

class MockAPIResponse:
    """Mock HTTP response for testing"""
    
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
    
    def json(self):
        return self.json_data
    
    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"HTTP {self.status_code}",
                request=Mock(),
                response=self
            )

@pytest.fixture
def mock_external_api():
    """Mock external API calls"""
    with patch('httpx.Client') as mock_client:
        mock_response = MockAPIResponse([
            {"id": "1", "name": "Test University", "country": "Test Country"}
        ])
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response
        yield mock_client

def test_plugin_with_mocked_api(mock_external_api):
    """Test plugin with mocked external API"""
    from custom_plugins import UniversityPlugin
    
    plugin = UniversityPlugin()
    result = plugin.search_universities("test")
    
    data = json.loads(result)
    assert len(data) == 1
    assert data[0]["name"] == "Test University"
```

## Continuous Integration

### GitHub Actions Configuration

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.13]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install uv
      run: curl -LsSf https://astral.sh/uv/install.sh | sh
    
    - name: Install dependencies
      run: |
        cd src/sk-agents
        uv sync --dev
    
    - name: Run linting
      run: |
        cd src/sk-agents
        uv run ruff check .
    
    - name: Run type checking
      run: |
        cd src/sk-agents
        uv run mypy src/
    
    - name: Run tests
      run: |
        cd src/sk-agents
        uv run pytest tests/ -v --cov=sk_agents --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./src/sk-agents/coverage.xml
```

## Testing Best Practices

### Test Organization

1. **Clear Test Names**: Use descriptive names that explain what is being tested
2. **Arrange-Act-Assert**: Structure tests with clear setup, execution, and verification
3. **One Assertion Per Test**: Focus each test on a single behavior
4. **Test Data Management**: Use fixtures and factories for consistent test data

### Mocking Guidelines

1. **Mock External Dependencies**: Always mock external APIs and services
2. **Mock at the Right Level**: Mock at the boundary of your system
3. **Verify Mock Interactions**: Assert that mocks are called correctly
4. **Reset Mocks**: Clean up mocks between tests

### Performance Testing

1. **Baseline Measurements**: Establish performance baselines
2. **Realistic Load**: Test with realistic user loads and data
3. **Resource Monitoring**: Monitor CPU, memory, and network usage
4. **Regression Detection**: Detect performance regressions early

### Test Maintenance

1. **Regular Review**: Review and update tests regularly
2. **Remove Obsolete Tests**: Remove tests for deprecated functionality
3. **Refactor Test Code**: Keep test code clean and maintainable
4. **Documentation**: Document complex test scenarios

## Running Tests

### Local Testing

```bash
# Run all tests
cd src/sk-agents
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_plugins.py

# Run with coverage
uv run pytest --cov=sk_agents --cov-report=html

# Run performance tests
uv run pytest tests/performance/ -m performance

# Run with specific markers
uv run pytest -m "not slow"
```

### Test Configuration

```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    performance: marks tests as performance tests
    unit: marks tests as unit tests
addopts = 
    --strict-markers
    --disable-warnings
    --tb=short
```

---

**Last Updated**: [Current Date]
**Version**: 1.0
**Maintainer**: Teal Agents Development Team
