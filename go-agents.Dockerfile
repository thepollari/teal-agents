FROM golang:1.21-alpine AS builder

RUN apk add --no-cache git make

WORKDIR /build

COPY go.mod go.sum ./
RUN go mod download

COPY pkg/ ./pkg/

RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o agent ./pkg/agents/...

FROM alpine:latest

RUN apk --no-cache add ca-certificates

RUN addgroup -g 1000 skagent && \
    adduser -D -u 1000 -G skagent skagent

WORKDIR /app

COPY --from=builder /build/agent .

RUN chown -R skagent:skagent /app

USER skagent

EXPOSE 8000

ENTRYPOINT ["./agent"]
