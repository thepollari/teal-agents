.PHONY: build test lint clean run-server run-tests benchmark

# Build targets
build:
	go build -o bin/agent-server ./cmd/agent-server
	go build -o bin/config-validator ./cmd/config-validator
	go build -o bin/benchmark ./cmd/benchmark

# Testing targets
test:
	go test ./... -v

test-race:
	go test -race ./...

test-cover:
	go test -cover ./...

benchmark:
	go test -bench=. ./tests/benchmarks/

# Linting and formatting
lint:
	golangci-lint run

fmt:
	go fmt ./...

# Development targets
run-server:
	go run ./cmd/agent-server

run-tests: test

# Cleanup
clean:
	rm -rf bin/

# Docker targets
docker-build:
	docker build -t teal-agents-go .

# Dependencies
deps:
	go mod download
	go mod tidy
