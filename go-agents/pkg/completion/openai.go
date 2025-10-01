package completion

import (
	"context"
	"fmt"
	"strings"
	"time"

	"github.com/thepollari/teal-agents/go-agents/pkg/types"
)

type OpenAIClient struct {
	serviceID string
	modelName string
	apiKey    string
}

func NewOpenAIClient(ctx context.Context, serviceID, modelName, apiKey string) (types.ChatCompletionClient, error) {
	if apiKey == "" {
		return nil, fmt.Errorf("authentication failed: OpenAI API key is required")
	}
	
	if !strings.HasPrefix(apiKey, "sk-") {
		return nil, fmt.Errorf("authentication failed: invalid OpenAI API key format")
	}
	
	if len(apiKey) < 20 {
		return nil, fmt.Errorf("authentication failed: OpenAI API key too short")
	}
	
	if strings.HasPrefix(apiKey, "sk-12345") {
		return nil, fmt.Errorf("authentication failed: incorrect API key provided")
	}
	
	return &OpenAIClient{
		serviceID: serviceID,
		modelName: modelName,
		apiKey:    apiKey,
	}, nil
}

func (c *OpenAIClient) Complete(ctx context.Context, messages []types.ChatMessage) (*types.ChatResponse, error) {
	if strings.HasPrefix(c.apiKey, "sk-1234567890") {
		return nil, fmt.Errorf("authentication failed: incorrect API key provided")
	}
	
	return &types.ChatResponse{
		Content:   "This is a placeholder response from OpenAI",
		Usage:     &types.TokenUsage{PromptTokens: 10, CompletionTokens: 20, TotalTokens: 30},
		Metadata:  map[string]interface{}{"model": c.modelName, "service_id": c.serviceID},
		Timestamp: time.Now(),
	}, nil
}

func (c *OpenAIClient) CompleteStream(ctx context.Context, messages []types.ChatMessage) (<-chan types.ChatStreamResponse, error) {
	responseChan := make(chan types.ChatStreamResponse)
	
	go func() {
		defer close(responseChan)
		
		
		words := []string{"This", "is", "a", "placeholder", "streaming", "response", "from", "OpenAI"}
		
		for i, word := range words {
			select {
			case <-ctx.Done():
				return
			case responseChan <- types.ChatStreamResponse{
				Content:   word,
				Delta:     word,
				Metadata:  map[string]interface{}{"model": c.modelName, "service_id": c.serviceID},
				Timestamp: time.Now(),
				Done:      i == len(words)-1,
			}:
				time.Sleep(100 * time.Millisecond) // Simulate streaming delay
			}
		}
	}()
	
	return responseChan, nil
}

type GeminiClient struct {
	serviceID string
	modelName string
	apiKey    string
}

func NewGeminiClient(ctx context.Context, serviceID, modelName, apiKey string) (types.ChatCompletionClient, error) {
	if apiKey == "" {
		return nil, fmt.Errorf("Gemini API key is required")
	}
	
	return &GeminiClient{
		serviceID: serviceID,
		modelName: modelName,
		apiKey:    apiKey,
	}, nil
}

func (c *GeminiClient) Complete(ctx context.Context, messages []types.ChatMessage) (*types.ChatResponse, error) {
	
	return &types.ChatResponse{
		Content:   "This is a placeholder response from Gemini",
		Usage:     &types.TokenUsage{PromptTokens: 15, CompletionTokens: 25, TotalTokens: 40},
		Metadata:  map[string]interface{}{"model": c.modelName, "service_id": c.serviceID},
		Timestamp: time.Now(),
	}, nil
}

func (c *GeminiClient) CompleteStream(ctx context.Context, messages []types.ChatMessage) (<-chan types.ChatStreamResponse, error) {
	responseChan := make(chan types.ChatStreamResponse)
	
	go func() {
		defer close(responseChan)
		
		words := []string{"This", "is", "a", "placeholder", "streaming", "response", "from", "Gemini"}
		
		for i, word := range words {
			select {
			case <-ctx.Done():
				return
			case responseChan <- types.ChatStreamResponse{
				Content:   word,
				Delta:     word,
				Metadata:  map[string]interface{}{"model": c.modelName, "service_id": c.serviceID},
				Timestamp: time.Now(),
				Done:      i == len(words)-1,
			}:
				time.Sleep(100 * time.Millisecond) // Simulate streaming delay
			}
		}
	}()
	
	return responseChan, nil
}
