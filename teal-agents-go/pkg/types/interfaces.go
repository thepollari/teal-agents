package types

import (
	"context"
)

type BaseHandler interface {
	Invoke(ctx context.Context, inputs map[string]interface{}) (*InvokeResponse, error)
	InvokeStream(ctx context.Context, inputs map[string]interface{}) (<-chan PartialResponse, error)
}

type ChatCompletionFactory interface {
	GetChatCompletionForModelName(modelName, serviceID string) (ChatCompletionClientBase, error)
	GetModelTypeForName(modelName string) ModelType
	ModelSupportsStructuredOutput(modelName string) bool
	GetConfigs() []Config
}

type ChatCompletionClientBase interface {
	GetChatMessageContents(ctx context.Context, chatHistory ChatHistory, settings interface{}, kernel interface{}, arguments map[string]interface{}) ([]ChatMessageContent, error)
}

type Plugin interface {
	GetName() string
	GetDescription() string
	GetFunctions() []Function
}

type Function interface {
	GetName() string
	GetDescription() string
	Invoke(ctx context.Context, kernel interface{}, arguments map[string]interface{}) (interface{}, error)
}
