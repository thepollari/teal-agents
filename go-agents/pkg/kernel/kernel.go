package kernel

import (
	"context"
	"fmt"
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
