# [Agent Name] - Teal Agents Framework

## Overview

[Brief description of what this agent does and its primary purpose. Include the main use cases and target audience.]

**Agent Type**: [AppV1/AppV2/AppV3]  
**API Version**: [skagents/v1, skagents/v2alpha1, or tealagents/v1alpha1]  
**Version**: [Agent version number]  
**Status**: [Development/Beta/Production]

## Features

- **[Primary Feature]**: [Description of main capability]
- **[Secondary Feature]**: [Description of additional capability]
- **[Plugin Integration]**: [List of integrated plugins and their purposes]
- **[Special Capabilities]**: [Multi-modal, streaming, state management, etc.]

## Architecture

### Component Overview
```
┌─────────────────────────────────────────┐
│              [Agent Name]               │
├─────────────────────────────────────────┤
│  FastAPI Endpoints                      │
│  • REST: /[AgentName]/[version]/        │
│  • WebSocket: /[AgentName]/[version]/stream │
├─────────────────────────────────────────┤
│  Agent Handler ([AppV1/V2/V3])          │
│  • Input Processing                     │
│  • Plugin Orchestration                 │
│  • Response Generation                  │
├─────────────────────────────────────────┤
│  Plugins                                │
│  • [Plugin1]: [Purpose]                 │
│  • [Plugin2]: [Purpose]                 │
├─────────────────────────────────────────┤
│  External Integrations                  │
│  • [API1]: [Purpose]                    │
│  • [Service2]: [Purpose]                │
└─────────────────────────────────────────┘
```

### Configuration Structure
```yaml
apiVersion: [API version]
kind: Agent
name: [AgentName]
version: [version]
metadata:
  description: "[Agent description]"
  skills:
    - id: "[skill_id]"
      name: "[Skill Name]"
      description: "[What this skill does]"
spec:
  model: [model_name]
  system_prompt: |
    [Agent behavior instructions]
  plugins:
    - [PluginName]
  [additional_config_options]
```

## Prerequisites

### System Requirements
- **Python**: 3.11+ (3.13+ recommended)
- **Package Manager**: uv or pip
- **Memory**: [Minimum RAM requirements]
- **Storage**: [Disk space requirements]

### API Keys and Services
- **[Primary LLM Provider]**: [OpenAI/Anthropic/Google] API key
- **[External Service 1]**: API key and endpoint configuration
- **[External Service 2]**: Authentication credentials
- **[Optional Services]**: Additional integrations

### Dependencies
```bash
# Core framework dependencies
uv add semantic-kernel
uv add fastapi
uv add uvicorn

# Agent-specific dependencies
uv add [specific-library-1]
uv add [specific-library-2]
```

## Installation and Setup

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/thepollari/teal-agents.git
cd teal-agents

# Navigate to agent directory
cd [path/to/agent/directory]

# Install dependencies
uv sync --dev
```

### 2. Configuration

Create a `.env` file with required environment variables:

```bash
# Core configuration
TA_SERVICE_CONFIG=/absolute/path/to/config.yaml

# LLM Provider API Key
[PROVIDER]_API_KEY=your_api_key_here

# Agent-specific configuration
[AGENT_SPECIFIC_VAR_1]=value1
[AGENT_SPECIFIC_VAR_2]=value2

# Optional: Custom completion factory
TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE=/path/to/custom_factory.py
TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS=CustomFactoryClass

# Optional: State management
TA_STATE_MANAGEMENT=redis  # or in-memory
TA_REDIS_HOST=localhost
TA_REDIS_PORT=6379

# Optional: Telemetry
TA_TELEMETRY_ENABLED=false
```

### 3. Agent Configuration File

Create `config.yaml`:

```yaml
apiVersion: [API version]
kind: Agent
name: [AgentName]
version: [version]
description: "[Agent description]"
metadata:
  description: "[Detailed description]"
  documentation_url: "[Documentation URL]"
  skills:
    - id: "[skill_id]"
      name: "[Skill Name]"
      description: "[Skill description]"
      tags: ["tag1", "tag2"]
      examples: ["Example usage"]
      input_modes: ["text", "image"]  # if applicable
      output_modes: ["text"]
spec:
  model: [model_name]
  system_prompt: |
    [Detailed system prompt with agent behavior instructions]
  plugins:
    - [PluginName1]
    - [PluginName2]
  max_tokens: [token_limit]
  temperature: [temperature_value]
  [additional_model_parameters]
