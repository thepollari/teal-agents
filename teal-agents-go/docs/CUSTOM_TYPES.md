# Custom Types in Teal Agents Go

This document explains how to use custom types with the Golang implementation of Teal Agents.

## Overview

The Golang implementation supports custom types through a **build-time approach** where custom types must be compiled into the binary. This is different from Python's dynamic module loading due to Go's static nature.

## Build-Time Approach

### Why Build-Time?

Go is a statically compiled language that doesn't support Python's dynamic module loading. The available options were:

1. **Build-time approach**: Compile custom types into the binary ✅ (Current implementation)
2. **Accept limitations**: Document that Go requires custom types to be compiled in

This approach ensures stability and avoids runtime crashes while maintaining type safety.

## How It Works

### Type Registration System

Custom types are registered using `init()` functions that execute when the binary starts:

1. **Standard Types**: Built-in types like `BaseInput`, `InvokeResponse`, etc.
2. **Custom Types**: User-defined types registered through `init()` functions
3. **Build Tags**: Use `-tags custom_types` to include custom type packages

## Creating Custom Types

### 1. Create Custom Types Package

Create a separate package for your custom types:

```
examples/math_agent/
├── types/
│   └── custom_types.go
├── config.yaml
└── main.go
```

### 2. Define Your Types

```go
// examples/math_agent/types/custom_types.go
package types

import (
    "github.com/thepollari/teal-agents-go/pkg/types"
)

type MathInput struct {
    Number1   int    `json:"number_1"`
    Number2   int    `json:"number_2"`
    Operation string `json:"operation"`
}

type MathOutput struct {
    Result int    `json:"result"`
    Error  string `json:"error,omitempty"`
}

func RegisterCustomTypes(tl *types.TypeLoader) {
    tl.RegisterType("MathInput", MathInput{})
    tl.RegisterType("MathOutput", MathOutput{})
}

func init() {
    types.RegisterTypeRegistrationFunc(RegisterCustomTypes)
}
```

### 3. Create Import File with Build Tag

```go
// cmd/sk-agents/import_custom_types.go
//go:build custom_types

package main

import (
    _ "github.com/thepollari/teal-agents-go/examples/math_agent/types"
)
```

### 4. Build with Custom Types

```bash
# Build binary with custom types
go build -tags custom_types -o sk-agents ./cmd/sk-agents/

# Run with custom types compiled in
./sk-agents
```

## Configuration

Update your agent configuration to use the custom types:

```yaml
# config.yaml
apiVersion: skagents/v1
kind: Agent
metadata:
  name: MathAgent
  version: "1.0.0"
  description: "Agent that performs mathematical operations using custom types"
spec:
  model_name: gpt-3.5-turbo
  service_id: openai
  settings:
    temperature: 0.7
    max_tokens: 1000
  input_type: MathInput    # Reference your custom input type
  output_type: MathOutput  # Reference your custom output type
```

## Usage Example

### Building and Running

```bash
cd teal-agents-go

# Build with custom types
go build -tags custom_types -o cmd/sk-agents/sk-agents ./cmd/sk-agents/

# Run the agent
cd examples/math_agent
export TA_SERVICE_CONFIG="$(pwd)/config.yaml"
export OPENAI_API_KEY="your-api-key"
export PORT=8080

../../cmd/sk-agents/sk-agents
```

### Testing Custom Types

1. **Check Agent Card**:
```bash
curl http://localhost:8080/math-service/1.0.0/agent-card | jq
```

Expected response:
```json
{
  "customInputType": true,
  "customOutputType": true,
  "inputType": "MathInput",
  "outputType": "MathOutput"
}
```

2. **Invoke with Custom Input**:
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"number_1": 10, "number_2": 5, "operation": "add"}' \
  http://localhost:8080/math-service/1.0.0/
```

## User Instructions

### For Users Who Need Custom Types

If you need custom types, you must:

1. **Create your custom types package** following the structure above
2. **Update the import file** to include your custom types package
3. **Build your own binary** using `go build -tags custom_types`
4. **Deploy your custom binary** instead of the standard one

### For Users Who Don't Need Custom Types

If you only use standard types or remote agents:

1. **Use the standard binary** (no build tags needed)
2. **Remote agents are the primary use case** and work without custom types
3. **Standard types** (BaseInput, InvokeResponse) work out of the box

## Limitations

### Go vs Python Differences

| Feature | Python | Go (Build-time) |
|---------|--------|-----------------|
| Dynamic loading | ✅ Runtime | ❌ Compile-time only |
| Type discovery | ✅ Automatic | ❌ Manual registration |
| Binary distribution | ✅ Single binary | ❌ Custom binary needed |
| Type safety | ⚠️ Runtime errors | ✅ Compile-time safety |

### Impact on Functionality

- **✅ Remote agents**: Work perfectly (primary use case)
- **✅ Standard types**: Work out of the box
- **⚠️ Custom types**: Require custom binary build
- **❌ Dynamic type loading**: Not supported in Go

## Troubleshooting

### Common Issues

1. **Custom types not recognized**
   - Ensure you built with `-tags custom_types`
   - Verify the import file includes your custom types package
   - Check that `init()` function is called

2. **Build errors**
   - Verify Go module paths are correct
   - Ensure custom types package is properly structured
   - Check import paths in import_custom_types.go

3. **Server crashes**
   - The build-time approach eliminates crashes from dynamic loading
   - If crashes occur, check for other issues (missing config, etc.)

### Debug Logging

The system provides debug logging:

```
2025/09/25 14:32:36 Applied 1 custom type registration functions
2025/09/25 14:32:54 Custom input type 'MathInput' is registered
2025/09/25 14:32:54 Custom output type 'MathOutput' is registered
2025/09/25 14:33:05 Successfully parsed custom input type: MathInput
```

## Testing Results

### Successful Build-Time Test

**Build Command**: 
```bash
go build -tags custom_types -o cmd/sk-agents/sk-agents ./cmd/sk-agents/
```

**Environment**:
- TA_SERVICE_CONFIG: `/path/to/examples/math_agent/config.yaml`
- Custom types compiled into binary

**Results**:
- ✅ Binary builds successfully with custom types
- ✅ Server starts without crashes
- ✅ Custom types registered via init() functions
- ✅ Agent card shows `customInputType: true`, `customOutputType: true`
- ✅ Invoke endpoint processes custom input correctly

**Agent Card Response**:
```json
{
  "name": "MathAgent",
  "version": "1.0.0",
  "inputType": "MathInput",
  "outputType": "MathOutput",
  "customInputType": true,
  "customOutputType": true
}
```

**Server Logs**:
```
2025/09/25 14:32:36 Applied 1 custom type registration functions
2025/09/25 14:33:05 Successfully parsed custom input type: MathInput
```

This confirms that the build-time custom type approach works correctly and eliminates the crashes from dynamic loading attempts.
