# Teal Agents Framework - Testing Guide

## Overview

This guide provides comprehensive testing strategies and best practices for the Teal Agents Framework. It covers unit testing, integration testing, mocking strategies, and debugging techniques to ensure robust and reliable agent implementations.

## Testing Philosophy

The Teal Agents Framework follows a multi-layered testing approach:

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions and workflows
3. **End-to-End Tests**: Test complete agent functionality
4. **Performance Tests**: Validate performance under load
5. **Security Tests**: Ensure proper authentication and authorization

## Test Structure and Organization

### Directory Structure
```
src/sk-agents/
├── tests/                          # Main test directory
│   ├── __init__.py
│   ├── conftest.py                 # Pytest configuration and fixtures
│   ├── test_app.py                 # Application-level tests
│   ├── test_agent_handler.py       # Agent handler tests
│   ├── test_plugin_loader.py       # Plugin loading tests
│   ├── test_routes.py              # API route tests
│   ├── custom/                     # Custom test utilities
│   │   └── mock_chat_completion_factory.py
│   └── fixtures/                   # Test data and fixtures
│       ├── configs/                # Test configuration files
│       └── data/                   # Test data files
├── plugins/                        # Plugin implementations
└── agents/                         # Agent configurations
```

### Test Categories

#### 1. Framework Core Tests
- **App routing and version selection**
- **Configuration parsing and validation**
- **Plugin loading and initialization**
- **Type loading and custom types**
- **State management (Redis, in-memory)**

#### 2. Agent Handler Tests
- **Agent execution workflows**
- **Input/output processing**
- **Streaming response handling**
- **Error handling and recovery**

#### 3. Plugin Tests
- **Plugin functionality**
- **External API integration**
- **Error handling**
- **Performance characteristics**

#### 4. Integration Tests
- **Complete agent workflows**
- **Multi-component interactions**
- **Real API integrations**
- **Orchestrator functionality**

## Testing Tools and Setup

### Required Dependencies
```toml
# pyproject.toml - Testing dependencies
[tool.uv.dev-dependencies]
pytest = "^8.0.0"
pytest-asyncio = "^0.23.0"
pytest-cov = "^4.0.0"
pytest-mock = "^3.12.0"
httpx = "^0.27.0"
respx = "^0.20.0"  # HTTP mocking
fakeredis = "^2.20.0"  # Redis mocking
```

### Pytest Configuration
```python
# conftest.py
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient
from ska_utils import AppConfig
from sk_agents.app import app

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)

@pytest.fixture
def mock_app_config():
    """Create a mock AppConfig for testing."""
    config = Mock(spec=AppConfig)
    config.get.return_value = "test_value"
    return config

@pytest.fixture
def sample_chat_history():
    """Sample chat history for testing."""
    return [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
        {"role": "user", "content": "How are you?"}
    ]

@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    import fakeredis
    return fakeredis.FakeRedis()
```

## Unit Testing Patterns

### Testing Agent Handlers

```python
# tests/test_agent_handler.py
import pytest
from unittest.mock import Mock, patch, AsyncMock
from sk_agents.skagents.v1.agent_builder import AgentBuilder
from sk_agents.ska_types import BaseConfig, BaseInput

class TestAgentHandler:
    
    @pytest.fixture
    def mock_config(self):
        """Mock agent configuration."""
        config = Mock(spec=BaseConfig)
        config.apiVersion = "skagents/v1"
        config.service_name = "TestAgent"
        config.version = "1.0"
        config.spec = Mock()
        config.spec.model = "gpt-4o"
        config.spec.system_prompt = "You are a test agent"
        config.spec.plugins = []
        return config
    
    @pytest.fixture
    def mock_app_config(self):
        """Mock application configuration."""
        app_config = Mock()
        app_config.get.return_value = "mock_value"
        return app_config
    
    def test_agent_builder_initialization(self, mock_config, mock_app_config):
        """Test agent builder initialization."""
        builder = AgentBuilder(mock_config, mock_app_config)
        assert builder.config == mock_config
        assert builder.app_config == mock_app_config
    
    @patch('sk_agents.skagents.kernel_builder.KernelBuilder')
    async def test_agent_invoke(self, mock_kernel_builder, mock_config, mock_app_config):
        """Test agent invocation."""
        # Setup mocks
        mock_kernel = Mock()
        mock_kernel_builder.return_value.build.return_value = mock_kernel
        mock_kernel.invoke_async.return_value = Mock(value="Test response")
        
        # Create agent handler
        builder = AgentBuilder(mock_config, mock_app_config)
        handler = builder.build()
        
        # Test invocation
        input_data = {"chat_history": [{"role": "user", "content": "Hello"}]}
        result = await handler.invoke(input_data)
        
        assert result is not None
        assert hasattr(result, 'output_raw')
    
    @patch('sk_agents.skagents.kernel_builder.KernelBuilder')
    async def test_agent_streaming(self, mock_kernel_builder, mock_config, mock_app_config):
        """Test agent streaming functionality."""
        # Setup streaming mock
        async def mock_stream():
            yield "Partial response 1"
            yield "Partial response 2"
            yield "Final response"
        
        mock_kernel = Mock()
        mock_kernel_builder.return_value.build.return_value = mock_kernel
        mock_kernel.invoke_stream_async.return_value = mock_stream()
        
        # Create agent handler
        builder = AgentBuilder(mock_config, mock_app_config)
        handler = builder.build()
        
        # Test streaming
        input_data = {"chat_history": [{"role": "user", "content": "Hello"}]}
        responses = []
        async for response in handler.invoke_stream(input_data):
            responses.append(response)
        
        assert len(responses) > 0
        assert any("response" in str(r) for r in responses)
```

