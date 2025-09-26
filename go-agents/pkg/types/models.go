package types

import (
	"time"
)

type ModelType string

const (
	ModelTypeOpenAI ModelType = "openai"
	ModelTypeGemini ModelType = "gemini"
)

type InvokeResponse struct {
	Result    interface{}            `json:"result"`
	Metadata  map[string]interface{} `json:"metadata,omitempty"`
	Timestamp time.Time              `json:"timestamp"`
}

type StreamResponse struct {
	Data      interface{}            `json:"data"`
	Metadata  map[string]interface{} `json:"metadata,omitempty"`
	Timestamp time.Time              `json:"timestamp"`
	Done      bool                   `json:"done"`
}

type ChatMessage struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type ChatResponse struct {
	Content   string                 `json:"content"`
	Usage     *TokenUsage            `json:"usage,omitempty"`
	Metadata  map[string]interface{} `json:"metadata,omitempty"`
	Timestamp time.Time              `json:"timestamp"`
}

type ChatStreamResponse struct {
	Content   string                 `json:"content"`
	Delta     string                 `json:"delta"`
	Usage     *TokenUsage            `json:"usage,omitempty"`
	Metadata  map[string]interface{} `json:"metadata,omitempty"`
	Timestamp time.Time              `json:"timestamp"`
	Done      bool                   `json:"done"`
}

type TokenUsage struct {
	PromptTokens     int `json:"prompt_tokens"`
	CompletionTokens int `json:"completion_tokens"`
	TotalTokens      int `json:"total_tokens"`
}

type FunctionParameter struct {
	Name        string      `json:"name"`
	Type        string      `json:"type"`
	Description string      `json:"description"`
	Required    bool        `json:"required"`
	Default     interface{} `json:"default,omitempty"`
}

type AgentConfig struct {
	Name          string   `yaml:"name"`
	Role          string   `yaml:"role,omitempty"`
	Model         string   `yaml:"model"`
	Temperature   *float64 `yaml:"temperature,omitempty"`
	SystemPrompt  string   `yaml:"system_prompt"`
	Plugins       []string `yaml:"plugins,omitempty"`
	RemotePlugins []string `yaml:"remote_plugins,omitempty"`
}
