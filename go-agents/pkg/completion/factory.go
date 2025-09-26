package completion

import (
	"context"
	"fmt"
	"strings"

	"github.com/thepollari/teal-agents/go-agents/pkg/config"
	"github.com/thepollari/teal-agents/go-agents/pkg/types"
)

type DefaultChatCompletionFactory struct {
	config       *config.AppConfig
	openAIModels []string
	geminiModels []string
}

func NewDefaultChatCompletionFactory(cfg *config.AppConfig) *DefaultChatCompletionFactory {
	return &DefaultChatCompletionFactory{
		config:       cfg,
		openAIModels: []string{"gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"},
		geminiModels: []string{"gemini-pro", "gemini-2.0-flash-lite"},
	}
}

func (f *DefaultChatCompletionFactory) GetChatCompletion(ctx context.Context, modelName, serviceID string) (types.ChatCompletionClient, error) {
	if f.isOpenAIModel(modelName) {
		return NewOpenAIClient(ctx, serviceID, modelName, f.config.OpenAIAPIKey)
	}
	
	if f.isGeminiModel(modelName) {
		return NewGeminiClient(ctx, serviceID, modelName, f.config.GeminiAPIKey)
	}
	
	return nil, fmt.Errorf("unsupported model: %s", modelName)
}

func (f *DefaultChatCompletionFactory) GetModelType(ctx context.Context, modelName string) (types.ModelType, error) {
	if f.isOpenAIModel(modelName) {
		return types.ModelTypeOpenAI, nil
	}
	
	if f.isGeminiModel(modelName) {
		return types.ModelTypeGemini, nil
	}
	
	return "", fmt.Errorf("unknown model: %s", modelName)
}

func (f *DefaultChatCompletionFactory) SupportsStructuredOutput(ctx context.Context, modelName string) bool {
	if f.isOpenAIModel(modelName) {
		return true
	}
	
	if f.isGeminiModel(modelName) {
		return strings.Contains(modelName, "pro") || strings.Contains(modelName, "flash")
	}
	
	return false
}

func (f *DefaultChatCompletionFactory) isOpenAIModel(modelName string) bool {
	for _, model := range f.openAIModels {
		if model == modelName {
			return true
		}
	}
	return strings.HasPrefix(modelName, "gpt-")
}

func (f *DefaultChatCompletionFactory) isGeminiModel(modelName string) bool {
	for _, model := range f.geminiModels {
		if model == modelName {
			return true
		}
	}
	return strings.HasPrefix(modelName, "gemini-")
}