### Testing Plugins

```python
# tests/test_custom_plugin.py
import pytest
from unittest.mock import Mock, patch
import httpx
from plugins.my_custom_plugin import MyCustomPlugin

class TestMyCustomPlugin:
    
    @pytest.fixture
    def plugin(self):
        """Create plugin instance for testing."""
        return MyCustomPlugin(authorization="test-token")
    
    def test_plugin_initialization(self, plugin):
        """Test plugin initialization."""
        assert plugin.authorization == "test-token"
        assert hasattr(plugin, 'api_base_url')
    
    @patch('httpx.Client')
    def test_fetch_data_success(self, mock_client, plugin):
        """Test successful data fetching."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.json.return_value = {"result": "test data", "status": "success"}
        mock_response.raise_for_status.return_value = None
        
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response
        
        # Test the function
        result = plugin.fetch_data("test query")
        
        assert result == {"result": "test data", "status": "success"}
        mock_client.return_value.__enter__.return_value.get.assert_called_once()
    
    @patch('httpx.Client')
    def test_fetch_data_http_error(self, mock_client, plugin):
        """Test HTTP error handling."""
        # Mock HTTP error
        mock_client.return_value.__enter__.return_value.get.side_effect = httpx.HTTPError("Connection failed")
        
        # Test error handling
        result = plugin.fetch_data("test query")
        
        assert "Error fetching data" in result
        assert "Connection failed" in result
    
    @patch('httpx.Client')
    def test_fetch_data_timeout(self, mock_client, plugin):
        """Test timeout handling."""
        # Mock timeout
        mock_client.return_value.__enter__.return_value.get.side_effect = httpx.TimeoutException("Request timeout")
        
        result = plugin.fetch_data("test query")
        
        assert "Error fetching data" in result
        assert "timeout" in result.lower()
    
    def test_validate_input_success(self, plugin):
        """Test input validation success."""
        result = plugin.validate_input("Valid Input Data")
        
        assert "Validated data: valid input data" in result
    
    def test_validate_input_empty(self, plugin):
        """Test empty input validation."""
        result = plugin.validate_input("")
        
        assert "Error: Empty input provided" in result
    
    def test_validate_input_whitespace(self, plugin):
        """Test whitespace-only input validation."""
        result = plugin.validate_input("   ")
        
        assert "Error: Empty input provided" in result
```

### Testing Configuration Loading

