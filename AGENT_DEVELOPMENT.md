# Teal Agents Framework - Agent Development Guide

## Overview

This guide provides step-by-step instructions for creating new agents using the Teal Agents Framework. Whether you're building a simple chat agent or a complex multi-modal assistant, this guide will walk you through the entire development process.

## Agent Development Workflow

### Phase 1: Planning and Design

#### 1. Define Agent Purpose
Before writing any code, clearly define:
- **Primary function**: What specific task will your agent perform?
- **Target users**: Who will interact with your agent?
- **Input/output types**: What data will your agent receive and return?
- **Required capabilities**: Plugins, multi-modal support, state management?

#### 2. Choose Agent Architecture
Select the appropriate agent version based on your requirements:

| Agent Version | Use Case | Key Features |
|---------------|----------|--------------|
| **AppV1** (`skagents/v1`) | Simple, stateless agents | Custom types, basic REST/WebSocket |
| **AppV2** (`skagents/v2alpha1`) | Multi-modal, collaborative agents | Image inputs, A2A communication, Redis state |
| **AppV3** (`tealagents/v1alpha1`) | Production chat applications | Authentication, sessions, persistent state |

#### 3. Plan Plugin Requirements
Identify external integrations needed:
- **APIs**: Weather, search, databases, etc.
- **Data sources**: Files, databases, web scraping
- **Processing tools**: Image analysis, document parsing
- **Communication**: Email, Slack, webhooks

### Phase 2: Environment Setup

#### 1. Set Up Development Environment
```bash
# Navigate to framework directory
cd src/sk-agents

# Install dependencies
uv sync --dev

# Create agent directory
mkdir -p agents/my-agent
cd agents/my-agent
```

#### 2. Create Agent Configuration
Create `config.yaml` with your agent specification:

```yaml
# Basic Agent (AppV1)
apiVersion: skagents/v1
kind: Agent
service_name: MyAgent
version: 1.0
description: "My custom agent description"
input_type: BaseInput  # or custom type
output_type: null      # or custom type
spec:
  model: gpt-4o
  system_prompt: |
    You are a helpful assistant that...
  plugins:
    - MyCustomPlugin
  max_tokens: 1000
```

```yaml
# Multi-modal Agent (AppV2)
apiVersion: skagents/v2alpha1
kind: Agent
name: MyMultiModalAgent
version: 1.0
metadata:
  description: "Agent that processes text and images"
  skills:
    - id: "image_analysis"
      name: "Image Analysis"
      description: "Analyze and describe images"
      input_modes: ["text", "image"]
      output_modes: ["text"]
spec:
  model: gpt-4o
  system_prompt: |
    You can analyze both text and images...
  plugins:
    - ImageProcessingPlugin
```

```yaml
# Stateful Agent (AppV3)
apiVersion: tealagents/v1alpha1
kind: Agent
name: MyStatefulAgent
version: 1.0
metadata:
  description: "Agent with persistent conversations"
  skills:
    - id: "conversation"
      name: "Conversational AI"
      description: "Maintain context across sessions"
spec:
  model: gpt-4o
  system_prompt: |
    You maintain conversation history and user context...
  plugins:
    - UserContextPlugin
```

### Phase 3: Plugin Development

#### 1. Create Plugin Structure
```bash
# Create plugin file
touch plugins/my_custom_plugin.py
```

#### 2. Implement Plugin Class
```python
# plugins/my_custom_plugin.py
from typing import Optional
from sk_agents.ska_types import BasePlugin
from semantic_kernel import kernel_function
import httpx
import logging

logger = logging.getLogger(__name__)

class MyCustomPlugin(BasePlugin):
    """Custom plugin for specific functionality."""
    
    def __init__(self, authorization: Optional[str] = None):
        super().__init__(authorization)
        self.api_base_url = "https://api.example.com"
    
    @kernel_function(
        description="Fetch data from external API",
        name="fetch_data"
    )
    def fetch_data(self, query: str) -> str:
        """
        Fetch data from external API based on query.
        
        Args:
            query: Search query or identifier
            
        Returns:
            JSON string with API response data
        """
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.api_base_url}/search",
                    params={"q": query},
                    headers={"Authorization": f"Bearer {self.authorization}"}
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"API request failed: {e}")
            return f"Error fetching data: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return f"Unexpected error: {str(e)}"
    
    @kernel_function(
        description="Process and validate input data",
        name="validate_input"
    )
    def validate_input(self, data: str) -> str:
        """
        Validate and process input data.
        
        Args:
            data: Raw input data to validate
            
        Returns:
            Validation result and processed data
        """
        if not data or len(data.strip()) == 0:
            return "Error: Empty input provided"
        
        # Add your validation logic here
        processed_data = data.strip().lower()
        
        return f"Validated data: {processed_data}"
```

