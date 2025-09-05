# Phase 1: Foundation, Maintenance, and Testing

This phase focuses on creating a baseline agent and ensuring the repository has a solid foundation of documentation, up-to-date dependencies, and automated tests.

## 🔧 Technical Prerequisites for Coding Agents

Before starting any task, coding agents should understand the **Teal Agents Framework** architecture:

### Framework Overview
- **Core Technology**: Built on Microsoft Semantic Kernel v1.33.0 with FastAPI
- **Package Manager**: Uses `uv` (not pip) for dependency management
- **Python Version**: Requires Python 3.13+
- **Configuration**: YAML-based configuration files, not code-first approach

### Project Structure
```
teal-agents/
├── src/sk-agents/                    # Main agent framework
│   ├── pyproject.toml                # Main dependencies 
│   ├── uv.lock                       # Lock file
│   ├── src/sk_agents/                # Framework source code & ACTUAL AGENTS
│   │   ├── weather-agent/            # Example agent
│   │   │   ├── config.yaml           # Agent configuration
│   │   │   ├── custom_plugins.py     # Custom plugins (if needed)
│   │   │   └── README.md             # Agent documentation
│   │   └── echo-agent/               # Another example
│   ├── docs/demos/                   # Demo configurations (PRESENTATION ONLY)
│   └── tests/                        # Test suite
├── shared/ska_utils/                 # Shared utilities
│   ├── pyproject.toml                # Utility dependencies
│   └── uv.lock                       # Utility lock file
└── src/orchestrators/                # Agent orchestration services
```

### Agent Development Pattern
1. **Configuration File**: Create `config.yaml` with agent specification
2. **Custom Plugins**: Create `custom_plugins.py` for external integrations
3. **Documentation**: Create `README.md` explaining the agent
4. **Environment**: Use `.env` files for API keys and configuration

### Key Commands
```bash
# Install dependencies
cd src/sk-agents && uv sync

# Run an agent (from src/sk-agents directory)
TA_SERVICE_CONFIG=src/sk_agents/weather-agent/config.yaml \
TA_PLUGIN_MODULE=src/sk_agents/weather-agent/custom_plugins.py \
uv run fastapi run src/sk_agents/app.py

# Run tests
uv run pytest tests/ -v

# Update dependencies
uv update
```

### Configuration Schema
All agents use this YAML structure:
```yaml
apiVersion: skagents/v1
kind: Sequential
description: "Agent description"
service_name: AgentName
version: 0.1
input_type: BaseInput
spec:
  agents:
    - name: default
      role: Agent Role
      model: gpt-4o-mini
      system_prompt: "System instructions"
      plugins: []  # Optional plugin list
  tasks:
    - name: task_name
      task_no: 1
      description: "Task description"
      instructions: "Detailed instructions"
      agent: default
```

---