```python
# tests/test_config_loading.py
import pytest
import tempfile
import yaml
from pathlib import Path
from pydantic_yaml import parse_yaml_file_as
from sk_agents.ska_types import BaseConfig

class TestConfigLoading:
    
    @pytest.fixture
    def sample_config_data(self):
        """Sample configuration data."""
        return {
            "apiVersion": "skagents/v1",
            "kind": "Agent",
            "service_name": "TestAgent",
            "version": "1.0",
            "description": "Test agent configuration",
            "spec": {
                "model": "gpt-4o",
                "system_prompt": "You are a test agent",
                "plugins": ["TestPlugin"],
                "max_tokens": 1000
            }
        }
    
    def test_valid_config_parsing(self, sample_config_data):
        """Test parsing valid configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(sample_config_data, f)
            config_path = f.name
        
        try:
            config = parse_yaml_file_as(BaseConfig, config_path)
            assert config.apiVersion == "skagents/v1"
            assert config.service_name == "TestAgent"
            assert config.version == "1.0"
            assert config.spec.model == "gpt-4o"
        finally:
            Path(config_path).unlink()
    
    def test_invalid_config_parsing(self):
        """Test parsing invalid configuration."""
        invalid_config = {
            "apiVersion": "invalid/version",
            "kind": "InvalidKind"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(invalid_config, f)
            config_path = f.name
        
        try:
            with pytest.raises(Exception):
                parse_yaml_file_as(BaseConfig, config_path)
        finally:
            Path(config_path).unlink()
    
    def test_missing_required_fields(self):
        """Test configuration with missing required fields."""
        incomplete_config = {
            "apiVersion": "skagents/v1"
            # Missing required fields
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(incomplete_config, f)
            config_path = f.name
        
        try:
            with pytest.raises(Exception):
                parse_yaml_file_as(BaseConfig, config_path)
        finally:
            Path(config_path).unlink()
```

## Integration Testing

### Testing Complete Agent Workflows

```python
# tests/test_agent_integration.py
import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from sk_agents.app import app

class TestAgentIntegration:
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_environment(self):
        """Mock environment variables."""
        with patch.dict('os.environ', {
            'TA_SERVICE_CONFIG': 'tests/fixtures/configs/test_agent.yaml',
            'OPENAI_API_KEY': 'test-key'
        }):
            yield
    
    def test_agent_basic_interaction(self, client, mock_environment):
        """Test basic agent interaction."""
        response = client.post(
            "/TestAgent/1.0/",
            json={
                "chat_history": [
                    {"role": "user", "content": "Hello, test agent!"}
                ]
            }
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "output_raw" in result or "response" in result
    
    def test_agent_with_plugins(self, client, mock_environment):
        """Test agent with plugin functionality."""
        with patch('plugins.test_plugin.TestPlugin.test_function') as mock_plugin:
            mock_plugin.return_value = "Plugin response"
            
            response = client.post(
                "/TestAgent/1.0/",
                json={
                    "chat_history": [
                        {"role": "user", "content": "Use the test function"}
                    ]
                }
            )
            
            assert response.status_code == 200
            result = response.json()
            # Verify plugin was called
            mock_plugin.assert_called()
    
    def test_agent_error_handling(self, client, mock_environment):
        """Test agent error handling."""
        # Test with invalid input
        response = client.post(
            "/TestAgent/1.0/",
            json={"invalid": "data"}
        )
        
        assert response.status_code in [400, 422]  # Bad request or validation error
    
    def test_agent_streaming(self, client, mock_environment):
        """Test agent streaming functionality."""
        # Note: WebSocket testing requires additional setup
        # This is a placeholder for streaming tests
        pass
```

### Testing Multi-Modal Agents

```python
# tests/test_multimodal_integration.py
import pytest
import base64
from fastapi.testclient import TestClient
from sk_agents.app import app

class TestMultiModalIntegration:
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def sample_image_base64(self):
        """Create a small test image in base64 format."""
        # Create a minimal PNG image (1x1 pixel)
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
        return base64.b64encode(png_data).decode('utf-8')
    
    def test_multimodal_text_and_image(self, client, sample_image_base64):
        """Test agent with both text and image inputs."""
        response = client.post(
            "/MultiModalAgent/1.0/",
            json={
                "chat_history": [
                    {
                        "role": "user",
                        "items": [
                            {"content_type": "text", "content": "What do you see in this image?"},
                            {"content_type": "image", "content": sample_image_base64}
                        ]
                    }
                ]
            }
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "output_raw" in result
    
    def test_embedded_image_type(self, client, sample_image_base64):
        """Test embedded image custom type."""
        response = client.post(
            "/MultiModalAgent/1.0/",
            json={
                "embedded_image": {
                    "format": "png",
                    "data": sample_image_base64
                }
            }
        )
        
        assert response.status_code == 200
```

## Mocking Strategies

### Mocking External APIs

