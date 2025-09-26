package kernel

import (
	"context"
	"fmt"
	"reflect"
	"strings"
	"sync"

	"github.com/thepollari/teal-agents/go-agents/pkg/types"
)

type Kernel struct {
	config     types.AgentConfig
	chatClient types.ChatCompletionClient
	plugins    map[string]types.Plugin
	functions  map[string]types.KernelFunction
	mu         sync.RWMutex
}

func NewKernel(config types.AgentConfig, chatClient types.ChatCompletionClient) *Kernel {
	return &Kernel{
		config:     config,
		chatClient: chatClient,
		plugins:    make(map[string]types.Plugin),
		functions:  make(map[string]types.KernelFunction),
	}
}

func (k *Kernel) InvokeFunction(ctx context.Context, pluginName, functionName string, args map[string]interface{}) (interface{}, error) {
	k.mu.RLock()
	defer k.mu.RUnlock()
	
	functionKey := fmt.Sprintf("%s.%s", pluginName, functionName)
	function, exists := k.functions[functionKey]
	if !exists {
		return nil, fmt.Errorf("function %s not found", functionKey)
	}
	
	return function.Invoke(ctx, args)
}

func (k *Kernel) GetFunction(pluginName, functionName string) (types.KernelFunction, error) {
	k.mu.RLock()
	defer k.mu.RUnlock()
	
	functionKey := fmt.Sprintf("%s.%s", pluginName, functionName)
	function, exists := k.functions[functionKey]
	if !exists {
		return nil, fmt.Errorf("function %s not found", functionKey)
	}
	
	return function, nil
}

func (k *Kernel) AddPlugin(ctx context.Context, plugin types.Plugin) error {
	k.mu.Lock()
	defer k.mu.Unlock()
	
	pluginName := plugin.GetName()
	k.plugins[pluginName] = plugin
	
	err := k.discoverPluginFunctions(plugin)
	if err != nil {
		return fmt.Errorf("failed to discover functions for plugin %s: %w", pluginName, err)
	}
	
	return nil
}

func (k *Kernel) GetPlugin(name string) (types.Plugin, error) {
	k.mu.RLock()
	defer k.mu.RUnlock()
	
	plugin, exists := k.plugins[name]
	if !exists {
		return nil, fmt.Errorf("plugin %s not found", name)
	}
	
	return plugin, nil
}

func (k *Kernel) ListPlugins() []string {
	k.mu.RLock()
	defer k.mu.RUnlock()
	
	names := make([]string, 0, len(k.plugins))
	for name := range k.plugins {
		names = append(names, name)
	}
	return names
}

func (k *Kernel) ListFunctions() []string {
	k.mu.RLock()
	defer k.mu.RUnlock()
	
	names := make([]string, 0, len(k.functions))
	for name := range k.functions {
		names = append(names, name)
	}
	return names
}

func (k *Kernel) GetChatClient() types.ChatCompletionClient {
	return k.chatClient
}

func (k *Kernel) GetConfig() types.AgentConfig {
	return k.config
}

func (k *Kernel) discoverPluginFunctions(plugin types.Plugin) error {
	pluginName := plugin.GetName()
	
	if provider, ok := plugin.(types.FunctionProvider); ok {
		functions := provider.GetFunctions()
		for _, function := range functions {
			functionKey := fmt.Sprintf("%s.%s", pluginName, function.GetName())
			k.functions[functionKey] = function
		}
		return nil
	}
	
	pluginValue := reflect.ValueOf(plugin)
	pluginType := reflect.TypeOf(plugin)
	
	if pluginType.Kind() == reflect.Ptr {
		pluginType = pluginType.Elem()
		pluginValue = pluginValue.Elem()
	}
	
	for i := 0; i < pluginType.NumMethod(); i++ {
		method := pluginType.Method(i)
		methodValue := pluginValue.Method(i)
		
		if !method.IsExported() || isInterfaceMethod(method.Name) {
			continue
		}
		
		if isKernelFunction(method.Type) {
			function := &ReflectionKernelFunction{
				name:        strings.ToLower(method.Name),
				description: fmt.Sprintf("Function %s from plugin %s", method.Name, pluginName),
				method:      methodValue,
				methodType:  method.Type,
			}
			
			functionKey := fmt.Sprintf("%s.%s", pluginName, function.GetName())
			k.functions[functionKey] = function
		}
	}
	
	return nil
}

func isInterfaceMethod(methodName string) bool {
	interfaceMethods := []string{
		"Initialize", "GetName", "GetDescription", // Plugin interface
		"String", "Error",                         // Standard Go interfaces
	}
	
	for _, interfaceMethod := range interfaceMethods {
		if methodName == interfaceMethod {
			return true
		}
	}
	return false
}

func isKernelFunction(methodType reflect.Type) bool {
	if methodType.NumIn() != 3 || methodType.NumOut() != 2 {
		return false
	}
	
	if methodType.In(1).String() != "context.Context" {
		return false
	}
	
	if methodType.In(2).String() != "map[string]interface {}" {
		return false
	}
	
	if methodType.Out(0).String() != "interface {}" {
		return false
	}
	
	if methodType.Out(1).String() != "error" {
		return false
	}
	
	return true
}

type ReflectionKernelFunction struct {
	name        string
	description string
	method      reflect.Value
	methodType  reflect.Type
	parameters  []types.FunctionParameter
}

func (f *ReflectionKernelFunction) Invoke(ctx context.Context, args map[string]interface{}) (interface{}, error) {
	callArgs := []reflect.Value{
		reflect.ValueOf(ctx),
		reflect.ValueOf(args),
	}
	
	results := f.method.Call(callArgs)
	
	result := results[0].Interface()
	
	if !results[1].IsNil() {
		err := results[1].Interface().(error)
		return result, err
	}
	
	return result, nil
}

func (f *ReflectionKernelFunction) GetName() string {
	return f.name
}

func (f *ReflectionKernelFunction) GetDescription() string {
	return f.description
}

func (f *ReflectionKernelFunction) GetParameters() []types.FunctionParameter {
	return f.parameters
}
