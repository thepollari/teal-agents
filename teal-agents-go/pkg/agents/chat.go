package agents

import (
	"context"
	"fmt"

	"github.com/thepollari/teal-agents-go/pkg/types"
)

type ChatAgents struct {
	agent              *SKAgent
	extraDataCollector *ExtraDataCollector
}

func NewChatAgents(agent *SKAgent, extraDataCollector *ExtraDataCollector) *ChatAgents {
	return &ChatAgents{
		agent:              agent,
		extraDataCollector: extraDataCollector,
	}
}

func (ca *ChatAgents) Invoke(ctx context.Context, inputs map[string]interface{}) (*types.InvokeResponse, error) {
	chatHistory, ok := inputs["chat_history"].(types.ChatHistory)
	if !ok {
		chatHistory = types.ChatHistory{}
	}

	if ca.extraDataCollector != nil {
		ca.extraDataCollector.AddExtraData("chat_invocation_started", true)
	}

	response, err := ca.agent.GetChatCompletion(ctx, chatHistory, inputs)
	if err != nil {
		return nil, fmt.Errorf("chat completion failed: %w", err)
	}

	var finalOutput string
	var tokenUsage types.TokenUsage

	if len(response) > 0 {
		finalOutput = response[len(response)-1].Content
		tokenUsage = types.TokenUsage{
			CompletionTokens: len(finalOutput) / 4, // Rough estimate
			PromptTokens:     len(fmt.Sprintf("%v", chatHistory)) / 4,
		}
		tokenUsage.TotalTokens = tokenUsage.CompletionTokens + tokenUsage.PromptTokens
	}

	var extraData interface{}
	if ca.extraDataCollector != nil {
		ca.extraDataCollector.AddExtraData("chat_invocation_completed", true)
		ca.extraDataCollector.AddExtraData("response_length", len(finalOutput))
		extraData = ca.extraDataCollector.GetExtraData()
	}

	return &types.InvokeResponse{
		OutputRaw:      &finalOutput,
		TokenUsage:     tokenUsage,
		ExtraData:      extraData,
		OutputPydantic: response,
	}, nil
}

func (ca *ChatAgents) InvokeStream(ctx context.Context, inputs map[string]interface{}) (<-chan types.PartialResponse, error) {
	responseChan := make(chan types.PartialResponse, 10)

	go func() {
		defer close(responseChan)

		if ca.extraDataCollector != nil {
			ca.extraDataCollector.AddExtraData("chat_stream_started", true)
		}

		response, err := ca.Invoke(ctx, inputs)
		if err != nil {
			responseChan <- types.PartialResponse{
				OutputPartial: fmt.Sprintf("Error: %v", err),
			}
			return
		}

		if response.OutputRaw != nil {
			output := *response.OutputRaw
			chunkSize := 20 // Stream in smaller chunks for chat

			for i := 0; i < len(output); i += chunkSize {
				end := i + chunkSize
				if end > len(output) {
					end = len(output)
				}

				responseChan <- types.PartialResponse{
					OutputPartial: output[i:end],
				}
			}
		}

		if ca.extraDataCollector != nil {
			ca.extraDataCollector.AddExtraData("chat_stream_completed", true)
		}
	}()

	return responseChan, nil
}
