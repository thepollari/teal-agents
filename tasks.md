# Phase 1: Foundation, Maintenance, and Testing

This phase focuses on creating a baseline agent and ensuring the repository has a solid foundation of documentation, up-to-date dependencies, and automated tests.

## 🔧 Technical Prerequisites for Coding Agents

Before starting any task, coding agents should understand the **Teal Agents Framework** architecture and the specific requirements for each task type:

### Framework Overview
- **Core Technology**: Built on Microsoft Semantic Kernel v1.33.0 with FastAPI
- **Package Manager**: Uses `uv` (not pip) for dependency management across multiple components
- **Python Version**: Requires Python 3.13+
- **Configuration**: YAML-based configuration files, not code-first approach
- **Multi-Component Structure**: 6 separate components with independent dependency management

### Multi-Component Project Structure
```
teal-agents/
├── src/sk-agents/                    # Main agent framework
│   ├── pyproject.toml                # Main dependencies 
│   ├── uv.lock                       # Lock file
│   ├── src/sk_agents/                # Framework source code & ACTUAL AGENTS
│   │   ├── weather-agent/            # Example weather agent
│   │   │   ├── config.yaml           # Agent configuration
│   │   │   ├── custom_plugins.py     # WeatherPlugin for Open-Meteo API
│   │   │   ├── streamlit_ui.py       # Streamlit testing interface
│   │   │   └── README.md             # Agent documentation
│   │   └── chat_completion/custom/   # Custom completion factories
│   │       └── gemini_chat_completion_factory.py  # Gemini integration
│   ├── docs/demos/                   # Demo configurations
│   └── tests/                        # Unit & E2E tests
│       ├── unit/                     # Unit tests with mocking
│       └── e2e/                      # Robot Framework E2E tests
├── shared/ska_utils/                 # Shared utilities
│   ├── pyproject.toml                # Utility dependencies
│   └── uv.lock                       # Utility lock file
└── src/orchestrators/                # Agent orchestration services
    ├── assistant-orchestrator/
    │   ├── orchestrator/pyproject.toml
    │   └── services/pyproject.toml
    ├── collab-orchestrator/orchestrator/pyproject.toml
    └── workflow-orchestrator/orchestrator/pyproject.toml
```

### Framework Capabilities

#### Agent Development & Documentation
- **Custom Completion Factories**: Extend Semantic Kernel with external LLM providers (Google Gemini, etc.)
- **Plugin Development**: Use `@kernel_function` decorators for external API integration
- **UI Development**: Streamlit for interactive testing interfaces
- **Documentation**: Comprehensive README files and architecture guides

#### Dependency Management & Security
- **Multi-Component Updates**: Sequential updates across 6 pyproject.toml files
- **Security Scanning**: pip-audit or safety across all components
- **Compatibility Testing**: Ensure inter-component dependency compatibility
- **Vulnerability Remediation**: Systematic patching while maintaining functionality

#### Testing Infrastructure
- **Unit Testing**: pytest with mocking for isolated component testing
- **E2E Testing**: Robot Framework for complete system integration testing
- **External API Mocking**: Network-level mocking vs component-level mocking
- **Test Organization**: Separate unit/ and e2e/ test directories

#### Framework Migration & Language Migration
- **Semantic Kernel → LangChain**: Complete framework migration with API compatibility
- **Python → Go**: Cross-language rewrite with performance improvements
- **Configuration Migration**: YAML schema updates while maintaining compatibility
- **Integration Testing**: Validation that migrations maintain functional parity

### Essential Framework Commands

```bash
# Weather Agent Development
cd src/sk-agents && uv add google-generativeai streamlit
TA_SERVICE_CONFIG=src/sk_agents/weather-agent/config.yaml \
TA_PLUGIN_MODULE=src/sk_agents/weather-agent/custom_plugins.py \
TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE=src/sk_agents/chat_completion/custom/gemini_chat_completion_factory.py \
TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS_NAME=GeminiChatCompletionFactory \
TA_API_KEY=your_gemini_api_key \
uv run fastapi run src/sk_agents/app.py

# Documentation Generation
find src/sk-agents/docs/demos/ -name "*.yaml" | wc -l  # Count demo configs
find src/sk-agents/src/sk_agents/ -name "README.md"    # Find existing docs

# Dependency & Security Management
for component in "shared/ska_utils" "src/sk-agents" "src/orchestrators/*/orchestrator" "src/orchestrators/*/services"; do
  cd "$component" && uv update && uv run pip-audit
done

# Unit Testing
cd src/sk-agents && uv run pytest tests/unit/ -v --cov=src/sk_agents

# E2E Testing
cd src/sk-agents && uv add --dev robotframework robotframework-requests robotframework-process
uv run robot tests/e2e/

# LangChain Migration
cd src/sk-agents && uv remove semantic-kernel
uv add langchain langchain-openai langchain-community langserve

# Go Migration
go mod init github.com/merck-gen/teal-agents-go
go get github.com/gin-gonic/gin gopkg.in/yaml.v3
```

### Configuration Schema Examples
```yaml
# Current Semantic Kernel Schema
apiVersion: skagents/v1
kind: Sequential
description: "Weather agent powered by Google Gemini"
service_name: WeatherAgent
version: 0.1
input_type: BaseInput
spec:
  agents:
    - name: default
      role: Weather Assistant
      model: gemini-1.5-flash
      system_prompt: "You are a helpful weather assistant..."
      plugins:
        - WeatherPlugin
  tasks:
    - name: weather_query
      task_no: 1
      description: "Process weather information requests"
      instructions: "Use the WeatherPlugin to get current weather data"
      agent: default

# Target LangChain Schema (for framework migration)
apiVersion: langchain/v1
kind: AgentExecutor
description: "Weather agent using LangChain"
service_name: WeatherAgent
version: 0.1
spec:
  llm:
    provider: custom_gemini
    model: gemini-1.5-flash
  tools: [weather_tool, geocoding_tool]
  agent_type: openai-functions
```

---

