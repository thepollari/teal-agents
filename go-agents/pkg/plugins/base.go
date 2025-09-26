package plugins

import (
	"context"
	"reflect"
	"sync"

	"github.com/thepollari/teal-agents/go-agents/pkg/types"
)

type BasePlugin struct {
	name                 string
	description          string
	authorization        string
	extraDataCollector   types.ExtraDataCollector
}

func NewBasePlugin(name, description string) *BasePlugin {
	return &BasePlugin{
		name:        name,
		description: description,
	}
}

func (p *BasePlugin) Initialize(ctx context.Context, authorization string, extraDataCollector types.ExtraDataCollector) error {
	p.authorization = authorization
	p.extraDataCollector = extraDataCollector
	return nil
}

func (p *BasePlugin) GetName() string {
	return p.name
}

func (p *BasePlugin) GetDescription() string {
	return p.description
}

type KernelFunction struct {
	Name        string
	Description string
	Parameters  []types.FunctionParameter
}

type PluginRegistry struct {
	plugins map[string]reflect.Type
	mu      sync.RWMutex
}

func NewPluginRegistry() *PluginRegistry {
	return &PluginRegistry{
		plugins: make(map[string]reflect.Type),
	}
}

func (r *PluginRegistry) Register(name string, pluginType reflect.Type) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.plugins[name] = pluginType
}

func (r *PluginRegistry) Create(ctx context.Context, name string, auth string, collector types.ExtraDataCollector) (types.Plugin, error) {
	r.mu.RLock()
	pluginType, exists := r.plugins[name]
	r.mu.RUnlock()
	
	if !exists {
		return nil, ErrPluginNotFound{Name: name}
	}
	
	pluginValue := reflect.New(pluginType.Elem())
	plugin := pluginValue.Interface().(types.Plugin)
	
	err := plugin.Initialize(ctx, auth, collector)
	if err != nil {
		return nil, err
	}
	
	return plugin, nil
}

func (r *PluginRegistry) ListPlugins() []string {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	names := make([]string, 0, len(r.plugins))
	for name := range r.plugins {
		names = append(names, name)
	}
	return names
}

type ErrPluginNotFound struct {
	Name string
}

func (e ErrPluginNotFound) Error() string {
	return "plugin not found: " + e.Name
}
