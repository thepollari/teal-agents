# Demo Configurations - Learning Path

This directory contains reference demo configurations that showcase the capabilities of the Teal Agents Framework. These demos are designed as learning materials and reference implementations, not as production-ready agents.

## Demo vs Working Agents

**Important Distinction:**
- **Demo Configurations** (this directory): Educational examples showing framework features
- **Working Agents** (`src/orchestrators/assistant-orchestrator/example/`): Production-ready implementations like the University Agent

## Learning Progression

### 1. Foundation Demos

#### [01_getting_started](01_getting_started/) - Basic Agent Setup
**Purpose**: Introduction to agent configuration and basic chat functionality
**Learning Objectives**:
- Understand YAML configuration structure
- Learn basic agent-user interaction patterns
- Configure environment variables and API keys
- Test agent responses through REST API

**Configuration Pattern**:
```yaml
apiVersion: skagents/v1
kind: Sequential
input_type: BaseInput
spec:
  agents:
    - name: default
      model: gpt-4o
      system_prompt: Basic instructions
  tasks:
    - name: chat_task
      agent: default
```

**Next Steps**: Move to plugin integration demos

### 2. Plugin Integration Demos

#### [03_plugins](03_plugins/) - Local Plugin Development
**Purpose**: Demonstrate custom plugin creation and integration
**Learning Objectives**:
- Create custom Python plugins
- Understand plugin function decorators
- Integrate plugins with agent workflows
- Handle plugin parameters and return values

**Key Concepts**:
- `@kernel_function` decorator usage
- Plugin class structure
- Parameter validation and type hints
- Plugin registration in agent configuration

#### [04_remote_plugins](04_remote_plugins/) - OpenAPI Integration
**Purpose**: Integrate external APIs as agent plugins
**Learning Objectives**:
- Configure remote plugin catalogs
- Use OpenAPI specifications for plugin generation
- Chain multiple API calls through agent reasoning
- Handle API authentication and error cases

**Configuration Pattern**:
```yaml
spec:
  agents:
    - name: default
      remote_plugins:
        - api_weather
        - api_geonames
```

**Migration to Production**: Reference University Agent's custom plugin implementation

### 3. Advanced Input Handling

#### [08_multi_modal](08_multi_modal/) - Multi-Modal Inputs
**Purpose**: Handle text, image, and structured data inputs
**Learning Objectives**:
- Configure `BaseMultiModalInput` for image processing
- Create custom input types with embedded images
- Process base64-encoded image data
- Combine text and visual reasoning

**Input Types**:
- `BaseMultiModalInput`: Chat history with mixed content types
- Custom input types with `EmbeddedImage` fields
- Base64 image encoding and format handling

## Cross-Reference: Demo to Production Patterns

| Demo Feature | Production Implementation | Location |
|--------------|--------------------------|----------|
| Basic Configuration | University Agent Config | `src/orchestrators/assistant-orchestrator/example/university/config.yaml` |
| Custom Plugins | UniversityPlugin | `src/orchestrators/assistant-orchestrator/example/university/custom_plugins.py` |
| Custom Completion Factory | GeminiChatCompletionFactory | `src/sk-agents/src/sk_agents/chat_completion/custom/gemini_chat_completion_factory.py` |
| API Integration | Universities API Plugin | University Agent implementation |
| UI Integration | Streamlit Interface | `src/orchestrators/assistant-orchestrator/example/university/streamlit_ui.py` |

## Migration Guide: Demo to Production

### Step 1: Choose Base Demo
Start with the demo that most closely matches your requirements:
- **Simple chat**: `01_getting_started`
- **API integration**: `04_remote_plugins`
- **Image processing**: `08_multi_modal`
- **Custom logic**: `03_plugins`

### Step 2: Create Working Agent Structure
```bash
mkdir -p src/orchestrators/assistant-orchestrator/example/your-agent
cd src/orchestrators/assistant-orchestrator/example/your-agent
```