```python
# tests/test_external_api_mocking.py
import pytest
import httpx
import respx
from plugins.weather_plugin import WeatherPlugin

class TestExternalAPIMocking:
    
    @pytest.fixture
    def weather_plugin(self):
        return WeatherPlugin(authorization="test-api-key")
    
    @respx.mock
    def test_weather_api_success(self, weather_plugin):
        """Test successful weather API call."""
        # Mock the external API
        respx.get("https://api.weather.com/current").mock(
            return_value=httpx.Response(
                200,
                json={
                    "temperature": 72,
                    "condition": "sunny",
                    "location": "New York"
                }
            )
        )
        
        result = weather_plugin.get_weather("New York")
        
        assert "72" in result
        assert "sunny" in result
    
    @respx.mock
    def test_weather_api_error(self, weather_plugin):
        """Test weather API error handling."""
        # Mock API error
        respx.get("https://api.weather.com/current").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
        
        result = weather_plugin.get_weather("Invalid City")
        
        assert "error" in result.lower()
```

### Mocking Chat Completion Services

```python
# tests/custom/mock_chat_completion_factory.py
from typing import List
from unittest.mock import Mock, AsyncMock
from ska_utils import Config
from sk_agents.ska_types import ChatCompletionFactory, ModelType
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase

class MockChatCompletionFactory(ChatCompletionFactory):
    """Mock chat completion factory for testing."""
    
    @staticmethod
    def get_configs() -> List[Config]:
        return []
    
    def get_chat_completion_for_model_name(
        self, model_name: str, service_id: str
    ) -> ChatCompletionClientBase:
        """Return mock chat completion client."""
        mock_client = Mock(spec=ChatCompletionClientBase)
        
        # Mock async methods
        mock_client.get_chat_message_contents_async = AsyncMock()
        mock_client.get_streaming_chat_message_contents_async = AsyncMock()
        
        # Configure mock responses
        mock_response = Mock()
        mock_response.content = "Mock response from test model"
        mock_client.get_chat_message_contents_async.return_value = [mock_response]
        
        # Configure streaming mock
        async def mock_stream():
            yield Mock(content="Mock ")
            yield Mock(content="streaming ")
            yield Mock(content="response")
        
        mock_client.get_streaming_chat_message_contents_async.return_value = mock_stream()
        
        return mock_client
    
    def get_model_type_for_name(self, model_name: str) -> ModelType:
        return ModelType.OPENAI
    
    def model_supports_structured_output(self, model_name: str) -> bool:
        return True
```

### Mocking State Management

```python
# tests/test_state_management.py
import pytest
from unittest.mock import Mock, AsyncMock
import fakeredis
from sk_agents.state import RedisStateManager, InMemoryStateManager

class TestStateManagement:
    
    @pytest.fixture
    def mock_redis(self):
        """Create fake Redis instance."""
        return fakeredis.FakeRedis()
    
    @pytest.fixture
    def redis_state_manager(self, mock_redis):
        """Create Redis state manager with fake Redis."""
        return RedisStateManager(redis_client=mock_redis)
    
    @pytest.fixture
    def memory_state_manager(self):
        """Create in-memory state manager."""
        return InMemoryStateManager()
    
    async def test_redis_state_storage(self, redis_state_manager):
        """Test Redis state storage."""
        session_id = "test-session-123"
        state_data = {"key": "value", "count": 42}
        
        # Store state
        await redis_state_manager.set_state(session_id, state_data)
        
        # Retrieve state
        retrieved_state = await redis_state_manager.get_state(session_id)
        
        assert retrieved_state == state_data
    
    async def test_memory_state_storage(self, memory_state_manager):
        """Test in-memory state storage."""
        session_id = "test-session-456"
        state_data = {"user": "test_user", "preferences": ["pref1", "pref2"]}
        
        # Store state
        await memory_state_manager.set_state(session_id, state_data)
        
        # Retrieve state
        retrieved_state = await memory_state_manager.get_state(session_id)
        
        assert retrieved_state == state_data
    
    async def test_state_expiration(self, redis_state_manager):
        """Test state expiration."""
        session_id = "expiring-session"
        state_data = {"temp": "data"}
        
        # Store with short TTL
        await redis_state_manager.set_state(session_id, state_data, ttl=1)
        
        # Should exist immediately
        state = await redis_state_manager.get_state(session_id)
        assert state == state_data
        
        # Wait for expiration (in real tests, you might mock time)
        import asyncio
        await asyncio.sleep(2)
        
        # Should be expired
        expired_state = await redis_state_manager.get_state(session_id)
        assert expired_state is None
```

## Performance Testing

### Load Testing

