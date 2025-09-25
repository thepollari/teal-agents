package kernel

import (
	"fmt"
	"log"

	"github.com/thepollari/teal-agents-go/pkg/types"
)

type ChatCompletionBuilder struct {
	appConfig      types.AppConfig
	customFactory  types.ChatCompletionFactory
	defaultFactory *DefaultChatCompletionFactory
}

func NewChatCompletionBuilder(appConfig types.AppConfig) *ChatCompletionBuilder {
	builder := &ChatCompletionBuilder{
		appConfig:      appConfig,
		defaultFactory: NewDefaultChatCompletionFactory(appConfig),
	}

	customModuleName := appConfig.Get("TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE")
	if customModuleName != "" {
		customClassName := appConfig.Get("TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS_NAME")
		if customClassName == "" {
			log.Printf("Warning: Custom Chat Completion Factory class name not provided")
		} else {
			log.Printf("Custom chat completion factory not yet implemented: %s.%s", customModuleName, customClassName)
		}
	}

	return builder
}

func (ccb *ChatCompletionBuilder) GetChatCompletionForModel(serviceID, modelName string) (types.ChatCompletionClientBase, error) {
	if ccb.customFactory != nil {
		client, err := ccb.customFactory.GetChatCompletionForModelName(modelName, serviceID)
		if err == nil {
			return client, nil
		}
		log.Printf("Warning: Could not find model %s using custom factory: %v", modelName, err)
	}

	return ccb.defaultFactory.GetChatCompletionForModelName(modelName, serviceID)
}

func (ccb *ChatCompletionBuilder) GetModelTypeForName(modelName string) types.ModelType {
	if ccb.customFactory != nil {
		modelType := ccb.customFactory.GetModelTypeForName(modelName)
		if modelType != "" {
			return modelType
		}
		log.Printf("Warning: Could not find model %s using custom factory", modelName)
	}

	return ccb.defaultFactory.GetModelTypeForName(modelName)
}

func (ccb *ChatCompletionBuilder) ModelSupportsStructuredOutput(modelName string) bool {
	if ccb.customFactory != nil {
		if ccb.customFactory.ModelSupportsStructuredOutput(modelName) {
			return true
		}
		log.Printf("Warning: Could not find model %s using custom factory", modelName)
	}

	return ccb.defaultFactory.ModelSupportsStructuredOutput(modelName)
}

type DefaultChatCompletionFactory struct {
	appConfig types.AppConfig
}

func NewDefaultChatCompletionFactory(appConfig types.AppConfig) *DefaultChatCompletionFactory {
	return &DefaultChatCompletionFactory{
		appConfig: appConfig,
	}
}

func (dcf *DefaultChatCompletionFactory) GetChatCompletionForModelName(modelName, serviceID string) (types.ChatCompletionClientBase, error) {
	modelType := dcf.GetModelTypeForName(modelName)

	switch modelType {
	case types.ModelTypeOpenAI:
		return dcf.createOpenAIClient(modelName, serviceID)
	case types.ModelTypeAnthropic:
		return dcf.createAnthropicClient(modelName, serviceID)
	case types.ModelTypeGoogle:
		return dcf.createGoogleClient(modelName, serviceID)
	default:
		return nil, fmt.Errorf("unsupported model type: %s", modelType)
	}
}

func (dcf *DefaultChatCompletionFactory) GetModelTypeForName(modelName string) types.ModelType {
	switch {
	case contains(modelName, "gpt") || contains(modelName, "openai"):
		return types.ModelTypeOpenAI
	case contains(modelName, "claude") || contains(modelName, "anthropic"):
		return types.ModelTypeAnthropic
	case contains(modelName, "gemini") || contains(modelName, "google"):
		return types.ModelTypeGoogle
	default:
		return types.ModelTypeOpenAI
	}
}

func (dcf *DefaultChatCompletionFactory) ModelSupportsStructuredOutput(modelName string) bool {
	modelType := dcf.GetModelTypeForName(modelName)

	switch modelType {
	case types.ModelTypeOpenAI:
		return true
	case types.ModelTypeAnthropic:
		return contains(modelName, "claude-3")
	case types.ModelTypeGoogle:
		return contains(modelName, "gemini")
	default:
		return false
	}
}

func (dcf *DefaultChatCompletionFactory) GetConfigs() []types.Config {
	return []types.Config{
		{
			EnvName:      "OPENAI_API_KEY",
			DefaultValue: "",
			Description:  "OpenAI API key for chat completion",
		},
		{
			EnvName:      "ANTHROPIC_API_KEY",
			DefaultValue: "",
			Description:  "Anthropic API key for chat completion",
		},
		{
			EnvName:      "GOOGLE_API_KEY",
			DefaultValue: "",
			Description:  "Google API key for chat completion",
		},
	}
}

func (dcf *DefaultChatCompletionFactory) createOpenAIClient(modelName, serviceID string) (types.ChatCompletionClientBase, error) {
	apiKey := dcf.appConfig.Get("OPENAI_API_KEY")
	if apiKey == "" {
		return nil, fmt.Errorf("OPENAI_API_KEY not configured")
	}

	return NewOpenAIChatCompletion(apiKey, modelName, serviceID), nil
}

func (dcf *DefaultChatCompletionFactory) createAnthropicClient(modelName, serviceID string) (types.ChatCompletionClientBase, error) {
	apiKey := dcf.appConfig.Get("ANTHROPIC_API_KEY")
	if apiKey == "" {
		return nil, fmt.Errorf("ANTHROPIC_API_KEY not configured")
	}

	return NewAnthropicChatCompletion(apiKey, modelName, serviceID), nil
}

func (dcf *DefaultChatCompletionFactory) createGoogleClient(modelName, serviceID string) (types.ChatCompletionClientBase, error) {
	apiKey := dcf.appConfig.Get("GOOGLE_API_KEY")
	if apiKey == "" {
		return nil, fmt.Errorf("GOOGLE_API_KEY not configured")
	}

	return NewGoogleChatCompletion(apiKey, modelName, serviceID), nil
}

func contains(s, substr string) bool {
	return len(s) >= len(substr) &&
		(s == substr ||
			(len(s) > len(substr) &&
				(s[:len(substr)] == substr ||
					s[len(s)-len(substr):] == substr ||
					containsSubstring(s, substr))))
}

func containsSubstring(s, substr string) bool {
	for i := 0; i <= len(s)-len(substr); i++ {
		if s[i:i+len(substr)] == substr {
			return true
		}
	}
	return false
}
