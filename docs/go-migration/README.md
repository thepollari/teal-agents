# Go Migration - Phase 1: Module Structure and Build System

This directory contains documentation for the multi-phase migration of teal-agents from Python to Go.

## Overview

This is Phase 1 of the migration, establishing the foundational Go project structure and build tooling. The Python codebase remains fully functional and unchanged.

## Go Module Structure

The Go module mirrors the existing Python package structure:

### Python → Go Package Mapping

| Python Package | Go Package | Description |
|---------------|-----------|-------------|
| `src/sk-agents/` | `pkg/agents/` | Core agent framework |
| `src/orchestrators/assistant-orchestrator/` | `pkg/orchestrators/assistant/` | Assistant orchestrator |
| `src/orchestrators/collab-orchestrator/` | `pkg/orchestrators/collaborative/` | Collaborative orchestrator |
| `shared/ska_utils/` | `pkg/shared/utils/` | Shared utilities |

## Directory Structure

```
teal-agents/
├── go.mod                      # Go module definition
├── go.sum                      # Go dependency checksums
├── Makefile                    # Build targets (Python + Go)
├── pkg/                        # Go source code
│   ├── agents/                 # Core agent framework
│   ├── orchestrators/
│   │   ├── assistant/         # Assistant orchestrator
│   │   └── collaborative/     # Collaborative orchestrator
│   └── shared/
│       └── utils/             # Shared utilities
├── bin/                        # Compiled Go binaries (gitignored)
├── go-agents.Dockerfile        # Docker build for agents
├── go-orchestrators.Dockerfile # Docker build for orchestrators
└── docs/go-migration/         # Migration documentation
```

## Build System

### Makefile Targets

#### Go-specific targets:
- `make go-build` - Build all Go binaries to `bin/` directory
- `make go-test` - Run tests with race detection and coverage
- `make go-clean` - Clean build artifacts and caches
- `make go-fmt` - Format Go code
- `make go-vet` - Run go vet for static analysis
- `make go-lint` - Run golangci-lint (if installed)
- `make go-docker-build` - Build Go Docker images
- `make go-all` - Run fmt, vet, build, and test

#### Existing Python/Docker targets remain unchanged:
- `make all` - Build all Python Docker images
- `make teal-agents` - Build teal-agents Python image
- `make orchestrator` - Build orchestrator Python images
- `make services` - Build services Python image
- `make clean` - Clean Python Docker images

## Docker Images

### Multi-stage Build Pattern

Both Dockerfiles use multi-stage builds for optimal image sizes:

1. **Build stage**: Uses `golang:1.21-alpine` with build tools
2. **Runtime stage**: Uses minimal `alpine:latest` with only the compiled binary

### Images:
- `teal-agents-go:latest` - Core agent framework
- `go-orchestrators:latest` - Orchestrator services (multi-target)

## Development Workflow

### Initial Setup

```bash
# Verify Go installation (1.21+)
go version

# Download dependencies
go mod download

# Verify module
go mod verify
```

### Development

```bash
# Format code before committing
make go-fmt

# Run static analysis
make go-vet

# Build binaries
make go-build

# Run tests
make go-test

# Build everything and run all checks
make go-all
```

### Docker Development

```bash
# Build Go Docker images
make go-docker-build

# Run agent container
docker run -p 8000:8000 teal-agents-go:latest

# Run assistant orchestrator
docker run -p 8000:8000 go-orchestrators:latest assistant

# Run collaborative orchestrator
docker run -p 8000:8000 go-orchestrators:latest collaborative
```

## Dependency Management

Dependencies are managed through `go.mod` and `go.sum`:

```bash
# Add a new dependency
go get github.com/example/package

# Update dependencies
go get -u ./...

# Tidy up go.mod
go mod tidy

# Verify dependencies
go mod verify
```

## Current Python Build System (Reference)

The existing Python build system uses:
- **Package manager**: `uv` (fast Python package installer)
- **Build backend**: `hatchling`
- **Python version**: 3.12
- **Docker base**: `python:3.12-slim`

This remains unchanged during the Go migration.

## Next Migration Phases

Future phases will involve:
1. Implementing core agent functionality in Go
2. Porting semantic-kernel dependencies
3. Migrating orchestrator logic
4. API endpoint migration
5. Integration testing
6. Production cutover

## Testing

Currently, the Go packages contain only placeholder code. As functionality is migrated:

```bash
# Run specific package tests
go test ./pkg/agents/...

# Run with verbose output
go test -v ./...

# Run with race detection
go test -race ./...

# Generate coverage report
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out
```

## CI/CD Integration

The Go build system is designed to integrate with existing CI/CD pipelines. Add to your workflows:

```yaml
- name: Go Build
  run: make go-all

- name: Go Docker Build
  run: make go-docker-build
```

## Notes

- All Go code follows standard Go project layout conventions
- The `pkg/` directory contains library code that can be imported
- Binaries are built to the `bin/` directory (gitignored)
- Docker images use non-root users for security
- Multi-stage builds minimize image sizes
