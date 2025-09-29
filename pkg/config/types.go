package config

import (
	"time"
)

type BaseConfig struct {
	APIVersion  string           `yaml:"apiVersion" json:"apiVersion"`
	Kind        string           `yaml:"kind,omitempty" json:"kind,omitempty"`
	Name        string           `yaml:"name,omitempty" json:"name,omitempty"`
	ServiceName string           `yaml:"service_name,omitempty" json:"service_name,omitempty"`
	Version     interface{}      `yaml:"version" json:"version"`
	Description string           `yaml:"description,omitempty" json:"description,omitempty"`
	Metadata    *ConfigMetadata  `yaml:"metadata,omitempty" json:"metadata,omitempty"`
	InputType   string           `yaml:"input_type,omitempty" json:"input_type,omitempty"`
	OutputType  string           `yaml:"output_type,omitempty" json:"output_type,omitempty"`
	Spec        *AgentSpec       `yaml:"spec,omitempty" json:"spec,omitempty"`
}

type ConfigMetadata struct {
	Description      string        `yaml:"description" json:"description"`
	Skills           []ConfigSkill `yaml:"skills" json:"skills"`
	DocumentationURL string        `yaml:"documentation_url,omitempty" json:"documentation_url,omitempty"`
}

type ConfigSkill struct {
	ID          string   `yaml:"id" json:"id"`
	Name        string   `yaml:"name" json:"name"`
	Description string   `yaml:"description" json:"description"`
	Tags        []string `yaml:"tags" json:"tags"`
	Examples    []string `yaml:"examples,omitempty" json:"examples,omitempty"`
	InputModes  []string `yaml:"input_modes,omitempty" json:"input_modes,omitempty"`
	OutputModes []string `yaml:"output_modes,omitempty" json:"output_modes,omitempty"`
}

type AgentSpec struct {
	Agents []AgentConfig `yaml:"agents" json:"agents"`
	Tasks  []TaskConfig  `yaml:"tasks" json:"tasks"`
}

type AgentConfig struct {
	Name         string   `yaml:"name" json:"name"`
	Role         string   `yaml:"role,omitempty" json:"role,omitempty"`
	Model        string   `yaml:"model" json:"model"`
	SystemPrompt string   `yaml:"system_prompt,omitempty" json:"system_prompt,omitempty"`
	Plugins      []string `yaml:"plugins,omitempty" json:"plugins,omitempty"`
}

type TaskConfig struct {
	Name         string `yaml:"name" json:"name"`
	TaskNo       int    `yaml:"task_no" json:"task_no"`
	Description  string `yaml:"description" json:"description"`
	Instructions string `yaml:"instructions,omitempty" json:"instructions,omitempty"`
	Agent        string `yaml:"agent" json:"agent"`
}

type TokenUsage struct {
	CompletionTokens int `json:"completion_tokens"`
	PromptTokens     int `json:"prompt_tokens"`
	TotalTokens      int `json:"total_tokens"`
}

type InvokeResponse struct {
	SessionID      string                 `json:"session_id,omitempty"`
	Source         string                 `json:"source,omitempty"`
	RequestID      string                 `json:"request_id,omitempty"`
	TokenUsage     TokenUsage             `json:"token_usage"`
	ExtraData      map[string]interface{} `json:"extra_data,omitempty"`
	OutputRaw      string                 `json:"output_raw,omitempty"`
	OutputPydantic interface{}            `json:"output_pydantic,omitempty"`
}

type PartialResponse struct {
	SessionID     string `json:"session_id,omitempty"`
	Source        string `json:"source,omitempty"`
	RequestID     string `json:"request_id,omitempty"`
	OutputPartial string `json:"output_partial"`
}

type IntermediateTaskResponse struct {
	TaskNo   int             `json:"task_no"`
	TaskName string          `json:"task_name"`
	Response *InvokeResponse `json:"response"`
}

type HistoryMessage struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type BaseInput struct {
	ChatHistory []HistoryMessage `json:"chat_history,omitempty"`
}

type MultiModalItem struct {
	ContentType string `json:"content_type"`
	Content     string `json:"content"`
}

type BaseMultiModalInput struct {
	SessionID   string               `json:"session_id,omitempty"`
	ChatHistory []HistoryMessage     `json:"chat_history,omitempty"`
	Items       []MultiModalItem     `json:"items,omitempty"`
}

type UserMessage struct {
	SessionID string             `json:"session_id,omitempty"`
	TaskID    string             `json:"task_id,omitempty"`
	Items     []MultiModalItem   `json:"items"`
	Context   map[string]string  `json:"context,omitempty"`
}

type StateResponse struct {
	SessionID string `json:"session_id"`
	TaskID    string `json:"task_id"`
	RequestID string `json:"request_id"`
	Status    string `json:"status"`
	Content   string `json:"content"`
}

type AgentTask struct {
	TaskID    string    `json:"task_id"`
	SessionID string    `json:"session_id"`
	UserID    string    `json:"user_id"`
	Status    string    `json:"status"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}
