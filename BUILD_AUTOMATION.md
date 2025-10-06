# Teal Agents Framework - Build Automation Guide

## Overview

The Teal Agents Framework uses a comprehensive build automation system based on Makefiles, Docker, and GitHub Actions. This guide documents all available build targets, development workflows, and deployment processes across the framework components.

## Repository Build Structure

The framework consists of multiple components, each with its own build configuration:

```
teal-agents/
├── Makefile                                    # Root build targets
├── shared/ska_utils/Makefile                   # Shared utilities build
├── src/sk-agents/Makefile                      # Core framework build
├── src/orchestrators/assistant-orchestrator/
│   ├── orchestrator/Makefile                   # AO orchestrator build
│   ├── services/Makefile                       # AO services build
│   └── example/Makefile                        # Development environment
└── src/orchestrators/collab-orchestrator/
    └── orchestrator/Makefile                   # CO orchestrator build
```

## Root Makefile Targets

### Primary Build Targets

```bash
# Build all components
make all

# Build individual components
make teal-agents    # Core agent framework
make orchestrator   # Assistant and Collaboration orchestrators
make services       # Assistant orchestrator services
```

### Docker Image Builds

The root Makefile builds the following Docker images:

| Target | Image | Dockerfile | Description |
|--------|-------|------------|-------------|
| `teal-agents` | `teal-agents:latest` | `teal-agents.Dockerfile` | Core agent framework |
| `orchestrator` | `ao:latest` | `ao.Dockerfile` | Assistant orchestrator |
| `orchestrator` | `co:latest` | `co.Dockerfile` | Collaboration orchestrator |
| `services` | `ao-services:latest` | `ao-services.Dockerfile` | Assistant orchestrator services |

### Cleanup Targets

```bash
# Remove all built Docker images
make clean
```

### Build Flags

Set `DOCKER_FLAGS` environment variable to pass additional flags to Docker builds:

```bash
# Build with no cache
DOCKER_FLAGS="--no-cache" make all

# Build with specific platform
DOCKER_FLAGS="--platform linux/amd64" make all
```

## Component-Specific Build Targets

### Shared Utilities (ska_utils)

```bash
cd shared/ska_utils

# Development setup
make sync          # Install dependencies with uv
make lint          # Run ruff linting
make mypy          # Run type checking
make test          # Run pytest
make coverage      # Run tests with coverage report

# Package building
make build         # Build Python wheel
make clean         # Clean build artifacts
```

### Core Framework (sk-agents)

```bash
cd src/sk-agents

# Development workflow
make sync          # Install dependencies
make lint          # Code linting with ruff
make mypy          # Type checking
make test          # Run unit tests
make coverage      # Test coverage analysis
make build-docs    # Build documentation site

# Package management
make build         # Build Python package
make clean         # Clean artifacts
```

### Assistant Orchestrator

```bash
cd src/orchestrators/assistant-orchestrator/orchestrator

# Standard development targets
make sync          # Dependency installation
make lint          # Code quality checks
make mypy          # Type validation
make test          # Unit test execution
make coverage      # Coverage reporting
make build         # Package building
```

### Assistant Orchestrator Services

```bash
cd src/orchestrators/assistant-orchestrator/services

# Service development workflow
make sync          # Environment setup
make lint          # Linting checks
make test          # Service testing
make coverage      # Test coverage
make build         # Service packaging
```

### Collaboration Orchestrator

```bash
cd src/orchestrators/collab-orchestrator/orchestrator

# Orchestrator development
make sync          # Setup dependencies
make lint          # Quality assurance
make mypy          # Type safety
make test          # Comprehensive testing
make coverage      # Coverage analysis
```

## Development Environment Setup

### Assistant Orchestrator Example Environment

The most comprehensive Makefile is located at `src/orchestrators/assistant-orchestrator/example/Makefile` and provides a complete development environment:

#### Environment Management

```bash
cd src/orchestrators/assistant-orchestrator/example

# Environment file setup
make copy-envs                    # Copy .env.example files to .env files
make prompt-api-keys-macos        # Interactive API key setup (macOS)
make prompt-api-keys-bash         # Interactive API key setup (Linux)
make remove-env-files             # Clean up environment files
```

#### Service Orchestration

