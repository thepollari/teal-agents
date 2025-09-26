package logging

import (
	"context"
	"fmt"
	"log/slog"
	"os"
)

var defaultLogger *slog.Logger

func init() {
	defaultLogger = slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelInfo,
	}))
}

func GetLogger() *slog.Logger {
	return defaultLogger
}

func SetLogger(logger *slog.Logger) {
	defaultLogger = logger
}

func InitLogger(level string) *slog.Logger {
	var logLevel slog.Level
	switch level {
	case "debug":
		logLevel = slog.LevelDebug
	case "info":
		logLevel = slog.LevelInfo
	case "warn":
		logLevel = slog.LevelWarn
	case "error":
		logLevel = slog.LevelError
	default:
		logLevel = slog.LevelInfo
	}

	logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
		Level: logLevel,
	}))
	
	SetLogger(logger)
	return logger
}

func WithContext(ctx context.Context) *slog.Logger {
	return defaultLogger.With(
		"request_id", getRequestID(ctx),
		"trace_id", getTraceID(ctx),
	)
}

func LogInvoke(ctx context.Context, pluginName, functionName string, args map[string]interface{}) {
	WithContext(ctx).Info("Function invocation started",
		"plugin", pluginName,
		"function", functionName,
		"args", args,
	)
}

func LogInvokeResult(ctx context.Context, pluginName, functionName string, result interface{}, err error) {
	logger := WithContext(ctx)
	if err != nil {
		logger.Error("Function invocation failed",
			"plugin", pluginName,
			"function", functionName,
			"error", err.Error(),
		)
	} else {
		logger.Info("Function invocation completed",
			"plugin", pluginName,
			"function", functionName,
			"result_type", getResultType(result),
		)
	}
}

func LogHTTPRequest(ctx context.Context, method, path string, statusCode int, duration string) {
	WithContext(ctx).Info("HTTP request completed",
		"method", method,
		"path", path,
		"status_code", statusCode,
		"duration", duration,
	)
}

func LogPluginLoad(ctx context.Context, pluginName string, err error) {
	logger := WithContext(ctx)
	if err != nil {
		logger.Error("Plugin loading failed",
			"plugin", pluginName,
			"error", err.Error(),
		)
	} else {
		logger.Info("Plugin loaded successfully",
			"plugin", pluginName,
		)
	}
}

func getRequestID(ctx context.Context) string {
	if requestID := ctx.Value("request_id"); requestID != nil {
		return requestID.(string)
	}
	return ""
}

func getTraceID(ctx context.Context) string {
	if traceID := ctx.Value("trace_id"); traceID != nil {
		return traceID.(string)
	}
	return ""
}

func getResultType(result interface{}) string {
	if result == nil {
		return "nil"
	}
	return fmt.Sprintf("%T", result)
}