```python
# tests/test_performance.py
import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from sk_agents.app import app

class TestPerformance:
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_concurrent_requests(self, client):
        """Test handling concurrent requests."""
        def make_request():
            response = client.post(
                "/TestAgent/1.0/",
                json={
                    "chat_history": [
                        {"role": "user", "content": "Quick test"}
                    ]
                }
            )
            return response.status_code
        
        # Make 10 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in futures]
        
        # All requests should succeed
        assert all(status == 200 for status in results)
    
    def test_response_time(self, client):
        """Test response time is within acceptable limits."""
        start_time = time.time()
        
        response = client.post(
            "/TestAgent/1.0/",
            json={
                "chat_history": [
                    {"role": "user", "content": "Performance test"}
                ]
            }
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 5.0  # Should respond within 5 seconds
    
    async def test_memory_usage(self):
        """Test memory usage doesn't grow excessively."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Simulate multiple agent interactions
        for _ in range(100):
            # Simulate agent processing
            await asyncio.sleep(0.01)
        
        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be reasonable (less than 100MB)
        assert memory_growth < 100 * 1024 * 1024
```

## Security Testing

### Authentication Testing

```python
# tests/test_security.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from sk_agents.app import app

class TestSecurity:
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_unauthorized_access(self, client):
        """Test that unauthorized requests are rejected."""
        # Assuming authentication is enabled
        response = client.post(
            "/SecureAgent/1.0/",
            json={"chat_history": [{"role": "user", "content": "test"}]}
        )
        
        # Should require authentication
        assert response.status_code in [401, 403]
    
    def test_invalid_token(self, client):
        """Test invalid authentication token."""
        response = client.post(
            "/SecureAgent/1.0/",
            headers={"Authorization": "Bearer invalid-token"},
            json={"chat_history": [{"role": "user", "content": "test"}]}
        )
        
        assert response.status_code in [401, 403]
    
    def test_input_validation(self, client):
        """Test input validation and sanitization."""
        # Test with malicious input
        malicious_inputs = [
            {"chat_history": [{"role": "user", "content": "<script>alert('xss')</script>"}]},
            {"chat_history": [{"role": "user", "content": "'; DROP TABLE users; --"}]},
            {"chat_history": [{"role": "user", "content": "A" * 10000}]}  # Very long input
        ]
        
        for malicious_input in malicious_inputs:
            response = client.post("/TestAgent/1.0/", json=malicious_input)
            # Should either reject or sanitize the input
            assert response.status_code in [200, 400, 422]
            
            if response.status_code == 200:
                # If accepted, response should not contain malicious content
                result = response.json()
                response_text = str(result)
                assert "<script>" not in response_text
                assert "DROP TABLE" not in response_text
```

## Debugging and Troubleshooting

### Debug Utilities

```python
# tests/debug_utils.py
import logging
import json
from typing import Any, Dict

def setup_debug_logging():
    """Set up detailed logging for debugging."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Enable specific loggers
    logging.getLogger('sk_agents').setLevel(logging.DEBUG)
    logging.getLogger('httpx').setLevel(logging.DEBUG)

def print_request_response(request_data: Dict[str, Any], response_data: Dict[str, Any]):
    """Print formatted request and response for debugging."""
    print("\n" + "="*50)
    print("REQUEST:")
    print(json.dumps(request_data, indent=2))
    print("\nRESPONSE:")
    print(json.dumps(response_data, indent=2))
    print("="*50 + "\n")

def debug_agent_state(agent_handler):
    """Print agent handler state for debugging."""
    print(f"Agent Config: {agent_handler.config}")
    print(f"App Config: {agent_handler.app_config}")
    print(f"Plugins: {getattr(agent_handler, 'plugins', 'None')}")
```

### Common Test Patterns

