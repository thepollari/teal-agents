package config

import (
	"fmt"
	"os"
	"path/filepath"

	"gopkg.in/yaml.v3"
)

type ConfigLoader interface {
	LoadAgent(path string) (*BaseConfig, error)
	ValidateConfig(config *BaseConfig) error
}

type DefaultConfigLoader struct{}

func NewConfigLoader() *DefaultConfigLoader {
	return &DefaultConfigLoader{}
}

func (cl *DefaultConfigLoader) LoadAgent(path string) (*BaseConfig, error) {
	if _, err := os.Stat(path); os.IsNotExist(err) {
		return nil, fmt.Errorf("configuration file not found: %s", path)
	}

	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read configuration file: %w", err)
	}

	var config BaseConfig
	if err := yaml.Unmarshal(data, &config); err != nil {
		return nil, fmt.Errorf("failed to parse YAML configuration: %w", err)
	}

	if config.Name == "" && config.ServiceName != "" {
		config.Name = config.ServiceName
	}

	return &config, nil
}

func (cl *DefaultConfigLoader) ValidateConfig(config *BaseConfig) error {
	if config == nil {
		return fmt.Errorf("configuration is nil")
	}

	if config.APIVersion == "" {
		return fmt.Errorf("apiVersion is required")
	}

	if config.Kind == "" {
		return fmt.Errorf("kind is required")
	}

	if config.Name == "" && config.ServiceName == "" {
		return fmt.Errorf("either name or service_name is required")
	}

	if config.Spec != nil {
		if err := cl.validateSpec(config.Spec); err != nil {
			return fmt.Errorf("spec validation failed: %w", err)
		}
	}

	return nil
}

func (cl *DefaultConfigLoader) validateSpec(spec *AgentSpec) error {
	if len(spec.Agents) == 0 {
		return fmt.Errorf("at least one agent must be defined")
	}

	for i, agent := range spec.Agents {
		if agent.Name == "" {
			return fmt.Errorf("agent[%d]: name is required", i)
		}
		if agent.Model == "" {
			return fmt.Errorf("agent[%d]: model is required", i)
		}
	}

	for i, task := range spec.Tasks {
		if task.Name == "" {
			return fmt.Errorf("task[%d]: name is required", i)
		}
		if task.Agent == "" {
			return fmt.Errorf("task[%d]: agent is required", i)
		}

		agentExists := false
		for _, agent := range spec.Agents {
			if agent.Name == task.Agent {
				agentExists = true
				break
			}
		}
		if !agentExists {
			return fmt.Errorf("task[%d]: references non-existent agent '%s'", i, task.Agent)
		}
	}

	return nil
}

func (cl *DefaultConfigLoader) LoadAgentFromDirectory(dir string) (*BaseConfig, error) {
	configPath := filepath.Join(dir, "config.yaml")
	return cl.LoadAgent(configPath)
}

func (cl *DefaultConfigLoader) LoadMultipleAgents(dir string) ([]*BaseConfig, error) {
	var configs []*BaseConfig

	err := filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if info.IsDir() {
			return nil
		}

		if filepath.Base(path) == "config.yaml" {
			config, err := cl.LoadAgent(path)
			if err != nil {
				return fmt.Errorf("failed to load config from %s: %w", path, err)
			}
			configs = append(configs, config)
		}

		return nil
	})

	if err != nil {
		return nil, err
	}

	return configs, nil
}
