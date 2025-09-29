package gemini

import (
	"context"
	"fmt"
	"os"

	"github.com/google/generative-ai-go/genai"
	"google.golang.org/api/option"

	"github.com/merck-gen/teal-agents-go/pkg/config"
)

type Client struct {
	client *genai.Client
	model  string
}

func NewClient(model string) (*Client, error) {
	apiKey := os.Getenv("GEMINI_API_KEY")
	if apiKey == "" {
		return nil, fmt.Errorf("GEMINI_API_KEY environment variable is required")
	}

	ctx := context.Background()
	client, err := genai.NewClient(ctx, option.WithAPIKey(apiKey))
	if err != nil {
		return nil, fmt.Errorf("failed to create Gemini client: %w", err)
	}

	return &Client{
		client: client,
		model:  model,
	}, nil
}

func (c *Client) Close() error {
	return c.client.Close()
}

func (c *Client) GenerateResponse(ctx context.Context, systemPrompt, userMessage string, chatHistory []config.HistoryMessage) (string, *config.TokenUsage, error) {
	model := c.client.GenerativeModel(c.model)
	
	if systemPrompt != "" {
		model.SystemInstruction = &genai.Content{
			Parts: []genai.Part{genai.Text(systemPrompt)},
		}
	}

	var parts []genai.Part
	
	for _, msg := range chatHistory {
		parts = append(parts, genai.Text(fmt.Sprintf("%s: %s", msg.Role, msg.Content)))
	}
	
	parts = append(parts, genai.Text(fmt.Sprintf("user: %s", userMessage)))

	resp, err := model.GenerateContent(ctx, parts...)
	if err != nil {
		return "", nil, fmt.Errorf("failed to generate content: %w", err)
	}

	if len(resp.Candidates) == 0 {
		return "", nil, fmt.Errorf("no response candidates generated")
	}

	candidate := resp.Candidates[0]
	if len(candidate.Content.Parts) == 0 {
		return "", nil, fmt.Errorf("no content parts in response")
	}

	var responseText string
	if textPart, ok := candidate.Content.Parts[0].(genai.Text); ok {
		responseText = string(textPart)
	} else {
		return "", nil, fmt.Errorf("unexpected content part type")
	}

	tokenUsage := &config.TokenUsage{
		CompletionTokens: 0, // Gemini API doesn't provide detailed token counts in the same way
		PromptTokens:     0,
		TotalTokens:      0,
	}

	if resp.UsageMetadata != nil {
		tokenUsage.PromptTokens = int(resp.UsageMetadata.PromptTokenCount)
		tokenUsage.CompletionTokens = int(resp.UsageMetadata.CandidatesTokenCount)
		tokenUsage.TotalTokens = int(resp.UsageMetadata.TotalTokenCount)
	}

	return responseText, tokenUsage, nil
}

func (c *Client) GenerateStreamResponse(ctx context.Context, systemPrompt, userMessage string, chatHistory []config.HistoryMessage) (<-chan string, <-chan error) {
	responseChan := make(chan string, 10)
	errorChan := make(chan error, 1)

	go func() {
		defer close(responseChan)
		defer close(errorChan)

		model := c.client.GenerativeModel(c.model)
		
		if systemPrompt != "" {
			model.SystemInstruction = &genai.Content{
				Parts: []genai.Part{genai.Text(systemPrompt)},
			}
		}

		var parts []genai.Part
		
		for _, msg := range chatHistory {
			parts = append(parts, genai.Text(fmt.Sprintf("%s: %s", msg.Role, msg.Content)))
		}
		
		parts = append(parts, genai.Text(fmt.Sprintf("user: %s", userMessage)))

		iter := model.GenerateContentStream(ctx, parts...)
		
		for {
			resp, err := iter.Next()
			if err != nil {
				if err.Error() == "iterator done" {
					break
				}
				errorChan <- fmt.Errorf("failed to get next response: %w", err)
				return
			}

			if len(resp.Candidates) > 0 && len(resp.Candidates[0].Content.Parts) > 0 {
				if textPart, ok := resp.Candidates[0].Content.Parts[0].(genai.Text); ok {
					responseChan <- string(textPart)
				}
			}
		}
	}()

	return responseChan, errorChan
}
