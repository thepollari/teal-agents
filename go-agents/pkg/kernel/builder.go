package kernel

import (
	"context"
	"fmt"

	"github.com/thepollari/teal-agents/go-agents/pkg/config"
	"github.com/thepollari/teal-agents/go-agents/pkg/completion"
	"github.com/thepollari/teal-agents/go-agents/pkg/plugins"
	"github.com/thepollari/teal-agents/go-agents/pkg/types"
)

type KernelBuilder struct {
	pluginRegistry *plugins.PluginRegistry
	chatFactory    types.ChatCompletionFactory
}

func NewKernelBuilder() types.KernelBuilder {
	appConfig := &config.AppConfig{
		OpenAIAPIKey: "", // Will be loaded from environment
		LogLevel:     "info",
		Port:         8000,
	}
	
	return &KernelBuilder{
		pluginRegistry: plugins.NewPluginRegistry(),
		chatFactory:    completion.NewDefaultChatCompletionFactory(appConfig),
	}
}

func (kb *KernelBuilder) BuildKernel(ctx context.Context, config types.AgentConfig) (types.Kernel, error) {
	chatClient, err := kb.chatFactory.GetChatCompletion(ctx, config.Model, "default")
	if err != nil {
		return nil, fmt.Errorf("failed to create chat completion client: %w", err)
	}
	
	kernel := &Kernel{
		config:     config,
		chatClient: chatClient,
		plugins:    make(map[string]types.Plugin),
		functions:  make(map[string]types.KernelFunction),
	}
	
	return kernel, nil
}

func (kb *KernelBuilder) AddPlugins(ctx context.Context, kernel types.Kernel, pluginNames []string) error {
	for _, pluginName := range pluginNames {
		plugin, err := kb.pluginRegistry.Create(ctx, pluginName, "", nil)
		if err != nil {
			return fmt.Errorf("failed to create plugin %s: %w", pluginName, err)
		}
		
		err = kernel.AddPlugin(ctx, plugin)
		if err != nil {
			return fmt.Errorf("failed to add plugin %s to kernel: %w", pluginName, err)
		}
	}
	
	return nil
}
