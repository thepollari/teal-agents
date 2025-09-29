package kernel

import (
	"context"
)

type Kernel interface {
	InvokeFunction(ctx context.Context, function KernelFunction, input FunctionInput) (FunctionResult, error)
	RegisterPlugin(plugin Plugin) error
	GetFunction(pluginName, functionName string) (KernelFunction, error)
	AddPlugin(plugin Plugin) error
}

type Plugin interface {
	Name() string
	Description() string
	GetFunctions() []KernelFunction
}

type KernelFunction interface {
	Name() string
	Description() string
	Execute(ctx context.Context, input FunctionInput) (FunctionResult, error)
	GetParameters() []FunctionParameter
}

type FunctionInput interface {
	GetValue(key string) (interface{}, bool)
	SetValue(key string, value interface{})
	GetAllValues() map[string]interface{}
}

type FunctionResult interface {
	GetValue() interface{}
	GetError() error
	GetMetadata() map[string]interface{}
}

type FunctionParameter struct {
	Name        string `json:"name"`
	Description string `json:"description"`
	Required    bool   `json:"required"`
	Type        string `json:"type"`
}
