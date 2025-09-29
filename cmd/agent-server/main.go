package main

import (
	"context"
	"flag"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/merck-gen/teal-agents-go/internal/gemini"
	"github.com/merck-gen/teal-agents-go/internal/handlers"
	"github.com/merck-gen/teal-agents-go/internal/university"
	"github.com/merck-gen/teal-agents-go/pkg/api"
	"github.com/merck-gen/teal-agents-go/pkg/config"
	"github.com/merck-gen/teal-agents-go/pkg/kernel"
	"github.com/merck-gen/teal-agents-go/pkg/plugins"
	"github.com/merck-gen/teal-agents-go/pkg/telemetry"
)

func main() {
	var (
		configPath = flag.String("config", "", "Path to agent configuration file")
		host       = flag.String("host", "0.0.0.0", "Server host")
		port       = flag.Int("port", 8000, "Server port")
		logLevel   = flag.String("log-level", "info", "Log level (debug, info, warn, error, fatal)")
	)
	flag.Parse()

	logger := telemetry.NewLogger(telemetry.LoggerConfig{
		Level:  telemetry.LogLevel(*logLevel),
		Format: "text",
		Output: "stdout",
	})

	logger.Info("Starting Teal Agents Go server...")

	if *configPath == "" {
		*configPath = os.Getenv("TA_SERVICE_CONFIG")
		if *configPath == "" {
			logger.Fatal("Configuration path must be provided via --config flag or TA_SERVICE_CONFIG environment variable")
		}
	}

	configLoader := config.NewConfigLoader()
	agentConfig, err := configLoader.LoadAgent(*configPath)
	if err != nil {
		logger.Fatalf("Failed to load configuration: %v", err)
	}

	if err := configLoader.ValidateConfig(agentConfig); err != nil {
		logger.Fatalf("Configuration validation failed: %v", err)
	}

	logger.Infof("Loaded configuration for agent: %s (version: %v)", agentConfig.Name, agentConfig.Version)

	k := kernel.NewKernel()

	pluginRegistry := plugins.NewRegistry()

	if agentConfig.Spec != nil && len(agentConfig.Spec.Agents) > 0 {
		for _, agent := range agentConfig.Spec.Agents {
			for _, pluginName := range agent.Plugins {
				if pluginName == "UniversityPlugin" {
					universityPlugin := university.NewUniversityPlugin()
					if err := k.RegisterPlugin(universityPlugin); err != nil {
						logger.Fatalf("Failed to register University plugin: %v", err)
					}
					if err := pluginRegistry.Register(universityPlugin); err != nil {
						logger.Fatalf("Failed to register University plugin in registry: %v", err)
					}
					logger.Info("Registered University plugin")
				}
			}
		}
	}

	var geminiClient *gemini.Client
	if agentConfig.Spec != nil && len(agentConfig.Spec.Agents) > 0 {
		model := agentConfig.Spec.Agents[0].Model
		if model != "" {
			var err error
			geminiClient, err = gemini.NewClient(model)
			if err != nil {
				logger.Fatalf("Failed to create Gemini client: %v", err)
			}
			logger.Infof("Initialized Gemini client with model: %s", model)
		}
	}

	server := api.NewServer(agentConfig, k, logger)

	if geminiClient != nil {
		universityHandler := handlers.NewUniversityHandler(k, geminiClient, logger, agentConfig)
		
		server.RegisterHandler("invoke", handlers.NewHandlerAdapter(universityHandler.HandleInvoke))
		server.RegisterHandler("invoke-stream", handlers.NewHandlerAdapter(universityHandler.HandleInvokeStream))
		server.RegisterHandler("agent-card", handlers.NewHandlerAdapter(universityHandler.HandleAgentCard))
		server.RegisterHandler("a2a-invoke", handlers.NewHandlerAdapter(universityHandler.HandleA2AInvoke))
		server.RegisterHandler("a2a-agent-card", handlers.NewHandlerAdapter(universityHandler.HandleA2AAgentCard))
		
		logger.Info("Registered University handlers")
	}

	serverConfig := api.ServerConfig{
		Host:         *host,
		Port:         *port,
		ReadTimeout:  30 * time.Second,
		WriteTimeout: 30 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		<-sigChan
		logger.Info("Received shutdown signal")
		cancel()
	}()

	if err := server.StartWithContext(ctx, serverConfig); err != nil {
		logger.Fatalf("Server failed: %v", err)
	}

	logger.Info("Server shutdown complete")
}
