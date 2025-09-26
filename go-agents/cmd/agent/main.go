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
	"github.com/thepollari/teal-agents/go-agents/pkg/server"
	"github.com/thepollari/teal-agents/go-agents/pkg/types"
)

func main() {
	configPath := os.Getenv("TA_SERVICE_CONFIG")
	if configPath == "" {
		log.Fatal("TA_SERVICE_CONFIG environment variable required")
	}
	
	cfg, err := config.LoadFromFile(configPath)
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}
	
	rootHandler, apiVersion, err := parseAPIVersion(cfg.APIVersion)
	if err != nil {
		log.Fatalf("Invalid API version: %v", err)
	}
	
	kernelBuilder := kernel.NewKernelBuilder()
	
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