#### 3. Advanced Plugin Patterns

##### Plugin with Configuration
```python
class ConfigurablePlugin(BasePlugin):
    def __init__(self, authorization: Optional[str] = None, config: dict = None):
        super().__init__(authorization)
        self.config = config or {}
        self.api_key = self.config.get('api_key')
        self.base_url = self.config.get('base_url', 'https://api.default.com')
```

##### Plugin with State Management
```python
class StatefulPlugin(BasePlugin):
    def __init__(self, authorization: Optional[str] = None):
        super().__init__(authorization)
        self.cache = {}
    
    @kernel_function(description="Store data in plugin cache")
    def store_data(self, key: str, value: str) -> str:
        self.cache[key] = value
        return f"Stored {key}: {value}"
    
    @kernel_function(description="Retrieve data from plugin cache")
    def get_data(self, key: str) -> str:
        return self.cache.get(key, "Key not found")
```

##### Plugin with Error Handling
```python
class RobustPlugin(BasePlugin):
    @kernel_function(description="Robust API call with retry logic")
    def robust_api_call(self, endpoint: str) -> str:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # API call logic
                return self._make_api_call(endpoint)
            except httpx.TimeoutException:
                if attempt == max_retries - 1:
                    return "Error: API timeout after retries"
                time.sleep(2 ** attempt)  # Exponential backoff
            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500:
                    # Retry on server errors
                    continue
                else:
                    # Don't retry on client errors
                    return f"Error: {e.response.status_code} - {e.response.text}"
```

### Phase 4: Custom Types (Optional)

#### 1. Define Custom Input Types
```python
# custom_types.py
from pydantic import BaseModel, Field
from semantic_kernel.kernel_pydantic import KernelBaseModel
from typing import List, Optional

class CustomInput(KernelBaseModel):
    """Custom input type for specialized agent."""
    
    user_query: str = Field(description="User's main query")
    context_data: Optional[dict] = Field(default=None, description="Additional context")
    preferences: Optional[List[str]] = Field(default=None, description="User preferences")
    session_id: Optional[str] = Field(default=None, description="Session identifier")

class CustomOutput(BaseModel):
    """Custom output type with structured response."""
    
    response: str = Field(description="Main response text")
    confidence: float = Field(description="Confidence score 0-1")
    sources: List[str] = Field(description="Information sources used")
    follow_up_questions: Optional[List[str]] = Field(default=None, description="Suggested follow-ups")
```

#### 2. Update Configuration for Custom Types
```yaml
apiVersion: skagents/v1
kind: Agent
service_name: MyAgent
version: 1.0
input_type: CustomInput
output_type: CustomOutput
spec:
  model: gpt-4o
  system_prompt: |
    You must respond with structured output including response, confidence, and sources.
```

### Phase 5: Custom Completion Factory (Advanced)

#### 1. Create Custom Completion Factory
```python
# custom_completion_factory.py
from typing import List
from ska_utils import AppConfig, Config
from sk_agents.ska_types import ChatCompletionFactory, ModelType
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.connectors.ai.google.google_ai import GoogleAIChatCompletion

class CustomChatCompletionFactory(ChatCompletionFactory):
    """Custom completion factory for specialized model integration."""
    
    @staticmethod
    def get_configs() -> List[Config]:
        return [
            Config(env_name="CUSTOM_API_KEY", is_required=True, default_value=None),
            Config(env_name="CUSTOM_MODEL_ENDPOINT", is_required=False, default_value="https://api.custom.com"),
        ]
    
    def get_chat_completion_for_model_name(
        self, model_name: str, service_id: str
    ) -> ChatCompletionClientBase:
        """Create chat completion client for specified model."""
        
        if model_name.startswith("custom-"):
            # Custom model integration
            return self._create_custom_client(model_name, service_id)
        elif model_name.startswith("gemini-"):
            # Google Gemini integration
            return GoogleAIChatCompletion(
                gemini_model_id=model_name,
                api_key=self.app_config.get("GOOGLE_API_KEY"),
                service_id=service_id
            )
        else:
            raise ValueError(f"Unsupported model: {model_name}")
    
    def get_model_type_for_name(self, model_name: str) -> ModelType:
        """Return model type for given model name."""
        if model_name.startswith("custom-"):
            return ModelType.OPENAI  # Use OpenAI-compatible interface
        elif model_name.startswith("gemini-"):
            return ModelType.GOOGLE
        else:
            raise ValueError(f"Unknown model type for: {model_name}")
    
    def model_supports_structured_output(self, model_name: str) -> bool:
        """Check if model supports structured output."""
        return model_name in ["custom-structured", "gemini-pro"]
    
    def _create_custom_client(self, model_name: str, service_id: str) -> ChatCompletionClientBase:
        """Create custom model client."""
        # Implement your custom model integration here
        pass
```

