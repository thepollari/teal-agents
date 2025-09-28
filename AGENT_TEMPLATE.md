# Agent Template - [Agent Name]

Use this template as a starting point for documenting new agents in the Teal Agents Framework. Replace bracketed placeholders with agent-specific information.

## Overview

**Agent Name**: [Agent Name]
**Purpose**: [Brief description of what the agent does]
**Domain**: [Domain or industry focus, e.g., Healthcare, Finance, Education]
**Version**: [Current version, e.g., 0.1.0]

### Key Features

- [Feature 1: Brief description]
- [Feature 2: Brief description]
- [Feature 3: Brief description]
- [Additional features as needed]

### Architecture Components

**Model Integration**: [LLM provider and model, e.g., OpenAI GPT-4, Google Gemini]
**Completion Factory**: [Custom or standard completion factory used]
**Plugins**: [List of plugins and their purposes]
**Input Types**: [Supported input types and formats]
**UI Integration**: [Web interface, API-only, or other interfaces]

## Setup and Installation

### Prerequisites

- Python 3.13+
- uv (Python package manager)
- [API keys or credentials needed]
- [Any additional system requirements]

### Environment Setup

1. **Install Dependencies:**
   ```bash
   cd /path/to/teal-agents/src/sk-agents
   uv sync --dev
   ```

2. **Configure Environment Variables:**
   ```bash
   # Required API keys
   export TA_API_KEY=[your_api_key]
   
   # Agent configuration (use absolute path)
   export TA_SERVICE_CONFIG=/absolute/path/to/[agent-directory]/config.yaml
   
   # Custom completion factory (if applicable)
   export TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE=/absolute/path/to/[completion_factory].py
   
   # Additional environment variables
   export [ADDITIONAL_VAR]=[value]
   ```

### Running the Agent

1. **Start the Agent Service:**
   ```bash
   cd /path/to/teal-agents/src/sk-agents
   uv run uvicorn sk_agents.app:app --host 0.0.0.0 --port [PORT]
   ```

2. **Verify Agent is Running:**
   ```bash
   curl http://localhost:[PORT]/.well-known/agent.json
   ```

3. **Test Basic Functionality:**
   ```bash
   curl -X POST http://localhost:[PORT]/invoke \
     -H "Content-Type: application/json" \
     -d '{"chat_history": [{"role": "user", "content": "[test query]"}]}'
   ```

## Configuration

### Agent Configuration (`config.yaml`)

```yaml
apiVersion: skagents/v1
kind: [Sequential|Parallel|Workflow]
description: [Agent description]
service_name: [AgentName]
version: [version]
input_type: [BaseInput|BaseMultiModalInput|CustomType]
spec:
  agents:
    - name: default
      role: [Agent Role]
      model: [model-name]
      system_prompt: |
        [System prompt instructions]
      plugins:
        - [PluginName]
  tasks:
    - name: [task_name]
      task_no: 1
      description: [Task description]
      instructions: |
        [Task-specific instructions]
      agent: default
```

### Key Configuration Elements

- **Model Selection**: [Explain model choice and alternatives]
- **System Prompt**: [Describe prompt engineering approach]
- **Plugin Integration**: [List plugins and their roles]
- **Task Definition**: [Explain task structure and flow]

## Plugin Development

### Custom Plugins

[If the agent uses custom plugins, document them here]

#### [PluginName] Plugin

**Purpose**: [What the plugin does]
**API Integration**: [External APIs or services used]
**Data Models**: [Pydantic models or data structures]

```python
class [PluginName]:
    @kernel_function(description="[Function description]")
    def [function_name](self, [parameters]) -> [return_type]:
        """
        [Detailed function documentation]
        
        Args:
            [parameter]: [description]
        
        Returns:
            [return_description]
        """
        # Implementation details
```

**Key Implementation Patterns**:
- [Pattern 1: e.g., Error handling approach]
- [Pattern 2: e.g., Data validation strategy]
- [Pattern 3: e.g., API rate limiting]

### Plugin Configuration

[Document how plugins are configured and registered]

## User Interface

### [UI Type - e.g., Streamlit, Web App, CLI]

[If the agent has a UI component, document it here]

#### Running the UI

1. **Start UI Interface:**
   ```bash
   cd /path/to/[agent-directory]
   [command to start UI]
   ```

