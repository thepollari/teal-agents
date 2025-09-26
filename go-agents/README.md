# Go Agents - Teal Agents Go Migration

This directory contains the Go implementation of the Teal Agents framework, migrated from the Python Semantic Kernel implementation.

## Architecture Overview

The Go implementation preserves all functionality from the Python version while leveraging Go's strengths:

- **Strong typing** with interfaces and struct tags
- **Goroutines and channels** for concurrent execution and streaming
- **Compile-time safety** with explicit error handling
- **Native HTTP performance** with Gin web framework

## Package Structure

```
pkg/
├── types/          # Core interfaces and types
├── config/         # YAML configuration handling
├── agents/         # Agent implementations (Sequential, Chat)
├── kernel/         # Kernel builder and management
├── plugins/        # Plugin system (local and remote)
├── completion/     # AI provider integrations
└── server/         # Web service layer

cmd/
└── agent/          # Main application entry point

examples/
├── getting_started/  # Basic configuration examples
└── plugins/         # Plugin configuration examples
```

## Key Migration Decisions

### Plugin System Migration

The Python dynamic plugin loading has been adapted for Go's compilation constraints:

1. **Local Plugins**: Compile-time registration with runtime instantiation
2. **Remote Plugins**: Direct HTTP-based migration (unchanged from Python)
3. **Function Discovery**: Struct tags replace Python decorators
4. **Plugin Registry**: Reflection-based factory pattern

### Concurrency Model

- **Python async/await** → **Go goroutines and channels**
- **Python generators** → **Go channels for streaming**
- **Context propagation** for cancellation and timeouts

### Configuration System

- **YAML unmarshaling** with struct tags
- **Type safety** with explicit field validation
- **API version parsing** for handler selection

## Building and Running

```bash
# Build all packages
go build ./...

# Run the agent
export TA_SERVICE_CONFIG=examples/getting_started/config.yaml
go run cmd/agent/main.go
```

## API Compatibility

The Go implementation maintains full API compatibility with the Python version:

- **REST endpoints**: `POST /{service_name}/{version}`
- **SSE streaming**: `GET /{service_name}/{version}/sse`
- **WebSocket**: `GET /{service_name}/{version}/ws`
- **Health check**: `GET /health`

## Configuration Format

The YAML configuration format is identical to the Python version:

```yaml
apiVersion: skagents/v1
kind: Sequential
description: Agent description
service_name: MyAgent
version: 0.1
input_type: BaseInput
spec:
  agents:
    - name: agent_name
      model: gpt-4o-mini
      system_prompt: "System prompt"
      plugins: ["plugin1", "plugin2"]
  tasks:
    - name: task_name
      task_no: 1
      description: "Task description"
      instructions: "Task instructions"
      agent: agent_name
```

## Plugin Development

### Local Plugins

```go
type MyPlugin struct {
    plugins.BasePlugin
}

func (p *MyPlugin) Initialize(ctx context.Context, auth string, collector types.ExtraDataCollector) error {
    return p.BasePlugin.Initialize(ctx, auth, collector)
}

// Register in init() function
func init() {
    plugins.GlobalRegistry.Register("my_plugin", reflect.TypeOf(&MyPlugin{}))
}
```

### Remote Plugins

Remote plugins work identically to the Python version, using OpenAPI specifications and HTTP calls.

## Performance Benefits

The Go implementation provides several performance improvements:

- **Native compilation** vs Python interpretation
- **Efficient goroutines** vs Python asyncio overhead
- **Static typing** eliminates runtime type checking
- **Memory efficiency** with struct packing and garbage collection

## Migration Status

✅ **Core Architecture**: Complete interface definitions and package structure
✅ **Configuration System**: YAML parsing and validation
✅ **Sequential Agent**: Task execution and streaming
✅ **Plugin System**: Registry and remote loading
✅ **Web Service**: REST, SSE, and WebSocket endpoints
✅ **AI Integration**: OpenAI and Gemini client factories

🚧 **In Progress**: Chat agent implementation, comprehensive testing
📋 **Planned**: Performance benchmarks, deployment configurations
