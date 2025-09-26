package config

import (
	"fmt"
	"os"
	"strings"
	
	"gopkg.in/yaml.v3"
)

type BaseConfig struct {
	APIVersion  string      `yaml:"apiVersion"`
	Kind        string      `yaml:"kind"`
	Description string      `yaml:"description"`
	ServiceName string      `yaml:"service_name"`
	Version     string      `yaml:"version"`
	InputType   string      `yaml:"input_type"`
	OutputType  string      `yaml:"output_type,omitempty"`
	Spec        SpecConfig  `yaml:"spec"`
}

type SpecConfig struct {
	Agents []AgentConfig `yaml:"agents"`
	Tasks  []TaskConfig  `yaml:"tasks"`
}

type AgentConfig struct {
	Name          string   `yaml:"name"`
	Role          string   `yaml:"role,omitempty"`
	Model         string   `yaml:"model"`
	Temperature   *float64 `yaml:"temperature,omitempty"`
	SystemPrompt  string   `yaml:"system_prompt"`
	Plugins       []string `yaml:"plugins,omitempty"`
	RemotePlugins []string `yaml:"remote_plugins,omitempty"`
}

type TaskConfig struct {
	Name         string `yaml:"name"`
	TaskNo       int    `yaml:"task_no"`
	Description  string `yaml:"description"`
	Instructions string `yaml:"instructions"`
	Agent        string `yaml:"agent"`
}

type AppConfig struct {
	OpenAIAPIKey string `yaml:"openai_api_key,omitempty"`
	GeminiAPIKey string `yaml:"gemini_api_key,omitempty"`
	LogLevel     string `yaml:"log_level,omitempty"`
	Port         int    `yaml:"port,omitempty"`
}

func LoadFromFile(path string) (*BaseConfig, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read config file: %w", err)
	}
	
	var config BaseConfig
	err = yaml.Unmarshal(data, &config)
	if err != nil {
		return nil, fmt.Errorf("failed to parse config: %w", err)
	}
	
	return &config, nil
}

func ParseAPIVersion(apiVersion string) (string, string, error) {
	parts := strings.Split(apiVersion, "/")
	if len(parts) != 2 {
		return "", "", fmt.Errorf("invalid API version format: %s", apiVersion)
	}
	return parts[0], parts[1], nil
}
