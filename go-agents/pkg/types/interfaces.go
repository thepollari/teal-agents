package types

import (
	"context"
)

type Handler interface {
	Invoke(ctx context.Context, inputs map[string]interface{}) (*InvokeResponse, error)
	InvokeStream(ctx context.Context, inputs map[string]interface{}) (<-chan StreamResponse, error)
}

type Plugin interface {
	Initialize(ctx context.Context, authorization string, extraDataCollector ExtraDataCollector) error
	GetName() string
	GetDescription() string
}

type ChatCompletionFactory interface {
	GetChatCompletion(ctx context.Context, modelName, serviceID string) (ChatCompletionClient, error)
	GetModelType(ctx context.Context, modelName string) (ModelType, error)
	SupportsStructuredOutput(ctx context.Context, modelName string) bool
}

type ChatCompletionClient interface {
	Complete(ctx context.Context, messages []ChatMessage) (*ChatResponse, error)
	CompleteStream(ctx context.Context, messages []ChatMessage) (<-chan ChatStreamResponse, error)
}

type KernelBuilder interface {
	BuildKernel(ctx context.Context, config AgentConfig) (Kernel, error)
	AddPlugins(ctx context.Context, kernel Kernel, plugins []string) error
	SetPluginCatalog(catalog interface{})
}

type Kernel interface {
	InvokeFunction(ctx context.Context, pluginName, functionName string, args map[string]interface{}) (interface{}, error)
	GetFunction(pluginName, functionName string) (KernelFunction, error)
	AddPlugin(ctx context.Context, plugin Plugin) error
	GetChatClient() ChatCompletionClient
}

type KernelFunction interface {
	Invoke(ctx context.Context, args map[string]interface{}) (interface{}, error)
	GetName() string
	GetDescription() string
	GetParameters() []FunctionParameter
}

type ExtraDataCollector interface {
	Collect(ctx context.Context, data map[string]interface{}) error
}

type FunctionProvider interface {
	GetFunctions() []KernelFunction
}
