# Teal Agents

Teal Agents is a comprehensive platform for building and deploying AI agents using Semantic Kernel. It provides a configuration-driven approach to creating agents with support for plugins, multi-modal inputs, custom completion factories, and various deployment patterns including REST APIs, WebSocket streaming, and Agent-to-Agent communication.

## Architecture Overview

The Teal Agents Framework is built on a layered architecture that separates concerns between configuration, orchestration, and execution:

### Core Components

**Framework Layer (`src/sk-agents/`)**
- **Semantic Kernel Integration**: Built on Microsoft's Semantic Kernel for AI orchestration and plugin management
- **FastAPI Web Layer**: Provides REST endpoints, WebSocket streaming, Server-Sent Events, and Agent-to-Agent (A2A) communication
- **Configuration-Driven Architecture**: YAML-based agent definitions with support for complex workflows and plugin compositions
- **Plugin System**: Extensible plugin architecture supporting both local custom plugins and remote OpenAPI-based plugins
- **Custom Completion Factories**: Pluggable LLM provider integration (OpenAI, Azure OpenAI, Google Gemini, etc.)

**Orchestration Layer (`src/orchestrators/`)**
- **Assistant Orchestrator**: Single-agent orchestration with plugin support and stateful interactions
- **Collaboration Orchestrator**: Multi-agent coordination and workflow management
- **Workflow Orchestrator**: Complex workflow execution (under development)

**Shared Infrastructure (`shared/ska_utils/`)**
- **AppConfig**: Environment variable management and configuration validation
- **Telemetry**: OpenTelemetry integration for observability and monitoring
- **Event Handling**: Redis Streams for event-driven architectures
- **Utility Functions**: Date handling, module loading, and common operations

### Agent Types and Patterns

**Demo Configurations vs Working Agents**
- **Demo Configurations** (`src/sk-agents/docs/demos/`): Reference implementations and learning materials showing framework capabilities
- **Working Agents** (`src/orchestrators/assistant-orchestrator/example/`): Production-ready agent implementations like the University Agent

**Configuration Schema**
All agents follow a consistent YAML configuration pattern:
```yaml
apiVersion: skagents/v1
kind: Sequential | Parallel | Workflow
description: Agent description
service_name: AgentName
version: 0.1
input_type: BaseInput | BaseMultiModalInput | CustomType
spec:
  agents:
    - name: agent_name
      role: Agent Role
      model: model_name
      system_prompt: Instructions
      plugins: [PluginList]
  tasks:
    - name: task_name
      description: Task description
      instructions: Task-specific instructions
      agent: agent_name
```

### API Generation and Communication

The framework automatically generates multiple API interfaces:
- **REST Endpoints**: Standard HTTP POST for synchronous agent invocation
- **Server-Sent Events (SSE)**: Streaming responses for real-time interaction
- **WebSocket Streaming**: Bidirectional communication for interactive sessions
- **Agent-to-Agent (A2A)**: Standardized protocol for agent composition and chaining

### Plugin Architecture

**Local/Custom Plugins**: Python classes implementing the Semantic Kernel plugin interface
```python
from semantic_kernel import kernel_function

class CustomPlugin:
    @kernel_function(description="Function description")
    def custom_function(self, parameter: str) -> str:
        return f"Processed: {parameter}"
```

**Remote Plugins**: OpenAPI-based integrations defined in remote plugin catalogs
```yaml
remote_plugins:
  - plugin_name: api_service
    openapi_json_path: ./path/to/openapi.json
    server_url: https://api.example.com
```

### Deployment Patterns

**Development**: Local development with hot-reload and debugging support
**Production**: Containerized deployment with environment-based configuration
**Microservices**: Individual agent services with A2A communication
**Orchestrated Workflows**: Complex multi-agent systems with state management

## Getting Started

### Quick Start with University Agent

The University Agent demonstrates a complete working implementation with custom completion factory, plugin development, and Streamlit UI integration.

