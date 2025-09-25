package types

import (
	"time"
)

type TokenUsage struct {
	CompletionTokens int `json:"completion_tokens"`
	PromptTokens     int `json:"prompt_tokens"`
	TotalTokens      int `json:"total_tokens"`
}

type InvokeResponse struct {
	SessionID      *string     `json:"session_id,omitempty"`
	Source         *string     `json:"source,omitempty"`
	RequestID      *string     `json:"request_id,omitempty"`
	TokenUsage     TokenUsage  `json:"token_usage"`
	ExtraData      interface{} `json:"extra_data,omitempty"`
	OutputRaw      *string     `json:"output_raw,omitempty"`
	OutputPydantic interface{} `json:"output_pydantic,omitempty"`
}

type PartialResponse struct {
	SessionID     *string `json:"session_id,omitempty"`
	Source        *string `json:"source,omitempty"`
	RequestID     *string `json:"request_id,omitempty"`
	OutputPartial string  `json:"output_partial"`
}

type IntermediateTaskResponse struct {
	TaskNo   int             `json:"task_no"`
	TaskName string          `json:"task_name"`
	Response *InvokeResponse `json:"response"`
}

type ModelType string

const (
	ModelTypeOpenAI    ModelType = "openai"
	ModelTypeAnthropic ModelType = "anthropic"
	ModelTypeGoogle    ModelType = "google"
)

type ContentType string

const (
	ContentTypeImage ContentType = "image"
	ContentTypeText  ContentType = "text"
)

type MultiModalItem struct {
	ContentType ContentType `json:"content_type"`
	Content     string      `json:"content"`
}

type HistoryMessage struct {
	Role    string `json:"role"` // "user" or "assistant"
	Content string `json:"content"`
}

type HistoryMultiModalMessage struct {
	Role  string           `json:"role"` // "user" or "assistant"
	Items []MultiModalItem `json:"items"`
}

type BaseInput struct {
	ChatHistory []HistoryMessage `json:"chat_history,omitempty"`
}

type BaseInputWithUserContext struct {
	ChatHistory []HistoryMessage  `json:"chat_history,omitempty"`
	UserContext map[string]string `json:"user_context,omitempty"`
}

type BaseMultiModalInput struct {
	SessionID   *string                    `json:"session_id,omitempty"`
	ChatHistory []HistoryMultiModalMessage `json:"chat_history,omitempty"`
}

type ChatHistory []ChatMessageContent

type ChatMessageContent struct {
	Role      string                `json:"role"`
	Content   string                `json:"content"`
	Items     []FunctionCallContent `json:"items,omitempty"`
	Timestamp time.Time             `json:"timestamp"`
}

type FunctionCallContent struct {
	ID        string                 `json:"id"`
	Name      string                 `json:"name"`
	Arguments map[string]interface{} `json:"arguments"`
}

type Config struct {
	EnvName      string `json:"env_name"`
	DefaultValue string `json:"default_value"`
	Description  string `json:"description"`
}

type AppConfig interface {
	Get(key string) string
	Set(key, value string)
	AddConfigs(configs []Config)
}
