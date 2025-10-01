package config

import (
	"fmt"
	"os"
	"strconv"
	"strings"
)

func ValidateConfig(config *BaseConfig) error {
	if config.APIVersion == "" {
		return fmt.Errorf("apiVersion is required")
	}
	
	if config.Kind == "" {
		return fmt.Errorf("kind is required")
	}
	
	if config.ServiceName == "" {
		return fmt.Errorf("service_name is required")
	}
	
	if config.Version == "" {
		return fmt.Errorf("version is required")
	}
	
	_, _, err := ParseAPIVersion(config.APIVersion)
	if err != nil {
		return fmt.Errorf("invalid apiVersion format: %w", err)
	}
	
	if len(config.Spec.Agents) == 0 {
		return fmt.Errorf("at least one agent must be defined in spec.agents")
	}
	
	if len(config.Spec.Tasks) == 0 {
		return fmt.Errorf("at least one task must be defined in spec.tasks")
	}
	
	agentNames := make(map[string]bool)
	for i, agent := range config.Spec.Agents {
		if agent.Name == "" {
			return fmt.Errorf("agent[%d].name is required", i)
		}
		
		if agentNames[agent.Name] {
			return fmt.Errorf("duplicate agent name: %s", agent.Name)
		}
		agentNames[agent.Name] = true
		
		if agent.Model == "" {
			return fmt.Errorf("agent[%d].model is required", i)
		}
		
		if agent.SystemPrompt == "" {
			return fmt.Errorf("agent[%d].system_prompt is required", i)
		}
		
		if agent.Temperature != nil && (*agent.Temperature < 0 || *agent.Temperature > 2) {
			return fmt.Errorf("agent[%d].temperature must be between 0 and 2", i)
		}
	}
	
	taskNames := make(map[string]bool)
	taskNumbers := make(map[int]bool)
	for i, task := range config.Spec.Tasks {
		if task.Name == "" {
			return fmt.Errorf("task[%d].name is required", i)
		}
		
		if taskNames[task.Name] {
			return fmt.Errorf("duplicate task name: %s", task.Name)
		}
		taskNames[task.Name] = true
		
		if task.TaskNo <= 0 {
			return fmt.Errorf("task[%d].task_no must be positive", i)
		}
		
		if taskNumbers[task.TaskNo] {
			return fmt.Errorf("duplicate task number: %d", task.TaskNo)
		}
		taskNumbers[task.TaskNo] = true
		
		if task.Agent == "" {
			return fmt.Errorf("task[%d].agent is required", i)
		}
		
		if !agentNames[task.Agent] {
			return fmt.Errorf("task[%d].agent references unknown agent: %s", i, task.Agent)
		}
		
		if task.Instructions == "" {
			return fmt.Errorf("task[%d].instructions is required", i)
		}
	}
	
	return nil
}

func LoadAppConfig() *AppConfig {
	config := &AppConfig{
		LogLevel: getEnvOrDefault("TA_LOG_LEVEL", "info"),
		Port:     getEnvIntOrDefault("PORT", getEnvIntOrDefault("TA_PORT", 8000)),
	}
	
	if openAIKey := os.Getenv("OPENAI_API_KEY"); openAIKey != "" {
		config.OpenAIAPIKey = openAIKey
	}
	
	if taAPIKey := os.Getenv("TA_API_KEY"); taAPIKey != "" {
		config.OpenAIAPIKey = taAPIKey
	}
	
	if geminiKey := os.Getenv("GEMINI_API_KEY"); geminiKey != "" {
		config.GeminiAPIKey = geminiKey
	}
	
	return config
}

func getEnvOrDefault(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getEnvIntOrDefault(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		if intValue, err := strconv.Atoi(value); err == nil {
			return intValue
		}
	}
	return defaultValue
}

func ValidateAgentConfig(agent AgentConfig) error {
	if agent.Name == "" {
		return fmt.Errorf("agent name is required")
	}
	
	if agent.Model == "" {
		return fmt.Errorf("agent model is required")
	}
	
	if agent.SystemPrompt == "" {
		return fmt.Errorf("agent system_prompt is required")
	}
	
	supportedModels := []string{
		"gpt-4o", "gpt-4o-mini", "gpt-4", "gpt-3.5-turbo",
		"gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash",
	}
	
	modelSupported := false
	for _, supportedModel := range supportedModels {
		if strings.HasPrefix(agent.Model, supportedModel) {
			modelSupported = true
			break
		}
	}
	
	if !modelSupported {
		return fmt.Errorf("unsupported model: %s", agent.Model)
	}
	
	return nil
}
