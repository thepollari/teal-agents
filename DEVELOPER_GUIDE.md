# Teal Agents Framework - Developer Guide

## Overview

This guide provides comprehensive instructions for setting up a development environment and working with the Teal Agents Framework. Whether you're contributing to the framework or building agents, this guide will help you get started quickly.

## Prerequisites

### System Requirements
- **Python**: 3.11 or higher (3.13+ recommended)
- **Package Manager**: [uv](https://docs.astral.sh/uv/) (preferred) or pip
- **Git**: For version control and repository management
- **Docker**: Optional, for orchestrator examples and services
- **Redis**: Optional, for stateful agents and orchestration

### API Keys
You'll need API keys for the LLM providers you plan to use:
- **OpenAI**: For GPT models (gpt-4o, gpt-4o-mini)
- **Anthropic**: For Claude models (claude-3-sonnet, claude-3-haiku)
- **Google**: For Gemini models (gemini-pro, gemini-flash)

## Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/thepollari/teal-agents.git
cd teal-agents
```

### 2. Install uv Package Manager

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Alternative: pip install uv
pip install uv
```

### 3. Set Up Core Framework

```bash
cd src/sk-agents
uv sync --dev
```

This installs all dependencies including development tools like pytest, ruff, and mypy.

### 4. Configure Environment Variables

Create a `.env` file in the `src/sk-agents` directory:

```bash
# Core configuration
TA_SERVICE_CONFIG=docs/demos/01_getting_started/config.yaml

# API Keys (choose your provider)
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_API_KEY=your_google_api_key

# Optional: Custom completion factory
TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE=/path/to/custom_factory.py
TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS=CustomChatCompletionFactory

# Optional: State management
TA_STATE_MANAGEMENT=redis  # or in-memory
TA_REDIS_HOST=localhost
TA_REDIS_PORT=6379
TA_REDIS_DB=0

# Optional: Telemetry
TA_TELEMETRY_ENABLED=false
TA_OTEL_ENDPOINT=http://localhost:4317
```

### 5. Verify Installation

```bash
# Run linting
uv run ruff check .

# Run tests
uv run pytest

# Start a demo agent
export TA_SERVICE_CONFIG=docs/demos/01_getting_started/config.yaml
uv run uvicorn sk_agents.app:app --host 0.0.0.0 --port 8000
```

Test the agent:
```bash
curl -X POST http://localhost:8000/SimpleAgent/1.0/ \
  -H "Content-Type: application/json" \
  -d '{"chat_history": [{"role": "user", "content": "Hello!"}]}'
```

## Development Workflows

### Working with the Core Framework

#### Project Structure
```
src/sk-agents/
├── src/sk_agents/           # Framework source code
│   ├── app.py              # Main FastAPI application
│   ├── appv1.py            # V1 agent execution
│   ├── appv2.py            # V2 multi-modal agents
│   ├── appv3.py            # V3 stateful agents
│   ├── ska_types.py        # Core types and interfaces
│   ├── routes.py           # API route definitions
│   ├── skagents/           # Agent builders and handlers
│   ├── tealagents/         # V3 agent implementations
│   └── utils.py            # Utility functions
├── docs/demos/             # Demo configurations
├── tests/                  # Test suite
└── pyproject.toml         # Project configuration
```

#### Code Style and Linting

The project uses `ruff` for linting and formatting:

```bash
# Check code style
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check . --fix

# Format code
uv run ruff format .
```

#### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_agent_handler.py

# Run with coverage
uv run pytest --cov=sk_agents

# Run tests with verbose output
uv run pytest -v
```

#### Type Checking

```bash
# Run mypy type checking
uv run mypy src/sk_agents
```

### Working with Orchestrators

#### Assistant Orchestrator Setup

```bash
cd src/orchestrators/assistant-orchestrator/example
```

Follow the specific README instructions for each orchestrator example.

#### Collaboration Orchestrator Setup

```bash
cd src/orchestrators/collab-orchestrator/orchestrator
```

See the orchestrator-specific documentation for setup instructions.

### Working with Shared Utilities

```bash
cd shared/ska_utils
uv sync --dev

# Run utility tests
uv run pytest
```

## Development Best Practices

### Code Organization

1. **Follow existing patterns**: Study existing code before adding new features
2. **Use type hints**: All new code should include proper type annotations
3. **Write tests**: Add tests for new functionality
4. **Document changes**: Update relevant documentation

### Configuration Management

1. **Use AppConfig**: Leverage the shared configuration system
2. **Environment variables**: Follow the `TA_*` naming convention
3. **Default values**: Provide sensible defaults for optional settings
4. **Validation**: Validate configuration values at startup

### Plugin Development

1. **Inherit from BasePlugin**: All plugins must extend the base class
2. **Use kernel_function decorator**: Mark plugin methods appropriately
3. **Handle errors gracefully**: Include proper error handling
4. **Document functions**: Provide clear descriptions for LLM usage

Example plugin structure:
```python
from sk_agents.ska_types import BasePlugin
from semantic_kernel import kernel_function

class MyPlugin(BasePlugin):
    def __init__(self, authorization: str | None = None):
        super().__init__(authorization)
    
    @kernel_function(description="Description for LLM")
    def my_function(self, param: str) -> str:
        """Detailed function documentation."""
        try:
            # Implementation
            return result
        except Exception as e:
            # Handle errors appropriately
            raise
```

### Testing Strategies

#### Unit Tests
- Test individual functions and classes
- Mock external dependencies
- Use pytest fixtures for common setup

#### Integration Tests
- Test complete agent workflows
- Use real API calls with test keys
- Verify end-to-end functionality

#### Mock Testing
```python
import pytest
from unittest.mock import Mock, patch

@patch('sk_agents.plugin_loader.load_plugin')
def test_plugin_loading(mock_load):
    mock_load.return_value = Mock()
    # Test implementation
```

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Ensure you're in the correct directory
cd src/sk-agents

# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall dependencies
uv sync --dev
```

#### 2. API Key Issues
```bash
# Verify environment variables
echo $OPENAI_API_KEY

# Check .env file loading
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"
```

#### 3. Configuration Errors
```bash
# Verify config file exists
ls -la docs/demos/01_getting_started/config.yaml

# Check config parsing
python -c "from pydantic_yaml import parse_yaml_file_as; from sk_agents.ska_types import BaseConfig; print(parse_yaml_file_as(BaseConfig, 'docs/demos/01_getting_started/config.yaml'))"
```

#### 4. Plugin Loading Issues
```bash
# Check plugin directory structure
ls -la plugins/

# Verify plugin class names
grep -r "class.*Plugin" plugins/
```

#### 5. Redis Connection Issues
```bash
# Check Redis status
redis-cli ping

# Verify Redis configuration
python -c "import redis; r = redis.Redis(host='localhost', port=6379, db=0); print(r.ping())"
```

### Debugging Techniques

#### 1. Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 2. Use Debugger
```python
import pdb; pdb.set_trace()  # Add breakpoint
```

#### 3. Test Individual Components
```bash
# Test specific agent handler
python -c "from sk_agents.skagents.v1.agent_builder import AgentBuilder; print('Import successful')"
```

#### 4. Validate Configuration
```bash
# Parse and validate config
python -c "
from pydantic_yaml import parse_yaml_file_as
from sk_agents.ska_types import BaseConfig
config = parse_yaml_file_as(BaseConfig, 'your_config.yaml')
print(f'Valid config: {config.name}')
"
```

## IDE Setup

### VS Code Configuration

Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "ruff",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"]
}
```

### PyCharm Configuration

1. Set Python interpreter to `.venv/bin/python`
2. Configure ruff as external tool
3. Set up pytest as test runner
4. Enable type checking with mypy

## Performance Optimization

### Development Performance

1. **Use uv**: Faster than pip for dependency management
2. **Parallel testing**: Use `pytest -n auto` for parallel test execution
3. **Incremental type checking**: Use mypy daemon for faster type checking

### Agent Performance

1. **Streaming responses**: Use WebSocket endpoints for real-time interaction
2. **Connection pooling**: Reuse HTTP connections for external APIs
3. **Caching**: Cache plugin results and model responses when appropriate
4. **Async operations**: Use async/await for I/O operations

## Contributing Workflow

### 1. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes
- Follow code style guidelines
- Add tests for new functionality
- Update documentation

### 3. Run Quality Checks
```bash
# Lint and format
uv run ruff check . --fix
uv run ruff format .

# Type check
uv run mypy src/sk_agents

# Run tests
uv run pytest
```

### 4. Commit Changes
```bash
git add .
git commit -m "feat: add new feature description"
```

### 5. Push and Create PR
```bash
git push origin feature/your-feature-name
# Create pull request on GitHub
```

## Additional Resources

- **[Agent Development Guide](AGENT_DEVELOPMENT.md)**: Step-by-step agent creation
- **[Testing Guide](TESTING_GUIDE.md)**: Comprehensive testing strategies
- **[Demo Documentation](src/sk-agents/docs/demos/README.md)**: Learning path through examples
- **[Contributing Guidelines](CONTRIBUTING.md)**: Contribution process and standards
- **[University Agent Example](src/orchestrators/assistant-orchestrator/example/university/README.md)**: Complete working agent implementation

## Getting Help

- **GitHub Issues**: Report bugs and request features
- **Discussions**: Ask questions and share ideas
- **Documentation**: Check existing docs and examples
- **Code Review**: Learn from existing implementations

For specific questions about development setup or contribution process, please create an issue on GitHub with the `question` label.
