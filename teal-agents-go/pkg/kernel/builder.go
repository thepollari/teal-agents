package kernel

import (
	"fmt"
	"log"

	"github.com/thepollari/teal-agents-go/pkg/types"
)

type KernelBuilder struct {
	appConfig             types.AppConfig
	chatCompletionBuilder *ChatCompletionBuilder
}

func NewKernelBuilder(appConfig types.AppConfig) *KernelBuilder {
	return &KernelBuilder{
		appConfig:             appConfig,
		chatCompletionBuilder: NewChatCompletionBuilder(appConfig),
	}
}

func (kb *KernelBuilder) Build(modelName, serviceID string, plugins []types.Plugin) (*Kernel, error) {
	chatCompletion, err := kb.chatCompletionBuilder.GetChatCompletionForModel(serviceID, modelName)
	if err != nil {
		return nil, fmt.Errorf("failed to create chat completion service: %w", err)
	}

	kernel := &Kernel{
		chatCompletion: chatCompletion,
		plugins:        make(map[string]types.Plugin),
		functions:      make(map[string]types.Function),
		modelName:      modelName,
		serviceID:      serviceID,
	}

	for _, plugin := range plugins {
		if err := kernel.AddPlugin(plugin); err != nil {
			return nil, fmt.Errorf("failed to add plugin %s: %w", plugin.GetName(), err)
		}
	}

	return kernel, nil
}

func (kb *KernelBuilder) GetModelType(modelName string) types.ModelType {
	return kb.chatCompletionBuilder.GetModelTypeForName(modelName)
}

func (kb *KernelBuilder) ModelSupportsStructuredOutput(modelName string) bool {
	return kb.chatCompletionBuilder.ModelSupportsStructuredOutput(modelName)
}

func (kb *KernelBuilder) LoadRemotePlugins(pluginConfigs []types.PluginConfig) ([]types.Plugin, error) {
	var plugins []types.Plugin

	for _, config := range pluginConfigs {
		if config.Type == "remote" {
			plugin, err := kb.loadRemotePlugin(config)
			if err != nil {
				log.Printf("Warning: Failed to load remote plugin %s: %v", config.Name, err)
				continue
			}
			plugins = append(plugins, plugin)
		}
	}

	return plugins, nil
}

func (kb *KernelBuilder) loadRemotePlugin(config types.PluginConfig) (types.Plugin, error) {
	if config.URL == nil {
		return nil, fmt.Errorf("remote plugin %s missing URL", config.Name)
	}

	loader := NewRemotePluginLoader()
	plugin, err := loader.LoadFromURL(*config.URL, config.Name)
	if err != nil {
		return nil, fmt.Errorf("failed to load remote plugin from %s: %w", *config.URL, err)
	}

	return plugin, nil
}

func (kb *KernelBuilder) LoadLocalPlugins(pluginConfigs []types.PluginConfig) ([]types.Plugin, error) {
	var plugins []types.Plugin

	for _, config := range pluginConfigs {
		if config.Type == "local" {
			plugin, err := kb.loadLocalPlugin(config)
			if err != nil {
				log.Printf("Warning: Failed to load local plugin %s: %v", config.Name, err)
				continue
			}
			plugins = append(plugins, plugin)
		}
	}

	return plugins, nil
}

func (kb *KernelBuilder) loadLocalPlugin(config types.PluginConfig) (types.Plugin, error) {
	if config.Path == nil {
		return nil, fmt.Errorf("local plugin %s missing path", config.Name)
	}

	loader := NewLocalPluginLoader()
	plugin, err := loader.LoadFromPath(*config.Path, config.Name)
	if err != nil {
		return nil, fmt.Errorf("failed to load local plugin from %s: %w", *config.Path, err)
	}

	return plugin, nil
}
