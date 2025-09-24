# Teal Agents Platform

## Overview
The Teal Agents Platform is a comprehensive framework for creating, deploying, and orchestrating AI-powered agents built on Microsoft's Semantic Kernel. The platform provides two major sets of functionality:

1. **Core Agent Framework** - A configuration-driven framework for creating and deploying individual agents with support for plugins, multi-modal inputs, and streaming responses
2. **Orchestrators** - Reusable orchestration patterns that allow you to compose multiple agents for complex collaborative workflows

## Architecture Overview

### Core Framework Components

The Teal Agents Framework follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Web Layer                        │
├─────────────────────────────────────────────────────────────┤
│  App Router (app.py) - Routes to AppV1/V2/V3 based on     │
│  apiVersion in configuration                                │
├─────────────────────────────────────────────────────────────┤
│  Agent Execution Layers:                                   │
│  • AppV1: Basic agents with custom input/output types      │
│  • AppV2: Multi-modal agents with A2A capabilities        │
│  • AppV3: Stateful agents with authentication              │
├─────────────────────────────────────────────────────────────┤
│  Semantic Kernel Integration Layer                         │
│  • Plugin System (BasePlugin inheritance)                  │
│  • Chat Completion Factories (OpenAI, Anthropic, Google)   │
│  • Kernel Builders and Agent Handlers                      │
├─────────────────────────────────────────────────────────────┤
│  Shared Utilities (ska_utils)                              │
│  • Configuration Management • Telemetry • Event Handling   │
└─────────────────────────────────────────────────────────────┘
```

### Configuration-Driven Approach

All agents are defined using YAML configuration files that specify:
- **apiVersion**: Determines which app version (V1/V2/V3) handles the agent
- **Agent Metadata**: Name, version, description, and capabilities
- **Execution Spec**: Model configuration, plugins, and behavior settings
- **Input/Output Types**: Custom types for structured data handling

Example configuration structure:
```yaml
apiVersion: skagents/v2alpha1  # Routes to AppV2
kind: Agent
name: MyAgent
version: 1.0
metadata:
  description: "Example agent with plugin support"
  skills:
    - id: "search"
      name: "Web Search"
      description: "Search the web for information"
spec:
  model: gpt-4o
  plugins:
    - WeatherPlugin
  system_prompt: "You are a helpful assistant..."
```

### Agent Execution Models

#### AppV1 (skagents/v1)
- **Purpose**: Basic agents with custom input/output types
- **Features**: REST and WebSocket endpoints, custom type loading
- **Use Cases**: Simple chat agents, basic task automation

#### AppV2 (skagents/v2alpha1)
- **Purpose**: Multi-modal agents with advanced capabilities
- **Features**: Image/text inputs, A2A (Agent-to-Agent) communication, Redis state management
- **Use Cases**: Multi-modal assistants, agent collaboration scenarios

#### AppV3 (tealagents/v1alpha1)
- **Purpose**: Stateful agents with authentication and session management
- **Features**: User sessions, authentication, persistent state, resume capabilities
- **Use Cases**: Production chat applications, user-specific agents

### Plugin System

Plugins extend agent capabilities through the `BasePlugin` class:

```python
from sk_agents.ska_types import BasePlugin
from semantic_kernel import kernel_function

class WeatherPlugin(BasePlugin):
    @kernel_function(description="Get current weather")
    def get_weather(self, location: str) -> str:
        # Plugin implementation
        return weather_data
```

### Orchestrator Architecture

#### Assistant Orchestrator
- **Purpose**: Chat-style applications with multiple specialized agents
- **Pattern**: Single-turn interactions with agent selection
- **Components**: Agent Selector, Fallback Agent, Agent Catalog (Kong)

#### Collaboration Orchestrator
- **Purpose**: Multi-agent collaboration for complex workflows
- **Patterns**: Team Orchestration (group chat) and Planning Orchestration (structured workflows)
- **Components**: Manager/Planning Agents, Task Agents, Human-in-the-Loop support

## Repository Structure

```
teal-agents/
├── src/sk-agents/                    # Core Agent Framework
│   ├── src/sk_agents/               # Framework source code
│   │   ├── app.py                   # Main FastAPI application entry point
│   │   ├── appv1.py, appv2.py, appv3.py  # Agent execution layers
│   │   ├── ska_types.py             # Core types and interfaces
│   │   └── skagents/                # Agent builders and handlers
│   ├── docs/demos/                  # Demo configurations (11 examples)
│   │   ├── 01_getting_started/      # Basic agent setup
│   │   ├── 03_plugins/              # Plugin usage examples
│   │   ├── 08_multi_modal/          # Multi-modal input handling
│   │   └── ...                      # Additional demo patterns
│   └── tests/                       # Framework tests
├── src/orchestrators/               # Orchestration services
│   ├── assistant-orchestrator/      # Chat-style orchestration
│   │   ├── example/university/      # Working university agent
│   │   └── orchestrator/            # Orchestrator implementation
│   └── collab-orchestrator/         # Multi-agent collaboration
├── shared/ska_utils/                # Shared utilities
│   └── src/ska_utils/              # Config, telemetry, events
└── docs/                           # Additional documentation
```

## Demo Configurations vs Working Agents

**Important Distinction:**

- **Demo Configurations** (`src/sk-agents/docs/demos/`): Reference examples showing configuration patterns and framework features. These are learning materials, not deployable agents.

- **Working Agents** (`src/orchestrators/assistant-orchestrator/example/`): Complete, deployable agent implementations with custom completion factories, plugins, and UI components.

## Getting Started

### Quick Start with Demo Agent

1. **Set up environment**:
   ```bash
   git clone https://github.com/thepollari/teal-agents.git
   cd teal-agents
   cd src/sk-agents
   uv sync --dev
   ```

2. **Configure API keys** (create `.env` file):
   ```bash
   OPENAI_API_KEY=your_openai_key
   # or ANTHROPIC_API_KEY, GOOGLE_API_KEY depending on model
   ```

3. **Run a demo agent**:
   ```bash
   export TA_SERVICE_CONFIG=docs/demos/01_getting_started/config.yaml
   uv run uvicorn sk_agents.app:app --host 0.0.0.0 --port 8000
   ```

4. **Test the agent**:
   ```bash
   curl -X POST http://localhost:8000/SimpleAgent/1.0/ \
     -H "Content-Type: application/json" \
     -d '{"chat_history": [{"role": "user", "content": "Hello!"}]}'
   ```

### Working with the University Agent

For a complete working agent example, see the [University Agent](src/orchestrators/assistant-orchestrator/example/university/README.md) which demonstrates:
- Custom Gemini completion factory integration
- Plugin development with external API integration
- Streamlit UI for interactive testing
- Production deployment patterns

## Development Resources

- **[Demo Documentation](src/sk-agents/docs/demos/README.md)**: Learning path through 11 demo configurations
- **[Developer Guide](DEVELOPER_GUIDE.md)**: Environment setup and development workflows
- **[Agent Development Guide](AGENT_DEVELOPMENT.md)**: Step-by-step agent creation
- **[Testing Guide](TESTING_GUIDE.md)**: Testing patterns and best practices
- **[Agent Template](AGENT_TEMPLATE.md)**: Template for documenting new agents

## Core Framework Documentation

For detailed framework documentation, see:
- [Core Framework README](src/sk-agents/README.md)
- [Orchestrators Overview](src/orchestrators/README.md)
- [Assistant Orchestrator](src/orchestrators/assistant-orchestrator/README.md)
- [Collaboration Orchestrator](src/orchestrators/collab-orchestrator/orchestrator/README.md)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for development guidelines and submission process.
