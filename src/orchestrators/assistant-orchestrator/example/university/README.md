# University Agent - Reference Implementation

The University Agent is a comprehensive working example that demonstrates the full capabilities of the Teal Agents Framework. It showcases custom completion factory integration, plugin development patterns, API integration, and UI development using Streamlit.

## Architecture Overview

The University Agent implements a complete agent system with the following components:

### Core Components

**Agent Configuration** (`config.yaml`)
- Google Gemini 2.0 Flash-Lite model integration
- Sequential task execution pattern
- Custom plugin registration
- Input/output type definitions

**Custom Completion Factory** (`GeminiChatCompletionFactory`)
- Demonstrates custom LLM provider integration
- Model validation and capability detection
- Structured output support
- API key management through AppConfig

**Custom Plugin Development** (`UniversityPlugin`)
- Real-world API integration with universities.hipolabs.com
- Pydantic model definitions for structured data
- Error handling and validation patterns
- Function calling with typed parameters

**Streamlit UI Integration**
- Interactive web interface for agent testing
- Real-time streaming responses
- Session state management
- User-friendly query interface

## Features

- **University Search**: Find universities by name, country, or domain
- **Real-time Data**: Live integration with universities.hipolabs.com API
- **Structured Responses**: Pydantic models for consistent data handling
- **Streaming Support**: Real-time response streaming via SSE and WebSocket
- **Multi-interface Access**: REST API, Streamlit UI, and programmatic access
- **Production Patterns**: Error handling, logging, and configuration management

## Setup and Installation

### Prerequisites

- Python 3.13+
- uv (Python package manager)
- Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Environment Setup

1. **Install Dependencies:**
   ```bash
   cd /path/to/teal-agents/src/sk-agents
   uv sync --dev
   ```

2. **Configure Environment Variables:**
   ```bash
   # Required: Google Gemini API key
   export TA_API_KEY=your_gemini_api_key_here
   
   # Required: Agent configuration (use absolute path)
   export TA_SERVICE_CONFIG=/absolute/path/to/teal-agents/src/orchestrators/assistant-orchestrator/example/university/config.yaml
   
   # Required: Custom completion factory (use absolute path)
   export TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE=/absolute/path/to/teal-agents/src/sk-agents/src/sk_agents/chat_completion/custom/gemini_chat_completion_factory.py
   ```

   **Critical**: Use absolute paths for configuration files to avoid import issues.

### Running the Agent

1. **Start the Agent Service:**
   ```bash
   cd /path/to/teal-agents/src/sk-agents
   uv run uvicorn sk_agents.app:app --host 0.0.0.0 --port 8001
   ```

2. **Verify Agent is Running:**
   ```bash
   curl http://localhost:8001/.well-known/agent.json
   ```

3. **Test Basic Functionality:**
   ```bash
   curl -X POST http://localhost:8001/invoke \
     -H "Content-Type: application/json" \
     -d '{"chat_history": [{"role": "user", "content": "Tell me about universities in Finland"}]}'
   ```

## Streamlit UI Interface

The University Agent includes a production-ready Streamlit interface demonstrating UI integration patterns:

### Running the UI

1. **Start Streamlit Interface:**
   ```bash
   cd /path/to/teal-agents/src/orchestrators/assistant-orchestrator/example/university
   uv run streamlit run streamlit_ui.py
   ```

2. **Access the Interface:**
   - Open browser to `http://localhost:8501`
   - Interface connects to agent service at `http://localhost:8001`

### UI Features

- **Interactive Chat**: Natural language queries about universities
- **Streaming Responses**: Real-time response display using SSE
- **Session Management**: Maintains conversation context
- **Error Handling**: User-friendly error messages and retry logic
- **Responsive Design**: Clean, professional interface

## Implementation Deep Dive

### Custom Completion Factory Pattern

The `GeminiChatCompletionFactory` demonstrates how to integrate custom LLM providers:

