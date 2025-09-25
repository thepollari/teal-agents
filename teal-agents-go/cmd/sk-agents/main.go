package main

import (
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/thepollari/teal-agents-go/internal/handlers"
	"github.com/thepollari/teal-agents-go/pkg/kernel"
	"github.com/thepollari/teal-agents-go/pkg/types"
	"gopkg.in/yaml.v3"
)

func main() {
	config, err := loadConfig()
	if err != nil {
		log.Fatalf("Failed to load configuration: %v", err)
	}

	appConfig := kernel.NewSimpleAppConfig()
	appConfig.LoadFromEnvironment()

	app := setupApplication(config, appConfig)

	port := os.Getenv("PORT")
	if port == "" {
		port = "8000"
	}

	log.Printf("Starting teal-agents-go server on port %s", port)
	log.Printf("Agent: %s v%v", getStringValue(config.Name), config.Version)
	log.Printf("Description: %s", getStringValue(config.Description))

	if err := http.ListenAndServe(":"+port, app); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}

func loadConfig() (*types.BaseConfig, error) {
	configPath := os.Getenv("TA_CONFIG_PATH")
	if configPath == "" {
		configPath = "config.yaml"
	}

	if _, err := os.Stat(configPath); err == nil {
		return loadConfigFromFile(configPath)
	}

	log.Printf("Configuration file not found, using default configuration")
	return getDefaultConfig(), nil
}

func loadConfigFromFile(path string) (*types.BaseConfig, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read config file: %w", err)
	}

	var config types.BaseConfig
	if err := yaml.Unmarshal(data, &config); err != nil {
		return nil, fmt.Errorf("failed to parse config file: %w", err)
	}

	return &config, nil
}

func getDefaultConfig() *types.BaseConfig {
	name := "teal-agents-go"
	version := "1.0.0"
	description := "Golang implementation of teal-agents with semantic kernel"
	inputType := "BaseInput"
	outputType := "InvokeResponse"

	return &types.BaseConfig{
		APIVersion:  "v1",
		Name:        &name,
		Version:     version,
		Description: &description,
		InputType:   &inputType,
		OutputType:  &outputType,
		Metadata: &types.ConfigMetadata{
			Description: description,
			Skills: []types.ConfigSkill{
				{
					ID:          "chat",
					Name:        "Chat Completion",
					Description: "Provides conversational AI capabilities",
					Tags:        []string{"chat", "ai", "conversation"},
					Examples:    []string{"Hello, how can I help you?"},
					InputModes:  []string{"text"},
					OutputModes: []string{"text"},
				},
			},
		},
		Spec: map[string]interface{}{
			"model_name": "gpt-3.5-turbo",
			"service_id": "openai",
			"settings": map[string]interface{}{
				"temperature": 0.7,
				"max_tokens":  1000,
			},
		},
	}
}

func setupApplication(config *types.BaseConfig, appConfig types.AppConfig) http.Handler {
	routes := handlers.NewRoutes(appConfig)

	name := getStringValue(config.Name)
	version := fmt.Sprintf("%v", config.Version)
	description := getStringValue(config.Description)

	return routes.GetRestRoutes(name, version, description, *config)
}

func getStringValue(s *string) string {
	if s == nil {
		return ""
	}
	return *s
}
