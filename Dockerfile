# Build stage
FROM golang:1.24-alpine AS builder

WORKDIR /app

# Copy go.mod and go.sum files
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy the source code
COPY . .

# Build the application
RUN CGO_ENABLED=0 GOOS=linux go build -o /app/bin/agent-server ./cmd/agent-server

# Final stage
FROM alpine:latest

WORKDIR /app

# Copy the binary from the builder stage
COPY --from=builder /app/bin/agent-server /app/agent-server

# Copy configuration files
COPY configs /app/configs

# Create a non-root user to run the application
RUN adduser -D -g '' appuser
USER appuser

# Set environment variables
ENV GIN_MODE=release

# Expose the port
EXPOSE 8000

# Set the entrypoint
ENTRYPOINT ["/app/agent-server"]
CMD ["--config", "/app/configs/agents/university-agent.yaml", "--host", "0.0.0.0", "--port", "8000"]
