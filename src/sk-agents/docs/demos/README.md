# Teal Agents Framework - Demo Configurations

## Overview

This directory contains 11 demo configurations that showcase the capabilities and configuration patterns of the Teal Agents Framework. These demos serve as learning materials and reference implementations, demonstrating the progression from basic agent setup to advanced multi-modal and plugin-enabled agents.

**Important**: These are demo configurations for learning purposes, not deployable agents. For working agent examples, see [Working Agents](../../../orchestrators/assistant-orchestrator/example/).

## Learning Path

The demos are organized to provide a structured learning experience:

### Foundation Level
1. **[01_getting_started](01_getting_started/)** - Basic agent configuration and setup
2. **[02_structured_output](02_structured_output/)** - Working with structured data types

### Intermediate Level
3. **[03_plugins](03_plugins/)** - Plugin system and custom tool integration
4. **[04_custom_types](04_custom_types/)** - Custom input/output type definitions
5. **[05_sequential_agent](05_sequential_agent/)** - Multi-step agent workflows
6. **[06_chat_agent](06_chat_agent/)** - Conversational agent patterns

### Advanced Level
7. **[07_streaming](07_streaming/)** - Real-time streaming responses
8. **[08_multi_modal](08_multi_modal/)** - Image and text input handling
9. **[09_custom_completion_factory](09_custom_completion_factory/)** - Custom model integrations
10. **[10_authorization](10_authorization/)** - Authentication and authorization
11. **[11_stateful_agent](11_stateful_agent/)** - Session management and persistent state

## Demo Configuration Patterns

### Basic Agent Structure

All demo configurations follow this YAML structure:

```yaml
apiVersion: skagents/v1  # or v2alpha1, tealagents/v1alpha1
kind: Agent              # or SequentialAgent, ChatAgent
name: DemoAgent
service_name: DemoAgent  # For v1 compatibility
version: 1.0
description: "Demo agent description"
metadata:                # For v2+ agents
  description: "Detailed description"
  skills:
    - id: "skill_id"
      name: "Skill Name"
      description: "What this skill does"
spec:
  model: gpt-4o         # Available models: gpt-4o, gpt-4o-mini, claude-3-sonnet, gemini-pro
  system_prompt: "Agent behavior instructions"
  plugins:              # Optional plugin list
    - PluginName
  max_tokens: 1000      # Optional response limits
```

### API Version Routing

The `apiVersion` field determines which app version handles the agent:

- **`skagents/v1`** → AppV1: Basic agents with custom types
- **`skagents/v2alpha1`** → AppV2: Multi-modal agents with A2A capabilities  
- **`tealagents/v1alpha1`** → AppV3: Stateful agents with authentication

## Demo Details

### 01_getting_started
**Purpose**: Introduction to basic agent configuration
**Key Concepts**: YAML structure, model selection, system prompts
**Input Type**: BaseInput (chat history)
**Learning Objectives**: 
- Understand basic agent configuration
- Learn YAML schema structure
- Test simple chat interactions

### 02_structured_output
**Purpose**: Working with structured data types
**Key Concepts**: Custom output types, Pydantic models
**Learning Objectives**:
- Define custom output schemas
- Handle structured responses
- Validate output formats

### 03_plugins
**Purpose**: Plugin system demonstration
**Key Concepts**: BasePlugin inheritance, kernel_function decorators
**Example Plugin**: WeatherPlugin with temperature and location functions
**Learning Objectives**:
- Create custom plugins
- Integrate external APIs
- Use function calling patterns

### 04_custom_types
**Purpose**: Custom input and output type definitions
**Key Concepts**: Type loading, custom_types.py files
**Learning Objectives**:
- Define custom input types
- Create domain-specific data structures
- Handle complex data validation

### 05_sequential_agent
**Purpose**: Multi-step agent workflows
**Key Concepts**: Sequential execution, task chaining
**Learning Objectives**:
- Design multi-step processes
- Handle intermediate results
- Coordinate sequential tasks

### 06_chat_agent
**Purpose**: Conversational agent patterns
**Key Concepts**: Chat history management, context preservation
**Learning Objectives**:
- Maintain conversation context
- Handle multi-turn interactions
- Implement chat-specific behaviors

### 07_streaming
**Purpose**: Real-time streaming responses
**Key Concepts**: WebSocket connections, streaming endpoints
**Learning Objectives**:
- Implement streaming responses
- Handle real-time communication
- Optimize response latency

### 08_multi_modal
**Purpose**: Image and text input handling
**Key Concepts**: BaseMultiModalInput, image encoding, content types
**Example Inputs**: Base64 encoded images, embedded_image types
**Learning Objectives**:
- Process multi-modal inputs
- Handle image data
- Combine text and visual information

### 09_custom_completion_factory
**Purpose**: Custom model integrations
**Key Concepts**: ChatCompletionFactory, custom model providers
**Learning Objectives**:
- Integrate custom LLM providers
- Implement completion factories
- Handle model-specific configurations

