# Weather Agent with Google Gemini Integration

A comprehensive weather agent system that demonstrates the Teal Agents Framework capabilities with Google Gemini API integration, designed for the assistant-orchestrator architecture.

## Overview

This weather agent provides:
- **Custom Gemini Chat Completion Factory**: Integrates Google Gemini API with the Semantic Kernel framework
- **Weather Plugin**: Uses Open-Meteo API for free weather data (no API key required)
- **Assistant-Orchestrator Integration**: Runs as a microservice within the orchestrator ecosystem

## Features

- 🌤️ Current weather information for any city worldwide
- 🌍 Geocoding support to find coordinates for locations
- 🤖 Powered by Google Gemini 1.5 Flash model
- 🆓 Uses free APIs (Open-Meteo for weather, Gemini free tier)
- ⚡ Real-time weather data with temperature, humidity, wind speed
- 🏗️ Microservice architecture with Kong gateway routing

## Architecture

This weather agent runs as part of the assistant-orchestrator system:
- **Agent Service**: Runs as a Docker container using the `teal-agents:latest` image
- **Kong Gateway**: Routes requests to the weather agent service
- **Volume Mounting**: Agent files are mounted from `./weather` to `/app/src/sk-agents/agents`
- **Environment Configuration**: Uses `weather.env` for service configuration

## Setup Instructions

### 1. Prerequisites

Ensure you have the assistant-orchestrator example environment set up:

```bash
cd ~/repos/teal-agents/src/orchestrators/assistant-orchestrator/example
```

### 2. Google Gemini API Key

1. Get a free Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Update the environment configuration:

```bash
# Copy the example environment file
cp weather.env.example weather.env

# Edit weather.env and set your API key
GEMINI_API_KEY=your-api-key-here
```

### 3. Build and Start the System

Build the base images (if not already done):

```bash
cd ~/repos/teal-agents
make all
```

Start the full example system:

```bash
cd src/orchestrators/assistant-orchestrator/example

# For macOS
make build-full-example-system-macos

# For Linux/Windows
make build-full-example-system-bash
```

### 4. Access the System

Once started, access the test environment at:
- **Main Interface**: http://localhost:8000/client
- **Kong Gateway**: http://localhost:8002/ (to view configured services)
- **Weather Agent Direct**: http://localhost:8103/WeatherAgent/0.1/openapi.json

## Usage

### Example Queries

Try these queries in the client interface at http://localhost:8000/client:

- "What's the weather in New York?"
- "How's the weather in Tokyo today?"
- "Tell me about the weather in London"
- "What are the coordinates of Paris?"
- "Is it raining in Seattle?"

### API Endpoints

The weather agent exposes these endpoints through Kong gateway:

- `GET /WeatherAgent/0.1/openapi.json` - OpenAPI specification
- `POST /WeatherAgent/0.1` - Main agent invocation endpoint
- `WS /WeatherAgent/0.1/stream` - WebSocket streaming endpoint

### Plugin Methods

The WeatherPlugin provides these kernel functions:

- `get_current_weather(city: str) -> str` - Returns JSON string with current weather data
- `get_coordinates(city: str) -> str` - Returns JSON string with latitude/longitude coordinates

## Configuration

### Agent Configuration (config.yaml)

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
      model: gemini-1.5-flash
      system_prompt: "You are a helpful weather assistant..."
      plugins:
        - WeatherPlugin
```

### Environment Variables (weather.env)

```bash
TA_API_KEY=<Your API Key>
TA_SERVICE_CONFIG=agents/config.yaml
TA_PLUGIN_MODULE=agents/custom_plugins.py
TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE=agents/gemini_chat_completion_factory.py
TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS_NAME=GeminiChatCompletionFactory
GEMINI_API_KEY=<Your Google Gemini API Key>
TA_OTEL_ENDPOINT=http://aspire:18889
```

## Development

### Local Development

For local development of the weather agent:

1. **Debug Mode**: Start other services without the weather agent:
```bash
make debug-test-agent-up
```

2. **Run Weather Agent Locally**: Start the weather agent on your machine:
```bash
cd ~/repos/teal-agents/src/sk-agents
export TA_SERVICE_CONFIG="$(pwd)/../orchestrators/assistant-orchestrator/example/weather/config.yaml"
export TA_PLUGIN_MODULE="$(pwd)/../orchestrators/assistant-orchestrator/example/weather/custom_plugins.py"
export TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE="$(pwd)/../orchestrators/assistant-orchestrator/example/weather/gemini_chat_completion_factory.py"
export TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS_NAME="GeminiChatCompletionFactory"
export GEMINI_API_KEY="your-api-key-here"
uv run fastapi run src/sk_agents/app.py --host 0.0.0.0 --port 8103
```

### Testing

Test the weather plugin directly:

```bash
cd ~/repos/teal-agents/src/sk-agents
python -c "
import sys
sys.path.insert(0, '../orchestrators/assistant-orchestrator/example/weather')
from custom_plugins import WeatherPlugin
plugin = WeatherPlugin()
print('Coordinates:', plugin.get_coordinates('New York'))
print('Weather:', plugin.get_current_weather('New York'))
"
```

### Updating the Agent

After making changes to the weather agent:

1. **Rebuild and Deploy**:
```bash
make deploy-updated-code
```

2. **View Logs**:
```bash
docker logs <weather_container_id>
```

## Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY environment variable is required"**
   - Ensure the GEMINI_API_KEY is set in `weather.env`
   - Verify the environment file is being loaded by the Docker container

2. **"Could not connect to weather agent"**
   - Check that the weather service is running: `docker ps | grep weather`
   - Verify the health check: `docker logs <weather_container_id>`

3. **"Model gemini-1.5-flash not supported"**
   - Verify your Gemini API key is valid and has access to the model
   - Check the custom completion factory is loading correctly

4. **Weather data not loading**
   - Check internet connectivity from the Docker container
   - Verify the Open-Meteo API is accessible
   - Check the city name spelling

### Monitoring

- **Kong Gateway**: http://localhost:8002/ - View configured services and routes
- **Aspire Dashboard**: Extract URL from Docker logs for the `aspire` container
- **DynamoDB Admin**: http://localhost:8400/ - View persistent storage

## API Rate Limits

- **Google Gemini Free Tier**: 15 requests per minute
- **Open-Meteo API**: No rate limits for reasonable usage

## Stopping the System

To stop all services:

```bash
make all-down
```

## License

This project is part of the Teal Agents Platform and follows the same licensing terms.
