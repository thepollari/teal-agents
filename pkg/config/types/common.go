package types

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

type SseEventType string

const (
	SseEventTypeIntermediateTaskResponse SseEventType = "intermediate-task-response"
	SseEventTypePartialResponse          SseEventType = "partial-response"
	SseEventTypeFinalResponse            SseEventType = "final-response"
	SseEventTypeUnknown                  SseEventType = "unknown"
)

type TaskStatus string

const (
	TaskStatusRunning   TaskStatus = "Running"
	TaskStatusPaused    TaskStatus = "Paused"
	TaskStatusCompleted TaskStatus = "Completed"
	TaskStatusFailed    TaskStatus = "Failed"
	TaskStatusCanceled  TaskStatus = "Canceled"
)

type Role string

const (
	RoleUser      Role = "user"
	RoleAssistant Role = "assistant"
	RoleSystem    Role = "system"
)
