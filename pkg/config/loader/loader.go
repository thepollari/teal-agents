package loader

import (
	"encoding/json"
	"fmt"
	"os"
	"strings"

	"github.com/go-playground/validator/v10"
	"github.com/spf13/viper"
	"github.com/thepollari/teal-agents/pkg/config/types"
	"gopkg.in/yaml.v3"
)

type ConfigLoader struct {
	validator *validator.Validate
	viper     *viper.Viper
}

func NewConfigLoader() *ConfigLoader {
	v := viper.New()
	v.SetEnvPrefix("TA")
	v.AutomaticEnv()
	v.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))

	return &ConfigLoader{
		validator: validator.New(),
		viper:     v,
	}
}

func (cl *ConfigLoader) LoadEnvConfig() (*types.EnvConfig, error) {
	config := types.DefaultEnvConfig()

	if err := cl.parseEnvStore("TA_ENV_STORE"); err != nil {
		return nil, fmt.Errorf("failed to parse TA_ENV_STORE: %w", err)
	}

	if err := cl.parseEnvStore("TA_ENV_GLOBAL_STORE"); err != nil {
		return nil, fmt.Errorf("failed to parse TA_ENV_GLOBAL_STORE: %w", err)
	}

	envVars := []string{
		"API_KEY", "SERVICE_CONFIG", "REMOTE_PLUGIN_PATH",
		"TYPES_MODULE", "PLUGIN_MODULE",
		"CUSTOM_CHAT_COMPLETION_FACTORY_MODULE",
		"CUSTOM_CHAT_COMPLETION_FACTORY_CLASS_NAME",
		"STRUCTURED_OUTPUT_TRANSFORMER_MODEL",
		"A2A_ENABLED", "AGENT_BASE_URL", "PROVIDER_ORG",
		"PROVIDER_URL", "A2A_OUTPUT_CLASSIFIER_MODEL",
		"STATE_MANAGEMENT", "AUTHORIZER_MODULE", "AUTHORIZER_CLASS",
		"REDIS_HOST", "REDIS_PORT", "REDIS_DB", "REDIS_TTL",
		"REDIS_SSL", "REDIS_PWD", "PERSISTENCE_MODULE",
		"PERSISTENCE_CLASS",
	}

	for _, envVar := range envVars {
		if err := cl.viper.BindEnv(envVar); err != nil {
			return nil, fmt.Errorf("failed to bind env var %s: %w", envVar, err)
		}
	}

	if err := cl.viper.Unmarshal(config); err != nil {
		return nil, fmt.Errorf("failed to unmarshal environment config: %w", err)
	}

	if err := cl.validator.Struct(config); err != nil {
		return nil, fmt.Errorf("environment config validation failed: %w", err)
	}

	return config, nil
}

func (cl *ConfigLoader) parseEnvStore(envVar string) error {
	envStoreJSON := os.Getenv(envVar)
	if envStoreJSON == "" {
		return nil
	}

	var envMap map[string]string
	if err := json.Unmarshal([]byte(envStoreJSON), &envMap); err != nil {
		return fmt.Errorf("failed to parse %s as JSON: %w", envVar, err)
	}

	for key, value := range envMap {
		if err := os.Setenv(key, value); err != nil {
			return fmt.Errorf("failed to set env var %s: %w", key, err)
		}
	}

	return nil
}

func (cl *ConfigLoader) LoadYAMLConfig(filePath string) (*types.BaseConfig, error) {
	data, err := os.ReadFile(filePath)
	if err != nil {
		return nil, fmt.Errorf("failed to read config file %s: %w", filePath, err)
	}

	var config types.BaseConfig
	if err := yaml.Unmarshal(data, &config); err != nil {
		return nil, fmt.Errorf("failed to parse YAML config: %w", err)
	}

	if err := cl.validator.Struct(config); err != nil {
		return nil, fmt.Errorf("config validation failed: %w", err)
	}

	return &config, nil
}