### Step 3: Adapt Configuration
1. Copy demo `config.yaml` as starting point
2. Update `service_name` and `description`
3. Configure appropriate `model` and completion factory
4. Add custom plugins to `plugins` list

### Step 4: Implement Custom Components
1. **Custom Plugins**: Create `custom_plugins.py` following University Agent pattern
2. **Completion Factory**: Use existing factories or create custom one
3. **Input Types**: Define custom input schemas if needed
4. **UI Integration**: Add Streamlit or other UI components

### Step 5: Environment Configuration
```bash
export TA_SERVICE_CONFIG=/absolute/path/to/your-agent/config.yaml
export TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE=/path/to/completion_factory.py
export TA_API_KEY=your_api_key
```

### Step 6: Testing and Deployment
1. Test locally with `uvicorn sk_agents.app:app`
2. Validate plugin functionality
3. Test UI integration if applicable
4. Deploy using production patterns

## Demo Testing Instructions

### Prerequisites
```bash
cd src/sk-agents
uv sync --dev
export TA_API_KEY=your_openai_or_other_api_key
```

### Running Individual Demos
```bash
# Basic demo
export TA_SERVICE_CONFIG=docs/demos/01_getting_started/config.yaml
uv run uvicorn sk_agents.app:app --host 0.0.0.0 --port 8000

# Plugin demo
export TA_SERVICE_CONFIG=docs/demos/03_plugins/config.yaml
uv run uvicorn sk_agents.app:app --host 0.0.0.0 --port 8000

# Remote plugin demo
export TA_SERVICE_CONFIG=docs/demos/04_remote_plugins/config.yaml
export TA_REMOTE_PLUGIN_PATH=docs/demos/04_remote_plugins/remote-plugin-catalog.yaml
uv run uvicorn sk_agents.app:app --host 0.0.0.0 --port 8000

# Multi-modal demo
export TA_SERVICE_CONFIG=docs/demos/08_multi_modal/config.yaml
uv run uvicorn sk_agents.app:app --host 0.0.0.0 --port 8000
```

### Testing API Endpoints
```bash
# Test basic chat
curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{"chat_history": [{"role": "user", "content": "Hello!"}]}'

# Test streaming
curl -X POST http://localhost:8000/sse \
  -H "Content-Type: application/json" \
  -d '{"chat_history": [{"role": "user", "content": "Tell me a story"}]}'
```

## Common Demo Patterns

### Configuration Structure
All demos follow consistent YAML structure:
- `apiVersion`: Framework version (currently `skagents/v1`)
- `kind`: Execution pattern (`Sequential`, `Parallel`, `Workflow`)
- `service_name`: Unique agent identifier
- `input_type`: Expected input schema
- `spec.agents`: Agent definitions with models and prompts
- `spec.tasks`: Task definitions linking to agents

### Environment Variables
Standard environment variables across demos:
- `TA_API_KEY`: LLM provider API key
- `TA_SERVICE_CONFIG`: Path to agent configuration file
- `TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE`: Custom completion factory path
- `TA_REMOTE_PLUGIN_PATH`: Remote plugin catalog path

### Error Handling
Common issues and solutions:
- **Missing API Key**: Ensure `TA_API_KEY` is set for your LLM provider
- **Configuration Path**: Use absolute paths for `TA_SERVICE_CONFIG`
- **Plugin Loading**: Verify plugin class names match configuration
- **Model Availability**: Check model names are supported by your provider

## Next Steps

After exploring demos:
1. **Create Working Agent**: Follow [AGENT_DEVELOPMENT.md](../../../AGENT_DEVELOPMENT.md)
2. **Study University Agent**: Examine production implementation patterns
3. **Develop Custom Plugins**: Create domain-specific functionality
4. **Deploy Production Agent**: Use orchestrator patterns for deployment

For questions or issues with demos, refer to [DEVELOPER_GUIDE.md](../../../DEVELOPER_GUIDE.md) troubleshooting section.
