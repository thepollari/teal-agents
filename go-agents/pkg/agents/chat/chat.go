package chat

import (
	"context"
	"fmt"
	"log/slog"
	"time"

	"github.com/google/uuid"
	"github.com/thepollari/teal-agents/go-agents/pkg/config"
	"github.com/thepollari/teal-agents/go-agents/pkg/logging"
	"github.com/thepollari/teal-agents/go-agents/pkg/types"
)

type ChatAgent struct {
	config        *config.BaseConfig
	kernelBuilder types.KernelBuilder
	logger        *slog.Logger
}

func NewChatAgent(cfg *config.BaseConfig, kernelBuilder types.KernelBuilder) (*ChatAgent, error) {
	logger := logging.GetLogger()
	
	return &ChatAgent{
		config:        cfg,
		kernelBuilder: kernelBuilder,
		logger:        logger,
	}, nil
}

func (a *ChatAgent) Invoke(ctx context.Context, inputs map[string]interface{}) (*types.InvokeResponse, error) {
	a.logger.Info("Chat agent invoked", "inputs", inputs)
	
	sessionID, ok := inputs["session_id"].(string)
	if !ok || sessionID == "" {
		sessionID = uuid.New().String()
	}
	
	requestID := uuid.New().String()
	
	result := map[string]interface{}{
		"session_id": sessionID,
		"request_id": requestID,
		"source":     fmt.Sprintf("%s:%s", a.config.ServiceName, a.config.Version),
		"output":     "This is a placeholder response from the Chat agent.",
		"token_usage": map[string]interface{}{
			"completion_tokens": 10,
			"prompt_tokens":     20,
			"total_tokens":      30,
		},
	}
	
	return &types.InvokeResponse{
		Result:    result,
		Timestamp: time.Now(),
	}, nil
}

func (a *ChatAgent) InvokeStream(ctx context.Context, inputs map[string]interface{}) (<-chan types.StreamResponse, error) {
	a.logger.Info("Chat agent stream invoked", "inputs", inputs)
	
	sessionID, ok := inputs["session_id"].(string)
	if !ok || sessionID == "" {
		sessionID = uuid.New().String()
	}
	
	requestID := uuid.New().String()
	
	responseChan := make(chan types.StreamResponse)
	
	go func() {
		defer close(responseChan)
		
		partialData := map[string]interface{}{
			"session_id": sessionID,
			"request_id": requestID,
			"source":     fmt.Sprintf("%s:%s", a.config.ServiceName, a.config.Version),
			"content":    "This is a partial response from the Chat agent.",
		}
		responseChan <- types.StreamResponse{
			Data:      partialData,
			Timestamp: time.Now(),
			Done:      false,
		}
		
		time.Sleep(100 * time.Millisecond)
		
		finalData := map[string]interface{}{
			"session_id": sessionID,
			"request_id": requestID,
			"source":     fmt.Sprintf("%s:%s", a.config.ServiceName, a.config.Version),
			"content":    "This is the final response from the Chat agent.",
			"token_usage": map[string]interface{}{
				"completion_tokens": 10,
				"prompt_tokens":     20,
				"total_tokens":      30,
			},
		}
		responseChan <- types.StreamResponse{
			Data:      finalData,
			Timestamp: time.Now(),
			Done:      true,
		}
	}()
	
	return responseChan, nil
}
