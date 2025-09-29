package plugins

import (
	"fmt"
	"sync"

	"github.com/merck-gen/teal-agents-go/pkg/kernel"
)

type Registry struct {
	plugins map[string]kernel.Plugin
	mutex   sync.RWMutex
}

func NewRegistry() *Registry {
	return &Registry{
		plugins: make(map[string]kernel.Plugin),
	}
}

func (r *Registry) Register(plugin kernel.Plugin) error {
	r.mutex.Lock()
	defer r.mutex.Unlock()

	name := plugin.Name()
	if _, exists := r.plugins[name]; exists {
		return fmt.Errorf("plugin %s already registered", name)
	}

	r.plugins[name] = plugin
	return nil
}

func (r *Registry) Get(name string) (kernel.Plugin, error) {
	r.mutex.RLock()
	defer r.mutex.RUnlock()

	plugin, exists := r.plugins[name]
	if !exists {
		return nil, fmt.Errorf("plugin %s not found", name)
	}

	return plugin, nil
}

func (r *Registry) List() []string {
	r.mutex.RLock()
	defer r.mutex.RUnlock()

	names := make([]string, 0, len(r.plugins))
	for name := range r.plugins {
		names = append(names, name)
	}

	return names
}

func (r *Registry) GetAll() map[string]kernel.Plugin {
	r.mutex.RLock()
	defer r.mutex.RUnlock()

	result := make(map[string]kernel.Plugin)
	for name, plugin := range r.plugins {
		result[name] = plugin
	}

	return result
}

func (r *Registry) Unregister(name string) error {
	r.mutex.Lock()
	defer r.mutex.Unlock()

	if _, exists := r.plugins[name]; !exists {
		return fmt.Errorf("plugin %s not found", name)
	}

	delete(r.plugins, name)
	return nil
}

func (r *Registry) Clear() {
	r.mutex.Lock()
	defer r.mutex.Unlock()

	r.plugins = make(map[string]kernel.Plugin)
}

func (r *Registry) Count() int {
	r.mutex.RLock()
	defer r.mutex.RUnlock()

	return len(r.plugins)
}