func (cl *ConfigLoader) LoadSequentialConfig(filePath string) (*types.SequentialConfig, error) {
	data, err := os.ReadFile(filePath)
	if err != nil {
		return nil, fmt.Errorf("failed to read config file %s: %w", filePath, err)
	}

	var config types.SequentialConfig
	if err := yaml.Unmarshal(data, &config); err != nil {
		return nil, fmt.Errorf("failed to parse YAML config: %w", err)
	}

	if err := cl.validator.Struct(config); err != nil {
		return nil, fmt.Errorf("sequential config validation failed: %w", err)
	}

	return &config, nil
}

func (cl *ConfigLoader) LoadChatConfig(filePath string) (*types.ChatConfig, error) {
	data, err := os.ReadFile(filePath)
	if err != nil {
		return nil, fmt.Errorf("failed to read config file %s: %w", filePath, err)
	}

	var config types.ChatConfig
	if err := yaml.Unmarshal(data, &config); err != nil {
		return nil, fmt.Errorf("failed to parse YAML config: %w", err)
	}

	if err := cl.validator.Struct(config); err != nil {
		return nil, fmt.Errorf("chat config validation failed: %w", err)
	}

	return &config, nil
}

func (cl *ConfigLoader) LoadTeamOrchestratorConfig(filePath string) (*types.TeamOrchestratorConfig, error) {
	data, err := os.ReadFile(filePath)
	if err != nil {
		return nil, fmt.Errorf("failed to read config file %s: %w", filePath, err)
	}

	var config types.TeamOrchestratorConfig
	if err := yaml.Unmarshal(data, &config); err != nil {
		return nil, fmt.Errorf("failed to parse YAML config: %w", err)
	}

	if err := cl.validator.Struct(config); err != nil {
		return nil, fmt.Errorf("team orchestrator config validation failed: %w", err)
	}

	return &config, nil
}

func (cl *ConfigLoader) LoadPlanningOrchestratorConfig(filePath string) (*types.PlanningOrchestratorConfig, error) {
	data, err := os.ReadFile(filePath)
	if err != nil {
		return nil, fmt.Errorf("failed to read config file %s: %w", filePath, err)
	}

	var config types.PlanningOrchestratorConfig
	if err := yaml.Unmarshal(data, &config); err != nil {
		return nil, fmt.Errorf("failed to parse YAML config: %w", err)
	}

	if err := cl.validator.Struct(config); err != nil {
		return nil, fmt.Errorf("planning orchestrator config validation failed: %w", err)
	}

	return &config, nil
}

func (cl *ConfigLoader) LoadAssistantOrchestratorConfig(filePath string) (*types.AssistantOrchestratorConfig, error) {
	data, err := os.ReadFile(filePath)
	if err != nil {
		return nil, fmt.Errorf("failed to read config file %s: %w", filePath, err)
	}

	var config types.AssistantOrchestratorConfig
	if err := yaml.Unmarshal(data, &config); err != nil {
		return nil, fmt.Errorf("failed to parse YAML config: %w", err)
	}

	if err := cl.validator.Struct(config); err != nil {
		return nil, fmt.Errorf("assistant orchestrator config validation failed: %w", err)
	}

	return &config, nil
}

func (cl *ConfigLoader) LoadConfigByKind(filePath string) (interface{}, error) {
	data, err := os.ReadFile(filePath)
	if err != nil {
		return nil, err
	}

	var temp map[string]interface{}
	if err := yaml.Unmarshal(data, &temp); err != nil {
		return nil, err
	}

	kindVal, ok := temp["kind"].(string)
	if !ok {
		baseConfig, err := cl.LoadYAMLConfig(filePath)
		if err != nil {
			return nil, err
		}
		return baseConfig, nil
	}

	switch kindVal {
	case "Sequential":
		return cl.LoadSequentialConfig(filePath)
	case "Chat":
		return cl.LoadChatConfig(filePath)
	case "TeamOrchestrator":
		return cl.LoadTeamOrchestratorConfig(filePath)
	case "PlanningOrchestrator":
		return cl.LoadPlanningOrchestratorConfig(filePath)
	case "AssistantOrchestrator":
		return cl.LoadAssistantOrchestratorConfig(filePath)
	default:
		baseConfig, err := cl.LoadYAMLConfig(filePath)
		if err != nil {
			return nil, err
		}
		return baseConfig, nil
	}
}