### 10_authorization
**Purpose**: Authentication and authorization
**Key Concepts**: Request authorization, security patterns
**Learning Objectives**:
- Implement authentication
- Handle authorization flows
- Secure agent endpoints

### 11_stateful_agent
**Purpose**: Session management and persistent state
**Key Concepts**: State managers, session persistence, user context
**Learning Objectives**:
- Manage user sessions
- Persist conversation state
- Handle reconnection scenarios

## Running Demo Configurations

### Prerequisites
- Python 3.11+ with uv package manager
- API keys for chosen model provider (OpenAI, Anthropic, Google)
- Docker (for some advanced demos)

### Setup Steps

1. **Navigate to framework directory**:
   ```bash
   cd src/sk-agents
   ```

2. **Install dependencies**:
   ```bash
   uv sync --dev
   ```

3. **Set environment variables**:
   ```bash
   # Choose your model provider
   export OPENAI_API_KEY=your_key        # For GPT models
   export ANTHROPIC_API_KEY=your_key     # For Claude models  
   export GOOGLE_API_KEY=your_key        # For Gemini models
   ```

4. **Run a demo**:
   ```bash
   export TA_SERVICE_CONFIG=docs/demos/01_getting_started/config.yaml
   uv run uvicorn sk_agents.app:app --host 0.0.0.0 --port 8000
   ```

5. **Test the agent**:
   ```bash
   # REST endpoint
   curl -X POST http://localhost:8000/SimpleAgent/1.0/ \
     -H "Content-Type: application/json" \
     -d '{"chat_history": [{"role": "user", "content": "Hello!"}]}'
   
   # WebSocket endpoint (for streaming)
   # Connect to ws://localhost:8000/SimpleAgent/1.0/stream
   ```

## Migration from Demos to Production

### Demo → Working Agent Migration Guide

1. **Choose appropriate apiVersion**:
   - Use `tealagents/v1alpha1` for production chat applications
   - Use `skagents/v2alpha1` for multi-modal or A2A scenarios
   - Use `skagents/v1` only for simple, stateless agents

2. **Add comprehensive metadata**:
   ```yaml
   metadata:
     description: "Production-ready agent description"
     documentation_url: "https://your-docs.com/agent"
     skills:
       - id: "primary_skill"
         name: "Primary Capability"
         description: "Detailed skill description"
         tags: ["tag1", "tag2"]
         examples: ["Example usage"]
         input_modes: ["text", "image"]
         output_modes: ["text"]
   ```

3. **Implement custom completion factory** (if needed):
   - Create factory class inheriting from `ChatCompletionFactory`
   - Configure via `TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE`
   - See [University Agent](../../../orchestrators/assistant-orchestrator/example/university/) example

4. **Add production plugins**:
   - Move from demo plugins to production-ready implementations
   - Add proper error handling and validation
   - Include comprehensive documentation

5. **Configure deployment environment**:
   - Set up proper environment variables
   - Configure state management (Redis for production)
   - Add monitoring and telemetry

6. **Add UI components** (optional):
   - Implement Streamlit or web UI
   - Add testing interfaces
   - Create user documentation

## Cross-Reference: Demos to Working Agents

| Demo Pattern | Working Agent Example | Key Differences |
|--------------|----------------------|-----------------|
| 03_plugins | University Agent | Production API integration, error handling |
| 08_multi_modal | University Agent | Real image processing, UI integration |
| 09_custom_completion_factory | University Agent | Gemini integration, production config |
| 11_stateful_agent | University Agent | Redis state, authentication |

## Troubleshooting

### Common Issues

1. **Configuration not found**:
   ```bash
   # Ensure TA_SERVICE_CONFIG points to correct file
   export TA_SERVICE_CONFIG=$(pwd)/docs/demos/01_getting_started/config.yaml
   ```

2. **API key errors**:
   ```bash
   # Verify API key is set for your chosen model
   echo $OPENAI_API_KEY  # Should not be empty
   ```

3. **Plugin loading errors**:
   - Check plugin class names match configuration
   - Verify plugin files are in correct directory
   - Ensure proper inheritance from BasePlugin

4. **Type loading errors**:
   - Verify custom_types.py exists if using custom types
   - Check type names match configuration
   - Ensure proper Pydantic model definitions

### Getting Help

- Review [Developer Guide](../../../DEVELOPER_GUIDE.md) for environment setup
- Check [Testing Guide](../../../TESTING_GUIDE.md) for debugging approaches
- See [Working Agent examples](../../../orchestrators/assistant-orchestrator/example/) for production patterns
- Consult framework [API documentation](../../README.md) for detailed specifications

## Next Steps

After working through these demos:

1. **Study the University Agent**: Complete working agent with all production features
2. **Create your own agent**: Use [Agent Development Guide](../../../AGENT_DEVELOPMENT.md)
3. **Explore orchestration**: Try [Assistant](../../../orchestrators/assistant-orchestrator/) or [Collaboration](../../../orchestrators/collab-orchestrator/) orchestrators
4. **Contribute**: Follow [Contributing Guidelines](../../../CONTRIBUTING.md) to add new demos or features