#### 2. Configure Custom Factory
```bash
# Environment variables
export TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE=/path/to/custom_completion_factory.py
export TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS=CustomChatCompletionFactory
export CUSTOM_API_KEY=your_custom_api_key
```

### Phase 6: Testing and Validation

#### 1. Unit Testing
```python
# tests/test_my_agent.py
import pytest
from unittest.mock import Mock, patch
from plugins.my_custom_plugin import MyCustomPlugin

class TestMyCustomPlugin:
    def test_plugin_initialization(self):
        plugin = MyCustomPlugin(authorization="test-token")
        assert plugin.authorization == "test-token"
    
    @patch('httpx.Client.get')
    def test_fetch_data_success(self, mock_get):
        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = {"result": "test data"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        plugin = MyCustomPlugin()
        result = plugin.fetch_data("test query")
        
        assert result == {"result": "test data"}
    
    @patch('httpx.Client.get')
    def test_fetch_data_error(self, mock_get):
        # Mock API error
        mock_get.side_effect = httpx.HTTPError("API Error")
        
        plugin = MyCustomPlugin()
        result = plugin.fetch_data("test query")
        
        assert "Error fetching data" in result
```

#### 2. Integration Testing
```python
# tests/test_agent_integration.py
import pytest
from fastapi.testclient import TestClient
from sk_agents.app import app

class TestAgentIntegration:
    def setup_method(self):
        self.client = TestClient(app)
    
    def test_agent_basic_interaction(self):
        response = self.client.post(
            "/MyAgent/1.0/",
            json={
                "chat_history": [
                    {"role": "user", "content": "Hello, test agent!"}
                ]
            }
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "response" in result
        assert result["response"] is not None
    
    def test_agent_plugin_functionality(self):
        response = self.client.post(
            "/MyAgent/1.0/",
            json={
                "chat_history": [
                    {"role": "user", "content": "Use the fetch_data function to get information about Python"}
                ]
            }
        )
        
        assert response.status_code == 200
        # Verify plugin was called and returned expected data
```

#### 3. Manual Testing
```bash
# Start your agent
export TA_SERVICE_CONFIG=agents/my-agent/config.yaml
uv run uvicorn sk_agents.app:app --host 0.0.0.0 --port 8000

# Test basic functionality
curl -X POST http://localhost:8000/MyAgent/1.0/ \
  -H "Content-Type: application/json" \
  -d '{"chat_history": [{"role": "user", "content": "Hello!"}]}'

# Test plugin functionality
curl -X POST http://localhost:8000/MyAgent/1.0/ \
  -H "Content-Type: application/json" \
  -d '{"chat_history": [{"role": "user", "content": "Use fetch_data to search for information about AI"}]}'
```

### Phase 7: UI Development (Optional)

#### 1. Create Streamlit Interface
```python
# ui/streamlit_app.py
import streamlit as st
import requests
import json

st.title("My Custom Agent")

# Configuration
AGENT_URL = "http://localhost:8000/MyAgent/1.0/"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Prepare request
    chat_history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in st.session_state.messages
    ]
    
    # Call agent
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    AGENT_URL,
                    json={"chat_history": chat_history},
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()
                
                assistant_response = result.get("output_raw", "No response received")
                st.markdown(assistant_response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_response
                })
                
            except requests.exceptions.RequestException as e:
                st.error(f"Error communicating with agent: {e}")
            except json.JSONDecodeError as e:
                st.error(f"Error parsing response: {e}")

# Sidebar with agent info
with st.sidebar:
    st.header("Agent Information")
    st.write("**Name:** My Custom Agent")
    st.write("**Version:** 1.0")
    st.write("**Model:** GPT-4o")
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
```

#### 2. Run Streamlit Interface
```bash
# Install Streamlit
uv add streamlit

# Run the interface
uv run streamlit run ui/streamlit_app.py --server.port 8501
```

### Phase 8: Documentation

#### 1. Create Agent README
Use the [Agent Template](AGENT_TEMPLATE.md) to document your agent:

