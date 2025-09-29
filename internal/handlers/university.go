package handlers

import (
	"context"
	"fmt"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"

	"github.com/merck-gen/teal-agents-go/internal/gemini"
	"github.com/merck-gen/teal-agents-go/pkg/config"
	"github.com/merck-gen/teal-agents-go/pkg/kernel"
)

type UniversityHandler struct {
	kernel       kernel.Kernel
	geminiClient *gemini.Client
	logger       *logrus.Logger
	agentConfig  *config.BaseConfig
}

func NewUniversityHandler(k kernel.Kernel, geminiClient *gemini.Client, logger *logrus.Logger, agentConfig *config.BaseConfig) *UniversityHandler {
	return &UniversityHandler{
		kernel:       k,
		geminiClient: geminiClient,
		logger:       logger,
		agentConfig:  agentConfig,
	}
}

func (uh *UniversityHandler) HandleInvoke(c *gin.Context) {
	var input config.BaseInput
	if err := c.ShouldBindJSON(&input); err != nil {
		uh.logger.Errorf("Failed to bind JSON input: %v", err)
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid JSON input"})
		return
	}

	requestID := fmt.Sprintf("req_%d", time.Now().UnixNano())
	sessionID := fmt.Sprintf("session_%d", time.Now().UnixNano())

	userMessage := ""
	if len(input.ChatHistory) > 0 {
		lastMessage := input.ChatHistory[len(input.ChatHistory)-1]
		if lastMessage.Role == "user" {
			userMessage = lastMessage.Content
		}
	}

	if userMessage == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "No user message found in chat history"})
		return
	}

	systemPrompt := ""
	if uh.agentConfig.Spec != nil && len(uh.agentConfig.Spec.Agents) > 0 {
		systemPrompt = uh.agentConfig.Spec.Agents[0].SystemPrompt
	}

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	response, tokenUsage, err := uh.geminiClient.GenerateResponse(ctx, systemPrompt, userMessage, input.ChatHistory)
	if err != nil {
		uh.logger.Errorf("Failed to generate response: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate response"})
		return
	}

	invokeResponse := config.InvokeResponse{
		SessionID:      sessionID,
		Source:         uh.agentConfig.Name,
		RequestID:      requestID,
		TokenUsage:     *tokenUsage,
		ExtraData:      make(map[string]interface{}),
		OutputRaw:      response,
		OutputPydantic: nil,
	}

	c.JSON(http.StatusOK, invokeResponse)
}

func (uh *UniversityHandler) HandleInvokeStream(c *gin.Context) {
	var input config.BaseInput
	if err := c.ShouldBindJSON(&input); err != nil {
		uh.logger.Errorf("Failed to bind JSON input: %v", err)
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid JSON input"})
		return
	}

	requestID := fmt.Sprintf("req_%d", time.Now().UnixNano())
	sessionID := fmt.Sprintf("session_%d", time.Now().UnixNano())

	userMessage := ""
	if len(input.ChatHistory) > 0 {
		lastMessage := input.ChatHistory[len(input.ChatHistory)-1]
		if lastMessage.Role == "user" {
			userMessage = lastMessage.Content
		}
	}

	if userMessage == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "No user message found in chat history"})
		return
	}

	systemPrompt := ""
	if uh.agentConfig.Spec != nil && len(uh.agentConfig.Spec.Agents) > 0 {
		systemPrompt = uh.agentConfig.Spec.Agents[0].SystemPrompt
	}

	c.Header("Content-Type", "text/event-stream")
	c.Header("Cache-Control", "no-cache")
	c.Header("Connection", "keep-alive")
	c.Header("Access-Control-Allow-Origin", "*")

	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()

	responseChan, errorChan := uh.geminiClient.GenerateStreamResponse(ctx, systemPrompt, userMessage, input.ChatHistory)

	for {
		select {
		case chunk, ok := <-responseChan:
			if !ok {
				finalResponse := config.InvokeResponse{
					SessionID:      sessionID,
					Source:         uh.agentConfig.Name,
					RequestID:      requestID,
					TokenUsage:     config.TokenUsage{}, // TODO: Get actual token usage from streaming
					ExtraData:      make(map[string]interface{}),
					OutputRaw:      "",
					OutputPydantic: nil,
				}
				c.SSEvent("final", finalResponse)
				c.Writer.Flush()
				return
			}

			partialResponse := config.PartialResponse{
				SessionID:     sessionID,
				Source:        uh.agentConfig.Name,
				RequestID:     requestID,
				OutputPartial: chunk,
			}
			c.SSEvent("partial", partialResponse)
			c.Writer.Flush()

		case err := <-errorChan:
			if err != nil {
				uh.logger.Errorf("Streaming error: %v", err)
				c.SSEvent("error", gin.H{"error": err.Error()})
				c.Writer.Flush()
				return
			}

		case <-ctx.Done():
			uh.logger.Warn("Streaming request timed out")
			c.SSEvent("error", gin.H{"error": "Request timed out"})
			c.Writer.Flush()
			return
		}
	}
}

func (uh *UniversityHandler) HandleAgentCard(c *gin.Context) {
	agentCard := gin.H{
		"name":        uh.agentConfig.Name,
		"version":     uh.agentConfig.Version,
		"description": uh.agentConfig.Description,
		"input_type":  uh.agentConfig.InputType,
		"output_type": uh.agentConfig.OutputType,
	}

	if uh.agentConfig.Metadata != nil {
		agentCard["metadata"] = gin.H{
			"description":       uh.agentConfig.Metadata.Description,
			"skills":           uh.agentConfig.Metadata.Skills,
			"documentation_url": uh.agentConfig.Metadata.DocumentationURL,
		}
	}

	c.JSON(http.StatusOK, agentCard)
}

func (uh *UniversityHandler) HandleA2AInvoke(c *gin.Context) {
	uh.HandleInvoke(c)
}

func (uh *UniversityHandler) HandleA2AAgentCard(c *gin.Context) {
	uh.HandleAgentCard(c)
}
