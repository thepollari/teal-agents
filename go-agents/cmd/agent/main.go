package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"

	"github.com/thepollari/teal-agents/go-agents/pkg/agents/chat"
	"github.com/thepollari/teal-agents/go-agents/pkg/agents/sequential"
	"github.com/thepollari/teal-agents/go-agents/pkg/config"
	"github.com/thepollari/teal-agents/go-agents/pkg/kernel"
	"github.com/thepollari/teal-agents/go-agents/pkg/logging"
	"github.com/thepollari/teal-agents/go-agents/pkg/plugins/remote"
	"github.com/thepollari/teal-agents/go-agents/pkg/server"
	"github.com/thepollari/teal-agents/go-agents/pkg/telemetry"
	"github.com/thepollari/teal-agents/go-agents/pkg/types"
)

func main() {
	appConfig := config.LoadAppConfig()
	logger := logging.InitLogger(appConfig.LogLevel)
	
	telemetryConfig := telemetry.GetConfigFromEnv()
	err := telemetry.Initialize(telemetryConfig)
	if err != nil {
		logger.Error("Failed to initialize telemetry", "error", err.Error())
		log.Fatalf("Failed to initialize telemetry: %v", err)
	}
	logger.Info("Telemetry initialized", "enabled", telemetryConfig.Enabled, "service", telemetryConfig.ServiceName)
	
	configPath := os.Getenv("TA_SERVICE_CONFIG")
	if configPath == "" && len(os.Args) >= 2 {
		configPath = os.Args[1]
	}
	if configPath == "" {
		logger.Error("Missing configuration file")
		log.Fatal("Usage: agent <config-file> or set TA_SERVICE_CONFIG environment variable")
	}
	
	logger.Info("Starting Teal Agents", "config_path", configPath, "log_level", appConfig.LogLevel)
	
	cfg, err := config.LoadFromFile(configPath)
	if err != nil {
		logger.Error("Failed to load configuration", "error", err.Error())
		log.Fatalf("Failed to load config: %v", err)
	}
	
	err = config.ValidateConfig(cfg)
	if err != nil {
		logger.Error("Configuration validation failed", "error", err.Error())
		log.Fatalf("Configuration validation failed: %v", err)
	}
	
	rootHandler, apiVersion, err := parseAPIVersion(cfg.APIVersion)
	if err != nil {
		log.Fatalf("Invalid API version: %v", err)
	}
	
	kernelBuilder := kernel.NewKernelBuilder()
	
	pluginCatalog, err := remote.NewPluginCatalog("examples/remote_plugins/catalog.yaml")
	if err != nil {
		logger.Warn("Failed to load plugin catalog", "error", err.Error())
	} else {
		kernelBuilder.SetPluginCatalog(pluginCatalog)
		logger.Info("Plugin catalog loaded successfully")
	}
	
	var handler types.Handler
	
	switch rootHandler {
	case "skagents":
		switch apiVersion {
		case "v1":
			switch cfg.Kind {
			case "Sequential":
				handler, err = sequential.NewSequentialAgent(cfg, kernelBuilder)
			case "Chat":
				handler, err = chat.NewChatAgent(cfg, kernelBuilder)
			default:
				log.Fatalf("Unknown kind: %s", cfg.Kind)
			}
		default:
			log.Fatalf("Unsupported API version: %s", apiVersion)
		}
	case "tealagents":
		switch apiVersion {
		case "v1alpha1":
			handler, err = sequential.NewSequentialAgent(cfg, kernelBuilder)
		default:
			log.Fatalf("Unsupported API version: %s", apiVersion)
		}
	default:
		log.Fatalf("Unknown root handler: %s", rootHandler)
	}
	
	if err != nil {
		log.Fatalf("Failed to create handler: %v", err)
	}
	
	srv := server.NewServer(cfg, handler)
	
	port := fmt.Sprintf("%d", appConfig.Port)
	logger.Info("Using port from config", "port", port)
	
	httpServer := &http.Server{
		Addr:    ":" + port,
		Handler: srv,
	}

	go func() {
		logger.Info("Starting server", "address", httpServer.Addr, "service", cfg.ServiceName)
		if err := httpServer.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Error("Server error", "error", err.Error())
			log.Fatalf("Server error: %v", err)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	logger.Info("Shutting down server...")
	if err := httpServer.Shutdown(ctx); err != nil {
		logger.Error("Server forced to shutdown", "error", err.Error())
		log.Fatalf("Server forced to shutdown: %v", err)
	}

	logger.Info("Server exited gracefully")
}

func parseAPIVersion(apiVersion string) (string, string, error) {
	parts := strings.Split(apiVersion, "/")
	if len(parts) != 2 {
		return "", "", fmt.Errorf("invalid API version format: %s", apiVersion)
	}
	return parts[0], parts[1], nil
}
