# Developer Guide - Teal Agents Framework

This guide provides comprehensive instructions for setting up a development environment and working with the Teal Agents Framework.

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Repository Structure](#repository-structure)
- [Core Framework Components](#core-framework-components)
- [Development Workflow](#development-workflow)
- [Testing and Validation](#testing-and-validation)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Development Environment Setup

### Prerequisites

**Required Software:**
- Python 3.13+ (managed via pyenv)
- uv (Python package manager)
- Git
- Node.js 18+ (for any frontend components)

**API Keys and Services:**
- OpenAI API key (for OpenAI models)
- Google AI API key (for Gemini models)
- Azure OpenAI credentials (for Azure models)
- Any domain-specific API keys for custom plugins

### Initial Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/thepollari/teal-agents.git
   cd teal-agents
   ```

2. **Set Up Python Environment:**
   ```bash
   # Ensure Python 3.13+ is available
   python --version
   
   # Install uv if not already installed
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Navigate to framework directory
   cd src/sk-agents
   
   # Install dependencies
   uv sync --dev
   ```

3. **Verify Installation:**
   ```bash
   # Check that dependencies are installed
   uv run python -c "import semantic_kernel; print('SK installed successfully')"
   uv run python -c "import fastapi; print('FastAPI installed successfully')"
   ```

### Environment Configuration

#### Core Environment Variables

Create a `.env` file in the project root or set environment variables:

```bash
# Required: API keys for LLM providers
export TA_API_KEY=your_primary_api_key
export OPENAI_API_KEY=your_openai_key  # If using OpenAI models
export GOOGLE_AI_API_KEY=your_gemini_key  # If using Gemini models

# Required: Agent configuration
export TA_SERVICE_CONFIG=/absolute/path/to/config.yaml

# Optional: Custom completion factory
export TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE=/absolute/path/to/completion_factory.py

# Optional: Remote plugin catalog
export TA_REMOTE_PLUGIN_PATH=/absolute/path/to/remote-plugin-catalog.yaml

# Optional: Telemetry and monitoring
export TA_TELEMETRY_ENABLED=true
export TA_OTEL_ENDPOINT=your_telemetry_endpoint
export TA_LOG_LEVEL=info  # debug, info, warning, error

# Optional: Environment stores (for complex configurations)
export TA_ENV_STORE='{"KEY1": "value1", "KEY2": "value2"}'
export TA_ENV_GLOBAL_STORE='{"GLOBAL_KEY": "global_value"}'
```

#### AppConfig Usage Patterns

The framework uses `AppConfig` from `ska_utils` for configuration management:

```python
from ska_utils import AppConfig, Config

# Define configuration requirements
MY_CONFIG = Config(
    env_name="MY_CUSTOM_CONFIG",
    is_required=True,
    default_value="default_value"
)

# Add to AppConfig
AppConfig.add_config(MY_CONFIG)

# Access configuration
app_config = AppConfig()
value = app_config.get("MY_CUSTOM_CONFIG")
```

**Key AppConfig Features:**
- Singleton pattern ensures consistent configuration access
- Environment variable validation and default values
- JSON parsing for complex configuration objects
- Automatic .env file loading

## Repository Structure

### Directory Organization

```
teal-agents/
├── shared/ska_utils/              # Shared utilities library
│   ├── src/ska_utils/            # Core utilities
│   │   ├── app_config.py         # Configuration management
│   │   ├── telemetry.py          # OpenTelemetry integration
│   │   ├── module_loader.py      # Dynamic module loading
│   │   └── standardized_dates.py # Date/time utilities
│   └── tests/                    # Utility tests
├── src/sk-agents/                # Core agent framework
│   ├── src/sk_agents/            # Framework source code
│   │   ├── app.py                # FastAPI application entry point
│   │   ├── routes.py             # API route generation
│   │   ├── skagents/             # Agent builders and handlers
│   │   │   ├── v1/               # Version 1 agent builders
│   │   │   ├── kernel_builder.py # Semantic Kernel setup
│   │   │   └── remote_plugin_loader.py # Plugin loading
│   │   ├── chat_completion/      # LLM provider integrations
│   │   │   ├── custom/           # Custom completion factories
│   │   │   └── factory.py        # Base factory classes
│   │   ├── authorization/        # Authentication and authorization
│   │   ├── state/                # State management
│   │   └── utils/                # Framework utilities
│   ├── docs/demos/               # Demo configurations
│   └── tests/                    # Framework tests
└── src/orchestrators/            # Agent orchestration services
    ├── assistant-orchestrator/   # Single-agent orchestration
    │   ├── orchestrator/         # Orchestrator service
    │   └── example/              # Working agent implementations
    ├── collab-orchestrator/      # Multi-agent collaboration
    └── workflow-orchestrator/    # Complex workflows
```

### Key Files and Their Purposes

**Framework Core:**
- `app.py`: FastAPI application with automatic route generation
- `routes.py`: Route generation logic for REST, SSE, WebSocket, and A2A
- `kernel_builder.py`: Semantic Kernel configuration and plugin loading
- `agent_builder.py`: Agent construction from YAML configurations

**Shared Infrastructure:**
- `app_config.py`: Centralized configuration management
- `telemetry.py`: OpenTelemetry setup for observability
- `module_loader.py`: Dynamic loading of plugins and completion factories

## Core Framework Components

### Agent Builder Architecture

The framework uses a builder pattern for agent construction:

```python
from sk_agents.skagents.v1.agent_builder import AgentBuilder
from sk_agents.skagents.kernel_builder import KernelBuilder

# Build kernel with plugins
kernel_builder = KernelBuilder(app_config)
kernel = kernel_builder.build_kernel_from_config(agent_config)

# Build agent from configuration
agent_builder = AgentBuilder()
agent = agent_builder.build_agent_from_config(agent_config, kernel)
```

**Key Builder Components:**
- **KernelBuilder**: Sets up Semantic Kernel with plugins and completion services
- **AgentBuilder**: Constructs agents from YAML configuration
- **ChatCompletionBuilder**: Manages LLM provider integrations
- **PluginLoader**: Handles local and remote plugin loading

### Plugin System Architecture

The framework supports two types of plugins:

#### Local/Custom Plugins

```python
from semantic_kernel import kernel_function

class CustomPlugin:
    @kernel_function(description="Custom function description")
    def custom_function(self, parameter: str) -> str:
        """
        Implement custom logic here.
        
        Args:
            parameter: Input parameter
            
        Returns:
            Processed result
        """
        return f"Processed: {parameter}"
```

**Plugin Registration:**
1. Create plugin class with `@kernel_function` decorators
2. Add plugin to agent configuration:
   ```yaml
   plugins:
     - CustomPlugin
   ```
3. Ensure plugin is importable from agent directory

#### Remote Plugins (OpenAPI)

```yaml
# remote-plugin-catalog.yaml
remote_plugins:
  - plugin_name: weather_api
    openapi_json_path: ./openapi_weather.json
    server_url: https://api.weather.com
```

**Remote Plugin Configuration:**
1. Obtain OpenAPI specification for target API
2. Define plugin in remote catalog
3. Reference in agent configuration:
   ```yaml
   remote_plugins:
     - weather_api
   ```
4. Set `TA_REMOTE_PLUGIN_PATH` environment variable

### Completion Factory System

Custom completion factories enable integration with any LLM provider:

```python
from sk_agents.ska_types import ChatCompletionFactory, ModelType

class CustomChatCompletionFactory(ChatCompletionFactory):
    def __init__(self, app_config: AppConfig):
        super().__init__(app_config)
        self.api_key = app_config.get("CUSTOM_API_KEY")
    
    def get_chat_completion_for_model_name(self, model_name: str, service_id: str):
        # Return appropriate chat completion client
        pass
    
    def get_model_type_for_name(self, model_name: str) -> ModelType:
        # Return model type classification
        pass
```

**Factory Integration:**
1. Implement `ChatCompletionFactory` interface
2. Set `TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE` to factory file path
3. Configure model names in agent YAML

## Development Workflow

### Creating a New Agent

1. **Choose Base Configuration:**
   ```bash
   # Start with a demo configuration
   cp -r src/sk-agents/docs/demos/01_getting_started src/orchestrators/assistant-orchestrator/example/my-agent
   cd src/orchestrators/assistant-orchestrator/example/my-agent
   ```

2. **Customize Configuration:**
   ```yaml
   # config.yaml
   apiVersion: skagents/v1
   kind: Sequential
   description: My custom agent
   service_name: MyAgent
   version: 0.1
   input_type: BaseInput
   spec:
     agents:
       - name: default
         role: My Agent Role
         model: gpt-4o
         system_prompt: Custom instructions
         plugins:
           - MyCustomPlugin
     tasks:
       - name: my_task
         description: Task description
         instructions: Task instructions
         agent: default
   ```

3. **Develop Custom Plugins:**
   ```python
   # custom_plugins.py
   from semantic_kernel import kernel_function
   
   class MyCustomPlugin:
       @kernel_function(description="My custom function")
       def my_function(self, input_text: str) -> str:
           return f"Processed: {input_text}"
   ```

4. **Set Environment Variables:**
   ```bash
   export TA_SERVICE_CONFIG=/absolute/path/to/my-agent/config.yaml
   export TA_API_KEY=your_api_key
   ```

5. **Test the Agent:**
   ```bash
   cd src/sk-agents
   uv run uvicorn sk_agents.app:app --host 0.0.0.0 --port 8000
   ```

### Development Best Practices

#### Code Organization

- **Separation of Concerns**: Keep configuration, plugins, and UI components separate
- **Consistent Naming**: Use descriptive names for agents, plugins, and functions
- **Documentation**: Document all custom plugins and configuration patterns
- **Version Control**: Use semantic versioning for agent configurations

#### Configuration Management

- **Absolute Paths**: Always use absolute paths for configuration files
- **Environment Variables**: Use environment variables for sensitive data
- **Validation**: Validate configuration before deployment
- **Defaults**: Provide sensible defaults for optional parameters

#### Plugin Development

- **Type Hints**: Use type hints for all plugin function parameters and returns
- **Error Handling**: Implement robust error handling and user-friendly messages
- **Documentation**: Provide clear descriptions for all kernel functions
- **Testing**: Write unit tests for plugin functionality

## Testing and Validation

### Linting and Code Quality

```bash
# Run linting
cd src/sk-agents
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check . --fix

# Format code
uv run ruff format .
```

### Unit Testing

```bash
# Run all tests
cd src/sk-agents
uv run pytest

# Run specific test file
uv run pytest tests/test_specific.py

# Run with coverage
uv run pytest --cov=sk_agents
```

### Integration Testing

```bash
# Test agent configuration loading
uv run python -c "
from sk_agents.skagents import load_config
config = load_config('/path/to/config.yaml')
print('Configuration loaded successfully')
"

# Test plugin loading
uv run python -c "
from custom_plugins import MyPlugin
plugin = MyPlugin()
print('Plugin loaded successfully')
"
```

### Manual Testing Workflow

1. **Configuration Validation:**
   ```bash
   # Validate YAML syntax
   python -c "import yaml; yaml.safe_load(open('config.yaml'))"
   
   # Test configuration loading
   export TA_SERVICE_CONFIG=/path/to/config.yaml
   cd src/sk-agents
   uv run python -c "from sk_agents.app import app; print('App loaded successfully')"
   ```

2. **API Testing:**
   ```bash
   # Start agent
   uv run uvicorn sk_agents.app:app --host 0.0.0.0 --port 8000
   
   # Test endpoints
   curl http://localhost:8000/.well-known/agent.json
   curl -X POST http://localhost:8000/invoke -H "Content-Type: application/json" -d '{"chat_history": [{"role": "user", "content": "Hello"}]}'
   ```

3. **Plugin Testing:**
   ```bash
   # Test plugin functions directly
   python -c "
   from custom_plugins import MyPlugin
   plugin = MyPlugin()
   result = plugin.my_function('test input')
   print(f'Plugin result: {result}')
   "
   ```

## Troubleshooting

### Common Development Issues

#### Configuration Loading Errors

**Problem**: `Cannot load configuration file`
**Causes**:
- Relative paths in environment variables
- Missing configuration files
- Invalid YAML syntax

**Solutions**:
```bash
# Use absolute paths
export TA_SERVICE_CONFIG=/absolute/path/to/config.yaml

# Validate YAML syntax
python -c "import yaml; print(yaml.safe_load(open('config.yaml')))"

# Check file permissions
ls -la /path/to/config.yaml
```

#### Plugin Import Errors

**Problem**: `Plugin not found` or `Import error`
**Causes**:
- Plugin class not properly defined
- Missing `@kernel_function` decorators
- Import path issues

**Solutions**:
```bash
# Test plugin import
python -c "from custom_plugins import PluginName; print('Import successful')"

# Check plugin class structure
python -c "
from custom_plugins import PluginName
import inspect
print(inspect.getmembers(PluginName, predicate=inspect.ismethod))
"

# Verify kernel function decorators
python -c "
from custom_plugins import PluginName
plugin = PluginName()
print(hasattr(plugin, '__kernel_function__'))
"
```

#### API Key and Authentication Issues

**Problem**: `Invalid API key` or `Authentication failed`
**Causes**:
- Missing or incorrect API keys
- Quota exceeded
- Wrong environment variable names

**Solutions**:
```bash
# Verify environment variables
echo $TA_API_KEY
echo $OPENAI_API_KEY

# Test API key directly
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models

# Check quota and usage
# (Provider-specific commands)
```

#### Dependency and Environment Issues

**Problem**: Import errors or missing dependencies
**Causes**:
- Incomplete dependency installation
- Python version compatibility
- Virtual environment issues

**Solutions**:
```bash
# Reinstall dependencies
cd src/sk-agents
uv sync --dev --force

# Check Python version
python --version

# Verify key dependencies
uv run python -c "import semantic_kernel, fastapi, pydantic; print('Core dependencies OK')"

# Check uv environment
uv run python -c "import sys; print(sys.path)"
```

### Debugging Techniques

#### Enable Debug Logging

```bash
export TA_LOG_LEVEL=debug
export TA_TELEMETRY_ENABLED=true
```

#### Use Interactive Debugging

```python
# Add to code for debugging
import pdb; pdb.set_trace()

# Or use ipdb for better interface
import ipdb; ipdb.set_trace()
```

#### Test Components Individually

```bash
# Test configuration loading
python -c "
from ska_utils import AppConfig
from sk_agents.configs import TA_API_KEY
AppConfig.add_config(TA_API_KEY)
config = AppConfig()
print(f'API Key configured: {bool(config.get(TA_API_KEY.env_name))}')
"

# Test kernel building
python -c "
from sk_agents.skagents.kernel_builder import KernelBuilder
from ska_utils import AppConfig
builder = KernelBuilder(AppConfig())
print('KernelBuilder created successfully')
"
```

## Best Practices

### Development Practices

1. **Use Version Control Effectively**:
   - Create feature branches for new agents or major changes
   - Write descriptive commit messages
   - Use pull requests for code review

2. **Configuration Management**:
   - Keep sensitive data in environment variables
   - Use absolute paths for file references
   - Validate configurations before deployment
   - Document configuration options

3. **Code Quality**:
   - Follow PEP 8 style guidelines
   - Use type hints consistently
   - Write comprehensive docstrings
   - Implement error handling

4. **Testing Strategy**:
   - Write unit tests for custom plugins
   - Test configuration loading
   - Validate API endpoints
   - Test error scenarios

### Performance Optimization

1. **Plugin Efficiency**:
   - Cache expensive operations
   - Use async/await for I/O operations
   - Implement proper error handling
   - Optimize API calls

2. **Configuration Optimization**:
   - Use appropriate model sizes
   - Configure reasonable timeouts
   - Implement rate limiting
   - Monitor resource usage

3. **Deployment Considerations**:
   - Use production-grade WSGI servers
   - Implement health checks
   - Configure logging and monitoring
   - Plan for horizontal scaling

### Security Best Practices

1. **API Key Management**:
   - Never commit API keys to version control
   - Use environment variables or secure vaults
   - Rotate keys regularly
   - Monitor usage and quotas

2. **Input Validation**:
   - Validate all user inputs
   - Sanitize data before processing
   - Implement rate limiting
   - Use HTTPS in production

3. **Access Control**:
   - Implement authentication where needed
   - Use authorization for sensitive operations
   - Log access and operations
   - Monitor for suspicious activity

## Additional Resources

### Documentation References

- [AGENT_DEVELOPMENT.md](AGENT_DEVELOPMENT.md) - Step-by-step agent creation
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Comprehensive testing strategies
- [University Agent README](src/orchestrators/assistant-orchestrator/example/university/README.md) - Reference implementation
- [Demo Configurations](src/sk-agents/docs/demos/README.md) - Learning materials

### External Resources

- [Semantic Kernel Documentation](https://learn.microsoft.com/en-us/semantic-kernel/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)

### Community and Support

- GitHub Issues: Report bugs and request features
- Discussions: Ask questions and share experiences
- Contributing Guidelines: See [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Last Updated**: [Current Date]
**Version**: 1.0
**Maintainer**: Teal Agents Development Team