1. **Environment Setup**:
```bash
git clone https://github.com/thepollari/teal-agents.git
cd teal-agents
cd src/sk-agents
uv sync --dev
```

2. **Configure Environment Variables**:
```bash
export TA_API_KEY=your_gemini_api_key
export TA_SERVICE_CONFIG=/absolute/path/to/teal-agents/src/orchestrators/assistant-orchestrator/example/university/config.yaml
export TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE=/absolute/path/to/teal-agents/src/sk-agents/src/sk_agents/chat_completion/custom/gemini_chat_completion_factory.py
```

3. **Run the Agent**:
```bash
uv run uvicorn sk_agents.app:app --host 0.0.0.0 --port 8001
```

4. **Test with Streamlit UI** (optional):
```bash
cd src/orchestrators/assistant-orchestrator/example/university
uv run streamlit run streamlit_ui.py
```

### Creating Your First Agent

1. **Choose a Demo Configuration**: Start with `src/sk-agents/docs/demos/01_getting_started/` for basic functionality
2. **Customize Configuration**: Modify the YAML file for your use case
3. **Develop Custom Plugins**: Create Python classes for domain-specific functionality
4. **Configure Completion Factory**: Set up your preferred LLM provider
5. **Deploy and Test**: Use the generated APIs for integration

## Repository Structure

```
teal-agents/
├── README.md                         # This file - project overview and architecture
├── CONTRIBUTING.md                   # Contribution guidelines
├── DEVELOPER_GUIDE.md               # Development environment setup
├── AGENT_DEVELOPMENT.md             # Step-by-step agent creation guide
├── TESTING_GUIDE.md                 # Testing patterns and best practices
├── AGENT_TEMPLATE.md                # Template for agent documentation
├── shared/ska_utils/                # Shared utilities library
│   ├── src/ska_utils/              # AppConfig, Telemetry, utilities
│   └── tests/                      # Utility tests
├── src/sk-agents/                  # Core agent framework
│   ├── src/sk_agents/              # Framework source code
│   │   ├── app.py                  # FastAPI application entry point
│   │   ├── routes.py               # API route generation
│   │   ├── skagents/               # Agent builders and handlers
│   │   └── chat_completion/        # LLM provider integrations
│   ├── docs/demos/                 # Demo configurations and examples
│   │   ├── README.md               # Demo index and learning path
│   │   ├── 01_getting_started/     # Basic agent demo
│   │   ├── 03_plugins/             # Plugin usage demo
│   │   ├── 04_remote_plugins/      # OpenAPI plugin integration
│   │   └── 08_multi_modal/         # Multi-modal input demo
│   └── tests/                      # Framework tests
└── src/orchestrators/              # Agent orchestration services
    ├── assistant-orchestrator/     # Single-agent orchestration
    │   ├── orchestrator/           # Orchestrator service
    │   └── example/                # Working agent implementations
    │       └── university/         # University Agent (reference implementation)
    ├── collab-orchestrator/        # Multi-agent collaboration
    └── workflow-orchestrator/      # Complex workflows (under development)
```

## Key Features

- **Configuration-Driven**: Define agents through YAML without code changes
- **Multi-Modal Support**: Text, image, and structured data inputs
- **Plugin Ecosystem**: Extensible functionality through local and remote plugins
- **Multiple LLM Providers**: OpenAI, Azure OpenAI, Google Gemini, and custom integrations
- **Streaming Support**: Real-time responses via SSE and WebSocket
- **Agent Composition**: A2A protocol for building complex agent systems
- **Production Ready**: Telemetry, monitoring, and deployment patterns included

## Next Steps

- **For Developers**: See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for environment setup
- **For Agent Creation**: Follow [AGENT_DEVELOPMENT.md](AGENT_DEVELOPMENT.md) for step-by-step instructions
- **For Demo Exploration**: Browse [src/sk-agents/docs/demos/README.md](src/sk-agents/docs/demos/README.md) for learning materials
- **For Testing**: Reference [TESTING_GUIDE.md](TESTING_GUIDE.md) for testing patterns

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.
