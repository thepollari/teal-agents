# Teal Agents Go

A Go implementation of the Teal Agents framework, providing a Semantic Kernel-based agent platform with plugin support and HTTP API.

## Features

- Complete Go implementation of the Teal Agents Python framework
- Semantic Kernel execution engine with plugin system
- University agent with Gemini integration
- YAML configuration system compatible with Python version
- HTTP API with exact Python endpoint compatibility
- Structured logging and telemetry
- Docker support for deployment

## Requirements

- Go 1.21 or later
- Gemini API key for LLM integration

## Installation

Clone the repository:

```bash
git clone https://github.com/merck-gen/teal-agents-go.git
cd teal-agents-go
```

Build the application:

```bash
go build ./...
```

## Configuration

The application uses YAML configuration files compatible with the Python version. Configuration files are located in the `configs` directory.

Example configuration for the University agent:

```yaml
apiVersion: v1
kind: Agent
name: university-agent
version: 1.0.0
description: "University information agent powered by Gemini"
input_type: "text"
output_type: "text"
service_name: university-agent

metadata:
  description: "An agent that can search for university information and provide details about universities worldwide."
  skills:
    - "Search for universities by name"
    - "Find universities in specific countries"
    - "Provide university details including websites, domains, and location"
  documentation_url: "https://example.com/docs/university-agent"

spec:
  agents:
    - name: university
      model: "gemini-1.5-flash-lite"
      system_prompt: |
        You are a helpful assistant that can search for information about universities worldwide.
        You have access to a plugin that can search for universities by name or country.
        When asked about a university, use the search_universities function to find information.
        When asked about universities in a specific country, use the get_universities_by_country function.
        Always provide helpful and accurate information based on the search results.
      plugins:
        - "UniversityPlugin"
      temperature: 0.7
      max_tokens: 1024
      top_p: 0.95
      top_k: 40
      
  tasks:
    - name: default
      agent: university
      description: "Default task for university information queries"
      input_schema: {}
      output_schema: {}
```

## Environment Variables

- `GEMINI_API_KEY`: API key for Gemini LLM integration
- `TA_SERVICE_CONFIG`: Path to the agent configuration file

## Running the Server

Run the server with a configuration file:

```bash
export GEMINI_API_KEY=your-api-key
export TA_SERVICE_CONFIG=configs/agents/university-agent.yaml
go run cmd/agent-server/main.go
```

Or specify the configuration file directly:

```bash
export GEMINI_API_KEY=your-api-key
go run cmd/agent-server/main.go --config configs/agents/university-agent.yaml
```

## Docker Deployment

Build and run using Docker:

```bash
docker build -t teal-agents-go .
docker run -p 8000:8000 -e GEMINI_API_KEY=your-api-key teal-agents-go
```

Or use Docker Compose:

```bash
export GEMINI_API_KEY=your-api-key
docker-compose up
```

## API Endpoints

The API endpoints are compatible with the Python version:

- `GET /health`: Health check endpoint
- `GET /{agent}/{version}/agent-card`: Get agent metadata
- `POST /{agent}/{version}/invoke`: Invoke the agent with a chat message
- `POST /{agent}/{version}/invoke-stream`: Invoke the agent with streaming response
- `GET /{agent}/{version}/ws`: WebSocket endpoint for real-time communication
- `POST /{agent}/{version}/a2a/invoke`: Agent-to-agent invoke endpoint
- `GET /{agent}/{version}/a2a/agent-card`: Agent-to-agent agent card endpoint
- `POST /{agent}/{version}/chat`: Stateful chat endpoint
- `POST /{agent}/{version}/resume`: Resume a previous session

## Testing

Run the tests:

```bash
go test ./... -v
```

Run with race detection:

```bash
go test -race ./...
```

Check test coverage:

```bash
go test -cover ./...
```

## Architecture

The project follows a clean architecture with the following structure:

- `cmd/`: Application entry points
- `pkg/`: Public packages
  - `kernel/`: Semantic Kernel execution engine
  - `plugins/`: Plugin interface and registry
  - `config/`: Configuration management
  - `api/`: HTTP API framework
  - `telemetry/`: Logging and monitoring
- `internal/`: Private implementation
  - `university/`: University plugin implementation
  - `gemini/`: Gemini API integration
  - `handlers/`: HTTP request handlers
- `configs/`: Configuration files
- `tests/`: Test suites
- `docs/`: Documentation

## Migration from Python

This Go implementation maintains full API compatibility with the Python version. The YAML configuration format is preserved, and all HTTP endpoints return identical JSON structures.

Key differences:

- Go's strong typing vs Python's dynamic typing
- Go's concurrency model using goroutines vs Python's async/await
- Go's error handling vs Python's exceptions
- Go's struct-based configuration vs Python's Pydantic models

## License

[MIT License](LICENSE)
