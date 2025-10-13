# Teal Agents Configuration Package

This package provides Go implementations for loading and validating YAML configuration files and environment variables, migrated from the Python implementation.

## Features

- YAML configuration loading using Viper
- Environment variable binding and overrides
- Validation using go-playground/validator
- Support for all orchestrator types (Sequential, Chat, Team, Planning, Assistant)
- Backward compatibility with existing Python YAML configs
- JSON-encoded environment variable stores (TA_ENV_STORE, TA_ENV_GLOBAL_STORE)

## Usage

### Loading Environment Variables

```go
import "github.com/thepollari/teal-agents/pkg/config/loader"

cl := loader.NewConfigLoader()
envConfig, err := cl.LoadEnvConfig()
if err != nil {
    log.Fatal(err)
}

fmt.Println("API Key:", envConfig.APIKey)
fmt.Println("Service Config:", envConfig.ServiceConfig)
```

### Loading YAML Configuration

```go
// Load any config by auto-detecting kind
config, err := cl.LoadConfigByKind("path/to/config.yaml")
if err != nil {
    log.Fatal(err)
}

// Or load specific config type
seqConfig, err := cl.LoadSequentialConfig("path/to/sequential.yaml")
chatConfig, err := cl.LoadChatConfig("path/to/chat.yaml")
```

### Validation

All configurations are automatically validated using struct tags:

```go
type AgentConfig struct {
    Temperature *float64 `validate:"omitempty,gte=0,lte=1"`
}
```

## Environment Variables

See `types/env_config.go` for the complete list of supported environment variables.

Required variables:
- TA_API_KEY
- TA_SERVICE_CONFIG
- TA_A2A_ENABLED
- TA_AGENT_BASE_URL
- TA_PROVIDER_ORG
- TA_PROVIDER_URL
- TA_STATE_MANAGEMENT
- TA_PERSISTENCE_MODULE
- TA_PERSISTENCE_CLASS

## Testing

```bash
make go-test-config                # Unit tests
make go-test-integration           # Integration tests with real configs
```