```python
class GeminiChatCompletionFactory(ChatCompletionFactory):
    _GEMINI_MODELS = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-lite"]
    
    def get_chat_completion_for_model_name(self, model_name: str, service_id: str):
        return GoogleAIChatCompletion(
            service_id=service_id,
            gemini_model_id=model_name,
            api_key=self.api_key,
        )
```

**Key Patterns**:
- Model validation and capability detection
- API key management through AppConfig
- Structured output support detection
- Error handling for unsupported models

### Plugin Development Patterns

The `UniversityPlugin` showcases best practices for plugin development:

```python
class UniversityPlugin:
    @kernel_function(description="Search for universities by name and/or country")
    def search_universities(self, name: str = "", country: str = "") -> str:
        # Implementation with error handling and validation
```

**Implementation Highlights**:
- **Pydantic Models**: Structured data handling with `University` model
- **API Integration**: HTTP client with error handling and retries
- **Parameter Validation**: Type hints and default values
- **Response Formatting**: JSON serialization for agent consumption
- **Error Handling**: Graceful degradation and user-friendly error messages

### Configuration Patterns

The agent configuration demonstrates production-ready patterns:

```yaml
apiVersion: skagents/v1
kind: Sequential
description: University agent powered by Google Gemini
service_name: UniversityAgent
version: 0.1
input_type: BaseInput
spec:
  agents:
    - name: default
      role: University Assistant
      model: gemini-2.0-flash-lite
      system_prompt: You are a helpful university assistant.
      plugins:
        - UniversityPlugin
  tasks:
    - name: university_assistance
      description: Help users with university-related queries
      instructions: Assist with university questions using the UniversityPlugin
      agent: default
```

## API Endpoints and Usage

### Available Endpoints

The University Agent automatically generates multiple API interfaces:

1. **Synchronous Invocation**
   ```bash
   POST /invoke
   Content-Type: application/json
   
   {
     "chat_history": [
       {"role": "user", "content": "Find universities in Tokyo"}
     ]
   }
   ```

2. **Server-Sent Events (Streaming)**
   ```bash
   POST /sse
   Content-Type: application/json
   
   # Same payload as /invoke, returns streaming response
   ```

3. **WebSocket Streaming**
   ```bash
   WebSocket /stream
   
   # Send JSON payload, receive streaming responses
   ```

4. **Agent Card Information**
   ```bash
   GET /.well-known/agent.json
   
   # Returns agent metadata and capabilities
   ```

### Example Queries and Responses

**Query**: "Tell me about universities in Finland"

**Response Structure**:
```json
{
  "token_usage": {
    "completion_tokens": 150,
    "prompt_tokens": 89,
    "total_tokens": 239
  },
  "output_raw": "I found several universities in Finland...",
  "extra_data": null
}
```

**Advanced Queries**:
- "Find universities with 'technology' in their name"
- "What universities are available in MIT's domain?"
- "Show me universities in both Finland and Sweden"
- "Compare universities in Tokyo and Kyoto"

## Testing and Validation

### Unit Testing Patterns

The University Agent demonstrates testing approaches:

1. **Plugin Testing**: Mock external API calls
2. **Configuration Validation**: YAML schema validation
3. **Integration Testing**: End-to-end agent workflows
4. **UI Testing**: Streamlit interface validation

### Manual Testing Checklist

- [ ] Agent starts without errors
- [ ] Plugin loads and functions correctly
- [ ] API endpoints respond appropriately
- [ ] Streaming responses work properly
- [ ] Streamlit UI connects and functions
- [ ] Error handling works for invalid queries
- [ ] Configuration changes take effect

### Performance Considerations

- **API Rate Limits**: Universities API has reasonable limits
- **Response Caching**: Consider caching for repeated queries
- **Streaming Efficiency**: SSE provides better UX for long responses
- **Error Recovery**: Graceful handling of API failures

## Deployment Patterns

### Development Deployment
```bash
# Local development with hot reload
uv run uvicorn sk_agents.app:app --reload --host 0.0.0.0 --port 8001
```