1.  **[Create a Weather Agent with Google Gemini and Streamlit UI](#task-1-create-a-weather-agent-with-google-gemini-and-streamlit-ui)**: A comprehensive task to create a weather agent system with custom Gemini integration, external API functionality, and interactive Streamlit testing interface.
2.  **[Comprehensive Repository Documentation and Agent Documentation](#task-2-comprehensive-repository-documentation-and-agent-documentation)**: Tests the agent's ability to read existing code and generate comprehensive documentation for the repository structure, framework components, and existing agents.
3.  **[Update Dependencies Across All Components](#task-3-update-dependencies-across-all-components)**: A maintenance task to update all Python packages to latest stable versions across the entire multi-component repository while maintaining compatibility.
4.  **[Comprehensive Security Vulnerability Assessment and Remediation](#task-4-comprehensive-security-vulnerability-assessment-and-remediation)**: A security-focused task to scan for and fix critical dependency vulnerabilities across all repository components.
5.  **[Generate Unit Tests for Weather Agent Components](#task-5-generate-unit-tests-for-weather-agent-components)**: Tests the ability to write comprehensive unit tests for individual weather agent components using mocking to eliminate external dependencies.
6.  **[Implement End-to-End Tests for Weather Agent System](#task-6-implement-end-to-end-tests-for-weather-agent-system)**: A comprehensive task to create end-to-end tests using Robot Framework that verify the complete weather agent system integration.

# Phase 2: Advanced Refactoring and Migration

This phase presents significant challenges that test the agent's ability to understand and execute large-scale changes across the entire codebase.

7.  **[Comprehensive Migration from Semantic Kernel to LangChain](#task-7-comprehensive-migration-from-semantic-kernel-to-langchain)**: A complex architectural refactoring task requiring a complete project-wide migration from Semantic Kernel to LangChain with comprehensive testing and validation.
8.  **[Complete Cross-Language Migration from Python to Go](#task-8-complete-cross-language-migration-from-python-to-go)**: The ultimate challenge, requiring a comprehensive rewrite of the entire repository from Python to Go with full feature parity and API compatibility.

---

# Detailed Task Descriptions

### **Task 1: Create a Weather Agent with Google Gemini and Streamlit UI**

**Title:** `feat: Create a weather agent with Google Gemini integration and Streamlit testing UI`

#### Description 📝
Create a comprehensive weather agent system that demonstrates the full Teal Agents Framework capabilities. This task involves building a custom chat completion factory for Google Gemini API integration, developing a weather agent with external API functionality, and creating an interactive Streamlit web interface for testing. This multi-part task serves as a complete baseline implementation showcasing modern AI agent architecture with both programmatic and user-friendly interfaces.

#### Technical Context 🔧
- The Teal Agents Framework uses YAML configuration files (`config.yaml`) and Semantic Kernel v1.33.0
- Agents are structured as directories under `src/sk-agents/src/sk_agents/` 
- Custom chat completion factories extend the framework's LLM integration capabilities
- Custom plugins should inherit from `BasePlugin` and use `@kernel_function` decorators
- Configuration follows the pattern: `apiVersion: skagents/v1`, `kind: Sequential`
- **Google Gemini** will provide the language model capabilities via custom completion factory
- **Streamlit** will provide a simple web UI for testing the agent interactively

#### Multi-Part Implementation Strategy 🎯

This task is divided into three interconnected sub-tasks that build upon each other:

##### **Sub-task 1.1: Custom Gemini Chat Completion Factory**
Create a custom chat completion factory that integrates Google Gemini API with the Semantic Kernel framework.

**Technical Requirements:**
- Extend or implement the Semantic Kernel chat completion interface
- Use Google AI Python SDK (`google-generativeai`) for Gemini API integration
- Support Gemini 1.5 Flash model (free tier with 15 requests/minute)
- Handle API key management via environment variables
- Implement proper error handling and rate limiting awareness

**Expected Deliverables:**
- `src/sk_agents/chat_completion/custom/gemini_chat_completion_factory.py`
- Factory class that follows Semantic Kernel patterns
- Integration with `google-generativeai` library
- Environment variable configuration for API key

##### **Sub-task 1.2: Weather Agent Implementation**
Develop a weather agent that uses the custom Gemini completion factory and integrates with external weather APIs.

**Technical Requirements:**
- Create agent configuration that uses the custom Gemini completion factory
- Implement weather plugin using Open-Meteo API (free, no API key required)
- Support natural language queries about weather conditions
- Provide structured weather data with temperature, conditions, and location
- Include comprehensive error handling for API failures and invalid locations

**Expected Deliverables:**
- `src/sk_agents/src/sk_agents/weather-agent/config.yaml` (configured for Gemini)
- `src/sk_agents/src/sk_agents/weather-agent/custom_plugins.py` (WeatherPlugin)
- `src/sk_agents/src/sk_agents/weather-agent/README.md` (documentation)
- Integration with Open-Meteo Geocoding and Weather APIs

##### **Sub-task 1.3: Streamlit Testing Interface**
Create an interactive web interface that provides a chat-like experience for testing the weather agent.

**Technical Requirements:**
- Implement chat-style interface using Streamlit's `st.chat_message` and `st.chat_input`
- Maintain conversation history within the session
- Connect to the weather agent's FastAPI endpoint
- Display weather information in a user-friendly format
- Include agent status monitoring and error handling
- Provide example queries and usage instructions

**Expected Deliverables:**
- `src/sk_agents/src/sk_agents/weather-agent/streamlit_ui.py`
- Chat-like interface with conversation history
- Integration with weather agent API endpoints
- User-friendly weather data presentation
- Status monitoring and error handling UI

#### Recommended Implementation Approach 📋

**Phase 1 - Gemini Integration (Sub-task 1.1):**
1. **Dependency Setup**: Add `google-generativeai` to `src/sk-agents/pyproject.toml`
2. **Factory Implementation**: Create Gemini completion factory following Semantic Kernel patterns
3. **Configuration**: Support environment variable for API key (`GEMINI_API_KEY`)
4. **Testing**: Verify integration with simple text completion

**Phase 2 - Weather Agent (Sub-task 1.2):**
1. **Directory Structure**: Create `src/sk-agents/src/sk_agents/weather-agent/`
2. **Configuration**: Set up `config.yaml` to use custom Gemini completion factory
3. **Weather Plugin**: Implement using Open-Meteo API (geocoding + weather endpoints)
4. **Testing**: Verify agent responds to weather queries using Gemini

**Phase 3 - Streamlit UI (Sub-task 1.3):**
1. **Dependencies**: Add `streamlit` to dev dependencies
2. **Interface Design**: Create chat-style UI with conversation flow
3. **Agent Integration**: Connect to running weather agent FastAPI service
4. **User Experience**: Polish interface with status indicators and helpful messaging

#### Technical Integration Points 🔗

**Gemini Completion Factory Structure:**
```python
# Required factory interface for Task 5 testing compatibility
class GeminiChatCompletionFactory:
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        # Initialize Google AI client
        pass
    
    def create_chat_completion(self, **kwargs):
        # Return Semantic Kernel compatible completion service
        pass
```

**Weather Plugin Structure:**
```python
# Required plugin interface for Task 5 testing compatibility
class WeatherPlugin(BasePlugin):
    @kernel_function(description="Get current weather information for a city")
    def get_current_weather(self, city: str) -> str:
        # Return JSON string with weather data
        pass
    
    @kernel_function(description="Get latitude and longitude coordinates for a city")
    def get_coordinates(self, city: str) -> str:
        # Return JSON string with coordinates
        pass
```

**Weather Agent Configuration:**
```yaml
apiVersion: skagents/v1
kind: Sequential
description: "Weather agent powered by Google Gemini"
service_name: WeatherAgent
version: 0.1
input_type: BaseInput
spec:
  agents:
    - name: default
      role: Weather Assistant
      model: gemini-1.5-flash  # Custom model reference
      system_prompt: "You are a helpful weather assistant..."
      plugins:
        - WeatherPlugin
```

**Streamlit Chat Interface Pattern:**
```python
# Chat message flow
if prompt := st.chat_input("Ask about weather"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Call weather agent API
    response = requests.post(AGENT_ENDPOINT, json={"chat_history": [...]})
    
    # Display agent response
    with st.chat_message("assistant"):
        st.markdown(agent_response)
```

#### Acceptance Criteria ✅

**Sub-task 1.1 - Gemini Integration:**
-   [ ] Add `google-generativeai` dependency to `src/sk-agents/pyproject.toml`
-   [ ] Create `src/sk-agents/src/sk_agents/chat_completion/custom/gemini_chat_completion_factory.py`
-   [ ] **Factory Interface Requirements**: GeminiChatCompletionFactory class must implement:
    -   [ ] `__init__(self, api_key: str, model_name: str = "gemini-1.5-flash")` - Constructor
    -   [ ] `create_chat_completion(**kwargs)` - Returns Semantic Kernel compatible service
-   [ ] Factory class integrates with Google AI Python SDK and returns Semantic Kernel compatible services
-   [ ] Support for environment variable `GEMINI_API_KEY` configuration
-   [ ] Factory supports Gemini 1.5 Flash model with proper parameter handling
-   [ ] Include error handling for API key validation and rate limiting

**Sub-task 1.2 - Weather Agent:**
-   [ ] Create directory `src/sk-agents/src/sk_agents/weather-agent/` with required files
-   [ ] Agent configuration (`config.yaml`) references custom Gemini completion factory
-   [ ] Weather plugin (`custom_plugins.py`) integrates with Open-Meteo APIs (geocoding + weather)
-   [ ] **Plugin Interface Requirements**: WeatherPlugin class must implement these specific methods:
    -   [ ] `get_current_weather(city: str) -> str` - Returns JSON string with weather data
    -   [ ] `get_coordinates(city: str) -> str` - Returns JSON string with lat/lng coordinates
-   [ ] Plugin uses `@kernel_function` decorators for method registration
-   [ ] Plugin supports location resolution and current weather data retrieval
-   [ ] Agent accepts natural language weather queries and returns informative responses
-   [ ] Include comprehensive error handling for invalid locations and API failures
-   [ ] Documentation (`README.md`) explains setup, configuration, and usage

**Sub-task 1.3 - Streamlit UI:**
-   [ ] Add `streamlit` to dev dependencies in `src/sk-agents/pyproject.toml`
-   [ ] Create `streamlit_ui.py` with chat-style interface using `st.chat_message` components
-   [ ] UI maintains conversation history and displays user/assistant message flow
-   [ ] Interface connects to weather agent FastAPI endpoints and handles responses
-   [ ] Display weather data in user-friendly format within chat context
-   [ ] Include agent status monitoring (connection health, response handling)
-   [ ] Provide example queries and clear usage instructions in the UI
-   [ ] Handle errors gracefully with informative chat responses

**Integration & End-to-End Testing:**
-   [ ] Weather agent starts successfully with custom Gemini factory: `TA_SERVICE_CONFIG=... TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE=... TA_API_KEY=... uv run fastapi run src/sk_agents/app.py`
-   [ ] Streamlit UI launches and connects to running agent: `cd .../weather-agent && uv run streamlit run streamlit_ui.py`
-   [ ] Complete workflow: User query → Streamlit UI → Weather Agent → Gemini API → Weather API → Response chain
-   [ ] Agent successfully uses Gemini for natural language processing and weather plugin for data retrieval
-   [ ] UI displays weather information in conversational format from Gemini-powered responses

**Documentation & Usability:**
-   [ ] Updated `README.md` includes complete setup instructions for all three components
-   [ ] Document Google Gemini API key setup and free tier limitations
-   [ ] Include step-by-step workflow: environment setup → start agent → start UI → test functionality
-   [ ] Provide example queries and expected response patterns
-   [ ] Document the custom completion factory pattern for future LLM integrations


### **Task 2: Comprehensive Repository Documentation and Agent Documentation**

**Title:** `docs: Create comprehensive documentation for repository structure, framework components, and existing agents`

#### Description 📖
The repository needs comprehensive documentation to improve maintainability, onboarding, and understanding of the Teal Agents Framework architecture. This task involves documenting the actual repository structure, framework components, demo configurations, working agents, and creating architectural overviews. The goal is to make the codebase accessible to both new developers and AI coding agents.

#### Technical Context 🔧
- **Demo Configurations**: Located in `src/sk-agents/docs/demos/` (reference examples only, not runnable agents)
- **Working Agents**: Located in `src/sk-agents/src/sk_agents/` (actual deployable agents like weather-agent)
- **Framework Core**: Located in `src/sk-agents/src/sk_agents/` (app.py, core modules, utilities)
- **Shared Utilities**: Located in `shared/ska_utils/` (cross-component utilities)
- **Orchestrators**: Located in `src/orchestrators/` (assistant-orchestrator, collab-orchestrator)
- **Main README**: Repository root needs architectural overview and getting started guide

#### Multi-Part Documentation Strategy 🎯

This task is divided into interconnected sub-tasks that comprehensively document the entire codebase:

##### **Sub-task 2.1: Framework Architecture Documentation**
Create high-level architectural documentation explaining the Teal Agents Framework components and their relationships.

**Technical Requirements:**
- Document the distinction between demo configurations vs working agents
- Explain the Semantic Kernel integration and FastAPI web layer
- Document the plugin system, custom completion factories, and configuration patterns
- Explain the orchestrator concepts and microservice architecture
- Create clear diagrams or ASCII art showing component relationships

**Expected Deliverables:**
- Update main `README.md` with "Architecture Overview" section
- Document framework components: agents, plugins, completion factories, orchestrators
- Explain configuration-driven approach and YAML schema patterns
- Include getting started guide for creating new agents
- Document deployment patterns and environment management

##### **Sub-task 2.2: Demo Configuration Documentation**
Document all existing demo configurations to serve as learning materials and reference implementations.

**Technical Requirements:**
- Analyze all configurations in `src/sk-agents/docs/demos/` directories
- Document each demo's purpose, configuration pattern, and learning objectives
- Explain differences between demo types (basic, plugins, multi-modal, etc.)
- Create cross-references showing how demos relate to working agent implementations
- Document the progression from simple to complex demo patterns

**Expected Deliverables:**
- `src/sk-agents/docs/demos/README.md` with comprehensive demo index
- Individual `README.md` files for each demo explaining purpose and usage
- Documentation showing how to adapt demos into working agents
- Cross-reference table mapping demos to actual implementation patterns
- Migration guide from demo configs to production agent configs

##### **Sub-task 2.3: Working Agent Documentation**
Create comprehensive documentation for all working agents in the repository, starting with the weather-agent.

**Technical Requirements:**
- Document the weather-agent implementation thoroughly
- Create template documentation structure for future agents
- Document the custom Gemini completion factory integration
- Explain the plugin development patterns used in weather-agent
- Document the Streamlit UI integration and testing approaches

**Expected Deliverables:**
- Enhanced `src/sk-agents/src/sk_agents/weather-agent/README.md`
- Documentation template for future agents (`AGENT_TEMPLATE.md`)
- Document custom completion factory development patterns
- Explain plugin development best practices with weather plugin as example
- Document UI development patterns using Streamlit integration

##### **Sub-task 2.4: Developer Onboarding Documentation**
Create comprehensive guides for developers and AI coding agents working with the repository.

**Technical Requirements:**
- Document development environment setup (uv, Python 3.13+, dependencies)
- Create step-by-step guide for creating new agents
- Document testing patterns (unit tests, integration tests, mocking strategies)
- Explain common development workflows and troubleshooting
- Document contribution guidelines and code organization principles

**Expected Deliverables:**
- `DEVELOPER_GUIDE.md` with comprehensive development instructions
- `AGENT_DEVELOPMENT.md` with step-by-step agent creation guide
- `TESTING_GUIDE.md` documenting testing patterns and best practices
- Update `CONTRIBUTING.md` with Teal Agents specific guidelines
- Create troubleshooting guide for common development issues

#### Repository Structure Analysis 🏗️

**Current Structure to Document:**
```
teal-agents/
├── README.md                         # Main project overview (needs update)
├── tasks.md                          # Task definitions for AI coding agents
├── shared/ska_utils/                 # Shared utilities library
│   ├── src/ska_utils/               # Utility modules (telemetry, config, etc.)
│   └── tests/                       # Utility tests
├── src/sk-agents/                   # Main agent framework
│   ├── src/sk_agents/               # Framework source + working agents
│   │   ├── app.py                   # FastAPI application entry point
│   │   ├── chat_completion/custom/  # Custom completion factories
│   │   ├── weather-agent/           # Working weather agent
│   │   └── [other framework modules]
│   ├── docs/demos/                  # Demo configurations (examples only)
│   │   ├── 01_getting_started/      # Basic agent demo
│   │   ├── 03_plugins/              # Plugin usage demo
│   │   ├── 08_multi_modal/          # Multi-modal demo
│   │   └── [other demos]
│   └── tests/                       # Framework and agent tests
└── src/orchestrators/               # Agent orchestration services
    ├── assistant-orchestrator/      # Assistant orchestrator
    └── collab-orchestrator/         # Collaboration orchestrator
```

#### Acceptance Criteria ✅

**Sub-task 2.1 - Framework Architecture:**
-   [ ] Update main `README.md` with comprehensive "Architecture Overview" section
-   [ ] Document the distinction between demo configurations (`docs/demos/`) and working agents (`src/sk_agents/`)
-   [ ] Explain Semantic Kernel integration, FastAPI web layer, and plugin system architecture
-   [ ] Document configuration-driven approach with YAML schema explanation
-   [ ] Include orchestrator concepts and microservice architecture patterns
-   [ ] Create getting started guide referencing weather-agent as example implementation
-   [ ] Document deployment patterns and environment variable management

**Sub-task 2.2 - Demo Configuration Documentation:**
-   [ ] Create comprehensive `src/sk-agents/docs/demos/README.md` with demo index and learning path
-   [ ] Ensure each demo directory (`01_getting_started`, `03_plugins`, etc.) has detailed `README.md`
-   [ ] Document each demo's purpose, configuration pattern, expected input/output, and learning objectives
-   [ ] Create cross-reference guide showing how demos relate to working agent implementations
-   [ ] Include migration guide explaining how to adapt demo configs for production agents
-   [ ] Document the progression from simple demos to complex implementations

**Sub-task 2.3 - Working Agent Documentation:**
-   [ ] Enhance `src/sk-agents/src/sk_agents/weather-agent/README.md` with comprehensive implementation details
-   [ ] Document the custom Gemini completion factory integration pattern
-   [ ] Explain weather plugin development with Open-Meteo API integration
-   [ ] Document Streamlit UI development and agent testing patterns
-   [ ] Create `AGENT_TEMPLATE.md` providing structure for future agent documentation
-   [ ] Document plugin development best practices using WeatherPlugin as reference
-   [ ] Include complete setup, configuration, and deployment instructions

**Sub-task 2.4 - Developer Onboarding:**
-   [ ] Create `DEVELOPER_GUIDE.md` with environment setup (uv, Python 3.13+, dependencies)
-   [ ] Create `AGENT_DEVELOPMENT.md` with step-by-step agent creation workflow
-   [ ] Create `TESTING_GUIDE.md` documenting unit test, integration test, and mocking patterns
-   [ ] Update `CONTRIBUTING.md` with Teal Agents specific development guidelines
-   [ ] Include troubleshooting guide for common issues (dependency conflicts, config errors, API problems)
-   [ ] Document code organization principles and contribution workflow

**Integration & Consistency:**
-   [ ] All documentation uses consistent terminology and references correct file paths
-   [ ] Documentation accurately reflects actual repository structure and working code
-   [ ] Cross-references between documents are accurate and helpful
-   [ ] Code examples in documentation are tested and functional
-   [ ] Documentation serves both human developers and AI coding agents effectively


### **Task 3: Update Dependencies Across All Components**

**Title:** `chore: Update all Python packages to latest stable versions across entire repository`

#### Description ⬆️
This is a comprehensive maintenance task to ensure the entire Teal Agents repository is using the most recent and secure versions of its dependencies. The repository has multiple Python components with their own dependency management, requiring a systematic approach to update all packages while maintaining compatibility across the integrated system.

#### Technical Context 🔧
- The project uses `uv` as the package manager (not pip) across all components
- **Multiple dependency trees** requiring coordinated updates:
  - `src/sk-agents/pyproject.toml` - Main agent framework and weather agent
  - `shared/ska_utils/pyproject.toml` - Shared utilities library
  - `src/orchestrators/assistant-orchestrator/orchestrator/pyproject.toml` - Assistant orchestrator
  - `src/orchestrators/assistant-orchestrator/services/pyproject.toml` - Assistant orchestrator services
  - `src/orchestrators/collab-orchestrator/orchestrator/pyproject.toml` - Collaboration orchestrator
  - `src/orchestrators/workflow-orchestrator/orchestrator/pyproject.toml` - Workflow orchestrator
- The project requires Python 3.13+ and uses modern dependency management with `uv.lock` files
- Components have interdependencies (ska_utils is used by other components)

#### Multi-Component Update Strategy 🎯

This task requires updating dependencies in the correct order to maintain compatibility:

##### **Phase 1: Core Dependencies (Shared Utilities)**
Update the shared utilities first since other components depend on it.

**Technical Requirements:**
- Update `shared/ska_utils/pyproject.toml` dependencies
- Test ska_utils functionality independently
- Ensure no breaking changes in the public API
- Update lock file and verify installation

##### **Phase 2: Main Agent Framework**
Update the core agent framework and weather agent dependencies.

**Technical Requirements:**
- Update `src/sk-agents/pyproject.toml` dependencies
- Ensure compatibility with updated ska_utils
- Test weather agent functionality with new dependencies
- Verify custom Gemini completion factory still works
- Test Streamlit UI integration

##### **Phase 3: Orchestrator Components**
Update all orchestrator components, handling potential interdependencies.

**Technical Requirements:**
- Update assistant-orchestrator (both orchestrator and services)
- Update collaboration orchestrator
- Update workflow orchestrator
- Test orchestrator functionality if possible
- Resolve any cross-component dependency conflicts

#### Recommended Implementation Approach 📋

**Dependency Analysis Phase:**
1. **Map Dependency Relationships**: Use `uv show --tree` in each component to understand current structure
2. **Identify Shared Dependencies**: Look for common packages across components (Semantic Kernel, FastAPI, etc.)
3. **Version Constraint Analysis**: Check for version pinning that might cause conflicts

**Update Strategy:**
1. **Sequential Updates**: Update components in dependency order (shared utilities first)
2. **Compatibility Testing**: Test each component after updates
3. **Conflict Resolution**: Address version conflicts between components
4. **Integration Testing**: Ensure components still work together

#### Component Testing Commands 🔧

**Shared Utilities Testing:**
```bash
cd shared/ska_utils && uv sync && uv run pytest tests/ -v
```

**Agent Framework Testing:**
```bash
cd src/sk-agents && uv sync
# Test framework startup
uv run python -c "import sk_agents; print('Framework imports successfully')"
# Test weather agent
TA_SERVICE_CONFIG=src/sk_agents/weather-agent/config.yaml \
TA_PLUGIN_MODULE=src/sk_agents/weather-agent/custom_plugins.py \
TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE=src/sk_agents/chat_completion/custom/gemini_chat_completion_factory.py \
TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS_NAME=GeminiChatCompletionFactory \
TA_API_KEY=test_key \
uv run python -m sk_agents.app --help
```

**Orchestrator Testing:**
```bash
# Assistant Orchestrator
cd src/orchestrators/assistant-orchestrator/orchestrator && uv sync
cd ../services && uv sync

# Collaboration Orchestrator  
cd src/orchestrators/collab-orchestrator/orchestrator && uv sync
```

#### Acceptance Criteria ✅

**Phase 1 - Shared Utilities:**
-   [ ] Update `shared/ska_utils/pyproject.toml` dependencies to latest stable versions
-   [ ] Run `uv update` to update the lock file in shared utilities
-   [ ] Verify installation works: `cd shared/ska_utils && uv sync`
-   [ ] Run existing tests: `cd shared/ska_utils && uv run pytest tests/ -v`
-   [ ] Ensure no breaking changes in ska_utils public API

**Phase 2 - Agent Framework:**
-   [ ] Update `src/sk-agents/pyproject.toml` dependencies to latest stable versions
-   [ ] Ensure compatibility with updated ska_utils dependency
-   [ ] Run `uv update` to update the lock file
-   [ ] Verify framework imports: `cd src/sk-agents && uv sync && uv run python -c "import sk_agents"`
-   [ ] Test weather agent can start (even with dummy API key): Weather agent startup command completes without import errors
-   [ ] Verify Streamlit UI dependencies are still compatible
-   [ ] Run existing tests if present: `cd src/sk-agents && uv run pytest tests/ -v`

**Phase 3 - Orchestrator Components:**
-   [ ] Update all orchestrator `pyproject.toml` files: assistant-orchestrator (orchestrator + services), collab-orchestrator, workflow-orchestrator
-   [ ] Run `uv update` in each orchestrator directory to update lock files
-   [ ] Verify installation in each component: `uv sync` completes without errors
-   [ ] Test imports in each orchestrator component
-   [ ] Resolve any cross-component dependency conflicts

**Integration & Validation:**
-   [ ] All `uv sync` commands complete successfully across all components
-   [ ] No dependency conflicts between components (check for version incompatibilities)
-   [ ] Weather agent functionality verified with updated dependencies
-   [ ] Document any breaking changes or migration requirements discovered
-   [ ] All existing tests pass with updated dependencies

**Documentation:**
-   [ ] Document the dependency update process for future maintenance
-   [ ] Note any version constraints that should be maintained
-   [ ] Include troubleshooting guide for common dependency conflicts


### **Task 4: Comprehensive Security Vulnerability Assessment and Remediation**

**Title:** `security: Scan for and fix critical dependency vulnerabilities across all repository components`

#### Description 🛡️
This task focuses on improving the security posture of the entire Teal Agents repository ecosystem. The agent must use security scanning tools to identify vulnerabilities across all Python components and orchestrators, then systematically remediate any discovered issues while maintaining system functionality and component compatibility.

#### Technical Context 🔧
- The project uses `uv` package manager with `uv.lock` files across multiple components
- **Multiple component security scanning required**:
  - `src/sk-agents/` - Main agent framework (includes weather agent)
  - `shared/ska_utils/` - Shared utilities library
  - `src/orchestrators/assistant-orchestrator/orchestrator/` - Assistant orchestrator core
  - `src/orchestrators/assistant-orchestrator/services/` - Assistant orchestrator services
  - `src/orchestrators/collab-orchestrator/orchestrator/` - Collaboration orchestrator
  - `src/orchestrators/workflow-orchestrator/orchestrator/` - Workflow orchestrator
- Modern Python security tools include `pip-audit`, `safety`, and `uv audit` (if available)
- Components have interdependencies that must be considered during security remediation

#### Multi-Component Security Strategy 🎯

This task requires systematic security assessment across all components with coordinated remediation:

##### **Phase 1: Security Tool Setup and Initial Scanning**
Install security scanning tools and perform comprehensive vulnerability assessment.

**Technical Requirements:**
- Install `pip-audit` or similar security scanning tools
- Perform initial scans across all components
- Catalog all discovered vulnerabilities with severity levels
- Identify cross-component dependency relationships that might affect remediation

##### **Phase 2: Vulnerability Analysis and Prioritization**
Analyze discovered vulnerabilities and create remediation strategy.

**Technical Requirements:**
- Categorize vulnerabilities by severity (Critical, High, Medium, Low)
- Identify shared dependencies across components
- Plan remediation order considering component interdependencies
- Check for known CVEs and security advisories

##### **Phase 3: Systematic Remediation**
Fix vulnerabilities while maintaining system functionality.

**Technical Requirements:**
- Update vulnerable packages in dependency order (shared utilities first)
- Test each component after security patches
- Ensure weather agent functionality remains intact
- Verify no new vulnerabilities introduced by updates

#### Security Scanning Implementation 🔍

**Tool Installation Options:**
```bash
# Option 1: Install pip-audit in main component
cd src/sk-agents && uv add --dev pip-audit

# Option 2: Install pip-audit globally
pip install pip-audit

# Option 3: Use safety (alternative tool)
cd src/sk-agents && uv add --dev safety
```

**Comprehensive Scanning Commands:**
```bash
# Scan all components systematically
components=(
  "shared/ska_utils"
  "src/sk-agents" 
  "src/orchestrators/assistant-orchestrator/orchestrator"
  "src/orchestrators/assistant-orchestrator/services"
  "src/orchestrators/collab-orchestrator/orchestrator"
  "src/orchestrators/workflow-orchestrator/orchestrator"
)

for component in "${components[@]}"; do
  echo "Scanning $component..."
  cd "$component" && uv run pip-audit
  cd - > /dev/null
done
```

**Alternative Scanning Approaches:**
```bash
# Using pip-audit directly on lock files
pip-audit --requirement shared/ska_utils/pyproject.toml
pip-audit --requirement src/sk-agents/pyproject.toml

# Using safety (if preferred)
cd src/sk-agents && uv run safety check

# Check for known CVEs
pip-audit --desc --format=json > security_report.json
```

#### Remediation Testing Strategy 🧪

**Component-Specific Testing:**
```bash
# Test shared utilities after patches
cd shared/ska_utils && uv sync && uv run pytest tests/ -v

# Test agent framework and weather agent
cd src/sk-agents && uv sync
# Test weather agent with security patches
TA_SERVICE_CONFIG=src/sk_agents/weather-agent/config.yaml \
TA_PLUGIN_MODULE=src/sk_agents/weather-agent/custom_plugins.py \
TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE=src/sk_agents/chat_completion/custom/gemini_chat_completion_factory.py \
TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS_NAME=GeminiChatCompletionFactory \
TA_API_KEY=test_key \
uv run python -c "import sk_agents; print('Security patches applied successfully')"

# Test orchestrator components
cd src/orchestrators/assistant-orchestrator/orchestrator && uv sync
cd ../services && uv sync
cd ../../collab-orchestrator/orchestrator && uv sync
```

#### Acceptance Criteria ✅

**Phase 1 - Security Assessment:**
-   [ ] Install security scanning tool (`pip-audit` or `safety`) in at least one component
-   [ ] Perform security scans on all 6 components: ska_utils, sk-agents, assistant-orchestrator (orchestrator + services), collab-orchestrator, workflow-orchestrator
-   [ ] Generate comprehensive vulnerability report documenting all findings
-   [ ] Categorize vulnerabilities by severity level (Critical, High, Medium, Low)
-   [ ] Identify any shared vulnerable dependencies across components

**Phase 2 - Vulnerability Analysis:**
-   [ ] Create remediation plan prioritizing critical and high-severity vulnerabilities
-   [ ] Document which components share vulnerable dependencies
-   [ ] Research security advisories and CVE details for discovered vulnerabilities
-   [ ] Plan update sequence considering component interdependencies (ska_utils first)

**Phase 3 - Remediation Implementation:**
-   [ ] Update vulnerable packages in `pyproject.toml` files across all affected components
-   [ ] Use `uv update` to refresh lock files after security patches
-   [ ] Ensure no new vulnerabilities introduced by dependency updates
-   [ ] Resolve any dependency conflicts caused by security updates

**Phase 4 - Functionality Verification:**
-   [ ] All components install successfully: `uv sync` completes without errors
-   [ ] Shared utilities tests pass: `cd shared/ska_utils && uv run pytest tests/ -v`
-   [ ] Agent framework imports successfully after patches
-   [ ] Weather agent functionality verified with updated dependencies
-   [ ] Orchestrator components install and import successfully

**Phase 5 - Security Validation:**
-   [ ] Re-run security scans on all components to verify vulnerabilities resolved
-   [ ] Confirm no critical or high-severity vulnerabilities remain
-   [ ] Generate final security report showing before/after vulnerability status
-   [ ] Document any vulnerabilities that couldn't be resolved and their mitigation strategies

**Documentation & Process:**
-   [ ] Document the security scanning and remediation process for future use
-   [ ] Include security scanning in recommended maintenance workflows
-   [ ] Create security incident response guidelines for future vulnerability discoveries
-   [ ] Document any security-related configuration changes or workarounds applied


### **Task 5: Generate Unit Tests for Weather Agent Components**

**Title:** `test: Generate comprehensive unit tests for individual weather agent components`

#### Description 🧪
The weather agent system created in Task 1 needs focused unit testing for its individual components. This task involves writing isolated unit tests that verify the behavior of each component independently, using mocking to eliminate external dependencies. The focus is on testing component logic, error handling, and data transformation without testing integration between components.

#### Technical Context 🔧
- The project already includes `pytest` and `pytest-mock` in dev dependencies (`src/sk-agents/pyproject.toml`)
- Existing test structure is in `src/sk-agents/tests/`
- **Components to unit test in isolation**:
  - `WeatherPlugin` class: `get_current_weather()` and `get_coordinates()` methods
  - `GeminiChatCompletionFactory` class: factory initialization and service creation
- Use `pytest-asyncio` for async test support (already included)
- **External dependencies to mock**:
  - Open-Meteo Geocoding API (`geocoding-api.open-meteo.com`)
  - Open-Meteo Weather API (`api.open-meteo.com`)
  - Google Gemini API (`generativeai.GenerativeModel`)

#### Unit Testing Strategy 🎯

Focus on isolated testing of individual components without integration testing:

##### **Component 1: WeatherPlugin Unit Tests**
Test weather plugin methods in complete isolation from the agent framework.

**Technical Requirements:**
- Test `get_current_weather()` method behavior with various inputs
- Test `get_coordinates()` method for geocoding functionality
- Mock all HTTP requests to Open-Meteo APIs
- Test error handling for API failures, timeouts, invalid responses
- Test data transformation and JSON formatting
- Test weather code to description mapping
- Verify input validation and sanitization

##### **Component 2: Gemini Completion Factory Unit Tests**
Test the completion factory as an isolated unit.

**Technical Requirements:**
- Test factory initialization with different configurations
- Mock Google Gemini API client instantiation
- Test service creation without actual API calls
- Test error handling for invalid API keys and configuration
- Test parameter validation and default handling
- Verify factory interface compliance (without Semantic Kernel integration)

#### Focused Test Structure 📁

**Simple, focused test organization:**
```
src/sk-agents/tests/
├── unit/
│   ├── __init__.py
│   ├── test_weather_plugin.py           # WeatherPlugin unit tests only
│   └── test_gemini_completion_factory.py   # Factory unit tests only
├── fixtures/
│   ├── weather_api_responses.json       # Mock API response data
│   └── geocoding_api_responses.json     # Mock geocoding data
└── conftest.py                          # Shared test fixtures
```

#### Unit Testing Best Practices 📋

**Isolated Component Testing:**
```python
# Example unit test structure (WeatherPlugin)
class TestWeatherPlugin:
    def test_get_current_weather_success(self, mock_requests):
        # Test successful weather retrieval with mocked API
        
    def test_get_current_weather_invalid_city(self, mock_requests):
        # Test error handling for invalid city names
        
    def test_get_coordinates_success(self, mock_requests):
        # Test successful geocoding with mocked API
        
    def test_weather_code_mapping(self):
        # Test weather code to description mapping (no external calls)
```

**Mock Strategy Examples:**
```python
# Mock external HTTP calls
@patch('urllib.request.urlopen')
def test_weather_api_call(self, mock_urlopen):
    # Mock HTTP response from Open-Meteo API
    
@patch('google.generativeai.GenerativeModel')
def test_gemini_factory_init(self, mock_model):
    # Mock Gemini model initialization
```

#### Acceptance Criteria ✅

**WeatherPlugin Unit Tests:**
-   [ ] Create `src/sk-agents/tests/unit/test_weather_plugin.py` with isolated WeatherPlugin tests
-   [ ] Test `get_current_weather()` method: successful responses, invalid cities, API errors, network failures
-   [ ] Test `get_coordinates()` method: successful geocoding, location not found, malformed responses
-   [ ] All external HTTP requests mocked using `pytest-mock` or `unittest.mock`
-   [ ] Test weather code description mapping without external dependencies
-   [ ] Test JSON response format validation and error message structure
-   [ ] Test input validation and edge cases (empty strings, special characters)

**Gemini Completion Factory Unit Tests:**
-   [ ] Create `src/sk-agents/tests/unit/test_gemini_completion_factory.py`
-   [ ] Test factory initialization with valid and invalid parameters
-   [ ] Mock Google Gemini API client creation (no actual API calls)
-   [ ] Test configuration parameter handling and validation
-   [ ] Test error handling for missing API keys and invalid model names
-   [ ] Test factory interface methods without Semantic Kernel dependencies

**Test Infrastructure:**
-   [ ] Create realistic mock data in `fixtures/` directory for API responses
-   [ ] Create shared test fixtures in `conftest.py` for common test setup
-   [ ] All tests run in isolation: `cd src/sk-agents && uv run pytest tests/unit/ -v`
-   [ ] Tests execute quickly (<10 seconds) since they have no external dependencies
-   [ ] Tests achieve good coverage (>80%) of the individual component logic
-   [ ] No external API calls made during test execution (all mocked)

**Test Quality:**
-   [ ] Each test focuses on a single behavior or error condition
-   [ ] Tests use descriptive names that explain what is being tested
-   [ ] Mock data represents realistic API responses and error conditions
-   [ ] Tests verify both success paths and comprehensive error handling
-   [ ] No dependencies on agent configuration, Semantic Kernel, or FastAPI framework


### **Task 6: Implement End-to-End Tests for Weather Agent System**

**Title:** `test: Implement comprehensive E2E tests for the complete weather agent system using Robot Framework`

#### Description 🚦
The weather agent system created in Task 1 needs comprehensive end-to-end testing to ensure it works correctly when deployed as a complete system. This task involves creating integration tests that verify the entire workflow from HTTP requests through the FastAPI service, agent processing, external API calls, and response formatting. The focus is on testing the complete system integration without mocking internal components.

#### Technical Context 🔧
- The Teal Agents Framework runs on FastAPI with configurable ports
- Weather agent endpoints follow REST API patterns accessible via `/docs` Swagger UI
- **Complete system integration testing**:
  - FastAPI service startup and shutdown
  - Agent configuration loading and validation
  - HTTP endpoint accessibility and routing
  - Complete request/response workflow
  - External API integration (with network-level mocking)
  - Error handling and edge cases
- Robot Framework provides structured, keyword-driven testing
- Network-level mocking isolates external dependencies while testing integration

#### End-to-End Testing Strategy 🎯

Focus on complete system integration without internal component mocking:

##### **Component 1: Service Lifecycle Management**
Test the complete FastAPI service startup, configuration, and shutdown.

**Technical Requirements:**
- Test weather agent service startup with proper configuration
- Verify all required environment variables and dependencies
- Test graceful service shutdown and cleanup
- Test service health and readiness endpoints
- Verify correct port binding and HTTP server configuration
- Test service restart and recovery scenarios

##### **Component 2: Complete API Workflow Testing**
Test the full HTTP request/response cycle through the agent system.

**Technical Requirements:**
- Test weather agent HTTP endpoints with various request formats
- Verify complete request processing: HTTP → Agent → Gemini → Weather API → Response
- Test agent configuration loading and plugin integration
- Test error propagation through the complete system
- Verify response formatting and HTTP status codes
- Test concurrent request handling and performance

##### **Component 3: External API Integration Testing**
Test integration with external services using network-level mocking.

**Technical Requirements:**
- Mock external APIs at network level (not component level)
- Test weather agent responses to various external API scenarios
- Test error handling for external API failures
- Test timeout and retry behavior
- Verify data transformation through the complete pipeline
- Test edge cases and malformed external responses

#### Focused E2E Test Structure 📁

**Robot Framework organization for system testing:**
```
src/sk-agents/tests/e2e/
├── weather_agent_system.robot        # Main E2E test suite
├── keywords/
│   ├── service_management.robot      # Service start/stop/health
│   ├── api_workflow.robot            # HTTP request/response testing
│   └── external_mocking.robot        # Network-level mocking setup
├── resources/
│   ├── test_configurations.yaml      # Test agent configurations
│   ├── mock_external_responses.json  # Mock external API data
│   └── test_data.json               # Test request/response data
└── libraries/
    └── WeatherAgentLibrary.py        # Custom Python test helpers
```

#### Integration Testing Best Practices 📋

**Complete System Testing:**
```robot
*** Test Cases ***
Weather Agent Complete Workflow
    [Documentation]    Test complete weather request workflow
    [Setup]    Start Weather Agent Service    port=8001
    [Teardown]    Stop Weather Agent Service
    
    Setup External API Mocks
    Send Weather Request    city=Prague
    Verify Weather Response Format
    Verify External API Called
    
Weather Agent Error Handling
    [Documentation]    Test error handling through complete system
    [Setup]    Start Weather Agent Service    port=8001
    [Teardown]    Stop Weather Agent Service
    
    Setup External API Error Mocks
    Send Weather Request    city=InvalidCity
    Verify Error Response Format
    Verify Graceful Error Handling
```

**Service Management Examples:**
```robot
*** Keywords ***
Start Weather Agent Service
    [Arguments]    ${port}=8001
    Set Environment Variable    TA_SERVICE_CONFIG    src/sk_agents/weather-agent/config.yaml
    Set Environment Variable    TA_PLUGIN_MODULE    src/sk_agents/weather-agent/custom_plugins.py
    Start Process    uvicorn    sk_agents.app:app    --host=0.0.0.0    --port=${port}
    Wait For Service Health    http://localhost:${port}/health
```

#### Acceptance Criteria ✅

**Service Lifecycle Testing:**
-   [ ] Add Robot Framework dependencies: `robotframework`, `robotframework-requests`, `robotframework-process`
-   [ ] Create `src/sk-agents/tests/e2e/weather_agent_system.robot` with complete system tests
-   [ ] Implement service startup/shutdown keywords that manage FastAPI process lifecycle
-   [ ] Test weather agent starts successfully with all required environment variables
-   [ ] Test service health endpoints and readiness verification
-   [ ] Implement proper test cleanup and service shutdown procedures

**Complete API Workflow Testing:**
-   [ ] Test complete HTTP request workflow: Request → FastAPI → Agent → Gemini → Weather API → Response
-   [ ] Verify weather agent processes various natural language weather queries
-   [ ] Test HTTP endpoint accessibility and correct routing to agent endpoints
-   [ ] Verify proper HTTP status codes for success and error scenarios
-   [ ] Test request/response format validation through the complete system
-   [ ] Test concurrent request handling and basic performance characteristics

**External Integration Testing:**
-   [ ] Implement network-level mocking for Open-Meteo and Gemini APIs
-   [ ] Test weather agent behavior with various external API response scenarios
-   [ ] Test error handling when external APIs are unavailable or return errors
-   [ ] Verify proper timeout and retry behavior for external service calls
-   [ ] Test data transformation and formatting through the complete pipeline
-   [ ] Test edge cases: malformed external responses, rate limiting, network issues

**Test Infrastructure:**
-   [ ] Create reusable Robot Framework keywords for service management
-   [ ] Implement custom Python libraries for complex test setup and verification
-   [ ] Create comprehensive test data sets covering various weather scenarios
-   [ ] All E2E tests run successfully: `cd src/sk-agents && uv run robot tests/e2e/`
-   [ ] Tests demonstrate complete system functionality without internal mocking
-   [ ] Test suite includes proper setup, execution, and cleanup phases

**System Integration Validation:**
-   [ ] Tests verify the weather agent works as a complete deployed system
-   [ ] Validate configuration loading, plugin integration, and external API calls
-   [ ] Test error scenarios and recovery at the system level
-   [ ] Verify performance and reliability characteristics of the complete system
-   [ ] Document test execution procedures and expected outcomes for future use

<br>

### **Task 7: Comprehensive Migration from Semantic Kernel to LangChain**

**Title:** `refactor: Migrate entire repository from Semantic Kernel to LangChain with comprehensive testing and validation`

#### Description 🏗️
Perform a comprehensive, project-wide migration of the entire Teal Agents repository from the **Semantic Kernel** framework to the **LangChain** framework. This is a complex architectural refactoring task that tests deep codebase understanding, framework adaptability, and systematic migration planning. The migration must maintain functional parity while adopting LangChain's architectural patterns and best practices.

#### Technical Context 🔧
- **Current Architecture**: Semantic Kernel v1.33.0 with FastAPI, custom completion factories, and plugin system
- **Target Architecture**: LangChain with LangServe for web deployment, tools, chains, and runnables
- **Migration Scope**: All components across the repository:
  - `src/sk-agents/` - Main agent framework and weather agent
  - `src/sk-agents/docs/demos/` - All demo configurations
  - `shared/ska_utils/` - Shared utilities (if Semantic Kernel dependent)
  - `src/orchestrators/` - Agent orchestration services
- **Compatibility Requirements**: Maintain API contracts and external interface compatibility
- **Testing Requirements**: All existing unit tests and E2E tests must pass with new implementation

#### Multi-Phase Migration Strategy 🎯

This migration requires careful planning and execution across multiple phases:

##### **Phase 1: Architecture Analysis and Planning**
Analyze current Semantic Kernel usage and design LangChain equivalents.

**Technical Requirements:**
- Audit all Semantic Kernel dependencies and usage patterns
- Map Semantic Kernel concepts to LangChain equivalents
- Design new YAML configuration schema for LangChain
- Plan migration path for custom completion factories
- Identify breaking changes and mitigation strategies

**Expected Deliverables:**
- Migration plan document with detailed component mapping
- New LangChain-based YAML schema design
- Compatibility analysis and breaking change assessment
- Migration timeline and risk assessment

##### **Phase 2: Core Framework Migration**
Migrate the core agent framework and infrastructure.

**Technical Requirements:**
- Replace Semantic Kernel dependencies with LangChain ecosystem
- Implement LangChain-based agent execution engine
- Migrate custom completion factories to LangChain providers
- Convert plugin system from `@kernel_function` to LangChain tools
- Update FastAPI integration to use LangServe patterns

**Expected Deliverables:**
- Updated `src/sk-agents/pyproject.toml` with LangChain dependencies
- New LangChain-based agent execution engine
- Migrated custom completion factories (Gemini integration)
- Updated core framework modules and utilities

##### **Phase 3: Weather Agent Migration**
Migrate the weather agent as a reference implementation.

**Technical Requirements:**
- Convert WeatherPlugin to LangChain tool format
- Update weather agent configuration to LangChain schema
- Maintain existing API endpoints and response formats
- Ensure Streamlit UI continues to work
- Validate complete weather agent workflow

**Expected Deliverables:**
- Migrated `src/sk_agents/weather-agent/` with LangChain implementation
- Updated configuration files using new schema
- Converted weather tools and chain logic
- Validated Streamlit UI integration

##### **Phase 4: Demo and Documentation Migration**
Migrate all demo configurations and update documentation.

**Technical Requirements:**
- Convert all demo configurations in `src/sk-agents/docs/demos/`
- Update documentation to reflect LangChain architecture
- Create migration guide for future agent development
- Update troubleshooting guides and best practices

**Expected Deliverables:**
- All demo configurations converted to LangChain format
- Updated architecture documentation
- Migration guide and best practices documentation
- Developer onboarding materials updated for LangChain

#### Detailed Technical Mappings 🔧

**Framework Component Migrations:**
```
Semantic Kernel → LangChain:
├── @kernel_function → @tool decorator
├── BasePlugin → BaseTool class  
├── Sequential agent → AgentExecutor/Chain
├── ChatCompletion → ChatModel/LLM
├── KernelBuilder → Chain composition
├── FastAPI routes → LangServe add_routes()
└── Plugin execution → Tool invocation
```

**Configuration Schema Migration:**
```yaml
# Current Semantic Kernel Schema
apiVersion: skagents/v1
kind: Sequential
spec:
  agents:
    - name: default
      model: gemini-1.5-flash
      plugins: [WeatherPlugin]

# Target LangChain Schema  
apiVersion: langchain/v1
kind: AgentExecutor
spec:
  llm:
    provider: custom_gemini
    model: gemini-1.5-flash
  tools: [weather_tool]
  agent_type: openai-functions
```

**Code Migration Examples:**
```python
# Before (Semantic Kernel)
from semantic_kernel.functions import kernel_function

class WeatherPlugin(BasePlugin):
    @kernel_function(description="Get weather")
    def get_weather(self, city: str) -> str:
        return self._fetch_weather(city)

# After (LangChain)
from langchain.tools import tool
from langchain.tools import BaseTool

@tool
def get_weather(city: str) -> str:
    """Get weather information for a city."""
    return _fetch_weather(city)

class WeatherTool(BaseTool):
    name = "get_weather"
    description = "Get weather information for a city"
    
    def _run(self, city: str) -> str:
        return _fetch_weather(city)
```

#### Migration Testing Strategy 🧪

**Comprehensive Validation Approach:**
```bash
# Pre-migration baseline testing
cd src/sk-agents && uv run pytest tests/ -v --tb=short
cd src/sk-agents && uv run robot tests/e2e/

# Post-migration validation testing  
cd src/sk-agents && uv run pytest tests/ -v --tb=short
cd src/sk-agents && uv run robot tests/e2e/

# API compatibility testing
curl -X POST "http://localhost:8001/WeatherAgent/0.1/" \
  -H "Content-Type: application/json" \
  -d '{"chat_history": [{"role": "user", "content": "Weather in Prague?"}]}'
```

#### Acceptance Criteria ✅

**Phase 1 - Architecture Analysis:**
-   [ ] Complete audit of Semantic Kernel usage across all repository components
-   [ ] Design new LangChain-based YAML configuration schema
-   [ ] Create detailed migration plan mapping all Semantic Kernel concepts to LangChain
-   [ ] Identify and document all breaking changes and required adaptations
-   [ ] Plan migration timeline and risk mitigation strategies

**Phase 2 - Core Framework Migration:**
-   [ ] Replace `semantic-kernel` dependencies with `langchain`, `langchain-openai`, `langchain-community`, `langserve`
-   [ ] Implement new LangChain-based agent execution engine
-   [ ] Migrate custom Gemini completion factory to LangChain provider pattern
-   [ ] Convert core plugin system from Semantic Kernel to LangChain tools
-   [ ] Update FastAPI integration to use LangServe deployment patterns
-   [ ] Ensure shared utilities (ska_utils) work with new framework

**Phase 3 - Weather Agent Migration:**
-   [ ] Convert WeatherPlugin to LangChain BaseTool or @tool implementation
-   [ ] Update weather agent configuration to use new LangChain schema
-   [ ] Maintain existing HTTP API endpoints and response format compatibility
-   [ ] Ensure Streamlit UI continues to work with migrated agent
-   [ ] Validate complete weather workflow: UI → LangServe → Agent → Tools → APIs

**Phase 4 - Demo and Documentation Migration:**
-   [ ] Convert all demo configurations in `src/sk-agents/docs/demos/` to LangChain format
-   [ ] Update main README.md and architecture documentation to reflect LangChain concepts
-   [ ] Create comprehensive migration guide for future agent development
-   [ ] Update DEVELOPER_GUIDE.md and TESTING_GUIDE.md for LangChain patterns
-   [ ] Document new LangChain-specific troubleshooting and best practices

**Migration Validation:**
-   [ ] All existing unit tests pass with new LangChain implementation
-   [ ] All existing E2E tests pass with new LangChain implementation  
-   [ ] Weather agent API endpoints maintain exact same input/output format
-   [ ] Streamlit UI works identically with migrated backend
-   [ ] Performance benchmarks show comparable or improved performance
-   [ ] All orchestrator components updated to work with new framework

**Quality Assurance:**
-   [ ] Code quality maintained: linting, type checking, and formatting standards
-   [ ] Documentation accuracy: all code examples tested and functional
-   [ ] Migration reproducibility: process documented for future framework changes
-   [ ] Rollback plan: ability to revert to Semantic Kernel if critical issues discovered
-   [ ] Knowledge transfer: team understands new LangChain architecture and patterns

<br>

### **Task 8: Complete Cross-Language Migration from Python to Go**

**Title:** `refactor: Comprehensive rewrite of the entire repository from Python to Go with full feature parity`

#### Description 🚀
This is the ultimate software engineering challenge: a complete cross-language migration of the entire `teal-agents` repository from **Python** to **Go (Golang)**. Building on the **Semantic Kernel-based** implementation (before Task 7), this task requires re-implementing all core concepts, architectural patterns, and functionality using idiomatic Go practices while maintaining complete API compatibility and feature parity.

#### Technical Context 🔧
- **Source Architecture**: Python Semantic Kernel implementation with FastAPI, custom plugins, and YAML configuration
- **Target Architecture**: Go-based agent framework with equivalent web service and AI integration
- **Migration Scope**: Complete repository transformation:
  - Core Semantic Kernel agent framework and execution engine
  - Weather agent with all existing functionality
  - All demo configurations and examples
  - Shared utilities and orchestrator concepts
  - Testing frameworks and deployment infrastructure
- **Compatibility Requirements**: Full API compatibility, YAML configuration format preservation, performance improvements
- **Go Ecosystem Integration**: Modern Go practices, dependency management, and tooling

#### Multi-Phase Go Implementation Strategy 🎯

This migration requires systematic planning and execution across multiple development phases:

##### **Phase 1: Go Architecture Design and Foundation**
Design Go-native architecture that preserves Python Semantic Kernel functionality while leveraging Go strengths.

**Technical Requirements:**
- Design Go package architecture for agents, plugins, configuration, and web services
- Plan Go module structure and dependency management strategy
- Design Go interfaces that map to Python Semantic Kernel concepts (kernel, functions, plugins)
- Plan concurrency patterns for agent execution using Go goroutines
- Design YAML configuration system using Go structs and unmarshaling

**Expected Deliverables:**
- Go module initialization and project structure
- Architecture design document with package relationships
- Interface definitions for kernel, agents, plugins, and configuration
- Dependency management strategy (go.mod design)
- Concurrency and error handling patterns

##### **Phase 2: Core Semantic Kernel Framework Implementation**
Implement the core Semantic Kernel-equivalent execution engine and framework infrastructure.

**Technical Requirements:**
- Implement kernel execution engine with function/plugin invocation
- Create YAML configuration loading and validation system
- Implement HTTP server using Gin with FastAPI-equivalent route handling
- Design plugin/function interface system with Go interfaces
- Implement logging, telemetry, and error handling

**Expected Deliverables:**
- Core kernel execution engine (`pkg/kernel/`)
- Configuration system (`pkg/config/`)
- HTTP API framework (`pkg/api/`)
- Plugin interface system (`pkg/plugins/`)
- Logging and monitoring infrastructure

##### **Phase 3: Weather Agent Go Implementation**
Implement the weather agent as a complete Go application with all existing features.

**Technical Requirements:**
- Implement weather plugin in Go with Open-Meteo API integration
- Create Gemini API integration using Go HTTP client
- Implement YAML agent configuration loading and plugin registration
- Create HTTP endpoints matching Python FastAPI exactly
- Implement comprehensive error handling and logging

**Expected Deliverables:**
- Weather plugin implementation (`internal/weather/`)
- Gemini integration service (`internal/gemini/`)
- Weather agent YAML configuration and registration
- HTTP API handlers with exact Python compatibility
- Complete weather agent deployment package

##### **Phase 4: Testing and Validation Infrastructure**
Implement comprehensive testing infrastructure to validate Go implementation.

**Technical Requirements:**
- Implement unit tests for all Go packages using testify
- Create integration tests for complete weather agent workflow
- Implement API compatibility tests against Python baseline
- Create performance benchmarks comparing Go vs Python
- Implement test data management and mocking infrastructure

**Expected Deliverables:**
- Complete unit test suite for all Go packages
- Integration test framework for end-to-end validation
- API compatibility test suite
- Performance benchmark suite
- Test infrastructure and CI/CD integration

#### Detailed Go Architecture Design 🏗️

**Go Project Structure (Enhanced):**
```
teal-agents-go/
├── go.mod                           # Go module definition
├── go.sum                           # Dependency checksums
├── Makefile                         # Build and development tasks
├── cmd/
│   ├── agent-server/                # Main server application
│   │   └── main.go
│   ├── config-validator/            # Configuration validation tool
│   │   └── main.go
│   └── benchmark/                   # Performance benchmarking tool
│       └── main.go
├── pkg/                             # Public packages
│   ├── kernel/                      # Semantic Kernel execution engine
│   │   ├── executor.go
│   │   ├── function.go
│   │   └── interfaces.go
│   ├── plugins/                     # Plugin interface and registry
│   │   ├── registry.go
│   │   ├── base.go
│   │   └── interfaces.go
│   ├── config/                      # Configuration management
│   │   ├── loader.go
│   │   ├── validator.go
│   │   └── types.go
│   ├── api/                         # HTTP API framework
│   │   ├── server.go
│   │   ├── middleware.go
│   │   └── handlers.go
│   └── telemetry/                   # Logging and monitoring
│       ├── logger.go
│       └── metrics.go
├── internal/                        # Private implementation
│   ├── weather/                     # Weather tool implementation
│   │   ├── tool.go
│   │   ├── client.go
│   │   └── types.go
│   ├── gemini/                      # Gemini API integration
│   │   ├── client.go
│   │   ├── completion.go
│   │   └── types.go
│   └── handlers/                    # HTTP request handlers
│       ├── weather.go
│       └── health.go
├── configs/                         # Configuration files
│   ├── agents/                      # Agent YAML configurations
│   │   └── weather-agent.yaml
│   └── demos/                       # Demo configurations
├── tests/                           # Test suites
│   ├── unit/                        # Unit tests
│   ├── integration/                 # Integration tests
│   ├── api/                         # API compatibility tests
│   └── benchmarks/                  # Performance benchmarks
├── docs/                            # Go-specific documentation
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── DEPLOYMENT.md
└── docker/                          # Docker configurations
    ├── Dockerfile
    └── docker-compose.yaml
```

**Go Technology Stack (Enhanced):**
```go
// Core dependencies
require (
    github.com/gin-gonic/gin v1.9.1          // HTTP web framework
    github.com/sashabaranov/go-openai v1.15.3 // OpenAI/Gemini API client
    gopkg.in/yaml.v3 v3.0.1                  // YAML configuration parsing
    github.com/go-resty/resty/v2 v2.7.0      // HTTP client for external APIs
    github.com/stretchr/testify v1.8.4       // Testing framework
    github.com/sirupsen/logrus v1.9.3        // Structured logging
    github.com/prometheus/client_golang v1.16.0 // Metrics and monitoring
    github.com/spf13/cobra v1.7.0            // CLI framework
    github.com/spf13/viper v1.16.0           // Configuration management
)
```

**Go Interface Design Examples:**
```go
// Kernel interface (Semantic Kernel equivalent)
type Kernel interface {
    InvokeFunction(ctx context.Context, function KernelFunction, input FunctionInput) (FunctionResult, error)
    RegisterPlugin(plugin Plugin) error
    GetFunction(pluginName, functionName string) (KernelFunction, error)
}

// Plugin interface (Semantic Kernel plugin equivalent)
type Plugin interface {
    Name() string
    Description() string
    GetFunctions() []KernelFunction
}

// Function interface (Semantic Kernel function equivalent)
type KernelFunction interface {
    Name() string
    Description() string
    Execute(ctx context.Context, input FunctionInput) (FunctionResult, error)
    GetParameters() []FunctionParameter
}

// Configuration interface
type ConfigLoader interface {
    LoadAgent(path string) (*AgentConfig, error)
    ValidateConfig(config *AgentConfig) error
}
```

#### Cross-Language Migration Strategy 🔄

**Python to Go Concept Mapping:**
```
Python Semantic Kernel → Go Implementation:
├── Semantic Kernel → Go Kernel interface
├── KernelFunction → Go KernelFunction interface  
├── Plugin → Go Plugin interface
├── FastAPI routes → Gin HTTP handlers
├── Pydantic models → Go structs with validation
├── Python async/await → Go goroutines/channels
├── Python error handling → Go error interface
├── Python logging → Go logrus/slog
└── Python testing → Go testify/testing
```

**API Compatibility Preservation:**
```go
// HTTP endpoint compatibility
type WeatherRequest struct {
    ChatHistory []ChatMessage `json:"chat_history"`
}

type WeatherResponse struct {
    SessionID    string      `json:"session_id"`
    Source       string      `json:"source"`
    RequestID    string      `json:"request_id"`
    TokenUsage   TokenUsage  `json:"token_usage"`
    ExtraData    interface{} `json:"extra_data"`
    OutputRaw    string      `json:"output_raw"`
    OutputData   interface{} `json:"output_pydantic"`
}
```

#### Go Development and Testing Strategy 🧪

**Go-Specific Testing Approach:**
```bash
# Go testing commands
go test ./... -v                     # Run all tests
go test -race ./...                  # Race condition detection
go test -cover ./...                 # Coverage analysis
go test -bench=. ./...               # Benchmark tests
go test -cpuprofile=cpu.prof ./...   # Performance profiling

# API compatibility validation
go run cmd/compatibility-test/main.go --python-baseline=http://localhost:8001

# Performance benchmarking
go test -bench=BenchmarkWeatherAgent -benchmem ./tests/benchmarks/
```

#### Acceptance Criteria ✅

**Phase 1 - Go Architecture Foundation:**
-   [ ] Initialize Go module: `go mod init github.com/merck-gen/teal-agents-go`
-   [ ] Design and implement complete Go package architecture
-   [ ] Create Go interfaces that map to all Python LangChain concepts
-   [ ] Implement Go configuration system with YAML unmarshaling and validation
-   [ ] Design concurrency patterns using goroutines for agent execution
-   [ ] Create comprehensive architecture documentation for Go implementation

**Phase 2 - Core Framework Implementation:**
-   [ ] Implement core Semantic Kernel execution engine with function and plugin support
-   [ ] Create HTTP server using Gin with middleware and routing (FastAPI equivalent)
-   [ ] Implement YAML configuration loading and validation system
-   [ ] Create plugin interface system with registration and discovery
-   [ ] Implement structured logging and telemetry collection
-   [ ] Create error handling patterns and recovery mechanisms

**Phase 3 - Weather Agent Implementation:**
-   [ ] Implement complete weather plugin in Go with Open-Meteo integration
-   [ ] Create Gemini API client and integration service in Go
-   [ ] Implement YAML agent configuration loading and plugin registration
-   [ ] Create HTTP API handlers with exact Python endpoint compatibility
-   [ ] Implement comprehensive error handling and input validation
-   [ ] Package complete weather agent as deployable Go application

**Phase 4 - Testing and Validation:**
-   [ ] Create comprehensive unit test suite using testify framework
-   [ ] Implement integration tests for complete weather agent workflow
-   [ ] Create API compatibility test suite validating exact Python equivalence
-   [ ] Implement performance benchmarks comparing Go vs Python performance
-   [ ] Create test data management and external API mocking infrastructure
-   [ ] Validate all existing Python test scenarios pass with Go implementation

**Cross-Language Compatibility:**
-   [ ] All HTTP API endpoints return identical JSON structures to Python version
-   [ ] YAML configuration files are fully compatible between Python and Go versions
-   [ ] Environment variable patterns and configuration methods are preserved
-   [ ] Error messages and status codes match Python implementation exactly
-   [ ] Performance benchmarks show Go implementation meets or exceeds Python performance

**Production Readiness:**
-   [ ] Docker support with optimized Go multi-stage builds
-   [ ] CI/CD pipeline integration with Go testing and building
-   [ ] Comprehensive deployment documentation for Go application
-   [ ] Migration guide for transitioning from Python to Go deployment
-   [ ] Monitoring and observability integration using Go metrics libraries
-   [ ] Security scanning and vulnerability assessment for Go dependencies

**Quality Assurance:**
-   [ ] Go code follows standard formatting (gofmt) and linting (golangci-lint)
-   [ ] Code coverage analysis shows >80% coverage across all packages
-   [ ] Race condition detection passes with `-race` flag
-   [ ] Memory leak detection and performance profiling completed
-   [ ] Documentation includes Go-specific development and deployment guides

---


## 🛠️ Troubleshooting Guide for Coding Agents

### Framework-Specific Troubleshooting

#### Weather Agent Development Issues

**Gemini API Integration Problems:**
```bash
# Test Gemini API connectivity
python -c "import google.generativeai as genai; genai.configure(api_key='your_key'); print('API key valid')"

# Check custom completion factory loading
echo $TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE
echo $TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS_NAME

# Verify factory class exists
python -c "from src.sk_agents.chat_completion.custom.gemini_chat_completion_factory import GeminiChatCompletionFactory; print('Factory loaded')"
```

**Weather Plugin Issues:**
```bash
# Test Open-Meteo API directly
curl "https://geocoding-api.open-meteo.com/v1/search?name=Prague&count=1"
curl "https://api.open-meteo.com/v1/forecast?latitude=50.0755&longitude=14.4378&current_weather=true"

# Verify plugin functions
python -c "from src.sk_agents.weather-agent.custom_plugins import WeatherPlugin; p = WeatherPlugin(); print(p.get_coordinates('Prague'))"
```

**Streamlit UI Problems:**
```bash
# Check Streamlit installation
uv run streamlit --version

# Test UI with agent running
cd src/sk_agents/src/sk_agents/weather-agent
uv run streamlit run streamlit_ui.py --server.port 8501

# Debug API connection
curl -X POST "http://localhost:8001/WeatherAgent/0.1/" -H "Content-Type: application/json" -d '{"chat_history": []}'
```

#### Documentation Issues

**Missing Demo Configurations:**
```bash
# Find all demo directories
find src/sk-agents/docs/demos/ -type d -name "*" | sort

# Check for missing README files
find src/sk-agents/docs/demos/ -type d -exec test ! -f {}/README.md \; -print

# Validate YAML in demos
for file in $(find src/sk-agents/docs/demos/ -name "*.yaml"); do
  python -c "import yaml; yaml.safe_load(open('$file'))" || echo "Invalid: $file"
done
```

#### Dependency & Security Issues

**Multi-Component Dependency Conflicts:**
```bash
# Check for version conflicts across components
for component in "shared/ska_utils" "src/sk-agents" "src/orchestrators/assistant-orchestrator/orchestrator" "src/orchestrators/assistant-orchestrator/services" "src/orchestrators/collab-orchestrator/orchestrator" "src/orchestrators/workflow-orchestrator/orchestrator"; do
  echo "=== $component ==="
  cd "$component" && uv pip list | grep -E "(semantic-kernel|fastapi|pydantic)"
  cd - > /dev/null
done

# Reset environment if sync fails
for component in "shared/ska_utils" "src/sk-agents" "src/orchestrators/assistant-orchestrator/orchestrator" "src/orchestrators/assistant-orchestrator/services" "src/orchestrators/collab-orchestrator/orchestrator" "src/orchestrators/workflow-orchestrator/orchestrator"; do
  cd "$component" && rm -rf .venv uv.lock && uv sync
  cd - > /dev/null
done
```

**Security Scanning Issues:**
```bash
# Install security tools globally if component installation fails
pip install pip-audit safety

# Run security scans with verbose output
for component in "shared/ska_utils" "src/sk-agents"; do
  echo "Scanning $component..."
  cd "$component" && pip-audit --desc --format=json
  cd - > /dev/null
done

# Check for specific vulnerabilities
pip-audit --requirement src/sk-agents/pyproject.toml --vulnerability-id PYSEC-2023-XXX
```

#### Testing Infrastructure Issues

**Unit Test Problems:**
```bash
# Run tests with detailed output
cd src/sk-agents && uv run pytest tests/unit/ -v -s --tb=long

# Check mock imports
python -c "from unittest.mock import patch, MagicMock; print('Mocking available')"

# Test specific component in isolation
cd src/sk-agents && uv run pytest tests/unit/test_weather_plugin.py::TestWeatherPlugin::test_get_current_weather_success -v

# Check test dependencies
uv run python -c "import pytest, pytest_mock, pytest_asyncio; print('Test dependencies OK')"
```

**Robot Framework E2E Issues:**
```bash
# Install Robot Framework dependencies
cd src/sk-agents && uv add --dev robotframework robotframework-requests robotframework-process

# Test Robot Framework installation
uv run robot --version

# Debug test execution
uv run robot --loglevel DEBUG --output debug_output.xml tests/e2e/

# Check service startup in tests
ps aux | grep "uvicorn\|fastapi" | grep -v grep

# Test external API mocking
curl -X GET "http://localhost:8001/health" || echo "Service not running"
```

#### Framework Migration Issues

**LangChain Migration Problems:**
```bash
# Check LangChain installation
cd src/sk-agents && uv run python -c "import langchain, langchain_openai, langchain_community, langserve; print('LangChain installed')"

# Test configuration migration
python -c "import yaml; config = yaml.safe_load(open('migrated_config.yaml')); print(config['apiVersion'])"

# Verify API compatibility
curl -X POST "http://localhost:8001/WeatherAgent/0.1/" -H "Content-Type: application/json" -d '{"chat_history": []}' | jq '.'
```

**Go Migration Problems:**
```bash
# Check Go installation
go version

# Test Go module initialization
cd teal-agents-go && go mod tidy

# Build Go application
go build -o agent-server cmd/agent-server/main.go

# Test API compatibility
go run cmd/compatibility-test/main.go --python-baseline=http://localhost:8001

# Run Go tests
go test ./... -v -race -cover
```

### General Troubleshooting Commands

#### Component Status Check
```bash
# Check all component environments
for component in "shared/ska_utils" "src/sk-agents" "src/orchestrators/assistant-orchestrator/orchestrator" "src/orchestrators/assistant-orchestrator/services" "src/orchestrators/collab-orchestrator/orchestrator" "src/orchestrators/workflow-orchestrator/orchestrator"; do
  echo "=== $component ==="
  cd "$component" && uv run python --version && echo "Python OK" || echo "Python FAIL"
  cd - > /dev/null
done
```

#### Environment Variables Debug
```bash
# Check all required environment variables for weather agent
echo "TA_SERVICE_CONFIG: $TA_SERVICE_CONFIG"
echo "TA_PLUGIN_MODULE: $TA_PLUGIN_MODULE"
echo "TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE: $TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE"
echo "TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS_NAME: $TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS_NAME"
echo "TA_API_KEY: ${TA_API_KEY:+SET}${TA_API_KEY:-NOT_SET}"

# Test configuration loading
python -c "import os; print('Config exists:', os.path.exists(os.environ.get('TA_SERVICE_CONFIG', '')))"
```

#### Port and Process Management
```bash
# Find processes using common ports
lsof -i :8001 -i :8501

# Kill hanging processes
pkill -f "uvicorn\|fastapi\|streamlit"

# Test port availability
nc -z localhost 8001 && echo "Port 8001 in use" || echo "Port 8001 available"
```

### Common Error Messages and Solutions

- **"ModuleNotFoundError: No module named 'google.generativeai'"**: Run `cd src/sk-agents && uv add google-generativeai`
- **"Custom completion factory not found"**: Check `TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE` and `TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS_NAME`
- **"Open-Meteo API error"**: Check internet connection and API endpoints
- **"Robot Framework import error"**: Run `cd src/sk-agents && uv add --dev robotframework robotframework-requests`
- **"LangChain compatibility error"**: Ensure all Semantic Kernel imports are replaced
- **"Go build error"**: Check Go version (1.19+) and run `go mod tidy`
- **"Security scan failed"**: Install pip-audit globally or use alternative security tools
- **"Dependency conflict"**: Use `uv update` in correct order (ska_utils first, then other components)

### Framework Development Best Practices

1. **Weather Agent Development**: Test each component (factory, plugin, UI) independently before integration
2. **Documentation**: Use existing demo patterns as templates for new documentation
3. **Dependency Management**: Update shared utilities first, then dependent components in order
4. **Security**: Prioritize critical/high vulnerabilities, document any that can't be fixed
5. **Unit Testing**: Mock all external dependencies, focus on component logic only
6. **E2E Testing**: Test complete system without internal mocking, use network-level mocking
7. **Framework Migration**: Maintain API compatibility, test before/after migration thoroughly
8. **Language Migration**: Preserve YAML configuration format, validate API responses match exactly