1.  **[Create a Weather Agent](#task-1-create-a-weather-agent)**: A simple task to create a new, functional agent that interacts with an external API.
2.  **[Document Existing Agents](#task-2-document-existing-agents)**: Tests the agent's ability to read existing code and generate human-readable documentation.
3.  **[Update Dependencies](#task-3-update-dependencies)**: A maintenance task to update all project packages to their latest stable versions and resolve any conflicts.
4.  **[Fix Security Vulnerabilities](#task-4-fix-security-vulnerabilities)**: A security-focused task to find and fix known vulnerabilities in the project's dependencies.
5.  **[Generate Unit Tests](#task-5-generate-unit-tests)**: Tests the ability to write unit tests for an agent's internal logic, including the use of mocking.
6.  **[Implement E2E Tests with Robot Framework](#task-6-implement-e2e-tests-with-robot-framework)**: A hard task to create end-to-end tests that manage a running service and its dependencies.

# Phase 2: Advanced Refactoring and Migration

This phase presents significant challenges that test the agent's ability to understand and execute large-scale changes across the entire codebase.

7.  **[Migrate Repository from Semantic Kernel to LangChain](#task-7-migrate-from-semantic-kernel-to-langchain)**: A project-wide migration from one agent framework to another, requiring changes to every agent.
8.  **[Rewrite Repository from Python to Go](#task-8-rewrite-from-python-to-go)**: The ultimate challenge, requiring a complete rewrite of the project in a different programming language while maintaining functional parity.

---

# Detailed Task Descriptions

### **Task 1: Create a Weather Agent**

**Title:** `feat: Create a weather agent using an external API`

#### Description 📝
Create a new, self-contained agent called `weather-agent` that takes a city name as input and returns the current weather for that city. This agent must use a free, public weather API (e.g., OpenWeatherMap, WeatherAPI.com) to fetch the data. This task serves as a baseline for testing core functionality.

#### Technical Context 🔧
- The Teal Agents Framework uses YAML configuration files (`config.yaml`)
- Agents are structured as directories under `src/sk-agents/src/sk_agents/` 
- The framework uses Semantic Kernel and FastAPI for the web interface
- Custom plugins should inherit from `BasePlugin` and use `@kernel_function` decorators
- Configuration follows the pattern: `apiVersion: skagents/v1`, `kind: Sequential`

#### Recommended Implementation Approach 📋
1. **Directory Structure**: Create `src/sk-agents/src/sk_agents/weather-agent/` containing:
   - `config.yaml` (agent configuration)
   - `custom_plugins.py` (weather API plugin)
   - `README.md` (documentation)
   - `.env.example` (environment template)

2. **Weather API**: Use OpenWeatherMap API (free tier, no credit card required) or Open-Meteo (completely free)
   - OpenWeatherMap: `https://api.openweathermap.org/data/2.5/weather`
   - Open-Meteo: `https://api.open-meteo.com/v1/forecast` (no API key needed)

3. **Configuration Pattern**: Follow existing demos structure but place in `src/sk_agents/` directory for actual use

#### Acceptance Criteria ✅
-   [ ] A new directory `src/sk-agents/src/sk_agents/weather-agent/` is created with the necessary `config.yaml`, `custom_plugins.py`, and `README.md` files.
-   [ ] The agent configuration follows the existing framework pattern (Sequential agent with plugins).
-   [ ] The agent accepts a city name as input and uses a WeatherPlugin to fetch data.
-   [ ] If using OpenWeatherMap, the API key is managed via environment variable (`WEATHER_API_KEY`).
-   [ ] The agent's response includes temperature, weather condition, and city name.
-   [ ] The agent includes error handling for invalid city names or API failures.
-   [ ] A `.env.example` file demonstrates required environment variables.
-   [ ] The weather agent can be started using: `TA_SERVICE_CONFIG=src/sk_agents/weather-agent/config.yaml TA_PLUGIN_MODULE=src/sk_agents/weather-agent/custom_plugins.py fastapi run src/sk_agents/app.py`


### **Task 2: Document Existing Agents**

**Title:** `docs: Document existing agents and create a project overview`

#### Description 📖
The repository needs better documentation to improve maintainability and onboarding. This task involves two parts: generating detailed documentation for existing agents and creating a high-level architectural overview for the project's README.

#### Technical Context 🔧
- Existing demo agents are located in `src/sk-agents/docs/demos/` (for presentations/examples only)
- Actual working agents should be created in `src/sk-agents/src/sk_agents/` directory
- Each agent directory typically contains: `config.yaml`, `custom_plugins.py` (if applicable), and `README.md`
- The main project README is at the repository root (`/Users/pollarij/work/git_workspace/Github/genai/teal-agents/README.md`)
- Agent configurations use YAML format with specific schema (`apiVersion: skagents/v1`, `kind: Sequential`)

#### Recommended Implementation Approach 📋
1. **Survey Existing Demos**: Analyze all configurations in `src/sk-agents/docs/demos/` for reference patterns
2. **Agent Directory Structure**: Ensure `src/sk-agents/src/sk_agents/` is used for actual working agents
3. **Documentation Template**: Create consistent README template for agent documentation
4. **Architecture Documentation**: Focus on the microservice pattern, configuration-first approach, and orchestrator concepts

#### Acceptance Criteria ✅
-   [ ] For each existing demo in `src/sk-agents/docs/demos/` (e.g., `01_getting_started`, `03_plugins`, etc.), ensure a comprehensive `README.md` exists.
-   [ ] Each demo's `README.md` must explain its purpose, the expected input format, output format, and include usage examples with environment setup.
-   [ ] Document the proper location for actual working agents: `src/sk-agents/src/sk_agents/` (vs demos in `docs/demos/`).
-   [ ] Document the YAML configuration schema and explain key fields like `apiVersion`, `kind`, `agents`, `tasks`, and `plugins`.
-   [ ] The main `README.md` file in the repository root is updated with a new "Project Architecture" section.
-   [ ] The new section explains how agents work as microservices, the role of YAML configurations, the plugin system, and how orchestrators compose multiple agents.
-   [ ] Include a section on getting started with creating new agents, referencing the weather-agent as an example.


### **Task 3: Update Dependencies**

**Title:** `chore: Update all Python packages to latest stable versions`

#### Description ⬆️
This is a standard maintenance task to ensure the project is using the most recent and secure versions of its dependencies. The goal is to update all packages listed in `pyproject.toml` to their latest stable versions and ensure the application remains fully functional.

#### Technical Context 🔧
- The project uses `uv` as the package manager (not pip)
- Main dependencies are in `src/sk-agents/pyproject.toml`
- Shared utilities are in `shared/ska_utils/pyproject.toml`
- The project requires Python 3.13+ and uses modern dependency management with `uv.lock`

#### Recommended Implementation Approach 📋
1. **Dependency Analysis**: Use `uv show --tree` to understand current dependency structure
2. **Update Strategy**: Use `uv update` to update all dependencies, then test functionality
3. **Version Constraints**: Consider compatibility with Semantic Kernel and FastAPI ecosystems
4. **Testing**: Ensure the application starts and basic functionality works

#### Acceptance Criteria ✅
-   [ ] The `src/sk-agents/pyproject.toml` file is analyzed and dependencies are updated to latest stable versions.
-   [ ] The `shared/ska_utils/pyproject.toml` file is also updated for consistency.
-   [ ] Use `uv update` to update the lock files (`uv.lock`) in both directories.
-   [ ] Any dependency conflicts introduced by the updates are successfully resolved.
-   [ ] After updating, run `uv sync` to ensure dependencies install without errors.
-   [ ] Test that the application starts correctly: `cd src/sk-agents && uv run fastapi run src/sk_agents/app.py`
-   [ ] Verify a sample agent (like the weather-agent) works correctly with updated dependencies.
-   [ ] If existing tests are present, ensure they pass with the updated dependencies.


### **Task 4: Fix Security Vulnerabilities**

**Title:** `security: Scan for and fix critical dependency vulnerabilities`

#### Description 🛡️
This task focuses on improving the security posture of the application. The agent must use security scanning tools to identify vulnerabilities in the project's dependencies and remediate any discovered issues.

#### Technical Context 🔧
- The project uses `uv` package manager with `uv.lock` files
- Security scanning should cover both `src/sk-agents/` and `shared/ska_utils/` dependencies
- Modern Python security tools include `pip-audit`, `safety`, and `uv audit` (if available)

#### Recommended Implementation Approach 📋
1. **Install Security Tools**: Use `uv add --dev pip-audit` or `pip install pip-audit`
2. **Scan Strategy**: Run scans on both dependency trees
3. **Remediation**: Update vulnerable packages to secure versions
4. **Verification**: Re-scan to confirm fixes

#### Security Scanning Commands 🔍
```bash
# Install scanning tool
uv add --dev pip-audit

# Scan main project
cd src/sk-agents && uv run pip-audit

# Scan shared utilities  
cd shared/ska_utils && uv run pip-audit

# Alternative using pip-audit directly
pip-audit --requirement src/sk-agents/pyproject.toml
```

#### Acceptance Criteria ✅
-   [ ] Install `pip-audit` as a development dependency in the project.
-   [ ] Run security scans on both `src/sk-agents/` and `shared/ska_utils/` dependency trees.
-   [ ] Document all discovered vulnerabilities in the task output.
-   [ ] Update the affected packages in `pyproject.toml` files to versions that resolve the vulnerabilities.
-   [ ] Use `uv update` to refresh lock files after making changes.
-   [ ] Re-run security scans to verify that vulnerabilities have been resolved.
-   [ ] Ensure the application starts and functions correctly after security patches: `cd src/sk-agents && uv run fastapi run src/sk_agents/app.py`
-   [ ] Test that existing agents (like weather-agent) still work correctly.


### **Task 5: Generate Unit Tests**

**Title:** `test: Generate comprehensive unit tests for an agent`

#### Description 🧪
The codebase lacks sufficient testing. This task is to write a comprehensive suite of unit tests for the `weather-agent` created in Task 1. The tests should verify the agent's internal logic without making actual external API calls. Use the `pytest` framework and mock the external weather API.

#### Technical Context 🔧
- The project already includes `pytest` and `pytest-mock` in dev dependencies (`src/sk-agents/pyproject.toml`)
- Existing test structure is in `src/sk-agents/tests/`
- Weather agent plugin should be tested separately from the agent configuration
- Use `pytest-asyncio` for async test support (already included)

#### Testing Strategy 🎯
1. **Plugin Testing**: Test the WeatherPlugin class methods individually
2. **Mock External APIs**: Mock HTTP requests to weather services
3. **Error Handling**: Test invalid inputs and API failures
4. **Integration Testing**: Test the plugin within the agent framework

#### Recommended Test Structure 📁
```
src/sk-agents/tests/
├── test_weather_agent_plugin.py  # Plugin unit tests
├── test_weather_agent_integration.py  # Integration tests
└── fixtures/
    └── weather_api_responses.json  # Mock API responses
```

#### Acceptance Criteria ✅
-   [ ] A test file `src/sk-agents/tests/test_weather_agent_plugin.py` is created to test the WeatherPlugin class.
-   [ ] Unit tests cover both plugin methods: `get_temperature()` and `get_lat_lng_for_location()` (or equivalent).
-   [ ] External API calls are properly mocked using `pytest-mock` to avoid real network requests.
-   [ ] Tests cover successful scenarios with various city inputs and expected weather data.
-   [ ] Tests cover failure scenarios: invalid city names, API errors, network timeouts, malformed responses.
-   [ ] Mock data fixtures are created to simulate realistic API responses.
-   [ ] All tests can be run successfully: `cd src/sk-agents && uv run pytest tests/test_weather_agent*.py -v`
-   [ ] Tests achieve good code coverage of the weather plugin functionality.
-   [ ] Integration test verifies the weather agent works end-to-end with mocked APIs.

<br>

### **Task 6: Implement E2E Tests with Robot Framework**

**Title:** `test: Implement E2E tests for the API using Robot Framework`

#### Description 🚦
To ensure our agents work as expected when deployed, create an end-to-end (E2E) test suite using **Robot Framework**. These tests will spin up an agent's service as a separate process and make real HTTP requests to its API endpoints. The test suite should target the `weather-agent`.

#### Technical Context 🔧
- The Teal Agents Framework runs on FastAPI (default port 8000)
- Agent endpoints follow REST API patterns (see `/docs` for Swagger UI)
- Tests should run the agent in a separate process and make HTTP requests
- Network-level mocking can be achieved with tools like `responses` or `httpretty`

#### E2E Testing Strategy 🎯
1. **Service Management**: Start/stop the weather-agent FastAPI service
2. **API Testing**: Test actual HTTP endpoints with Robot Framework
3. **Network Mocking**: Mock external weather APIs at the network level
4. **Cleanup**: Ensure proper service shutdown after tests

#### Robot Framework Structure 📁
```
src/sk-agents/tests/e2e/
├── weather_agent.robot           # Main test suite
├── keywords/
│   ├── agent_management.robot    # Start/stop agent keywords
│   └── api_testing.robot         # HTTP request keywords
└── resources/
    └── mock_responses.json       # Mock API response data
```

#### FastAPI Service Commands 🚀
```bash
# Start weather agent service
cd src/sk-agents
TA_SERVICE_CONFIG=src/sk_agents/weather-agent/config.yaml \
TA_PLUGIN_MODULE=src/sk_agents/weather-agent/custom_plugins.py \
uv run fastapi run src/sk_agents/app.py --port 8001

# Test endpoint
curl -X POST "http://localhost:8001/invoke" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the weather in Prague?"}'
```

#### Acceptance Criteria ✅
-   [ ] Add `robotframework`, `robotframework-requests`, and `robotframework-pythonlibcore` to dev dependencies.
-   [ ] Create test suite `src/sk-agents/tests/e2e/weather_agent.robot` with proper Robot Framework syntax.
-   [ ] Implement `Suite Setup` keyword that starts the weather-agent FastAPI service on a test port (e.g., 8001).
-   [ ] Implement `Suite Teardown` keyword that gracefully shuts down the web service.
-   [ ] Create test cases for successful weather queries and error scenarios (invalid cities, API failures).
-   [ ] Implement network-level mocking of external weather APIs using Python libraries or Robot Framework keywords.
-   [ ] Tests make actual HTTP requests to the running agent service endpoints.
-   [ ] Verify response format, status codes, and error handling in the Robot Framework tests.
-   [ ] Tests can be executed: `cd src/sk-agents && uv run robot tests/e2e/weather_agent.robot`
-   [ ] All E2E tests pass and demonstrate the weather agent working end-to-end.

<br>

### **Task 7: Migrate from Semantic Kernel to LangChain**

**Title:** `refactor: Migrate entire repository from Semantic Kernel to LangChain`

#### Description 🏗️
Perform a project-wide migration of all agents from the **Semantic Kernel** framework to the **LangChain** framework. This is a complex refactoring task that tests deep codebase understanding and adaptability.

#### Technical Context 🔧
- Current framework: Semantic Kernel v1.33.0 with FastAPI
- Target framework: LangChain with LangServe for web deployment
- Key migration points: Plugin system, agent configuration, web API layer
- LangChain equivalents: Tools (vs Plugins), Chains (vs Sequential agents), Runnable interface

#### Migration Strategy 🔄
1. **Dependency Migration**: Replace `semantic-kernel` with `langchain`, `langchain-openai`, `langserve`
2. **Plugin → Tools**: Convert `@kernel_function` plugins to LangChain tools
3. **Agent Configuration**: Redesign YAML schema for LangChain concepts
4. **API Layer**: Replace FastAPI agent endpoints with LangServe
5. **Chain Logic**: Convert Sequential agent logic to LangChain chains

#### LangChain Architecture Changes 🏗️
```
Current (Semantic Kernel):           Target (LangChain):
├── config.yaml (SK schema)    →    ├── config.yaml (LC schema)
├── custom_plugins.py          →    ├── tools.py
├── FastAPI app.py             →    ├── LangServe app.py
└── Sequential agents          →    └── LangChain chains/agents
```

#### Key Technical Mappings 🔧
- `@kernel_function` → `@tool` decorator
- `BasePlugin` → `BaseTool` class
- Sequential agent → `AgentExecutor` or custom chain
- FastAPI endpoints → LangServe `add_routes()`

#### Acceptance Criteria ✅
-   [ ] Remove `semantic-kernel` dependency and add `langchain`, `langchain-openai`, `langchain-community`, and `langserve`.
-   [ ] Convert all plugin classes from `BasePlugin` to LangChain `BaseTool` implementations.
-   [ ] Replace `@kernel_function` decorators with LangChain `@tool` decorators.
-   [ ] Redesign YAML configuration schema to use LangChain concepts (agents, tools, chains).
-   [ ] Replace FastAPI agent logic with LangServe deployment pattern.
-   [ ] Convert Sequential agent execution to LangChain `AgentExecutor` or equivalent chains.
-   [ ] Update all demo configurations in `src/sk-agents/docs/demos/` to use new LangChain schema.
-   [ ] Update the agent directory structure (`src/sk-agents/src/sk_agents/`) to use new LangChain schema.
-   [ ] Ensure the weather-agent works with the new LangChain implementation.
-   [ ] Update documentation to reflect LangChain architecture and concepts.
-   [ ] All existing unit and E2E tests pass with the new LangChain implementation.
-   [ ] API endpoints maintain the same contract (input/output format) for backward compatibility.

<br>

### **Task 8: Rewrite from Python to Go**

**Title:** `refactor: Rewrite the entire repository in Go (Golang)`

#### Description 🚀
This is a major undertaking to test cross-language translation. The goal is to rewrite the entire `teal-agents` repository from **Python** to **Go (Golang)**, building on the **LangChain** version from the previous step. This involves re-implementing the core concepts using idiomatic Go practices.

#### Technical Context 🔧
- Source: Python LangChain implementation with LangServe
- Target: Go with appropriate web framework and AI libraries
- Go ecosystem: Gin/Echo for web, Go OpenAI SDK, custom agent framework
- Architecture: Maintain microservice pattern and configuration-driven approach

#### Go Implementation Strategy 🔄
1. **Project Structure**: Initialize Go module with proper package organization
2. **Web Framework**: Use Gin or Echo for HTTP API (equivalent to FastAPI/LangServe)
3. **AI Integration**: Use Go OpenAI SDK or similar for LLM interactions
4. **Configuration**: Use YAML parsing libraries (gopkg.in/yaml.v3)
5. **Plugin System**: Design Go interface-based plugin architecture
6. **Testing**: Use Go standard testing package and testify for assertions

#### Go Project Structure 🏗️
```
teal-agents-go/
├── go.mod
├── go.sum
├── cmd/
│   └── agent-server/
│       └── main.go
├── pkg/
│   ├── agents/
│   ├── plugins/
│   ├── config/
│   └── api/
├── internal/
│   ├── weather/
│   └── handlers/
├── configs/
│   ├── demos/                        # Demo configurations (from Python)
│   └── sk_agents/                    # Working agent configurations
│       └── weather-agent/
├── tests/
└── docs/
```

#### Go Technology Stack 🛠️
- **Web Framework**: Gin (`github.com/gin-gonic/gin`)
- **AI/LLM**: OpenAI Go SDK (`github.com/sashabaranov/go-openai`)
- **Configuration**: YAML v3 (`gopkg.in/yaml.v3`)
- **HTTP Client**: Standard library or Resty (`github.com/go-resty/resty/v2`)
- **Testing**: Testify (`github.com/stretchr/testify`)

#### API Compatibility Requirements 🔗
- Maintain same HTTP endpoints and JSON structures
- Same configuration file format (YAML schema)
- Same plugin interface concepts (adapted to Go interfaces)
- Same environment variable patterns

#### Acceptance Criteria ✅
-   [ ] Initialize a new Go module: `go mod init github.com/MSDLLCpapers/teal-agents-go`
-   [ ] Remove all Python code and replace with equivalent Go implementation.
-   [ ] Implement Go web server using Gin that exposes the same API endpoints as the Python version.
-   [ ] Create Go package structure for agents, plugins, configuration, and API handling.
-   [ ] Implement weather agent functionality in Go with the same external API integration.
-   [ ] Maintain YAML configuration compatibility - Go agent should read same config files.
-   [ ] Implement plugin interface system in Go that matches Python plugin functionality.
-   [ ] Create Go unit tests using standard testing package that cover the weather plugin functionality.
-   [ ] Implement Go integration tests that verify end-to-end agent functionality.
-   [ ] Update main `README.md` with Go-specific build and run instructions.
-   [ ] All API endpoints return the same JSON structures and response formats as Python version.
-   [ ] Performance benchmarks show Go implementation meets or exceeds Python performance.
-   [ ] Docker support for Go application (update Dockerfiles if needed).

---

## 🛠️ Troubleshooting Guide for Coding Agents

### Common Issues and Solutions

#### Dependency Management
```bash
# If uv sync fails
uv clean && uv sync

# If lock file conflicts
rm uv.lock && uv lock

# Check dependency tree
uv show --tree
```

#### Agent Startup Issues
```bash
# Check required environment variables
echo $TA_SERVICE_CONFIG
echo $TA_PLUGIN_MODULE

# Verify config file exists
ls -la src/sk_agents/weather-agent/config.yaml

# Test config syntax
python -c "import yaml; yaml.safe_load(open('config.yaml'))"
```

#### Testing Problems
```bash
# Run specific test
uv run pytest tests/test_weather_agent.py::test_function -v

# Run with coverage
uv run pytest --cov=src/sk_agents tests/

# Debug robot framework
uv run robot --loglevel DEBUG tests/e2e/
```

#### Common Error Messages
- **"Module not found"**: Check `TA_PLUGIN_MODULE` path and ensure file exists
- **"Config validation error"**: Verify YAML syntax and required fields
- **"Port already in use"**: Change port or kill existing process
- **"API key missing"**: Check environment variables in `.env` file

### Best Practices for Coding Agents
1. **Always check existing project structure** before creating new directories
2. **Read existing demo configurations** to understand patterns
3. **Test incrementally** - don't implement everything at once
4. **Use project's existing patterns** (uv, pytest, FastAPI)
5. **Validate configurations** before running agents
6. **Mock external APIs** in tests to avoid rate limits
7. **Document environment setup** clearly for other developers
