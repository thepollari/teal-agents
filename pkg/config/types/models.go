package types

import "time"

type ExtraDataElement struct {
	Key   string `json:"key" yaml:"key"`
	Value string `json:"value" yaml:"value"`
}

type ExtraData struct {
	Items []ExtraDataElement `json:"items" yaml:"items"`
}

type TokenUsage struct {
	CompletionTokens int `json:"completion_tokens" yaml:"completion_tokens"`
	PromptTokens     int `json:"prompt_tokens" yaml:"prompt_tokens"`
	TotalTokens      int `json:"total_tokens" yaml:"total_tokens"`
}

type MultiModalItem struct {
	ContentType ContentType `json:"content_type" yaml:"content_type"`
	Content     string      `json:"content" yaml:"content"`
}

type HistoryMessage struct {
	Role    Role   `json:"role" yaml:"role"`
	Content string `json:"content" yaml:"content"`
}

type HistoryMultiModalMessage struct {
	Role  Role             `json:"role" yaml:"role"`
	Items []MultiModalItem `json:"items" yaml:"items"`
}

type BaseInput struct {
	ChatHistory []HistoryMessage `json:"chat_history,omitempty" yaml:"chat_history,omitempty"`
}

type BaseMultiModalInput struct {
	SessionID   *string                    `json:"session_id,omitempty" yaml:"session_id,omitempty"`
	ChatHistory []HistoryMultiModalMessage `json:"chat_history,omitempty" yaml:"chat_history,omitempty"`
}

type UserMessage struct {
	SessionID   *string            `json:"session_id,omitempty" yaml:"session_id,omitempty"`
	TaskID      *string            `json:"task_id,omitempty" yaml:"task_id,omitempty"`
	Items       []MultiModalItem   `json:"items" yaml:"items"`
	UserContext *map[string]string `json:"user_context,omitempty" yaml:"user_context,omitempty"`
}

type AgentTaskItem struct {
	TaskID           string           `json:"task_id" yaml:"task_id"`
	Role             Role             `json:"role" yaml:"role"`
	Item             MultiModalItem   `json:"item" yaml:"item"`
	RequestID        string           `json:"request_id" yaml:"request_id"`
	Updated          time.Time        `json:"updated" yaml:"updated"`
	PendingToolCalls []map[string]any `json:"pending_tool_calls,omitempty" yaml:"pending_tool_calls,omitempty"`
	ChatHistory      any              `json:"chat_history,omitempty" yaml:"chat_history,omitempty"`
}

type AgentTask struct {
	TaskID      string          `json:"task_id" yaml:"task_id"`
	SessionID   string          `json:"session_id" yaml:"session_id"`
	UserID      string          `json:"user_id" yaml:"user_id"`
	Items       []AgentTaskItem `json:"items" yaml:"items"`
	CreatedAt   time.Time       `json:"created_at" yaml:"created_at"`
	LastUpdated time.Time       `json:"last_updated" yaml:"last_updated"`
	Status      TaskStatus      `json:"status" yaml:"status"`
}

type TealAgentsResponse struct {
	SessionID  string     `json:"session_id" yaml:"session_id"`
	TaskID     string     `json:"task_id" yaml:"task_id"`
	RequestID  string     `json:"request_id" yaml:"request_id"`
	Output     string     `json:"output" yaml:"output"`
	Source     *string    `json:"source,omitempty" yaml:"source,omitempty"`
	TokenUsage TokenUsage `json:"token_usage" yaml:"token_usage"`
	ExtraData  *ExtraData `json:"extra_data,omitempty" yaml:"extra_data,omitempty"`
}

type TealAgentsPartialResponse struct {
	SessionID     string  `json:"session_id" yaml:"session_id"`
	TaskID        string  `json:"task_id" yaml:"task_id"`
	RequestID     string  `json:"request_id" yaml:"request_id"`
	OutputPartial string  `json:"output_partial" yaml:"output_partial"`
	Source        *string `json:"source,omitempty" yaml:"source,omitempty"`
}

type HitlResponse struct {
	TaskID       string           `json:"task_id" yaml:"task_id"`
	SessionID    string           `json:"session_id" yaml:"session_id"`
	RequestID    string           `json:"request_id" yaml:"request_id"`
	Message      string           `json:"message" yaml:"message"`
	ApprovalURL  string           `json:"approval_url" yaml:"approval_url"`
	RejectionURL string           `json:"rejection_url" yaml:"rejection_url"`
	ToolCalls    []map[string]any `json:"tool_calls" yaml:"tool_calls"`
}

type StateResponse struct {
	SessionID string     `json:"session_id" yaml:"session_id"`
	TaskID    string     `json:"task_id" yaml:"task_id"`
	RequestID string     `json:"request_id" yaml:"request_id"`
	Status    TaskStatus `json:"status" yaml:"status"`
	Content   any        `json:"content,omitempty" yaml:"content,omitempty"`
}

type ResumeRequest struct {
	Action string `json:"action" yaml:"action"`
}
