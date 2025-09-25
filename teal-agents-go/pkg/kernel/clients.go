package kernel

import (
	"context"
	"time"

	"github.com/thepollari/teal-agents-go/pkg/types"
)

type OpenAIChatCompletion struct {
	apiKey    string
	modelName string
	serviceID string
}

func NewOpenAIChatCompletion(apiKey, modelName, serviceID string) *OpenAIChatCompletion {
	return &OpenAIChatCompletion{
		apiKey:    apiKey,
		modelName: modelName,
		serviceID: serviceID,
	}
}

func (oai *OpenAIChatCompletion) GetChatMessageContents(ctx context.Context, chatHistory types.ChatHistory, settings interface{}, kernel interface{}, arguments map[string]interface{}) ([]types.ChatMessageContent, error) {

	response := types.ChatMessageContent{
		Role:      "assistant",
		Content:   "This is a placeholder response from OpenAI chat completion",
		Timestamp: time.Now(),
	}

	return []types.ChatMessageContent{response}, nil
}

type AnthropicChatCompletion struct {
	apiKey    string
	modelName string
	serviceID string
}

func NewAnthropicChatCompletion(apiKey, modelName, serviceID string) *AnthropicChatCompletion {
	return &AnthropicChatCompletion{
		apiKey:    apiKey,
		modelName: modelName,
		serviceID: serviceID,
	}
}

func (ant *AnthropicChatCompletion) GetChatMessageContents(ctx context.Context, chatHistory types.ChatHistory, settings interface{}, kernel interface{}, arguments map[string]interface{}) ([]types.ChatMessageContent, error) {

	response := types.ChatMessageContent{
		Role:      "assistant",
		Content:   "This is a placeholder response from Anthropic chat completion",
		Timestamp: time.Now(),
	}

	return []types.ChatMessageContent{response}, nil
}

type GoogleChatCompletion struct {
	apiKey    string
	modelName string
	serviceID string
}

func NewGoogleChatCompletion(apiKey, modelName, serviceID string) *GoogleChatCompletion {
	return &GoogleChatCompletion{
		apiKey:    apiKey,
		modelName: modelName,
		serviceID: serviceID,
	}
}

func (ggl *GoogleChatCompletion) GetChatMessageContents(ctx context.Context, chatHistory types.ChatHistory, settings interface{}, kernel interface{}, arguments map[string]interface{}) ([]types.ChatMessageContent, error) {

	response := types.ChatMessageContent{
		Role:      "assistant",
		Content:   "This is a placeholder response from Google chat completion",
		Timestamp: time.Now(),
	}

	return []types.ChatMessageContent{response}, nil
}
