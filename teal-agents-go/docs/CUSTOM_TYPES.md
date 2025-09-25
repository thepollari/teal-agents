# Custom Types in Teal Agents Go

This document explains how to use custom types with the `TA_TYPES_MODULE` environment variable in the Golang implementation of teal-agents.

## Overview

Unlike Python's dynamic module loading, Go uses a registry-based approach for custom types. Users must explicitly register their custom types with the TypeLoader during application startup.

## How It Works

1. **Define Custom Types**: Create Go structs that represent your custom input/output types
2. **Create Registration Function**: Write a function that registers your types with the TypeLoader
3. **Set Environment Variable**: Use `TA_TYPES_MODULE` to point to your custom types file
4. **Initialize**: The TypeLoader will detect your custom types file and log instructions

## Step-by-Step Guide

### 1. Create Custom Types File

Create a file (e.g., `custom_types.go`) with your custom types:

```go
package main

import (
    "github.com/thepollari/teal-agents-go/pkg/types"
)

// Custom input type for mathematical operations
type MathInput struct {
    Number1   int    `json:"number_1"`
    Number2   int    `json:"number_2"`
    Operation string `json:"operation"`
}

// Custom output type for mathematical results
type MathOutput struct {
    Result int    `json:"result"`
    Error  string `json:"error,omitempty"`
}

// Registration function - REQUIRED
func RegisterCustomTypes(tl *types.TypeLoader) {
    tl.RegisterType("MathInput", MathInput{})
    tl.RegisterType("MathOutput", MathOutput{})
}
```

### 2. Initialize Types in Your Application

In your main application or initialization code:

```go
package main

import (
    "github.com/thepollari/teal-agents-go/pkg/types"
)

func main() {
    // Get the global type loader
    typeLoader := types.GetTypeLoader()
    
    // Register your custom types
    RegisterCustomTypes(typeLoader)
    
    // Continue with your application...
}
```

### 3. Set Environment Variable

Set the `TA_TYPES_MODULE` environment variable to point to your custom types file:

```bash
export TA_TYPES_MODULE="/path/to/your/custom_types.go"
```

Or use it when starting your application:

```bash
TA_TYPES_MODULE="/path/to/custom_types.go" go run cmd/sk-agents/main.go
```

### 4. Configure Agent to Use Custom Types

Update your agent configuration to specify the custom input/output types:

```yaml
apiVersion: skagents/v1
name: MathAgent
serviceName: math-service
version: "1.0.0"
description: "Agent that performs mathematical operations"
inputType: "MathInput"    # Your custom input type
outputType: "MathOutput"  # Your custom output type
spec:
  model_name: "gpt-3.5-turbo"
  service_id: "openai"
  settings:
    temperature: 0.1
```

## Fallback Mechanism

If `TA_TYPES_MODULE` is not set, the TypeLoader will automatically look for `custom_types.go` in the same directory as your configuration file:

```
your-agent/
├── config.yaml
├── custom_types.go  # Automatically detected
└── main.go
```

## API Usage

Once registered, your custom types work seamlessly with the HTTP API:

### POST Request with Custom Input
```bash
curl -X POST http://localhost:8000/math-service/1.0.0/ \
  -H "Content-Type: application/json" \
  -d '{
    "number_1": 10,
    "number_2": 5,
    "operation": "add"
  }'
```

### Response with Custom Output
```json
{
  "result": 15,
  "error": ""
}
```

## Type Registration Methods

The TypeLoader provides several methods for working with custom types:

```go
// Register a custom type
typeLoader.RegisterType("MyType", MyType{})

// Get a registered type
typeRef, err := typeLoader.GetType("MyType")

// Create an instance of a registered type
instance, err := typeLoader.CreateInstance("MyType")

// Check if a standard type exists
typeRef, exists := typeLoader.GetStandardType("BaseInput")
```

## Best Practices

1. **Consistent Naming**: Use the same type names in your Go code and configuration files
2. **JSON Tags**: Always include JSON tags for proper serialization
3. **Error Handling**: Handle registration errors gracefully
4. **Documentation**: Document your custom types for other developers

## Troubleshooting

### Common Issues

1. **Type Not Found Error**
   - Ensure you've called `RegisterCustomTypes()` before using the type
   - Check that the type name matches exactly between registration and configuration

2. **JSON Parsing Errors**
   - Verify your JSON tags match the expected field names
   - Ensure required fields are present in requests

3. **Module Not Found Warning**
   - Check that `TA_TYPES_MODULE` points to an existing file
   - Verify the file path is absolute or relative to the working directory

### Debug Logging

The TypeLoader logs helpful information:

```
2025/09/25 12:09:32 Custom types module specified: /path/to/custom_types.go
2025/09/25 12:09:32 Note: Custom types must be registered using TypeLoader.RegisterType() in Go
```

## Differences from Python Implementation

| Aspect | Python | Go |
|--------|--------|-----|
| Loading | Automatic via `importlib` | Manual via `RegisterType()` |
| Type Discovery | Dynamic `getattr()` | Explicit registration |
| Runtime | Dynamic | Compile-time safe |
| Performance | Runtime overhead | Zero runtime overhead |

The Go approach trades Python's dynamic flexibility for compile-time safety and better performance.
