# Weather Agent with Google Gemini Integration

A comprehensive weather agent system that demonstrates the full Teal Agents Framework capabilities with Google Gemini API integration and Streamlit testing UI.

## Overview

This weather agent provides:
- **Custom Gemini Chat Completion Factory**: Integrates Google Gemini API with the Semantic Kernel framework
- **Weather Plugin**: Uses Open-Meteo API for free weather data (no API key required)
- **Streamlit UI**: Interactive web interface for testing the agent

## Features

- 🌤️ Current weather information for any city worldwide
- 🌍 Geocoding support to find coordinates for locations
- 🤖 Powered by Google Gemini 1.5 Flash model
- 💬 Chat-style interface with conversation history
- 🆓 Uses free APIs (Open-Meteo for weather, Gemini free tier)
- ⚡ Real-time weather data with temperature, humidity, wind speed

## Setup Instructions

### 1. Environment Setup

First, ensure you have the required dependencies installed:

```bash
cd ~/repos/teal-agents/src/sk-agents
uv sync --dev
```

### 2. Google Gemini API Key

1. Get a free Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Set the environment variable:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

### 3. Start the Weather Agent

Set the required environment variables and start the agent:

```bash
export TA_SERVICE_CONFIG="$(pwd)/src/sk_agents/weather-agent/config.yaml"
export TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE="src/sk_agents/chat_completion/custom/gemini_chat_completion_factory.py"
export TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS_NAME="GeminiChatCompletionFactory"
export GEMINI_API_KEY="your-api-key-here"

uv run fastapi run src/sk_agents/app.py --host 0.0.0.0 --port 8000
```

### 4. Start the Streamlit UI

In a new terminal, navigate to the weather agent directory and start the UI:

```bash
cd ~/repos/teal-agents/src/sk-agents/src/sk_agents/weather-agent
uv run streamlit run streamlit_ui.py
```

The Streamlit interface will be available at `http://localhost:8501`

## Usage

### Example Queries

Try these example queries in the Streamlit interface:

- "What's the weather in New York?"
- "How's the weather in Tokyo today?"
- "Tell me about the weather in London"
- "What are the coordinates of Paris?"
- "Is it raining in Seattle?"

### API Endpoints

The weather agent exposes these FastAPI endpoints:

- `GET /health` - Health check
- `POST /skagents/v1/invoke` - Main agent invocation endpoint

### Plugin Methods

The WeatherPlugin provides these kernel functions:

- `get_current_weather(city: str) -> str` - Returns JSON string with current weather data
- `get_coordinates(city: str) -> str` - Returns JSON string with latitude/longitude coordinates

## Architecture

### Custom Gemini Factory

The `GeminiChatCompletionFactory` class:
- Extends the Semantic Kernel `ChatCompletionFactory` interface
- Supports Gemini 1.5 Flash model (free tier with 15 requests/minute)
- Handles API key management via environment variables
- Provides proper error handling and rate limiting awareness

### Weather Plugin

The `WeatherPlugin` class:
- Inherits from `BasePlugin` with `@kernel_function` decorators
- Uses Open-Meteo API (free, no API key required)
- Supports natural language queries about weather conditions
- Provides structured weather data with temperature, conditions, and location
- Includes comprehensive error handling for API failures and invalid locations

### Streamlit Interface

The Streamlit UI provides:
- Chat-style interface using `st.chat_message` and `st.chat_input`
- Conversation history maintained within the session
- Connection to the weather agent's FastAPI endpoints
- User-friendly weather data presentation
- Agent status monitoring and error handling
- Example queries and usage instructions

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

### Environment Variables

- `GEMINI_API_KEY` - Google Gemini API key (required)
- `TA_SERVICE_CONFIG` - Path to agent config.yaml file
- `TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE` - Module path for custom factory
- `TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS_NAME` - Factory class name

## API Rate Limits

- **Google Gemini Free Tier**: 15 requests per minute
- **Open-Meteo API**: No rate limits for reasonable usage

## Troubleshooting

### Common Issues

1. **"Could not connect to weather agent"**
   - Ensure the FastAPI agent is running on port 8000
   - Check that all environment variables are set correctly

2. **"GEMINI_API_KEY environment variable is required"**
   - Set the GEMINI_API_KEY environment variable with your API key

3. **"Model gemini-1.5-flash not supported"**
   - Verify your Gemini API key is valid and has access to the model

4. **Weather data not loading**
   - Check internet connection
   - Verify the city name is spelled correctly
   - Open-Meteo API might be temporarily unavailable

### Testing the Setup

1. **Test the Gemini Factory**:
```bash
python -c "
from sk_agents.chat_completion.custom.gemini_chat_completion_factory import GeminiChatCompletionFactory
from ska_utils import AppConfig
import os
config = AppConfig()
factory = GeminiChatCompletionFactory(config)
print('✓ Gemini factory initialized successfully')
"
```

2. **Test the Weather Plugin**:
```bash
python -c "
from sk_agents.weather_agent.custom_plugins import WeatherPlugin
plugin = WeatherPlugin()
result = plugin.get_coordinates('New York')
print('✓ Weather plugin working:', result)
"
```

## Development

### Running Tests

```bash
cd ~/repos/teal-agents/src/sk-agents
uv run pytest
```

### Linting

```bash
uv run ruff check .
uv run ruff format .
```

## License

This project is part of the Teal Agents Platform and follows the same licensing terms.