```bash
# Full system deployment
make all-up                       # Start all services (AO + Services)
make all-down                     # Stop all services
make all-down-clean-images        # Stop services and remove images

# Development debugging
make debug-ao-up                  # Start services only (debug AO locally)
make debug-ao-down                # Stop services for AO debugging
make debug-services-up            # Start AO only (debug services locally)
make debug-services-down          # Stop AO for services debugging

# Dependencies only
make dependencies-up              # Start supporting services (Redis, Kong, etc.)
make dependencies-down            # Stop supporting services
```

#### Test Agent Development

```bash
# Test agent deployment
make test-agent-up                # Deploy with test agent
make test-agent-down              # Stop test agent deployment
make debug-test-agent-up          # Debug test agent locally
make debug-test-agent-down        # Stop test agent debugging
```

#### Complete Environment Workflows

```bash
# Full setup workflows
make build-full-example-system-macos    # Complete setup for macOS
make build-full-example-system-bash     # Complete setup for Linux

# Environment refresh
make refresh-env-macos                  # Rebuild entire environment (macOS)
make refresh-env-bash                   # Rebuild entire environment (Linux)

# Code deployment
make deploy-updated-code                # Deploy code changes to running system
```

#### Database Management

```bash
# Local database cleanup
make remove-local-db              # Remove local DynamoDB data
```

## GitHub Actions CI/CD

### Automated Build Pipeline

The framework uses GitHub Actions for automated building and deployment:

#### Build Workflow (`.github/workflows/build.yaml`)

**Triggers:**
- Push to `main` branch
- Changes to Dockerfiles or source code
- Manual workflow dispatch

**Process:**
1. **Change Detection**: Identifies which components changed
2. **Version Bumping**: Automatically increments development versions
3. **Docker Builds**: Builds and pushes images to GitHub Container Registry
4. **Registry Push**: Publishes to `ghcr.io/teal-agents/`

**Built Images:**
- `ghcr.io/teal-agents/teal-agents:latest`
- `ghcr.io/teal-agents/ao:latest`
- `ghcr.io/teal-agents/ao-services:latest`
- `ghcr.io/teal-agents/co:latest`

#### Release Workflow (`.github/workflows/release.yaml`)

**Triggers:**
- Manual workflow dispatch only

**Process:**
1. **Version Release**: Converts development versions to release versions
2. **Git Tagging**: Creates release tags
3. **Package Building**: Builds Python wheels for ska-utils and sk-agents
4. **Docker Publishing**: Publishes release-tagged Docker images
5. **GitHub Release**: Creates GitHub release with artifacts
6. **Next Development**: Bumps to next development version

#### Quality Assurance (`.github/workflows/check.yaml`)

**Automated Checks:**
- **Linting**: Runs `make lint` on all components
- **Type Checking**: Executes `make mypy` on ska-utils
- **Testing**: Runs `make coverage` on all components
- **Documentation**: Builds documentation with `make build-docs`

## Version Management

### Automated Versioning Strategy

The framework uses `hatch` for version management with the following patterns:

- **Development versions**: `X.Y.Z.devN` (e.g., `1.2.3.dev4`)
- **Release versions**: `X.Y.Z` (e.g., `1.2.3`)

### Version Bumping Commands

```bash
# Development version bump (CI)
uv run hatch version dev

# Release version (removes .dev suffix)
uv run hatch version release

# Next patch development version
uv run hatch version patch,dev
```

### Component Version Synchronization

All components maintain synchronized versioning:
- `shared/ska_utils` - Base version reference
- `src/sk-agents` - Core framework version
- `src/orchestrators/assistant-orchestrator/orchestrator` - AO version
- `src/orchestrators/assistant-orchestrator/services` - AO services version
- `src/orchestrators/collab-orchestrator/orchestrator` - CO version

## Docker Configuration

### Multi-Stage Builds

All Dockerfiles use multi-stage builds for optimization:

1. **Base Stage**: Python environment setup
2. **Dependencies Stage**: Package installation
3. **Application Stage**: Code copying and configuration
4. **Runtime Stage**: Final optimized image

### Build Context

All Docker builds use the repository root as build context to access:
- Shared utilities (`shared/ska_utils`)
- Common configuration files
- Cross-component dependencies

### Registry Configuration

