# University Agent

A comprehensive university agent powered by Google Gemini that provides information about universities and higher education institutions worldwide.

## Overview

The University Agent demonstrates the full Teal Agents Framework capabilities by integrating:
- **Google Gemini 1.5 Flash** for natural language processing via custom chat completion factory
- **Universities API** (universities.hipolabs.com) for real-time university data
- **Streamlit UI** for interactive testing and user experience

## Features

- Search universities by name or partial name
- Find universities in specific countries
- Get detailed information including:
  - University name and location
  - Official websites
  - Domain names
  - Country and state/province information
- Natural language conversation interface
- Real-time API integration with comprehensive error handling

## Setup

### Prerequisites

1. **Google Gemini API Key**: Get a free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Environment Setup**: Ensure you have the Teal Agents framework installed

### Configuration

1. Set your Gemini API key:
```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
```

2. Configure the agent to use the custom Gemini completion factory:
```bash
export TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE="sk_agents.chat_completion.custom.gemini_chat_completion_factory"
export TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS_NAME="GeminiChatCompletionFactory"
```

### Running the Agent

#### Option 1: Direct Agent API

```bash
cd ~/repos/teal-agents/src/sk-agents
export TA_SERVICE_CONFIG="$(pwd)/../../orchestrators/assistant-orchestrator/example/university/config.yaml"
export TA_PLUGIN_MODULE="$(pwd)/../../orchestrators/assistant-orchestrator/example/university/custom_plugins.py"
uv run uvicorn sk_agents.app:app --host 0.0.0.0 --port 8000
```

#### Option 2: Streamlit UI (Recommended)

```bash
cd ~/repos/teal-agents/src/orchestrators/assistant-orchestrator/example/university
uv run streamlit run streamlit_ui.py
```

## Usage Examples

### Example Queries

- "Find universities in Finland"
- "Search for Aalto University"
- "What universities are in the United States?"
- "Tell me about universities in Japan"
- "Find technical universities in Germany"

### API Response Format

The agent returns structured information about universities:

```json
{
  "message": "Found 5 universities for query: Aalto",
  "universities": [
    {
      "name": "Aalto University",
      "web_pages": ["https://www.aalto.fi"],
      "domains": ["aalto.fi"],
      "country": "Finland",
      "state_province": null,
      "alpha_two_code": "FI"
    }
  ]
}
```

## Architecture

### Components

1. **GeminiChatCompletionFactory** (`src/sk-agents/src/sk_agents/chat_completion/custom/gemini_chat_completion_factory.py`)
   - Custom completion factory for Google Gemini integration
   - Supports Gemini 1.5 Flash model with structured output
   - Environment variable configuration for API key

2. **UniversityPlugin** (`custom_plugins.py`)
   - `search_universities(query: str)` - Search by name or partial name
   - `get_universities_by_country(country: str)` - Find universities in specific country
   - Integration with universities.hipolabs.com API
   - Comprehensive error handling and response formatting

3. **Agent Configuration** (`config.yaml`)
   - Sequential agent using Gemini 1.5 Flash model
   - University-focused system prompt
   - Plugin integration and task definition

4. **Streamlit UI** (`streamlit_ui.py`)
   - Chat-style interface with conversation history
   - Real-time agent communication
   - User-friendly university data presentation

### Data Flow

```
User Query → Streamlit UI → University Agent → Gemini API → University API → Formatted Response
```

## API Integration

### Universities API (universities.hipolabs.com)

- **Endpoint**: `http://universities.hipolabs.com/search`
- **Parameters**: 
  - `name` - University name search
  - `country` - Country filter
- **Rate Limits**: Free tier, no API key required
- **Response**: JSON array of university objects

### Google Gemini API

- **Model**: gemini-1.5-flash
- **Rate Limits**: 15 requests/minute (free tier)
- **Features**: Natural language processing, structured output support

## Error Handling

The agent includes comprehensive error handling for:
- API timeouts and network issues
- Invalid search queries
- Empty result sets
- Malformed API responses
- Rate limiting scenarios

## Development

### Testing

```bash
# Lint checks
cd ~/repos/teal-agents/src/sk-agents && uv run ruff check
cd ~/repos/teal-agents/src/orchestrators/assistant-orchestrator/orchestrator && uv run ruff check

# Run tests
cd ~/repos/teal-agents/src/sk-agents && uv run pytest
```

### Extending the Agent

To add new functionality:

1. **New Plugin Methods**: Add `@kernel_function` decorated methods to `UniversityPlugin`
2. **Additional APIs**: Integrate other education-related APIs
3. **Enhanced UI**: Extend Streamlit interface with new features
4. **Custom Models**: Support additional Gemini models or other LLM providers

## Troubleshooting

### Common Issues

1. **"ModuleNotFoundError: No module named 'google.generativeai'"**
   ```bash
   cd ~/repos/teal-agents/src/sk-agents && uv add google-generativeai
   ```

2. **"Custom completion factory not found"**
   - Check `TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE` and `TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS_NAME` environment variables

3. **"Universities API error"**
   - Check internet connection and API endpoint availability

4. **"Gemini API key error"**
   - Verify `GEMINI_API_KEY` environment variable is set correctly

### Debug Mode

Enable debug logging:
```bash
export TA_LOG_LEVEL="debug"
```

## License

This project is part of the Teal Agents Framework. See the main repository for license information.
