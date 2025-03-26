# Teal Agents Framework
## Chat-Only Agents with PlugIns
Chat-only agents do support the same plug-in architecture as sequential agents.

### Example Configuration

```yaml
apiVersion: skagents/v1
kind: Chat
description: >
  A weather chat agent
service_name: WeatherBot
version: 0.1
input_type: BaseInputWithUserContext
spec:
  agent:
    name: default
    role: Default Agent
    model: gpt-4o
    system_prompt: >
      You are a helpful assistant.
    plugins:
    - WeatherPlugin
```