```

## Plugin Documentation

### [Plugin1Name]

**Purpose**: [What this plugin does]  
**External API**: [API used, if any]  
**Authentication**: [How authentication is handled]

#### Functions
- **`function_name(param: type) -> return_type`**: [Function description]
- **`another_function(param: type) -> return_type`**: [Function description]

#### Configuration
```python
# Plugin-specific environment variables
PLUGIN1_API_KEY=your_api_key
PLUGIN1_BASE_URL=https://api.example.com
```

#### Example Usage
```python
# How the plugin is used within the agent
result = plugin.function_name("example input")
```

### [Plugin2Name]

[Similar structure for additional plugins]

## Custom Completion Factory (if applicable)

### Overview
[Description of custom completion factory and why it's needed]

### Implementation
```python
# custom_completion_factory.py
from typing import List
from ska_utils import Config
from sk_agents.ska_types import ChatCompletionFactory, ModelType

class [CustomFactoryName](ChatCompletionFactory):
    @staticmethod
    def get_configs() -> List[Config]:
        return [
            Config(env_name="CUSTOM_API_KEY", is_required=True, default_value=None),
            # Additional configs
        ]
    
    def get_chat_completion_for_model_name(self, model_name: str, service_id: str):
        # Implementation details
        pass
    
    def get_model_type_for_name(self, model_name: str) -> ModelType:
        # Model type mapping
        pass
    
    def model_supports_structured_output(self, model_name: str) -> bool:
        # Structured output support
        pass
```

### Configuration
```bash
export TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE=/path/to/custom_completion_factory.py
export TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS=[CustomFactoryName]
```

## Usage Examples

### Basic Interaction

```bash
# Start the agent
export TA_SERVICE_CONFIG=/path/to/config.yaml
uv run uvicorn sk_agents.app:app --host 0.0.0.0 --port 8000
```

```bash
# REST API call
curl -X POST http://localhost:8000/[AgentName]/[version]/ \
  -H "Content-Type: application/json" \
  -d '{
    "chat_history": [
      {"role": "user", "content": "Hello, [agent name]!"}
    ]
  }'
```

### Advanced Usage

```bash
# Multi-modal input (if supported)
curl -X POST http://localhost:8000/[AgentName]/[version]/ \
  -H "Content-Type: application/json" \
  -d '{
    "chat_history": [
      {
        "role": "user",
        "items": [
          {"content_type": "text", "content": "Analyze this image"},
          {"content_type": "image", "content": "[base64_encoded_image]"}
        ]
      }
    ]
  }'
```

### Plugin-Specific Examples

```bash
# Using specific plugin functionality
curl -X POST http://localhost:8000/[AgentName]/[version]/ \
  -H "Content-Type: application/json" \
  -d '{
    "chat_history": [
      {"role": "user", "content": "Use [plugin_function] to [specific_task]"}
    ]
  }'
```

## User Interface (if applicable)

### Streamlit Interface

[If the agent includes a Streamlit UI]

```bash
# Install Streamlit
uv add streamlit

# Run the interface
uv run streamlit run ui/streamlit_app.py --server.port 8501
```

**Features**:
- [UI feature 1]
- [UI feature 2]
- [UI feature 3]

### Web Interface

[If the agent includes a web interface]

[Setup and usage instructions]

## API Reference

### Endpoints

#### POST /[AgentName]/[version]/
**Description**: [Endpoint description]

**Request Body**:
```json
{
  "chat_history": [
    {
      "role": "user|assistant",
      "content": "string"
    }
  ],
  "session_id": "string (optional)",
  "[custom_field]": "[custom_value]"
}
```

**Response**:
```json
{
  "session_id": "string",
  "source": "string",
  "request_id": "string",
  "token_usage": {
    "completion_tokens": 0,
    "prompt_tokens": 0,
    "total_tokens": 0
  },
  "output_raw": "string",
  "output_pydantic": null,
  "extra_data": {}
}
```

#### WebSocket /[AgentName]/[version]/stream
**Description**: [WebSocket endpoint description]

**Message Format**:
```json
{
  "chat_history": [...],
  "session_id": "string (optional)"
}
```

**Response Stream**:
```json
{
  "output_partial": "string",
  "session_id": "string"
}
```

### Error Responses

| Status Code | Description | Response Format |
|-------------|-------------|-----------------|
| 400 | Bad Request | `{"detail": "Error description"}` |
| 401 | Unauthorized | `{"detail": "Authentication required"}` |
| 422 | Validation Error | `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}` |
| 500 | Internal Server Error | `{"detail": "Internal server error"}` |

## Testing

### Unit Tests

```bash
# Run all tests
uv run pytest tests/

# Run specific test file
uv run pytest tests/test_[agent_name].py

# Run with coverage
uv run pytest --cov=[agent_module] tests/
```

### Integration Tests

```bash
# Test complete agent workflow
uv run pytest tests/test_integration.py

# Test with real APIs (requires API keys)
uv run pytest tests/test_integration.py --real-apis
```

### Manual Testing

```bash
# Test basic functionality
curl -X POST http://localhost:8000/[AgentName]/[version]/ \
  -H "Content-Type: application/json" \
  -d '{"chat_history": [{"role": "user", "content": "Test message"}]}'

