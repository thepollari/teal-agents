package plugins

import (
	"context"
	"fmt"

	"github.com/merck-gen/teal-agents-go/pkg/kernel"
)

type BasePlugin struct {
	name        string
	description string
	functions   []kernel.KernelFunction
}

func NewBasePlugin(name, description string) *BasePlugin {
	return &BasePlugin{
		name:        name,
		description: description,
		functions:   make([]kernel.KernelFunction, 0),
	}
}

func (bp *BasePlugin) Name() string {
	return bp.name
}

func (bp *BasePlugin) Description() string {
	return bp.description
}

func (bp *BasePlugin) GetFunctions() []kernel.KernelFunction {
	return bp.functions
}

func (bp *BasePlugin) AddFunction(function kernel.KernelFunction) {
	bp.functions = append(bp.functions, function)
}

type BaseFunction struct {
	name        string
	description string
	parameters  []kernel.FunctionParameter
	executor    func(ctx context.Context, input kernel.FunctionInput) (kernel.FunctionResult, error)
}

func NewBaseFunction(name, description string, executor func(ctx context.Context, input kernel.FunctionInput) (kernel.FunctionResult, error)) *BaseFunction {
	return &BaseFunction{
		name:        name,
		description: description,
		parameters:  make([]kernel.FunctionParameter, 0),
		executor:    executor,
	}
}

func (bf *BaseFunction) Name() string {
	return bf.name
}

func (bf *BaseFunction) Description() string {
	return bf.description
}

func (bf *BaseFunction) GetParameters() []kernel.FunctionParameter {
	return bf.parameters
}

func (bf *BaseFunction) AddParameter(param kernel.FunctionParameter) {
	bf.parameters = append(bf.parameters, param)
}

func (bf *BaseFunction) Execute(ctx context.Context, input kernel.FunctionInput) (kernel.FunctionResult, error) {
	if bf.executor == nil {
		return kernel.NewFunctionResult(nil, fmt.Errorf("function %s has no executor", bf.name)), fmt.Errorf("function %s has no executor", bf.name)
	}
	return bf.executor(ctx, input)
}
