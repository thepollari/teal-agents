# Contributing to Teal Agents

We welcome contributions to the Teal Agents project! This document provides comprehensive guidelines for contributing to the project, including development setup, coding standards, testing requirements, and submission processes.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Environment Setup](#development-environment-setup)
- [Code Organization and Standards](#code-organization-and-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation Standards](#documentation-standards)
- [Submission Process](#submission-process)
- [Review Process](#review-process)
- [Community Guidelines](#community-guidelines)

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.13+ installed (managed via pyenv recommended)
- uv (Python package manager)
- Git configured with your name and email
- A GitHub account for submitting pull requests

### Initial Setup

1. **Fork the Repository**
   ```bash
   # Fork via GitHub UI, then clone your fork
   git clone https://github.com/YOUR_USERNAME/teal-agents.git
   cd teal-agents
   ```

2. **Set Up Remote**
   ```bash
   git remote add upstream https://github.com/thepollari/teal-agents.git
   git fetch upstream
   ```

3. **Create Development Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

## Development Environment Setup

### Core Dependencies

1. **Install uv Package Manager**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source ~/.bashrc  # or restart terminal
   ```

2. **Install Project Dependencies**
   ```bash
   cd src/sk-agents
   uv sync --dev
   ```

3. **Verify Installation**
   ```bash
   uv run python -c "import semantic_kernel, fastapi; print('Dependencies installed successfully')"
   ```

### Environment Configuration

1. **Set Up Environment Variables**
   ```bash
   # Create .env file for development
   cat > .env << EOF
   TA_API_KEY=your_test_api_key
   TA_LOG_LEVEL=debug
   TA_TELEMETRY_ENABLED=false
   EOF
   ```

2. **Configure Git Hooks** (Optional but recommended)
   ```bash
   # Set up pre-commit hooks for code quality
   uv run pre-commit install
   ```

### Development Tools

**Required Tools:**
- **Linting**: `ruff` for code formatting and linting
- **Type Checking**: `mypy` for static type analysis
- **Testing**: `pytest` with coverage reporting
- **Documentation**: `mkdocs` for documentation generation

**Verification Commands:**
```bash
# Lint code
cd src/sk-agents && uv run ruff check .

# Format code
cd src/sk-agents && uv run ruff format .

# Type checking
cd src/sk-agents && uv run mypy src/

# Run tests
cd src/sk-agents && uv run pytest
```

## Code Organization and Standards

### Project Structure

Understanding the project structure is crucial for effective contributions:

```
teal-agents/
├── shared/ska_utils/              # Shared utilities (AppConfig, Telemetry)
├── src/sk-agents/                 # Core framework
│   ├── src/sk_agents/            # Framework source code
│   │   ├── app.py                # FastAPI application
│   │   ├── routes.py             # API route generation
│   │   ├── skagents/             # Agent builders and handlers
│   │   └── chat_completion/      # LLM provider integrations
│   ├── docs/demos/               # Demo configurations
│   └── tests/                    # Test suites
└── src/orchestrators/            # Agent orchestration services
    ├── assistant-orchestrator/   # Single-agent orchestration
    └── collab-orchestrator/      # Multi-agent collaboration
```

### Coding Standards

#### Python Code Style

1. **Follow PEP 8**: Use `ruff` for automatic formatting
2. **Type Hints**: Always use type hints for function parameters and return values
3. **Docstrings**: Use Google-style docstrings for all public functions and classes
4. **Import Organization**: Group imports (standard library, third-party, local)

**Example Function:**
```python
from typing import Optional, List
import json

def process_university_data(
    universities: List[dict], 
    country_filter: Optional[str] = None
) -> str:
    """
    Process university data and return formatted JSON.
    
    Args:
        universities: List of university dictionaries
        country_filter: Optional country filter
        
    Returns:
        JSON string of processed universities
        
    Raises:
        ValueError: If universities list is empty
    """
    if not universities:
        raise ValueError("Universities list cannot be empty")
    
    filtered = universities
    if country_filter:
        filtered = [u for u in universities if u.get("country") == country_filter]
    
    return json.dumps(filtered, indent=2)
```

#### Configuration Standards

1. **YAML Configuration**: Follow consistent indentation (2 spaces)
2. **Environment Variables**: Use `TA_` prefix for framework variables
3. **Validation**: Always validate configuration inputs

**Example Configuration:**
```yaml
apiVersion: skagents/v1
kind: Sequential
description: >
  Clear, concise description of agent purpose
service_name: AgentName  # PascalCase, no spaces
version: 0.1.0
input_type: BaseInput
spec:
  agents:
    - name: default
      role: Descriptive agent role
      model: gpt-4o
      system_prompt: >
        Clear instructions for the agent.
        Include plugin usage guidelines.
      plugins:
        - PluginName
  tasks:
    - name: task_name
      description: Task description
      instructions: >
        Detailed task instructions
      agent: default
```

#### Plugin Development Standards

1. **Class Structure**: Use clear class names and organize functions logically
2. **Error Handling**: Implement comprehensive error handling
3. **Documentation**: Document all kernel functions with clear descriptions
4. **Testing**: Write unit tests for all plugin functions

**Example Plugin:**
```python
from semantic_kernel import kernel_function
from typing import Optional
import json
import httpx

class UniversityPlugin:
    """
    Plugin for searching and retrieving university information.
    
    This plugin integrates with the universities.hipolabs.com API
    to provide comprehensive university data.
    """
    
    def __init__(self):
        self.base_url = "http://universities.hipolabs.com"
    
    @kernel_function(description="Search for universities by name and/or country")
    def search_universities(
        self, 
        name: str = "", 
        country: str = ""
    ) -> str:
        """
        Search for universities using name and country filters.
        
        Args:
            name: University name to search for
            country: Country to filter by
            
        Returns:
            JSON string containing university results
        """
        try:
            params = {}
            if name:
                params["name"] = name
            if country:
                params["country"] = country
            
            with httpx.Client() as client:
                response = client.get(
                    f"{self.base_url}/search",
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                universities = response.json()
            
            return json.dumps(universities)
            
        except httpx.RequestError as e:
            return json.dumps({
                "error": f"Network error: {str(e)}",
                "query": {"name": name, "country": country}
            })
        except Exception as e:
            return json.dumps({
                "error": f"Unexpected error: {str(e)}",
                "query": {"name": name, "country": country}
            })
```

## Testing Requirements

### Test Coverage Requirements

- **Minimum Coverage**: 80% for new code
- **Critical Paths**: 95% coverage for core framework components
- **Plugin Functions**: 100% coverage for all kernel functions

### Testing Standards

1. **Unit Tests**: Test individual functions and classes in isolation
2. **Integration Tests**: Test component interactions and API endpoints
3. **End-to-End Tests**: Test complete agent workflows
4. **Performance Tests**: Test under realistic load conditions

### Test Structure

```python
# tests/unit/test_your_plugin.py
import pytest
import json
from unittest.mock import Mock, patch
from your_plugin import YourPlugin

class TestYourPlugin:
    """Comprehensive test suite for YourPlugin"""
    
    def setup_method(self):
        """Set up test fixtures before each test"""
        self.plugin = YourPlugin()
    
    def test_function_success(self):
        """Test successful function execution"""
        # Arrange
        expected_result = {"key": "value"}
        
        # Act
        result = self.plugin.your_function("test_input")
        data = json.loads(result)
        
        # Assert
        assert data == expected_result
    
    def test_function_error_handling(self):
        """Test function error handling"""
        with patch.object(self.plugin, '_helper_method') as mock_helper:
            mock_helper.side_effect = Exception("Test error")
            
            result = self.plugin.your_function("test_input")
            data = json.loads(result)
            
            assert "error" in data
            assert "Test error" in data["error"]
    
    @pytest.mark.parametrize("input_value,expected", [
        ("test1", "result1"),
        ("test2", "result2"),
        ("", "empty_result"),
    ])
    def test_function_parameters(self, input_value, expected):
        """Test function with various parameter combinations"""
        result = self.plugin.your_function(input_value)
        assert expected in result
```

### Running Tests

```bash
# Run all tests
cd src/sk-agents
uv run pytest

# Run with coverage
uv run pytest --cov=sk_agents --cov-report=html

# Run specific test categories
uv run pytest tests/unit/          # Unit tests only
uv run pytest tests/integration/   # Integration tests only
uv run pytest -m "not slow"       # Skip slow tests

# Run tests for specific component
uv run pytest tests/unit/test_plugins.py -v
```

## Documentation Standards

### Documentation Requirements

1. **Code Documentation**: All public functions and classes must have docstrings
2. **README Updates**: Update relevant README files for new features
3. **API Documentation**: Document new API endpoints and parameters
4. **Configuration Documentation**: Document new configuration options

### Documentation Style

1. **Markdown Format**: Use consistent Markdown formatting
2. **Code Examples**: Include working code examples
3. **Cross-References**: Link related documentation sections
4. **User Perspective**: Write from the user's perspective

## Submission Process

### Pre-Submission Checklist

Before submitting a pull request, ensure:

- [ ] Code follows project style guidelines
- [ ] All tests pass locally
- [ ] Code coverage meets requirements
- [ ] Documentation is updated
- [ ] Commit messages are clear and descriptive
- [ ] Branch is up-to-date with main branch

### Pull Request Process

1. **Update Your Branch**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run Quality Checks**
   ```bash
   cd src/sk-agents
   uv run ruff check . && uv run ruff format .
   uv run mypy src/
   uv run pytest --cov=sk_agents
   ```

3. **Commit Changes**
   ```bash
   git add specific_files  # Don't use git add .
   git commit -m "feat: add university search plugin
   
   - Implement UniversityPlugin with search functionality
   - Add comprehensive error handling and validation
   - Include unit tests with 95% coverage
   - Update documentation with usage examples"
   ```

4. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   # Create PR via GitHub UI
   ```

### Commit Message Standards

Use conventional commit format:

```
type(scope): brief description

Detailed description of changes made.

- Bullet point 1
- Bullet point 2

Closes #issue_number
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions or modifications
- `chore`: Maintenance tasks

## Review Process

### Review Criteria

Pull requests are reviewed based on:

1. **Code Quality**: Adherence to coding standards and best practices
2. **Functionality**: Correctness and completeness of implementation
3. **Testing**: Adequate test coverage and quality
4. **Documentation**: Clear and comprehensive documentation
5. **Performance**: No significant performance regressions
6. **Security**: No security vulnerabilities introduced

### Review Timeline

- **Initial Review**: Within 2-3 business days
- **Follow-up Reviews**: Within 1-2 business days
- **Merge**: After approval from at least one maintainer

### Addressing Review Feedback

1. **Respond Promptly**: Address feedback within a reasonable timeframe
2. **Ask Questions**: Seek clarification if feedback is unclear
3. **Make Changes**: Implement requested changes thoroughly
4. **Update Tests**: Ensure tests reflect any changes made
5. **Re-request Review**: Request re-review after making changes

## Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please:

- Be respectful and constructive in all interactions
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

### Communication Channels

- **GitHub Issues**: Bug reports, feature requests, and discussions
- **Pull Requests**: Code contributions and reviews
- **Discussions**: General questions and community discussions

### Getting Help

If you need help with:

- **Development Setup**: Check [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
- **Agent Creation**: Follow [AGENT_DEVELOPMENT.md](AGENT_DEVELOPMENT.md)
- **Testing**: Reference [TESTING_GUIDE.md](TESTING_GUIDE.md)
- **Specific Questions**: Open a GitHub issue or discussion

### Recognition

Contributors are recognized through:

- **Contributor List**: Maintained in project documentation
- **Release Notes**: Acknowledgment in release announcements
- **Community Highlights**: Featured contributions in project updates

## Troubleshooting Common Issues

### Development Environment Issues

**Issue**: Dependencies not installing correctly
```bash
# Solution: Clean and reinstall
cd src/sk-agents
rm -rf .venv
uv sync --dev
```

**Issue**: Tests failing locally
```bash
# Solution: Check environment variables and dependencies
export TA_API_KEY=test_key
uv run pytest -v
```

**Issue**: Linting errors
```bash
# Solution: Auto-fix formatting issues
uv run ruff check . --fix
uv run ruff format .
```

### Git Workflow Issues

**Issue**: Branch out of sync with main
```bash
# Solution: Rebase on latest main
git fetch upstream
git rebase upstream/main
```

**Issue**: Merge conflicts
```bash
# Solution: Resolve conflicts manually
git status  # See conflicted files
# Edit files to resolve conflicts
git add resolved_files
git rebase --continue
```

## Advanced Contribution Topics

### Creating New Orchestrators

When contributing new orchestrators:

1. Follow the existing orchestrator structure
2. Implement required interfaces
3. Add comprehensive tests
4. Document configuration options
5. Provide example implementations

### Adding LLM Provider Support

When adding new LLM providers:

1. Implement `ChatCompletionFactory` interface
2. Add model validation and capability detection
3. Handle provider-specific authentication
4. Include comprehensive error handling
5. Add integration tests with mocked responses

### Framework Extensions

When extending core framework functionality:

1. Maintain backward compatibility
2. Follow existing architectural patterns
3. Add comprehensive documentation
4. Include migration guides if needed
5. Coordinate with maintainers for major changes

---

**Thank you for contributing to Teal Agents!**

Your contributions help make the framework better for everyone. If you have questions or need assistance, don't hesitate to reach out through GitHub issues or discussions.

**Last Updated**: [Current Date]
**Version**: 1.0
**Maintainer**: Teal Agents Development Team