# Test plugin functionality
curl -X POST http://localhost:8000/[AgentName]/[version]/ \
  -H "Content-Type: application/json" \
  -d '{"chat_history": [{"role": "user", "content": "Use [plugin_function] with test data"}]}'
```

## Performance Considerations

### Optimization Tips
- **[Optimization 1]**: [Description and implementation]
- **[Optimization 2]**: [Description and implementation]
- **Caching**: [What is cached and how]
- **Connection Pooling**: [How connections are managed]

### Resource Usage
- **Memory**: [Typical memory usage patterns]
- **CPU**: [CPU usage characteristics]
- **Network**: [Network usage patterns]
- **Storage**: [Storage requirements]

### Scaling Considerations
- **Horizontal Scaling**: [How to scale across multiple instances]
- **Load Balancing**: [Load balancing strategies]
- **State Management**: [How state is handled in scaled deployments]

## Troubleshooting

### Common Issues

#### Issue 1: [Common problem description]
**Symptoms**: [What users see]  
**Cause**: [Root cause]  
**Solution**: 
```bash
# Commands or configuration changes to fix
```

#### Issue 2: [Another common problem]
**Symptoms**: [What users see]  
**Cause**: [Root cause]  
**Solution**: [Step-by-step fix]

### Debugging

#### Enable Debug Logging
```bash
export LOG_LEVEL=DEBUG
uv run uvicorn sk_agents.app:app --log-level debug
```

#### Check Configuration
```bash
# Validate configuration file
python -c "
from pydantic_yaml import parse_yaml_file_as
from sk_agents.ska_types import BaseConfig
config = parse_yaml_file_as(BaseConfig, 'config.yaml')
print('Configuration is valid')
"
```

#### Test Plugin Functionality
```python
# Test plugin in isolation
from plugins.[plugin_name] import [PluginClass]
plugin = [PluginClass]()
result = plugin.[function_name]("test input")
print(result)
```

### Error Messages

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "[Error 1]" | [Cause 1] | [Solution 1] |
| "[Error 2]" | [Cause 2] | [Solution 2] |

## Deployment

### Local Deployment

```bash
# Production-like local deployment
export TA_SERVICE_CONFIG=/path/to/production/config.yaml
export TA_STATE_MANAGEMENT=redis
uv run uvicorn sk_agents.app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY . .

RUN pip install uv && uv sync --frozen

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "sk_agents.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t [agent-name] .
docker run -p 8000:8000 --env-file .env [agent-name]
```

### Production Deployment

#### Environment Variables
```bash
# Production environment setup
export TA_SERVICE_CONFIG=/app/config/production.yaml
export TA_STATE_MANAGEMENT=redis
export TA_REDIS_HOST=production-redis.example.com
export TA_TELEMETRY_ENABLED=true
export TA_OTEL_ENDPOINT=https://telemetry.example.com
```

#### Health Checks
```bash
# Health check endpoint
curl http://localhost:8000/[AgentName]/[version]/docs
```

#### Monitoring
- **Metrics**: [What metrics to monitor]
- **Logs**: [Important log patterns]
- **Alerts**: [When to alert]

## Security Considerations

### Authentication
[How authentication is implemented and configured]

### Authorization
[How authorization is handled]

### Data Privacy
[How sensitive data is handled]

### API Security
[Security measures for API endpoints]

## Contributing

### Development Setup
[Instructions for setting up development environment]

### Code Style
[Code style guidelines specific to this agent]

### Testing Requirements
[Testing requirements for contributions]

### Submission Process
[How to submit changes]

## Changelog

### Version [X.Y.Z] - [Date]
- **Added**: [New features]
- **Changed**: [Changes to existing features]
- **Fixed**: [Bug fixes]
- **Removed**: [Removed features]

### Version [X.Y.Z-1] - [Date]
[Previous version changes]

## License

[License information]

## Support and Contact

- **GitHub Issues**: [Link to issues page]
- **Documentation**: [Link to additional documentation]
- **Contact**: [Contact information]
- **Community**: [Links to community resources]

## Related Resources

- **[Teal Agents Framework Documentation](../README.md)**
- **[Developer Guide](../DEVELOPER_GUIDE.md)**
- **[Agent Development Guide](../AGENT_DEVELOPMENT.md)**
- **[Testing Guide](../TESTING_GUIDE.md)**
- **[Demo Examples](../src/sk-agents/docs/demos/README.md)**
- **[Other Working Agents](../src/orchestrators/assistant-orchestrator/example/)**

---

**Note**: This template should be customized for each specific agent implementation. Remove sections that don't apply and add agent-specific details where indicated.
