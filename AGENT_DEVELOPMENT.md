# Agent Development Guide - Step-by-Step

This guide provides a comprehensive, step-by-step process for creating new agents in the Teal Agents Framework, from initial concept to production deployment.

## Table of Contents

- [Planning Your Agent](#planning-your-agent)
- [Setting Up the Development Environment](#setting-up-the-development-environment)
- [Creating the Agent Structure](#creating-the-agent-structure)
- [Configuration Development](#configuration-development)
- [Plugin Development](#plugin-development)
- [Custom Completion Factory (Optional)](#custom-completion-factory-optional)
- [Testing and Validation](#testing-and-validation)
- [UI Development (Optional)](#ui-development-optional)
- [Deployment Preparation](#deployment-preparation)
- [Production Deployment](#production-deployment)

## Planning Your Agent

### Step 1: Define Agent Purpose and Scope

Before writing any code, clearly define your agent's purpose:

**Agent Planning Worksheet:**
```
Agent Name: _______________
Domain/Industry: _______________
Primary Use Case: _______________
Target Users: _______________
Key Capabilities:
- Capability 1: _______________
- Capability 2: _______________
- Capability 3: _______________

External APIs/Services Needed:
- Service 1: _______________
- Service 2: _______________

Input Types:
□ Text only
□ Multi-modal (images)
□ Structured data
□ Custom input format

Output Requirements:
□ Simple text responses
□ Structured data
□ File generation
□ API calls to external systems
```

### Step 2: Choose Reference Implementation

Select the most appropriate demo or existing agent as a starting point:

- **Simple Chat Agent**: Use `01_getting_started` demo
- **API Integration**: Use `04_remote_plugins` demo or University Agent
- **Multi-modal Processing**: Use `08_multi_modal` demo
- **Complex Workflows**: Use University Agent as comprehensive example

### Step 3: Identify Required Components

Based on your planning, identify what components you'll need:

**Component Checklist:**
- [ ] Basic agent configuration (always required)
- [ ] Custom plugins for domain-specific functionality
- [ ] Custom completion factory for specific LLM provider
- [ ] Remote plugin integration for external APIs
- [ ] Custom input/output types
- [ ] User interface (web, CLI, API-only)
- [ ] Authentication and authorization
- [ ] State management for multi-turn conversations

## Setting Up the Development Environment

### Step 4: Environment Preparation

1. **Ensure Prerequisites:**
   ```bash
   # Verify Python version
   python --version  # Should be 3.13+
   
   # Verify uv installation
   uv --version
   
   # Navigate to framework
   cd /path/to/teal-agents/src/sk-agents
   
   # Install dependencies
   uv sync --dev
   ```

2. **Create Agent Directory:**
   ```bash
   # Create agent directory structure
   mkdir -p src/orchestrators/assistant-orchestrator/example/[your-agent-name]
   cd src/orchestrators/assistant-orchestrator/example/[your-agent-name]
   
   # Create initial files
   touch config.yaml
   touch custom_plugins.py
   touch README.md
   ```

3. **Set Up Environment Variables:**
   ```bash
   # Create .env file for development
   cat > .env << EOF
   TA_API_KEY=your_api_key_here
   TA_SERVICE_CONFIG=/absolute/path/to/your-agent/config.yaml
   TA_LOG_LEVEL=debug
   EOF
   ```

## Creating the Agent Structure

### Step 5: Basic Agent Configuration

Create your initial `config.yaml`:

```yaml
apiVersion: skagents/v1
kind: Sequential  # or Parallel, Workflow
description: >
  [Your agent description - what it does and who it's for]
service_name: [YourAgentName]  # No spaces, PascalCase
version: 0.1.0
input_type: BaseInput  # or BaseMultiModalInput, custom type
spec:
  agents:
    - name: default
      role: [Agent Role Description]
      model: gpt-4o  # or your preferred model
      system_prompt: >
        You are a helpful [domain] assistant.
        [Add specific instructions for your domain]
        
        [If using plugins, mention them here]
        Use the available plugins to provide accurate information.
        
        Always be helpful and ask for clarification if needed.
      plugins:
        # - YourCustomPlugin  # Uncomment when you create plugins
  tasks:
    - name: [task_name]
      task_no: 1
      description: [Task description]
      instructions: >
        [Specific instructions for this task]
        
        [Guidelines for plugin usage]
        [Expected behavior patterns]
      agent: default
```

### Step 6: Test Basic Configuration

1. **Validate YAML Syntax:**
   ```bash
   python -c "import yaml; print(yaml.safe_load(open('config.yaml')))"
   ```

2. **Test Agent Loading:**
   ```bash
   export TA_SERVICE_CONFIG=/absolute/path/to/your-agent/config.yaml
   export TA_API_KEY=your_api_key
   
   cd /path/to/teal-agents/src/sk-agents
   uv run uvicorn sk_agents.app:app --host 0.0.0.0 --port 8000
   ```

3. **Test Basic Functionality:**
   ```bash
   # In another terminal
   curl -X POST http://localhost:8000/invoke \
     -H "Content-Type: application/json" \
     -d '{"chat_history": [{"role": "user", "content": "Hello, can you help me?"}]}'
   ```

## Configuration Development

### Step 7: Refine Agent Configuration

Based on your testing, refine the configuration:

#### Advanced Configuration Options

```yaml
apiVersion: skagents/v1
kind: Sequential
description: >
  Detailed description of your agent's capabilities
service_name: YourAgentName
version: 0.1.0
input_type: BaseInput
metadata:  # Optional: for agent discovery and documentation
  description: Extended description
  documentation_url: https://your-docs.com
  skills:
    - id: skill1
      name: Skill Name
      description: What this skill does
      tags: [tag1, tag2]
      examples: ["Example query 1", "Example query 2"]
      input_modes: [text]
      output_modes: [text]
spec:
  agents:
    - name: default
      role: Specialized Agent Role
      model: gpt-4o
      system_prompt: >
        Comprehensive system prompt with:
        - Role definition
        - Behavioral guidelines
        - Plugin usage instructions
        - Output format requirements
        - Error handling instructions
      plugins:
        - YourCustomPlugin
      remote_plugins:  # If using remote plugins
        - external_api_plugin
  tasks:
    - name: primary_task
      task_no: 1
      description: Primary task description
      instructions: >
        Detailed task instructions including:
        - Expected inputs
        - Processing steps
        - Output requirements
        - Error handling
      agent: default
    # Add more tasks for complex workflows
```

#### Custom Input Types (Optional)

If you need custom input validation:

```python
# custom_types.py
from semantic_kernel.kernel_pydantic import KernelBaseModel
from typing import Optional, List

class YourCustomInput(KernelBaseModel):
    query: str
    context: Optional[str] = None
    filters: Optional[dict] = {}
    options: Optional[List[str]] = []
```

Update config.yaml:
```yaml
input_type: YourCustomInput
```

## Plugin Development

### Step 8: Create Custom Plugins

Develop plugins for domain-specific functionality:

#### Basic Plugin Structure

```python
# custom_plugins.py
from semantic_kernel import kernel_function
from typing import Optional
import httpx
import json
from pydantic import BaseModel

class YourDataModel(BaseModel):
    """Pydantic model for structured data handling"""
    id: str
    name: str
    description: Optional[str] = None
    # Add fields specific to your domain

class YourCustomPlugin:
    """
    Plugin for [domain-specific functionality].
    
    This plugin provides:
    - Function 1: Description
    - Function 2: Description
    """
    
    def __init__(self):
        self.base_url = "https://api.your-service.com"
        # Initialize any required clients or configurations
    
    @kernel_function(description="Primary function description")
    def primary_function(
        self, 
        query: str, 
        limit: int = 10,
        filter_type: str = "all"
    ) -> str:
        """
        Detailed function description.
        
        Args:
            query: Search query or input
            limit: Maximum number of results
            filter_type: Type of filtering to apply
            
        Returns:
            JSON string with results
        """
        try:
            # Implement your logic here
            results = self._call_external_api(query, limit, filter_type)
            
            # Convert to Pydantic models for validation
            validated_results = [YourDataModel(**item) for item in results]
            
            # Return as JSON string for agent consumption
            return json.dumps([result.dict() for result in validated_results])
            
        except Exception as e:
            return json.dumps({
                "error": f"Failed to process request: {str(e)}",
                "query": query
            })
    
    @kernel_function(description="Secondary function description")
    def secondary_function(self, input_param: str) -> str:
        """
        Another function for different functionality.
        """
        try:
            # Implement secondary functionality
            result = self._process_input(input_param)
            return json.dumps({"result": result, "input": input_param})
        except Exception as e:
            return json.dumps({"error": str(e), "input": input_param})
    
    def _call_external_api(self, query: str, limit: int, filter_type: str) -> list:
        """Private method for API calls"""
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.base_url}/search",
                    params={
                        "q": query,
                        "limit": limit,
                        "type": filter_type
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            raise Exception(f"API request failed: {e}")
        except httpx.HTTPStatusError as e:
            raise Exception(f"API returned error {e.response.status_code}: {e.response.text}")
    
    def _process_input(self, input_param: str) -> str:
        """Private method for input processing"""
        # Implement your processing logic
        return f"Processed: {input_param}"
```

#### Advanced Plugin Patterns

```python
# For plugins requiring authentication
class AuthenticatedPlugin:
    def __init__(self):
        self.api_key = os.getenv("YOUR_API_KEY")
        if not self.api_key:
            raise ValueError("YOUR_API_KEY environment variable is required")
    
    @kernel_function(description="Authenticated API call")
    def authenticated_call(self, query: str) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        # Implementation with authentication

# For plugins with caching
from functools import lru_cache

class CachedPlugin:
    @kernel_function(description="Cached function call")
    def cached_function(self, query: str) -> str:
        return self._cached_implementation(query)
    
    @lru_cache(maxsize=100)
    def _cached_implementation(self, query: str) -> str:
        # Expensive operation that benefits from caching
        pass

# For async plugins
import asyncio

class AsyncPlugin:
    @kernel_function(description="Async function")
    def async_function(self, query: str) -> str:
        # Run async code in sync context
        return asyncio.run(self._async_implementation(query))
    
    async def _async_implementation(self, query: str) -> str:
        # Async implementation
        pass
```

### Step 9: Register and Test Plugins

1. **Update Configuration:**
   ```yaml
   spec:
     agents:
       - name: default
         plugins:
           - YourCustomPlugin
   ```

2. **Test Plugin Loading:**
   ```bash
   python -c "
   from custom_plugins import YourCustomPlugin
   plugin = YourCustomPlugin()
   print('Plugin loaded successfully')
   print(dir(plugin))
   "
   ```

3. **Test Plugin Functions:**
   ```bash
   python -c "
   from custom_plugins import YourCustomPlugin
   plugin = YourCustomPlugin()
   result = plugin.primary_function('test query')
   print(f'Plugin result: {result}')
   "
   ```

## Custom Completion Factory (Optional)

### Step 10: Create Custom Completion Factory

If you need to integrate a specific LLM provider:

```python
# custom_completion_factory.py
from semantic_kernel.connectors.ai.chat_completion_client_base import (
    ChatCompletionClientBase,
)
from ska_utils import AppConfig, Config as UtilConfig
from sk_agents.ska_types import ChatCompletionFactory, ModelType

# Define configuration requirements
YOUR_API_KEY = Config(
    env_name="YOUR_API_KEY",
    is_required=True,
    default_value=None
)

class YourCustomChatCompletionFactory(ChatCompletionFactory):
    """
    Custom completion factory for [Your LLM Provider].
    
    Supports models: [list your supported models]
    """
    
    _SUPPORTED_MODELS: list[str] = [
        "your-model-1",
        "your-model-2",
        "your-model-3",
    ]
    
    _CONFIGS: list[UtilConfig] = [YOUR_API_KEY]
    
    def __init__(self, app_config: AppConfig):
        super().__init__(app_config)
        self.api_key = app_config.get(YOUR_API_KEY.env_name)
        self.base_url = "https://api.your-provider.com"
    
    @staticmethod
    def get_configs() -> list[UtilConfig]:
        return YourCustomChatCompletionFactory._CONFIGS
    
    def get_chat_completion_for_model_name(
        self, model_name: str, service_id: str
    ) -> ChatCompletionClientBase:
        if model_name not in self._SUPPORTED_MODELS:
            raise ValueError(f"Model {model_name} not supported")
        
        # Return your custom chat completion client
        # This would typically be a wrapper around your provider's SDK
        return YourCustomChatCompletionClient(
            service_id=service_id,
            model_name=model_name,
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def get_model_type_for_name(self, model_name: str) -> ModelType:
        if model_name in self._SUPPORTED_MODELS:
            return ModelType.CUSTOM  # or appropriate type
        else:
            raise ValueError(f"Unknown model name {model_name}")
    
    def model_supports_structured_output(self, model_name: str) -> bool:
        # Return True if your model supports structured output
        return model_name in ["your-model-1", "your-model-2"]
    
    def create_chat_completion(self, **kwargs):
        model_name = kwargs.get("model_name", self._SUPPORTED_MODELS[0])
        service_id = kwargs.get("service_id", "default_service")
        return self.get_chat_completion_for_model_name(model_name, service_id)
```

**Configure Custom Factory:**
```bash
export TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE=/absolute/path/to/custom_completion_factory.py
export YOUR_API_KEY=your_api_key
```

## Testing and Validation

### Step 11: Comprehensive Testing

#### Unit Testing

Create test files for your components:

```python
# test_custom_plugins.py
import pytest
import json
from custom_plugins import YourCustomPlugin, YourDataModel

class TestYourCustomPlugin:
    def setup_method(self):
        self.plugin = YourCustomPlugin()
    
    def test_primary_function_success(self):
        result = self.plugin.primary_function("test query")
        data = json.loads(result)
        assert isinstance(data, list)
        # Add more specific assertions
    
    def test_primary_function_error_handling(self):
        # Test error scenarios
        result = self.plugin.primary_function("")
        data = json.loads(result)
        assert "error" in data
    
    def test_data_model_validation(self):
        # Test Pydantic model validation
        valid_data = {"id": "1", "name": "Test"}
        model = YourDataModel(**valid_data)
        assert model.id == "1"
        assert model.name == "Test"

# Run tests
# uv run pytest test_custom_plugins.py -v
```

#### Integration Testing

```bash
# test_agent_integration.sh
#!/bin/bash

# Set environment variables
export TA_SERVICE_CONFIG=/absolute/path/to/config.yaml
export TA_API_KEY=your_api_key

# Start agent in background
cd /path/to/teal-agents/src/sk-agents
uv run uvicorn sk_agents.app:app --host 0.0.0.0 --port 8000 &
AGENT_PID=$!

# Wait for startup
sleep 5

# Test agent card
echo "Testing agent card..."
curl -s http://localhost:8000/.well-known/agent.json | jq .

# Test basic invocation
echo "Testing basic invocation..."
curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{"chat_history": [{"role": "user", "content": "Hello"}]}' | jq .

# Test plugin functionality
echo "Testing plugin functionality..."
curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{"chat_history": [{"role": "user", "content": "Use your plugin to search for test data"}]}' | jq .

# Cleanup
kill $AGENT_PID
```

#### Configuration Validation

```bash
# validate_config.py
import yaml
import jsonschema
from pathlib import Path

def validate_agent_config(config_path):
    """Validate agent configuration against schema"""
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Basic validation
    required_fields = ['apiVersion', 'kind', 'service_name', 'spec']
    for field in required_fields:
        assert field in config, f"Missing required field: {field}"
    
    # Validate spec structure
    spec = config['spec']
    assert 'agents' in spec, "Missing agents in spec"
    assert 'tasks' in spec, "Missing tasks in spec"
    
    # Validate agents
    for agent in spec['agents']:
        required_agent_fields = ['name', 'role', 'model']
        for field in required_agent_fields:
            assert field in agent, f"Missing required agent field: {field}"
    
    print("Configuration validation passed!")

if __name__ == "__main__":
    validate_agent_config("config.yaml")
```

### Step 12: Performance and Load Testing

```python
# load_test.py
import asyncio
import aiohttp
import time
import json

async def test_agent_performance():
    """Basic load testing for agent endpoints"""
    
    test_payload = {
        "chat_history": [
            {"role": "user", "content": "Test query for performance testing"}
        ]
    }
    
    async with aiohttp.ClientSession() as session:
        # Test concurrent requests
        tasks = []
        start_time = time.time()
        
        for i in range(10):  # 10 concurrent requests
            task = asyncio.create_task(
                make_request(session, test_payload)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # Analyze results
        successful = sum(1 for r in results if not isinstance(r, Exception))
        failed = len(results) - successful
        
        print(f"Performance Test Results:")
        print(f"Total requests: {len(results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Total time: {end_time - start_time:.2f}s")
        print(f"Average time per request: {(end_time - start_time) / len(results):.2f}s")

async def make_request(session, payload):
    """Make a single request to the agent"""
    async with session.post(
        "http://localhost:8000/invoke",
        json=payload,
        headers={"Content-Type": "application/json"}
    ) as response:
        return await response.json()

if __name__ == "__main__":
    asyncio.run(test_agent_performance())
```

## UI Development (Optional)

### Step 13: Create User Interface

#### Streamlit Interface

```python
# streamlit_ui.py
import streamlit as st
import requests
import json
from typing import Dict, Any

# Configuration
AGENT_URL = "http://localhost:8000"

def main():
    st.title("Your Agent Name")
    st.markdown("Description of what your agent does")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_agent_response(st.session_state.messages)
                st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

def get_agent_response(messages: list) -> str:
    """Get response from the agent"""
    try:
        # Convert messages to agent format
        chat_history = [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in messages
        ]
        
        payload = {"chat_history": chat_history}
        
        response = requests.post(
            f"{AGENT_URL}/invoke",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("output_raw", "No response received")
        else:
            return f"Error: {response.status_code} - {response.text}"
    
    except requests.exceptions.RequestException as e:
        return f"Connection error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

# Sidebar with agent information
def show_sidebar():
    with st.sidebar:
        st.header("Agent Information")
        
        # Get agent card
        try:
            response = requests.get(f"{AGENT_URL}/.well-known/agent.json")
            if response.status_code == 200:
                agent_info = response.json()
                st.json(agent_info)
            else:
                st.error("Could not load agent information")
        except:
            st.error("Agent not available")
        
        # Configuration options
        st.header("Options")
        st.checkbox("Show debug info", key="debug_mode")
        st.selectbox("Response format", ["Standard", "Detailed"], key="response_format")

if __name__ == "__main__":
    show_sidebar()
    main()
```

#### Web Interface (FastAPI + HTML)

```python
# web_ui.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def web_interface(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Create templates/index.html with your web interface
```

### Step 14: Test UI Integration

```bash
# Test Streamlit UI
cd /path/to/your-agent
uv run streamlit run streamlit_ui.py

# Test in browser at http://localhost:8501
```

## Deployment Preparation

### Step 15: Create Deployment Configuration

#### Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.13-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY src/sk-agents/pyproject.toml src/sk-agents/uv.lock ./
RUN pip install uv && uv sync --dev

# Copy application code
COPY . .

# Set working directory for agent
WORKDIR /app/src/sk-agents

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/.well-known/agent.json || exit 1

# Run application
CMD ["uv", "run", "uvicorn", "sk_agents.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  your-agent:
    build: .
    ports:
      - "8000:8000"
    environment:
      - TA_API_KEY=${TA_API_KEY}
      - TA_SERVICE_CONFIG=/app/src/orchestrators/assistant-orchestrator/example/your-agent/config.yaml
      - TA_TELEMETRY_ENABLED=true
      - TA_LOG_LEVEL=info
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/.well-known/agent.json"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Optional: Add monitoring
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
```

#### Environment Configuration

```bash
# production.env
TA_API_KEY=your_production_api_key
TA_SERVICE_CONFIG=/app/config/config.yaml
TA_TELEMETRY_ENABLED=true
TA_OTEL_ENDPOINT=https://your-telemetry-endpoint
TA_LOG_LEVEL=info
```

### Step 16: Documentation

Create comprehensive documentation:

```markdown
# README.md for your agent
# [Your Agent Name]

## Overview
[Description of your agent]

## Features
- [Feature 1]
- [Feature 2]

## Setup
[Setup instructions]

## Usage
[Usage examples]

## API Reference
[API documentation]

## Troubleshooting
[Common issues and solutions]
```

## Production Deployment

### Step 17: Deploy to Production

#### Local Production Testing

```bash
# Test production configuration
export TA_TELEMETRY_ENABLED=true
export TA_LOG_LEVEL=info
uv run uvicorn sk_agents.app:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Container Deployment

```bash
# Build and run with Docker
docker build -t your-agent:latest .
docker run -p 8000:8000 --env-file production.env your-agent:latest

# Or with Docker Compose
docker-compose up -d
```

#### Cloud Deployment

```bash
# Example for cloud deployment
# Adjust for your cloud provider (AWS, GCP, Azure, etc.)

# Build and push image
docker build -t your-registry/your-agent:latest .
docker push your-registry/your-agent:latest

# Deploy to cloud service
# (Cloud-specific deployment commands)
```

### Step 18: Monitoring and Maintenance

#### Health Monitoring

```python
# health_check.py
import requests
import time
import logging

def check_agent_health():
    """Monitor agent health and performance"""
    try:
        # Check agent card endpoint
        response = requests.get("http://localhost:8000/.well-known/agent.json", timeout=10)
        if response.status_code != 200:
            logging.error(f"Agent card check failed: {response.status_code}")
            return False
        
        # Check basic functionality
        test_payload = {"chat_history": [{"role": "user", "content": "Health check"}]}
        response = requests.post(
            "http://localhost:8000/invoke",
            json=test_payload,
            timeout=30
        )
        
        if response.status_code != 200:
            logging.error(f"Agent invoke check failed: {response.status_code}")
            return False
        
        logging.info("Agent health check passed")
        return True
    
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    while True:
        check_agent_health()
        time.sleep(60)  # Check every minute
```

#### Performance Monitoring

```python
# performance_monitor.py
import psutil
import requests
import time
import json

def monitor_performance():
    """Monitor system and agent performance"""
    # System metrics
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent
    
    # Agent metrics (if available)
    try:
        response = requests.get("http://localhost:8000/metrics", timeout=5)
        agent_metrics = response.json() if response.status_code == 200 else {}
    except:
        agent_metrics = {}
    
    metrics = {
        "timestamp": time.time(),
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent
        },
        "agent": agent_metrics
    }
    
    # Log or send to monitoring system
    print(json.dumps(metrics))

if __name__ == "__main__":
    while True:
        monitor_performance()
        time.sleep(30)  # Monitor every 30 seconds
```

## Best Practices Summary

### Development Best Practices

1. **Start Simple**: Begin with basic functionality and iterate
2. **Test Early**: Test each component as you build it
3. **Document Everything**: Keep documentation up-to-date
4. **Use Version Control**: Commit frequently with descriptive messages
5. **Follow Patterns**: Use existing agents as reference implementations

### Configuration Best Practices

1. **Use Absolute Paths**: Always use absolute paths for configuration files
2. **Environment Variables**: Keep sensitive data in environment variables
3. **Validate Configuration**: Test configuration loading before deployment
4. **Version Your Configs**: Track configuration changes

### Plugin Development Best Practices

1. **Error Handling**: Implement robust error handling
2. **Type Hints**: Use type hints for all function parameters
3. **Documentation**: Provide clear function descriptions
4. **Testing**: Write unit tests for plugin functions
5. **Performance**: Consider caching for expensive operations

### Deployment Best Practices

1. **Health Checks**: Implement comprehensive health monitoring
2. **Logging**: Use structured logging for debugging
3. **Monitoring**: Set up performance and error monitoring
4. **Scaling**: Plan for horizontal scaling if needed
5. **Security**: Follow security best practices for production

## Troubleshooting Common Issues

### Development Issues

- **Configuration not loading**: Check absolute paths and YAML syntax
- **Plugin not found**: Verify plugin class definition and imports
- **API key errors**: Confirm environment variables are set correctly
- **Import errors**: Ensure all dependencies are installed

### Deployment Issues

- **Container startup failures**: Check environment variables and file paths
- **Performance problems**: Monitor resource usage and optimize accordingly
- **Network connectivity**: Verify external API access and firewall settings

### Getting Help

- Review existing agent implementations (especially University Agent)
- Check the [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for environment setup
- Consult [TESTING_GUIDE.md](TESTING_GUIDE.md) for testing strategies
- Use the [AGENT_TEMPLATE.md](AGENT_TEMPLATE.md) for documentation structure

---

**Last Updated**: [Current Date]
**Version**: 1.0
**Maintainer**: Teal Agents Development Team