2. **Access the Interface:**
   - URL: [http://localhost:PORT]
   - Features: [List key UI features]

#### UI Features

- [Feature 1]: [Description]
- [Feature 2]: [Description]
- [Feature 3]: [Description]

## API Endpoints

### Available Endpoints

The agent automatically generates the following API interfaces:

1. **Synchronous Invocation**
   ```bash
   POST /invoke
   Content-Type: application/json
   
   {
     "chat_history": [
       {"role": "user", "content": "[example query]"}
     ]
   }
   ```

2. **Server-Sent Events (Streaming)**
   ```bash
   POST /sse
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

### Example Queries

**Basic Query**: "[Example user query]"
**Response**: "[Expected response format or content]"

**Advanced Query**: "[More complex example]"
**Response**: "[Expected response with plugin usage]"

## Testing and Validation

### Manual Testing Checklist

- [ ] Agent starts without errors
- [ ] Configuration loads correctly
- [ ] Plugins function as expected
- [ ] API endpoints respond appropriately
- [ ] Streaming responses work properly
- [ ] UI (if applicable) connects and functions
- [ ] Error handling works for invalid inputs
- [ ] [Agent-specific test cases]

### Automated Testing

[Document any automated tests or testing patterns]

```bash
# Run tests
[test commands]

# Validate configuration
[validation commands]
```

## Deployment

### Development Deployment

```bash
# Local development with hot reload
uv run uvicorn sk_agents.app:app --reload --host 0.0.0.0 --port [PORT]
```

### Production Deployment

```bash
# Production deployment
export TA_TELEMETRY_ENABLED=true
export TA_OTEL_ENDPOINT=[telemetry_endpoint]
uv run uvicorn sk_agents.app:app --host 0.0.0.0 --port [PORT] --workers 4
```

### Container Deployment

[If containerization is supported, provide Dockerfile or deployment instructions]

## Troubleshooting

### Common Issues

**Issue 1**: [Common problem description]
- **Symptoms**: [What users see]
- **Cause**: [Root cause]
- **Solution**: [How to fix]

**Issue 2**: [Another common problem]
- **Symptoms**: [What users see]
- **Cause**: [Root cause]
- **Solution**: [How to fix]

### Debugging Techniques

1. **Enable Debug Logging**:
   ```bash
   export TA_LOG_LEVEL=debug
   ```

2. **Test External Dependencies**:
   ```bash
   [commands to test external APIs or services]
   ```

3. **Validate Configuration**:
   ```bash
   [commands to validate agent configuration]
   ```

## Performance Considerations

### Optimization Strategies

- [Strategy 1: e.g., Response caching]
- [Strategy 2: e.g., API rate limiting]
- [Strategy 3: e.g., Streaming for long responses]

### Monitoring and Metrics

- [Key metrics to monitor]
- [Performance benchmarks]
- [Alerting thresholds]

## Extension and Customization

### Adding New Features

1. **New Plugin Development**:
   [Steps to add new plugins]

2. **Configuration Updates**:
   [How to modify agent behavior through configuration]

3. **UI Enhancements**:
   [How to extend the user interface]

### Integration Patterns

- [How to integrate with other agents]
- [API integration patterns]
- [Data flow considerations]

## Security Considerations

### Authentication and Authorization

- [How API keys are managed]
- [User authentication patterns]
- [Access control mechanisms]

### Data Privacy

- [Data handling policies]
- [Privacy considerations]
- [Compliance requirements]

## Production Considerations

### Scalability

- [Horizontal scaling approaches]
- [Load balancing strategies]
- [Performance optimization]

### Monitoring and Observability

- [Telemetry integration]
- [Health check endpoints]
- [Error tracking and alerting]

### Maintenance

- [Update procedures]
- [Backup strategies]
- [Disaster recovery plans]

## Related Documentation

- [AGENT_DEVELOPMENT.md](AGENT_DEVELOPMENT.md) - Step-by-step agent creation guide
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Development environment setup
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing patterns and best practices
- [University Agent README](src/orchestrators/assistant-orchestrator/example/university/README.md) - Reference implementation

## Support and Contributing

### Getting Help

- [Where to get support]
- [How to report issues]
- [Community resources]

### Contributing

- [How to contribute improvements]
- [Code review process]
- [Documentation standards]

---

**Template Version**: 1.0
**Last Updated**: [Date]
**Maintainer**: [Maintainer name/team]