### Production Deployment
```bash
# Production deployment with proper configuration
export TA_TELEMETRY_ENABLED=true
export TA_OTEL_ENDPOINT=your_telemetry_endpoint
uv run uvicorn sk_agents.app:app --host 0.0.0.0 --port 8001 --workers 4
```

### Container Deployment
```dockerfile
FROM python:3.13-slim
COPY . /app
WORKDIR /app/src/sk-agents
RUN pip install uv && uv sync --dev
CMD ["uv", "run", "uvicorn", "sk_agents.app:app", "--host", "0.0.0.0", "--port", "8001"]
```

## Troubleshooting Guide

### Common Issues and Solutions

**1. Import/Configuration Errors**
```
Error: Cannot load configuration file
Solution: Use absolute paths for TA_SERVICE_CONFIG and TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE
```

**2. API Key Issues**
```
Error: Invalid API key or quota exceeded
Solution: Verify Gemini API key at https://makersuite.google.com/app/apikey
```

**3. Plugin Loading Failures**
```
Error: UniversityPlugin not found
Solution: Ensure plugin class is properly defined and importable
```

**4. Network/API Issues**
```
Error: Cannot connect to universities.hipolabs.com
Solution: Check internet connectivity and API availability
```

**5. Streamlit Connection Issues**
```
Error: Cannot connect to agent service
Solution: Ensure agent is running on port 8001 before starting Streamlit
```

### Debugging Techniques

1. **Enable Debug Logging**:
   ```bash
   export TA_LOG_LEVEL=debug
   ```

2. **Test External API Directly**:
   ```bash
   curl "http://universities.hipolabs.com/search?name=MIT"
   ```

3. **Validate Configuration**:
   ```bash
   python -c "import yaml; print(yaml.safe_load(open('config.yaml')))"
   ```

4. **Check Plugin Import**:
   ```bash
   python -c "from custom_plugins import UniversityPlugin; print('Plugin loaded successfully')"
   ```

## Extension Patterns

### Adding New Plugins

1. **Create Plugin Class**:
   ```python
   class NewPlugin:
       @kernel_function(description="New functionality")
       def new_function(self, param: str) -> str:
           return f"Processed: {param}"
   ```

2. **Register in Configuration**:
   ```yaml
   plugins:
     - UniversityPlugin
     - NewPlugin
   ```

### Custom Input Types

1. **Define Pydantic Model**:
   ```python
   class CustomInput(KernelBaseModel):
       query: str
       filters: dict = {}
   ```

2. **Update Configuration**:
   ```yaml
   input_type: CustomInput
   ```

### UI Enhancements

1. **Add New Streamlit Components**:
   ```python
   st.sidebar.selectbox("Country Filter", countries)
   st.map(university_locations)
   ```

2. **Integrate with Agent State**:
   ```python
   if "conversation" not in st.session_state:
       st.session_state.conversation = []
   ```

## Production Considerations

### Security
- API key management through environment variables
- Input validation and sanitization
- Rate limiting and abuse prevention
- HTTPS deployment for production

### Monitoring
- OpenTelemetry integration for observability
- Health check endpoints
- Performance metrics collection
- Error tracking and alerting

### Scalability
- Horizontal scaling with multiple workers
- Load balancing for high availability
- Caching strategies for API responses
- Database integration for persistent state

## Next Steps

After understanding the University Agent:

1. **Create Custom Agent**: Use this as template for your domain
2. **Develop Custom Plugins**: Integrate your APIs and services
3. **Enhance UI**: Build domain-specific interfaces
4. **Deploy to Production**: Follow deployment patterns for your environment

For additional guidance, see:
- [AGENT_DEVELOPMENT.md](../../../../AGENT_DEVELOPMENT.md) - Step-by-step agent creation
- [DEVELOPER_GUIDE.md](../../../../DEVELOPER_GUIDE.md) - Development environment setup
- [TESTING_GUIDE.md](../../../../TESTING_GUIDE.md) - Testing patterns and best practices
