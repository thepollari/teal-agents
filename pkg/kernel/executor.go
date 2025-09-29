package kernel

import (
	"context"
	"fmt"
	"sync"
)

type DefaultKernel struct {
	plugins   map[string]Plugin
	functions map[string]KernelFunction
	mutex     sync.RWMutex
}

func NewKernel() *DefaultKernel {
	return &DefaultKernel{
		plugins:   make(map[string]Plugin),
		functions: make(map[string]KernelFunction),
	}
}

func (k *DefaultKernel) RegisterPlugin(plugin Plugin) error {
	k.mutex.Lock()
	defer k.mutex.Unlock()

	pluginName := plugin.Name()
	if _, exists := k.plugins[pluginName]; exists {
		return fmt.Errorf("plugin %s already registered", pluginName)
	}

	k.plugins[pluginName] = plugin

	for _, function := range plugin.GetFunctions() {
		functionKey := fmt.Sprintf("%s.%s", pluginName, function.Name())
		k.functions[functionKey] = function
	}

	return nil
}

func (k *DefaultKernel) AddPlugin(plugin Plugin) error {
	return k.RegisterPlugin(plugin)
}

func (k *DefaultKernel) GetFunction(pluginName, functionName string) (KernelFunction, error) {
	k.mutex.RLock()
	defer k.mutex.RUnlock()

	functionKey := fmt.Sprintf("%s.%s", pluginName, functionName)
	function, exists := k.functions[functionKey]
	if !exists {
		return nil, fmt.Errorf("function %s not found", functionKey)
	}

	return function, nil
}

func (k *DefaultKernel) InvokeFunction(ctx context.Context, function KernelFunction, input FunctionInput) (FunctionResult, error) {
	return function.Execute(ctx, input)
}

type DefaultFunctionInput struct {
	values map[string]interface{}
	mutex  sync.RWMutex
}

func NewFunctionInput() *DefaultFunctionInput {
	return &DefaultFunctionInput{
		values: make(map[string]interface{}),
	}
}

func (fi *DefaultFunctionInput) GetValue(key string) (interface{}, bool) {
	fi.mutex.RLock()
	defer fi.mutex.RUnlock()
	value, exists := fi.values[key]
	return value, exists
}

func (fi *DefaultFunctionInput) SetValue(key string, value interface{}) {
	fi.mutex.Lock()
	defer fi.mutex.Unlock()
	fi.values[key] = value
}

func (fi *DefaultFunctionInput) GetAllValues() map[string]interface{} {
	fi.mutex.RLock()
	defer fi.mutex.RUnlock()
	result := make(map[string]interface{})
	for k, v := range fi.values {
		result[k] = v
	}
	return result
}

type DefaultFunctionResult struct {
	value    interface{}
	err      error
	metadata map[string]interface{}
}

func NewFunctionResult(value interface{}, err error) *DefaultFunctionResult {
	return &DefaultFunctionResult{
		value:    value,
		err:      err,
		metadata: make(map[string]interface{}),
	}
}

func (fr *DefaultFunctionResult) GetValue() interface{} {
	return fr.value
}

func (fr *DefaultFunctionResult) GetError() error {
	return fr.err
}

func (fr *DefaultFunctionResult) GetMetadata() map[string]interface{} {
	return fr.metadata
}
