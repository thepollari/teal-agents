# University Agent

A comprehensive university agent powered by Google Gemini that provides information about universities and higher education institutions worldwide.

## Overview

The University Agent demonstrates the full Teal Agents Framework capabilities by integrating:
- **Google Gemini 2.0 Flash-Lite** for natural language processing via custom chat completion factory
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

Before running the University Agent, ensure you have the following installed and configured:

1. **Python 3.12+**: The Teal Agents framework requires Python 3.12 or higher
2. **UV Package Manager**: Install UV for dependency management
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. **Teal Agents Framework**: Clone and set up the repository
   ```bash
   git clone https://github.com/thepollari/teal-agents.git
   cd teal-agents
   ```
4. **Google Gemini API Key**: Get a free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Installation

1. **Install Dependencies**: Navigate to the sk-agents directory and install required packages
   ```bash
   cd ~/repos/teal-agents/src/sk-agents
   uv add google-generativeai
   ```

2. **Install Streamlit**: Navigate to the orchestrator directory and add Streamlit
   ```bash
   cd ~/repos/teal-agents/src/orchestrators/assistant-orchestrator/orchestrator
   uv add streamlit
   ```

3. **Verify Installation**: Check that all dependencies are installed correctly
   ```bash
   cd ~/repos/teal-agents/src/sk-agents
   uv run python -c "import google.generativeai; print('Google AI SDK installed successfully')"
   uv run python -c "import streamlit; print('Streamlit installed successfully')"
   ```

### Configuration

1. **Set your Gemini API key** (replace with your actual API key):
   ```bash
   export GEMINI_API_KEY="your_gemini_api_key_here"
   ```

2. **Configure the agent paths** (use absolute paths for reliability):
   ```bash
   export TA_SERVICE_CONFIG="/home/ubuntu/repos/teal-agents/src/orchestrators/assistant-orchestrator/example/university/config.yaml"
   export TA_PLUGIN_MODULE="/home/ubuntu/repos/teal-agents/src/orchestrators/assistant-orchestrator/example/university/custom_plugins.py"
   ```

3. **Configure the custom Gemini completion factory**:
   ```bash
   export TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE="src/sk_agents/chat_completion/custom/gemini_chat_completion_factory.py"
   export TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS_NAME="GeminiChatCompletionFactory"
   ```

4. **Verify Configuration**: Test that all environment variables are set correctly
   ```bash
   echo "API Key: ${GEMINI_API_KEY:0:10}..." # Shows first 10 chars of API key
   echo "Service Config: $TA_SERVICE_CONFIG"
   echo "Plugin Module: $TA_PLUGIN_MODULE"
   echo "Factory Module: $TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE"
   echo "Factory Class: $TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS_NAME"
   ```

### Running the Agent

**Important**: Complete all setup and configuration steps above before running the agent.

#### Option 1: Streamlit UI (Recommended)

1. **Start the Agent Server** (in terminal 1):
   ```bash
   cd ~/repos/teal-agents/src/sk-agents
   uv run uvicorn sk_agents.app:app --host 0.0.0.0 --port 8001
   ```

2. **Start the Streamlit UI** (in terminal 2):
   ```bash
   cd ~/repos/teal-agents/src/orchestrators/assistant-orchestrator/example/university
   uv run streamlit run streamlit_ui.py --server.port 8502
   ```

3. **Access the UI**: Open your browser and navigate to `http://localhost:8502`

#### Option 2: Direct Agent API

1. **Start the Agent Server**:
   ```bash
   cd ~/repos/teal-agents/src/sk-agents
   uv run uvicorn sk_agents.app:app --host 0.0.0.0 --port 8001
   ```

2. **Test with curl**:
   ```bash
   curl -X POST http://localhost:8001/UniversityAgent/0.1 \
     -H "Content-Type: application/json" \
     -d '{"chat_history": [{"role": "user", "content": "Find universities in Finland"}]}'
   ```

#### Verification

After starting the services, verify they're working:

1. **Check Agent Status**: Visit `http://localhost:8001/UniversityAgent/0.1/docs` in your browser
2. **Check Streamlit UI**: Visit `http://localhost:8502` and click "Check Agent Status"
3. **Test a Query**: Try asking "Find universities in Finland" in the Streamlit chat interface

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
   - Supports Gemini 2.0 Flash-Lite model with structured output
   - Environment variable configuration for API key

2. **UniversityPlugin** (`custom_plugins.py`)
   - `search_universities(query: str)` - Search by name or partial name
   - `get_universities_by_country(country: str)` - Find universities in specific country
   - Integration with universities.hipolabs.com API
   - Comprehensive error handling and response formatting

3. **Agent Configuration** (`config.yaml`)
   - Sequential agent using Gemini 2.0 Flash-Lite model
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

- **Model**: gemini-2.0-flash-lite
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