```markdown
# My Custom Agent

## Overview
Brief description of what your agent does and its primary use cases.

## Features
- List key capabilities
- Plugin integrations
- Special functionality

## Setup Instructions
Step-by-step setup guide including:
- Prerequisites
- Environment variables
- Configuration files
- Running the agent

## Usage Examples
Code examples and API calls demonstrating agent usage.

## Plugin Documentation
Details about custom plugins and their functions.

## Testing
How to run tests and validate functionality.

## Troubleshooting
Common issues and solutions.
```

#### 2. Update Configuration Documentation
Document all configuration options, environment variables, and customization points.

### Phase 9: Deployment Preparation

#### 1. Environment Configuration
```bash
# Production environment variables
export TA_SERVICE_CONFIG=/path/to/production/config.yaml
export TA_STATE_MANAGEMENT=redis
export TA_REDIS_HOST=production-redis-host
export TA_TELEMETRY_ENABLED=true
export TA_OTEL_ENDPOINT=https://telemetry.example.com
```

#### 2. Docker Configuration (Optional)
```dockerfile
# Dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy requirements
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uv", "run", "uvicorn", "sk_agents.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 3. Production Checklist
- [ ] All environment variables configured
- [ ] API keys secured and rotated
- [ ] Redis/state management configured
- [ ] Monitoring and logging enabled
- [ ] Error handling comprehensive
- [ ] Rate limiting implemented
- [ ] Security headers configured
- [ ] Documentation complete
- [ ] Tests passing
- [ ] Performance optimized

## Best Practices

### Code Quality
1. **Follow PEP 8**: Use consistent code style
2. **Type hints**: Add type annotations to all functions
3. **Error handling**: Implement comprehensive error handling
4. **Logging**: Add appropriate logging throughout your code
5. **Documentation**: Document all functions and classes

### Security
1. **API key management**: Never hardcode API keys
2. **Input validation**: Validate all user inputs
3. **Rate limiting**: Implement rate limiting for production
4. **Authentication**: Use proper authentication for sensitive agents
5. **HTTPS**: Always use HTTPS in production

### Performance
1. **Async operations**: Use async/await for I/O operations
2. **Connection pooling**: Reuse HTTP connections
3. **Caching**: Cache expensive operations when appropriate
4. **Streaming**: Use streaming for long responses
5. **Resource limits**: Set appropriate timeouts and limits

### Testing
1. **Unit tests**: Test individual components
2. **Integration tests**: Test complete workflows
3. **Mock external services**: Don't rely on external APIs in tests
4. **Edge cases**: Test error conditions and edge cases
5. **Performance tests**: Test under load

## Common Patterns

### Multi-step Workflows
```python
@kernel_function(description="Execute multi-step process")
def multi_step_process(self, input_data: str) -> str:
    # Step 1: Validate input
    if not self.validate_input(input_data):
        return "Invalid input"
    
    # Step 2: Process data
    processed = self.process_data(input_data)
    
    # Step 3: Generate output
    result = self.generate_output(processed)
    
    return result
```

### Conditional Logic
```python
@kernel_function(description="Handle different request types")
def handle_request(self, request_type: str, data: str) -> str:
    if request_type == "search":
        return self.search_data(data)
    elif request_type == "analyze":
        return self.analyze_data(data)
    elif request_type == "summarize":
        return self.summarize_data(data)
    else:
        return "Unknown request type"
```

### Data Transformation
```python
@kernel_function(description="Transform data between formats")
def transform_data(self, input_format: str, output_format: str, data: str) -> str:
    # Parse input
    parsed_data = self.parse_data(input_format, data)
    
    # Transform
    transformed = self.apply_transformation(parsed_data)
    
    # Format output
    return self.format_data(output_format, transformed)
```

## Next Steps

After completing your agent development:

1. **Test thoroughly**: Run all tests and manual validation
2. **Document completely**: Ensure all documentation is up to date
3. **Deploy safely**: Use staging environment before production
4. **Monitor actively**: Set up monitoring and alerting
5. **Iterate based on feedback**: Continuously improve based on user feedback

## Additional Resources

- **[Developer Guide](DEVELOPER_GUIDE.md)**: Development environment setup
- **[Testing Guide](TESTING_GUIDE.md)**: Comprehensive testing strategies
- **[Demo Examples](src/sk-agents/docs/demos/README.md)**: Learning from existing demos
- **[University Agent](src/orchestrators/assistant-orchestrator/example/university/README.md)**: Complete working example
- **[Contributing Guidelines](CONTRIBUTING.md)**: How to contribute back to the framework

For questions or support, please create an issue on GitHub or refer to the existing documentation and examples.
