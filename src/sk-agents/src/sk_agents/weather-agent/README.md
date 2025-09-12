# Weather Agent

A weather agent built with the Teal Agents Framework that provides current weather information for any city using the Open-Meteo API.

## Features

- Get current weather information for any city worldwide
- Returns temperature, weather condition, humidity, and wind speed
- Uses the free Open-Meteo API (no API key required)
- Handles invalid city names gracefully with error messages
- Built with Semantic Kernel and FastAPI

## Usage

### Starting the Agent

To start the weather agent, run the following command from the `src/sk-agents` directory:

```bash
TA_SERVICE_CONFIG=src/sk_agents/weather-agent/config.yaml TA_PLUGIN_MODULE=src/sk_agents/weather-agent/custom_plugins.py fastapi run src/sk_agents/app.py
```

The agent will be available at `http://localhost:8000`

### Testing the Agent

1. Visit `http://localhost:8000/docs` to access the Swagger UI
2. Use the `/invoke` endpoint to send weather requests
3. Example request body:
```json
{
  "chat_history": [
    {
      "role": "user",
      "content": "What's the weather like in New York?"
    }
  ]
}
```

### Example Interactions

**Valid City Request:**
- User: "What's the weather in London?"
- Agent: "The current weather in London is 68.5°F with partly cloudy skies. The humidity is 72% and wind speed is 8.3 mph."

**Invalid City Request:**
- User: "What's the weather in Nonexistentcity?"
- Agent: "I'm sorry, but I couldn't find weather data for 'Nonexistentcity'. Please check the spelling and try again."

## Configuration

The agent uses the following configuration:

- **API Version:** skagents/v1
- **Kind:** Sequential
- **Model:** gpt-4o-mini
- **Input Type:** BaseInput
- **Plugins:** WeatherPlugin

## Weather Data

The agent provides the following weather information:

- **City Name:** The resolved city name
- **Temperature:** Current temperature in Fahrenheit
- **Condition:** Weather condition (e.g., "Clear", "Partly Cloudy", "Rain")
- **Description:** Detailed weather description
- **Humidity:** Relative humidity percentage
- **Wind Speed:** Wind speed in mph

## Error Handling

The agent handles various error scenarios:

- **Invalid city names:** Returns a helpful message asking to check spelling
- **API failures:** Provides error information and suggests trying again
- **Network issues:** Handles timeout and connection errors gracefully

## Dependencies

- **Open-Meteo API:** Free weather API (no key required)
- **Open-Meteo Geocoding API:** For city name resolution
- **Requests:** HTTP client for API calls
- **Pydantic:** Data validation and serialization
- **Semantic Kernel:** AI framework for function calling

## Files

- `config.yaml` - Agent configuration
- `custom_plugins.py` - WeatherPlugin implementation
- `README.md` - This documentation
- `.env.example` - Environment variable template (for future extensions)
