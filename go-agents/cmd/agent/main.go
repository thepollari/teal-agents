package main

import (
	"fmt"
	"log"
	"os"
	"os/signal"
	"strings"
	"syscall"

	"github.com/thepollari/teal-agents/go-agents/pkg/agents/sequential"
	"github.com/thepollari/teal-agents/go-agents/pkg/config"
	"github.com/thepollari/teal-agents/go-agents/pkg/kernel"
	"github.com/thepollari/teal-agents/go-agents/pkg/logging"
	"github.com/thepollari/teal-agents/go-agents/pkg/plugins/remote"
	"github.com/thepollari/teal-agents/go-agents/pkg/server"
	"github.com/thepollari/teal-agents/go-agents/pkg/types"
)

func main() {
	appConfig := config.LoadAppConfig()
	logger := logging.InitLogger(appConfig.LogLevel)
	
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
				log.Fatalf("Chat agent not implemented yet")
			default:
				log.Fatalf("Unknown kind: %s", cfg.Kind)
			}
		default:
			log.Fatalf("Unsupported API version: %s", apiVersion)
		}
	case "tealagents":
		log.Fatalf("tealagents not implemented yet")
	default:
		log.Fatalf("Unknown root handler: %s", rootHandler)
	}
	
	if err != nil {
		log.Fatalf("Failed to create handler: %v", err)
	}
	
	srv := server.NewServer(cfg, handler)
	
	go func() {
		log.Printf("Starting server on port 8000...")
		if err := srv.Start(":8000"); err != nil {
			log.Fatalf("Server error: %v", err)
		}
	}()
	
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	
	log.Println("Shutting down server...")
}

func parseAPIVersion(apiVersion string) (string, string, error) {
	parts := strings.Split(apiVersion, "/")
	if len(parts) != 2 {
		return "", "", fmt.Errorf("invalid API version format: %s", apiVersion)
	}
	return parts[0], parts[1], nil
}
