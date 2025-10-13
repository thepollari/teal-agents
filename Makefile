.PHONY: all teal-agents orchestrator services go-build go-test go-clean go-fmt go-vet go-lint go-docker-build go-all

all : | teal-agents orchestrator services

teal-agents :
	@echo "Building Teal Agents..."
	@docker build ${DOCKER_FLAGS} -t teal-agents:latest -f teal-agents.Dockerfile --progress=plain .

orchestrator :
	@echo "Building Orchestrators..."
	@docker build ${DOCKER_FLAGS} -t ao:latest -f ao.Dockerfile --progress=plain .
	@docker build ${DOCKER_FLAGS} -t co:latest -f co.Dockerfile --progress=plain .

services :
	@echo "Building Services..."
	@docker build ${DOCKER_FLAGS} -t ao-services:latest -f ao-services.Dockerfile --progress=plain .

clean:
	@echo "Cleaning up..."
	@docker rmi teal-agents:latest || true
	@docker rmi ao:latest || true
	@docker rmi ao-services:latest || true

go-build:
	@echo "Building Go binaries..."
	@mkdir -p bin
	@go build -o bin/agent ./pkg/agents/...
	@go build -o bin/assistant-orchestrator ./pkg/orchestrators/assistant/...
	@go build -o bin/collaborative-orchestrator ./pkg/orchestrators/collaborative/...
	@echo "Go build complete. Binaries in bin/"

go-test:
	@echo "Running Go tests..."
	@go test -v -race -coverprofile=coverage.out ./...
	@go tool cover -html=coverage.out -o coverage.html
	@echo "Test coverage report generated: coverage.html"

go-clean:
	@echo "Cleaning Go build artifacts..."
	@rm -rf bin/
	@rm -f coverage.out coverage.html
	@go clean -cache -testcache -modcache

go-fmt:
	@echo "Formatting Go code..."
	@go fmt ./...

go-vet:
	@echo "Running go vet..."
	@go vet ./...

go-lint:
	@echo "Running golangci-lint..."
	@if command -v golangci-lint >/dev/null 2>&1; then \
		golangci-lint run ./...; \
	else \
		echo "golangci-lint not installed. Install with: go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest"; \
	fi

go-docker-build:
	@echo "Building Go Docker images..."
	@docker build ${DOCKER_FLAGS} -t teal-agents-go:latest -f go-agents.Dockerfile --progress=plain .
	@docker build ${DOCKER_FLAGS} -t go-orchestrators:latest -f go-orchestrators.Dockerfile --progress=plain .

go-test-config:
	@echo "Testing configuration loading..."
	@go test -v ./pkg/config/...

go-test-integration:
	@echo "Running integration tests with real config files..."
	@go test -v -tags=integration ./pkg/config/loader/tests/...

go-all: go-fmt go-vet go-build go-test

.DEFAULT_GOAL := all