**Development Images:**
- Registry: `ghcr.io/teal-agents/`
- Tags: `latest`, `<version>`
- Authentication: GitHub token

**Local Development:**
- Images tagged as `<component>:latest`
- No registry push required

## Environment Variables

### Build-Time Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `DOCKER_FLAGS` | Additional Docker build flags | None |
| `KONG_ALT` | Alternative Kong configuration | Default config |
| `AO_ALT` | Alternative AO configuration | Default config |

### Runtime Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `TA_API_KEY` | Teal Agents API key | Yes |
| `OPENAI_API_KEY` | OpenAI API access | Conditional |
| `ANTHROPIC_API_KEY` | Anthropic API access | Conditional |
| `GOOGLE_API_KEY` | Google AI API access | Conditional |

## Development Workflows

### New Developer Setup

```bash
# 1. Clone repository
git clone https://github.com/thepollari/teal-agents.git
cd teal-agents

# 2. Build all components
make all

# 3. Set up development environment
cd src/orchestrators/assistant-orchestrator/example
make build-full-example-system-bash  # or -macos

# 4. Verify setup
make dependencies-up
# Test individual components
```

### Code Change Deployment

```bash
# After making code changes
cd src/orchestrators/assistant-orchestrator/example
make deploy-updated-code
```

### Component Development

```bash
# Working on specific component
cd src/sk-agents  # or other component directory

# Development cycle
make sync          # Install dependencies
make lint          # Check code quality
make test          # Run tests
make coverage      # Verify coverage

# Build and test
make build
```

### Debugging Workflows

```bash
# Debug assistant orchestrator
make debug-ao-up
# Run AO locally with debugger
# Services run in containers

# Debug services
make debug-services-up
# Run services locally with debugger
# AO runs in container
```

## Troubleshooting

### Common Build Issues

**Docker build failures:**
```bash
# Clear Docker cache
docker builder prune -a

# Rebuild with no cache
DOCKER_FLAGS="--no-cache" make all
```

**Dependency conflicts:**
```bash
# Clean and reinstall
make clean
make sync
```

**Environment setup issues:**
```bash
# Reset environment
make refresh-env-bash  # or -macos
```

### Build Performance

**Parallel builds:**
```bash
# Use Docker BuildKit for faster builds
export DOCKER_BUILDKIT=1
make all
```

**Selective building:**
```bash
# Build only changed components
make teal-agents  # Instead of make all
```

### Version Conflicts

**Reset to clean state:**
```bash
# Clean all build artifacts
find . -name "dist" -type d -exec rm -rf {} +
find . -name "*.egg-info" -type d -exec rm -rf {} +
make clean
```

## Best Practices

### Development

1. **Always run `make sync`** before development work
2. **Use `make lint`** before committing changes
3. **Run `make coverage`** to ensure test coverage
4. **Test locally** with `make debug-*-up` targets

### CI/CD

1. **Let CI handle versioning** - don't manually bump versions
2. **Use draft PRs** for work-in-progress
3. **Monitor build logs** for early issue detection
4. **Test Docker images** locally before pushing

### Environment Management

1. **Use example Makefiles** for consistent environments
2. **Keep API keys secure** - never commit to repository
3. **Clean up regularly** with cleanup targets
4. **Document custom configurations** in team documentation

## Integration with IDEs

### VS Code

Add to `.vscode/tasks.json`:
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Build All",
            "type": "shell",
            "command": "make all",
            "group": "build"
        },
        {
            "label": "Run Tests",
            "type": "shell",
            "command": "make test",
            "group": "test"
        }
    ]
}
```

### PyCharm

Configure external tools for common make targets in Settings > Tools > External Tools.

## Advanced Usage

### Custom Build Configurations

Create local `Makefile.local` for custom targets:
```makefile
include Makefile

custom-build:
	@echo "Running custom build..."
	DOCKER_FLAGS="--platform linux/amd64" make all
```

### Multi-Platform Builds

```bash
# Build for multiple architectures
DOCKER_FLAGS="--platform linux/amd64,linux/arm64" make all
```

### Build Caching

```bash
# Use BuildKit cache mounts
export DOCKER_BUILDKIT=1
make all
```

This comprehensive build automation system ensures consistent, reliable builds across all development and production environments while providing flexibility for various development workflows.
