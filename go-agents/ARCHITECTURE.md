# Go Migration Architecture Design

## Overview

This document outlines the architectural decisions for migrating the Teal Agents framework from Python to Go, focusing on preserving functionality while leveraging Go's strengths.

## Core Design Principles

1. **API Compatibility**: Maintain identical REST/WebSocket/SSE endpoints
2. **Configuration Compatibility**: Preserve YAML configuration format
3. **Feature Parity**: All Python functionality available in Go
4. **Go Idioms**: Use Go best practices and patterns
5. **Performance**: Leverage Go's concurrency and compilation benefits

## Interface Design

### Handler Interface
```go
type Handler interface {
    Invoke(ctx context.Context, inputs map[string]interface{}) (*InvokeResponse, error)
    InvokeStream(ctx context.Context, inputs map[string]interface{}) (<-chan StreamResponse, error)
}
```

Maps to Python's `BaseHandler` with async methods converted to context-aware Go methods.

### Plugin Interface
```go
type Plugin interface {
    Initialize(ctx context.Context, authorization string, extraDataCollector ExtraDataCollector) error
    GetName() string
    GetDescription() string
}
```

Replaces Python's `BasePlugin` with explicit context support as requested by user.

### Kernel Interface
```go
type Kernel interface {
    InvokeFunction(ctx context.Context, pluginName, functionName string, args map[string]interface{}) (interface{}, error)
    GetFunction(pluginName, functionName string) (KernelFunction, error)
    AddPlugin(ctx context.Context, plugin Plugin) error
}
```

Mirrors Python's Semantic Kernel functionality with Go typing.

## Plugin System Migration

### Challenge: Dynamic Loading
Python uses `importlib` for runtime module loading, which Go cannot replicate due to compilation constraints.

### Solution: Hybrid Approach

1. **Compile-time Registration**
```go
func init() {
    plugins.Register("university", reflect.TypeOf(&UniversityPlugin{}))
}
```

2. **Runtime Instantiation**
```go
func (r *PluginRegistry) Create(ctx context.Context, name string) (Plugin, error) {
    pluginType := r.plugins[name]
    pluginValue := reflect.New(pluginType.Elem())
    return pluginValue.Interface().(Plugin), nil
}
```

3. **Remote Plugin Support** (unchanged from Python)
```go
type RemotePluginLoader struct {
    catalog map[string]RemotePlugin
    client  *http.Client
}
```

### Function Discovery Migration

**Python Decorators**:
```python
@kernel_function(description="Search universities")
def search_universities(self, query: str) -> List[University]:
    pass
```

**Go Struct Tags**:
```go
type SearchFunc struct {
    Description string `kernel:"Search universities"`
    Name        string `kernel:"search_universities"`
}

func (p *UniversityPlugin) SearchUniversities(ctx context.Context, query string) ([]University, error) {
    // Implementation
}
```

## Concurrency Model Migration

### Python Async/Await → Go Goroutines

**Python**:
```python
async def invoke_stream(self, inputs):
    async for result in self.process_tasks():
        yield result
```

**Go**:
```go
func (s *SequentialAgent) InvokeStream(ctx context.Context, inputs map[string]interface{}) (<-chan StreamResponse, error) {
    responseChan := make(chan StreamResponse)
    go func() {
        defer close(responseChan)
        // Process tasks and send to channel
    }()
    return responseChan, nil
}
```

### Benefits of Go Approach

1. **Type Safety**: Compile-time checking vs runtime errors
2. **Performance**: Native goroutines vs Python asyncio overhead
3. **Memory Efficiency**: Struct packing vs Python object overhead
4. **Cancellation**: Context-based cancellation vs Python asyncio.CancelledError

## Configuration System

### YAML Compatibility
Identical YAML structure with Go struct tags:

```go
type BaseConfig struct {
    APIVersion  string     `yaml:"apiVersion"`
    Kind        string     `yaml:"kind"`
    Description string     `yaml:"description"`
    ServiceName string     `yaml:"service_name"`
    Version     string     `yaml:"version"`
    Spec        SpecConfig `yaml:"spec"`
}
```

### Type Safety Benefits
- Compile-time validation of configuration structure
- Explicit field types vs Python's dynamic typing
- Clear error messages for invalid configurations

## Web Service Architecture

### Framework Choice: Gin
- **Performance**: Faster than Python FastAPI
- **Middleware**: Rich ecosystem for logging, CORS, etc.
- **WebSocket Support**: Via gorilla/websocket
- **SSE Support**: Native HTTP streaming

### Endpoint Mapping
```go
// Python: @app.post("/{service_name}/{version}")
v1.POST("", s.handleInvoke)

// Python: @app.get("/{service_name}/{version}/sse")
v1.GET("/sse", s.handleInvokeSSE)

// Python: @app.websocket("/{service_name}/{version}/stream")
v1.GET("/ws", s.handleWebSocket)
```

## AI Provider Integration

### Chat Completion Factory
```go
type ChatCompletionFactory interface {
    GetChatCompletion(ctx context.Context, modelName, serviceID string) (ChatCompletionClient, error)
    GetModelType(ctx context.Context, modelName string) (ModelType, error)
    SupportsStructuredOutput(ctx context.Context, modelName string) bool
}
```

Context support added as requested by user.

### Provider Support
- **OpenAI**: Direct API integration
- **Gemini**: Google AI SDK integration
- **Extensible**: Interface-based design for additional providers

## Error Handling Strategy

### Python Exceptions → Go Errors
```python
# Python
try:
    result = await agent.invoke(inputs)
except ValidationError as e:
    raise HTTPException(status_code=400, detail=str(e))
```

```go
// Go
result, err := agent.Invoke(ctx, inputs)
if err != nil {
    c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
    return
}
```

### Benefits
- **Explicit Error Handling**: No hidden exceptions
- **Error Wrapping**: Context-aware error chains
- **Type Safety**: Compile-time error checking

## Testing Strategy

### Unit Testing
- Interface mocking for external dependencies
- Table-driven tests for configuration parsing
- Benchmark tests for performance comparison

### Integration Testing
- HTTP endpoint testing with httptest
- WebSocket connection testing
- Plugin loading and execution testing

## Deployment Considerations

### Binary Distribution
- **Single Binary**: No Python runtime dependencies
- **Cross Compilation**: Multiple platform support
- **Container Images**: Smaller base images (scratch/distroless)

### Performance Characteristics
- **Memory Usage**: Lower baseline memory consumption
- **Startup Time**: Faster cold start vs Python
- **Throughput**: Higher concurrent request handling

## Migration Phases

### Phase 1: Foundation (Current)
✅ Core interfaces and types
✅ Configuration system
✅ Basic agent implementation
✅ Plugin registry framework
✅ Web service skeleton

### Phase 2: Implementation
- Complete agent implementations
- Full plugin system with reflection
- AI provider integrations
- Comprehensive testing

### Phase 3: Optimization
- Performance benchmarking
- Memory optimization
- Concurrent request handling
- Production deployment configs

## Conclusion

The Go migration preserves all Python functionality while providing:
- **Better Performance**: Native compilation and efficient concurrency
- **Type Safety**: Compile-time error detection
- **Operational Benefits**: Single binary deployment, lower resource usage
- **Maintainability**: Explicit interfaces and error handling

The hybrid plugin approach successfully addresses Go's compilation constraints while maintaining the flexibility of the original Python system.
