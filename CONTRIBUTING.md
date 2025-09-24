# Contributing to Teal Agents Framework

A big welcome and thank you for considering contributing to the Teal Agents open source project! It's people like you
that make it a reality for users in our community.

Reading and following these guidelines will help us make the contribution process easy and effective for everyone
involved. It also communicates that you agree to respect the time of the developers managing and developing these open
source projects. In return, we will reciprocate that respect by addressing your issue, assessing changes, and helping
you finalize your pull requests.

## Quicklinks

* [Code of Conduct](#code-of-conduct)
* [Getting Started](#getting-started)
    * [Issues](#issues)
    * [Pull Requests](#pull-requests)
* [Development Guidelines](#development-guidelines)
* [Teal Agents Specific Guidelines](#teal-agents-specific-guidelines)
* [Testing Requirements](#testing-requirements)
* [Documentation Standards](#documentation-standards)
* [Getting Help](#getting-help)

## Code of Conduct

We take our open source community seriously and hold ourselves and other contributors to high standards of
communication. By participating and contributing to this project, you agree to uphold our
[Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

Contributions are made to this repo via Issues and Pull Requests (PRs). A few general guidelines that cover both:

- Search for existing Issues and PRs before creating your own.
- We work hard to makes sure issues are handled in a timely manner but, depending on the impact, it could take a while
  to investigate the root cause. A friendly ping in the comment thread to the submitter or a contributor can help draw
  attention if your issue is blocking.

### Issues

Issues should be used to report problems with the framework, request a new feature, or to discuss potential changes
before a PR is created. When you create a new Issue, a template will be loaded that will guide you through collecting
and providing the information we need to investigate.

**Issue Categories**:
- **Bug Reports**: Problems with existing functionality
- **Feature Requests**: New capabilities or enhancements
- **Documentation**: Improvements to documentation
- **Agent Examples**: New demo configurations or working agents
- **Plugin Development**: New plugins or plugin improvements
- **Performance**: Performance-related issues or optimizations

If you find an Issue that addresses the problem you're having, please add your own reproduction information to the
existing issue rather than creating a new one. Adding a
[reaction](https://github.blog/2016-03-10-add-reactions-to-pull-requests-issues-and-comments/) can also help be
indicating to our maintainers that a particular problem is affecting more than just the reporter.

### Pull Requests

PRs to our framework are always welcome and can be a quick way to get your fix or improvement slated for the next
release. In general, PRs should:

- Only fix/add the functionality in question **OR** address wide-spread whitespace/style issues, not both.
- Add unit or integration tests for fixed or changed functionality (if a test suite already exists).
- Address a single concern in the least number of changed lines as possible.
- Include documentation in the repo.
- Be accompanied by a complete Pull Request template (loaded automatically when a PR is created).

For changes that address core functionality or would require breaking changes (e.g. a major release), it's best to open
an Issue to discuss your proposal first. This is not required but can save time creating and reviewing changes.

In general, we follow the ["fork-and-pull" Git workflow](https://github.com/susam/gitpr)

1. Fork the repository to your own Github account
2. Clone the project to your machine
3. Create a branch locally with a succinct but descriptive name
4. Commit changes to the branch
5. Following any formatting and testing guidelines specific to this repo
6. Push changes to your fork
7. Open a PR in our repository and follow the PR template so that we can efficiently review the changes.

## Development Guidelines

### Environment Setup

Before contributing, set up your development environment following the [Developer Guide](DEVELOPER_GUIDE.md):

```bash
# Clone and setup
git clone https://github.com/thepollari/teal-agents.git
cd teal-agents/src/sk-agents
uv sync --dev

# Install pre-commit hooks (recommended)
uv run pre-commit install
```

### Code Quality Standards

#### Linting and Formatting
We use `ruff` for both linting and formatting:

```bash
# Check code style
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check . --fix

# Format code
uv run ruff format .
```

#### Type Checking
All code should include proper type hints:

```bash
# Run type checking
uv run mypy src/sk_agents
```

#### Code Style Guidelines
- **Follow PEP 8**: Use consistent Python code style
- **Type hints**: Add type annotations to all functions and methods
- **Docstrings**: Use Google-style docstrings for all public functions
- **Error handling**: Implement comprehensive error handling with appropriate logging
- **Imports**: Organize imports (standard library, third-party, local)

Example code style:
```python
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

def process_data(input_data: str, options: Optional[dict] = None) -> List[str]:
    """Process input data with optional configuration.
    
    Args:
        input_data: Raw input string to process
        options: Optional configuration dictionary
        
    Returns:
        List of processed data strings
        
    Raises:
        ValueError: If input_data is empty or invalid
    """
    if not input_data.strip():
        raise ValueError("Input data cannot be empty")
    
    try:
        # Processing logic here
        result = []
        return result
    except Exception as e:
        logger.error(f"Failed to process data: {e}")
        raise
```

## Teal Agents Specific Guidelines

### Framework Architecture Understanding

Before contributing to core framework components, understand the architecture:

- **App Routing**: `app.py` routes to AppV1/V2/V3 based on `apiVersion`
- **Agent Handlers**: Each app version has specific handler patterns
- **Plugin System**: Plugins inherit from `BasePlugin` and use `@kernel_function`
- **Configuration**: YAML-driven configuration with Pydantic validation
- **State Management**: Support for both in-memory and Redis state storage

### Component-Specific Guidelines

#### Core Framework (`src/sk-agents/src/sk_agents/`)
- **Maintain backward compatibility** when modifying existing APIs
- **Add comprehensive tests** for new functionality
- **Update type definitions** in `ska_types.py` for new interfaces
- **Document configuration changes** in relevant demo configurations

#### Plugin Development
- **Inherit from BasePlugin**: All plugins must extend the base class
- **Use kernel_function decorator**: Mark plugin methods for LLM usage
- **Handle errors gracefully**: Include proper error handling and logging
- **Add comprehensive docstrings**: Describe function purpose for LLM understanding
- **Test with real APIs**: Include integration tests with actual API calls

Example plugin structure:
```python
from sk_agents.ska_types import BasePlugin
from semantic_kernel import kernel_function
import logging

logger = logging.getLogger(__name__)

class MyPlugin(BasePlugin):
    """Plugin for [specific functionality]."""
    
    def __init__(self, authorization: Optional[str] = None):
        super().__init__(authorization)
        # Plugin-specific initialization
    
    @kernel_function(
        description="Clear description for LLM usage",
        name="descriptive_function_name"
    )
    def my_function(self, param: str) -> str:
        """Detailed function documentation.
        
        Args:
            param: Description of parameter
            
        Returns:
            Description of return value
        """
        try:
            # Implementation
            return result
        except Exception as e:
            logger.error(f"Plugin function failed: {e}")
            return f"Error: {str(e)}"
```

#### Agent Development
- **Follow configuration patterns**: Use existing YAML schema patterns
- **Document thoroughly**: Include comprehensive README using [Agent Template](AGENT_TEMPLATE.md)
- **Add UI components**: Consider Streamlit or web interfaces for user interaction
- **Include examples**: Provide clear usage examples and API calls

#### Orchestrator Development
- **Understand orchestration patterns**: Study existing Assistant and Collaboration orchestrators
- **Support standard interfaces**: Ensure compatibility with agent catalog and discovery
- **Add comprehensive configuration**: Document all configuration options
- **Include deployment examples**: Provide Docker and production deployment examples

### Configuration Management

#### Environment Variables
Follow the `TA_*` naming convention:
```bash
TA_SERVICE_CONFIG=path/to/config.yaml
TA_STATE_MANAGEMENT=redis
TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE=path/to/factory.py
```

#### YAML Configuration
Use consistent YAML structure:
```yaml
apiVersion: skagents/v2alpha1  # Use appropriate version
kind: Agent
name: MyAgent
version: 1.0
metadata:
  description: "Clear agent description"
  skills:
    - id: "skill_id"
      name: "Skill Name"
      description: "What this skill does"
spec:
  model: gpt-4o
  system_prompt: |
    Clear instructions for agent behavior
  plugins:
    - PluginName
```

## Testing Requirements

### Test Coverage
All contributions must include appropriate tests:

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **Plugin Tests**: Test plugin functionality with mocked external APIs
- **Configuration Tests**: Test YAML parsing and validation

### Test Structure
```bash
tests/
├── test_[component].py     # Unit tests
├── test_integration.py     # Integration tests
├── fixtures/               # Test data and configurations
└── custom/                 # Custom test utilities
```

### Running Tests
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=sk_agents --cov-report=html

# Run specific test categories
uv run pytest -m "not integration"  # Unit tests only
uv run pytest -m integration        # Integration tests only
```

### Test Guidelines
- **Mock external dependencies**: Don't make real API calls in unit tests
- **Use realistic test data**: Test data should match real-world scenarios
- **Test error conditions**: Include tests for failure scenarios
- **Maintain test independence**: Tests should not depend on each other
- **Use descriptive test names**: Test names should clearly describe what they test

## Documentation Standards

### Code Documentation
- **Docstrings**: All public functions, classes, and modules must have docstrings
- **Type hints**: Include comprehensive type annotations
- **Inline comments**: Use sparingly, only for complex logic
- **README files**: Each major component should have a README

### User Documentation
- **Agent documentation**: Use the [Agent Template](AGENT_TEMPLATE.md) for new agents
- **Demo documentation**: Include clear setup and usage instructions
- **API documentation**: Document all endpoints and parameters
- **Configuration documentation**: Explain all configuration options

### Documentation Updates
When making changes that affect user-facing functionality:
- **Update relevant README files**
- **Add or update demo configurations**
- **Update API documentation**
- **Include migration guides** for breaking changes

## Commit Message Guidelines

Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(plugins): add weather plugin with OpenWeatherMap integration

fix(app): resolve configuration parsing error for v2alpha1 agents

docs(demos): add multi-modal demo with image processing example

test(plugins): add comprehensive tests for custom plugin functionality
```

## Review Process

### Pull Request Requirements
Before submitting a PR, ensure:
- [ ] All tests pass locally
- [ ] Code follows style guidelines (ruff check passes)
- [ ] Type checking passes (mypy)
- [ ] Documentation is updated
- [ ] Commit messages follow conventional format
- [ ] PR description clearly explains changes

### Review Criteria
PRs will be reviewed for:
- **Functionality**: Does the code work as intended?
- **Code Quality**: Is the code well-structured and maintainable?
- **Testing**: Are there adequate tests for the changes?
- **Documentation**: Is the documentation clear and complete?
- **Compatibility**: Does it maintain backward compatibility?
- **Performance**: Are there any performance implications?

### Feedback and Iteration
- **Address feedback promptly**: Respond to review comments in a timely manner
- **Ask questions**: If feedback is unclear, ask for clarification
- **Make incremental changes**: Address feedback in focused commits
- **Update documentation**: Keep documentation in sync with code changes

## Release Process

### Versioning
We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Preparation
- **Update CHANGELOG.md**: Document all changes
- **Update version numbers**: In relevant configuration files
- **Test thoroughly**: Run full test suite
- **Update documentation**: Ensure all docs are current

## Community Guidelines

### Communication
- **Be respectful**: Treat all community members with respect
- **Be constructive**: Provide helpful feedback and suggestions
- **Be patient**: Remember that maintainers are often volunteers
- **Be collaborative**: Work together to improve the framework

### Contribution Recognition
We recognize contributions through:
- **Contributor acknowledgments**: In release notes and documentation
- **Code attribution**: Proper git commit attribution
- **Community recognition**: Highlighting significant contributions
- **Maintainer opportunities**: For consistent, high-quality contributors

## Getting Help

For questions, support, or discussions:
- **GitHub Issues**: Report bugs, request features, or ask questions
- **GitHub Discussions**: Community discussions and general questions
- **Documentation**: Check existing guides and examples first
- **Email**: Contact david.daniel@merck.com for direct support

When asking for help:
- **Search existing issues** and discussions first
- **Provide context**: Include relevant code, configuration, and error messages
- **Be specific**: Describe what you expected vs. what actually happened
- **Include environment details**: Python version, OS, package versions
- **Share minimal reproducible examples** when possible

Thank you for contributing to the Teal Agents Framework! 🚀
