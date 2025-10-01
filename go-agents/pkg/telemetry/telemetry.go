package telemetry

import (
	"context"
	"fmt"
	"os"
	"time"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/codes"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp"
	"go.opentelemetry.io/otel/propagation"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.26.0"
	"go.opentelemetry.io/otel/trace"
)

var (
	tracer trace.Tracer
)

type TelemetryConfig struct {
	ServiceName    string
	ServiceVersion string
	Environment    string
	OTLPEndpoint   string
	Enabled        bool
}

func Initialize(config TelemetryConfig) error {
	if !config.Enabled {
		otel.SetTracerProvider(trace.NewNoopTracerProvider())
		tracer = otel.Tracer("noop")
		return nil
	}

	ctx := context.Background()

	res, err := resource.New(ctx,
		resource.WithAttributes(
			semconv.ServiceName(config.ServiceName),
			semconv.ServiceVersion(config.ServiceVersion),
			semconv.DeploymentEnvironment(config.Environment),
		),
	)
	if err != nil {
		return fmt.Errorf("failed to create resource: %w", err)
	}

	var exporter sdktrace.SpanExporter
	if config.OTLPEndpoint != "" {
		exporter, err = otlptracehttp.New(ctx,
			otlptracehttp.WithEndpoint(config.OTLPEndpoint),
		)
		if err != nil {
			return fmt.Errorf("failed to create OTLP exporter: %w", err)
		}
	} else {
		exporter = &noopExporter{}
	}

	tp := sdktrace.NewTracerProvider(
		sdktrace.WithBatcher(exporter),
		sdktrace.WithResource(res),
		sdktrace.WithSampler(sdktrace.AlwaysSample()),
	)

	otel.SetTracerProvider(tp)
	otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(
		propagation.TraceContext{},
		propagation.Baggage{},
	))

	tracer = otel.Tracer("teal-agents")
	return nil
}

func GetTracer() trace.Tracer {
	if tracer == nil {
		tracer = otel.Tracer("teal-agents")
	}
	return tracer
}

func StartSpan(ctx context.Context, name string, opts ...trace.SpanStartOption) (context.Context, trace.Span) {
	return GetTracer().Start(ctx, name, opts...)
}

func AddSpanAttributes(span trace.Span, attrs ...attribute.KeyValue) {
	span.SetAttributes(attrs...)
}

func RecordError(span trace.Span, err error) {
	if err != nil {
		span.RecordError(err)
		span.SetStatus(codes.Error, err.Error())
	}
}

func GetConfigFromEnv() TelemetryConfig {
	enabled := os.Getenv("OTEL_ENABLED") == "true"
	if os.Getenv("OTEL_SDK_DISABLED") == "true" {
		enabled = false
	}

	return TelemetryConfig{
		ServiceName:    getEnvOrDefault("OTEL_SERVICE_NAME", "teal-agents"),
		ServiceVersion: getEnvOrDefault("OTEL_SERVICE_VERSION", "0.1.0"),
		Environment:    getEnvOrDefault("OTEL_ENVIRONMENT", "development"),
		OTLPEndpoint:   os.Getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
		Enabled:        enabled,
	}
}

func getEnvOrDefault(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

type noopExporter struct{}

func (e *noopExporter) ExportSpans(ctx context.Context, spans []sdktrace.ReadOnlySpan) error {
	return nil
}

func (e *noopExporter) Shutdown(ctx context.Context) error {
	return nil
}

func InstrumentAgentInvocation(ctx context.Context, agentName, model string) (context.Context, trace.Span) {
	return StartSpan(ctx, "agent.invoke",
		trace.WithAttributes(
			attribute.String("agent.name", agentName),
			attribute.String("agent.model", model),
			attribute.String("component", "agent"),
		),
	)
}

func InstrumentPluginExecution(ctx context.Context, pluginName, functionName string) (context.Context, trace.Span) {
	return StartSpan(ctx, "plugin.execute",
		trace.WithAttributes(
			attribute.String("plugin.name", pluginName),
			attribute.String("plugin.function", functionName),
			attribute.String("component", "plugin"),
		),
	)
}

func InstrumentHTTPRequest(ctx context.Context, method, path string) (context.Context, trace.Span) {
	return StartSpan(ctx, fmt.Sprintf("HTTP %s %s", method, path),
		trace.WithAttributes(
			attribute.String("http.method", method),
			attribute.String("http.route", path),
			attribute.String("component", "http"),
		),
	)
}

func RecordTokenUsage(span trace.Span, promptTokens, completionTokens, totalTokens int) {
	AddSpanAttributes(span,
		attribute.Int("llm.usage.prompt_tokens", promptTokens),
		attribute.Int("llm.usage.completion_tokens", completionTokens),
		attribute.Int("llm.usage.total_tokens", totalTokens),
	)
}

func RecordResponseTime(span trace.Span, duration time.Duration) {
	AddSpanAttributes(span,
		attribute.Float64("response.duration_ms", float64(duration.Nanoseconds())/1e6),
	)
}