```python
# tests/test_common_patterns.py
import pytest
from unittest.mock import Mock, patch, AsyncMock

class TestCommonPatterns:
    
    def test_retry_logic(self):
        """Test retry logic in plugins."""
        with patch('httpx.Client.get') as mock_get:
            # First call fails, second succeeds
            mock_get.side_effect = [
                httpx.HTTPError("Temporary failure"),
                Mock(json=lambda: {"result": "success"})
            ]
            
            plugin = RetryablePlugin()
            result = plugin.api_call_with_retry("test")
            
            assert result == {"result": "success"}
            assert mock_get.call_count == 2
    
    def test_circuit_breaker(self):
        """Test circuit breaker pattern."""
        plugin = CircuitBreakerPlugin()
        
        # Simulate multiple failures to trip circuit breaker
        for _ in range(5):
            with patch('httpx.Client.get', side_effect=httpx.HTTPError("Service down")):
                result = plugin.protected_api_call("test")
                assert "error" in result.lower()
        
        # Circuit should be open now
        with patch('httpx.Client.get') as mock_get:
            result = plugin.protected_api_call("test")
            # Should not make actual call due to open circuit
            mock_get.assert_not_called()
            assert "circuit breaker" in result.lower()
    
    async def test_async_plugin_methods(self):
        """Test asynchronous plugin methods."""
        plugin = AsyncPlugin()
        
        with patch.object(plugin, '_async_api_call', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = "async result"
            
            result = await plugin.async_function("test input")
            
            assert result == "async result"
            mock_call.assert_called_once_with("test input")
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
cd src/sk-agents
uv run pytest

# Run specific test file
uv run pytest tests/test_agent_handler.py

# Run tests with specific pattern
uv run pytest -k "test_plugin"

# Run tests with verbose output
uv run pytest -v

# Run tests with coverage
uv run pytest --cov=sk_agents --cov-report=html

# Run tests in parallel
uv run pytest -n auto
```

### Test Configuration

```bash
# Run tests with specific environment
export TA_SERVICE_CONFIG=tests/fixtures/configs/test_config.yaml
export OPENAI_API_KEY=test-key
uv run pytest

# Run only unit tests
uv run pytest tests/ -m "not integration"

# Run only integration tests
uv run pytest tests/ -m integration

# Run tests with specific log level
uv run pytest --log-cli-level=DEBUG
```

### Continuous Integration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.11, 3.12, 3.13]
    
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install uv
      run: pip install uv
    
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
        uv run mypy src/sk_agents
    
    - name: Run tests
      run: |
        cd src/sk-agents
        uv run pytest --cov=sk_agents --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./src/sk-agents/coverage.xml
```

## Best Practices

### Test Organization
1. **Group related tests**: Use classes to group related test methods
2. **Use descriptive names**: Test names should clearly describe what they test
3. **Follow AAA pattern**: Arrange, Act, Assert
4. **One assertion per test**: Focus each test on a single behavior
5. **Use fixtures**: Share common setup code using pytest fixtures

### Mocking Guidelines
1. **Mock external dependencies**: Don't make real API calls in tests
2. **Mock at the right level**: Mock at the boundary of your system
3. **Verify interactions**: Assert that mocks were called correctly
4. **Use realistic data**: Mock responses should match real API responses
5. **Test error conditions**: Mock failures and edge cases

### Performance Considerations
1. **Fast tests**: Unit tests should run quickly (< 1 second each)
2. **Parallel execution**: Use pytest-xdist for parallel test execution
3. **Selective testing**: Use markers to run subsets of tests
4. **Resource cleanup**: Ensure tests clean up resources properly
5. **Avoid test interdependence**: Tests should be independent

### Security Testing
1. **Test authentication**: Verify auth requirements are enforced
2. **Input validation**: Test with malicious and edge case inputs
3. **Authorization**: Test that users can only access allowed resources
4. **Data sanitization**: Verify outputs don't contain sensitive data
5. **Rate limiting**: Test that rate limits are enforced

## Troubleshooting Common Issues

### Test Environment Issues
```bash
# Clear pytest cache
rm -rf .pytest_cache

# Reinstall dependencies
uv sync --dev

# Check Python path
python -c "import sys; print(sys.path)"
```

### Mock Issues
```python
# Reset mocks between tests
@pytest.fixture(autouse=True)
def reset_mocks():
    yield
    # Reset any global mocks here
```

### Async Test Issues
```python
# Ensure proper async test setup
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

### Configuration Issues
```python
# Use temporary config files
@pytest.fixture
def temp_config():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as f:
        yaml.dump(config_data, f)
        yield f.name
```

## Additional Resources

- **[Developer Guide](DEVELOPER_GUIDE.md)**: Development environment setup
- **[Agent Development Guide](AGENT_DEVELOPMENT.md)**: Creating new agents
- **[Demo Examples](src/sk-agents/docs/demos/README.md)**: Learning from examples
- **[University Agent Tests](src/orchestrators/assistant-orchestrator/example/university/)**: Real-world testing examples
- **[Pytest Documentation](https://docs.pytest.org/)**: Comprehensive pytest guide
- **[FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)**: FastAPI-specific testing patterns

For questions about testing strategies or debugging specific issues, please create an issue on GitHub with the `testing` label.
