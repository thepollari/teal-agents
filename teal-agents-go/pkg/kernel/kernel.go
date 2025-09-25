package kernel

import (
	"context"
	"fmt"

	"github.com/thepollari/teal-agents-go/pkg/types"
)

type Kernel struct {
	chatCompletion types.ChatCompletionClientBase
	plugins        map[string]types.Plugin
	functions      map[string]types.Function
	modelName      string
	serviceID      string
}

func (k *Kernel) AddPlugin(plugin types.Plugin) error {
	pluginName := plugin.GetName()

	if _, exists := k.plugins[pluginName]; exists {
		return fmt.Errorf("plugin %s already exists", pluginName)
	}

	k.plugins[pluginName] = plugin

	for _, function := range plugin.GetFunctions() {
		functionKey := fmt.Sprintf("%s.%s", pluginName, function.GetName())
		k.functions[functionKey] = function
	}

	return nil
}

func (k *Kernel) GetPlugin(name string) (types.Plugin, bool) {
	plugin, exists := k.plugins[name]
	return plugin, exists
}

func (k *Kernel) GetFunction(name string) (types.Function, bool) {
	function, exists := k.functions[name]
	return function, exists
}

func (k *Kernel) ListPlugins() []string {
	var names []string
	for name := range k.plugins {
		names = append(names, name)
	}
	return names
}

func (k *Kernel) ListFunctions() []string {
	var names []string
	for name := range k.functions {
		names = append(names, name)
	}
	return names
}

func (k *Kernel) InvokeFunction(ctx context.Context, functionName string, arguments map[string]interface{}) (interface{}, error) {
	function, exists := k.functions[functionName]
	if !exists {
		return nil, fmt.Errorf("function %s not found", functionName)
	}

	return function.Invoke(ctx, k, arguments)
}

func (k *Kernel) SelectAIService(arguments map[string]interface{}) (types.ChatCompletionClientBase, interface{}, error) {
	settings := map[string]interface{}{
		"model_name":  k.modelName,
		"service_id":  k.serviceID,
		"temperature": 0.7, // Default temperature
	}

	for key, value := range arguments {
		settings[key] = value
	}

	return k.chatCompletion, settings, nil
}

func (k *Kernel) GetModelName() string {
	return k.modelName
}

func (k *Kernel) GetServiceID() string {
	return k.serviceID
}
