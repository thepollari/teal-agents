package kernel

import (
	"context"
	"fmt"

	"github.com/thepollari/teal-agents/go-agents/pkg/config"
	"github.com/thepollari/teal-agents/go-agents/pkg/completion"
	"github.com/thepollari/teal-agents/go-agents/pkg/logging"
	"github.com/thepollari/teal-agents/go-agents/pkg/plugins"
	"github.com/thepollari/teal-agents/go-agents/pkg/plugins/remote"
	_ "github.com/thepollari/teal-agents/go-agents/pkg/plugins/university"
	"github.com/thepollari/teal-agents/go-agents/pkg/types"
)

type KernelBuilder struct {
	pluginRegistry *plugins.PluginRegistry
	chatFactory    types.ChatCompletionFactory
	pluginCatalog  *remote.PluginCatalog
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

func (kb *KernelBuilder) BuildKernel(ctx context.Context, agentConfig types.AgentConfig) (types.Kernel, error) {
	logger := logging.WithContext(ctx)
	logger.Info("Building kernel for agent", "agent", agentConfig.Name, "model", agentConfig.Model)
	
	configAgentConfig := config.AgentConfig{
		Name:          agentConfig.Name,
		Role:          agentConfig.Role,
		Model:         agentConfig.Model,
		Temperature:   agentConfig.Temperature,
		SystemPrompt:  agentConfig.SystemPrompt,
		Plugins:       agentConfig.Plugins,
		RemotePlugins: agentConfig.RemotePlugins,
		MaxTokens:     agentConfig.MaxTokens,
	}
	err := config.ValidateAgentConfig(configAgentConfig)
	if err != nil {
		logger.Error("Agent configuration validation failed", "error", err.Error())
		return nil, fmt.Errorf("invalid agent configuration: %w", err)
	}
	
	chatClient, err := kb.chatFactory.GetChatCompletion(ctx, agentConfig.Model, "default")
	if err != nil {
		logger.Error("Failed to create chat client", "error", err.Error(), "model", agentConfig.Model)
		return nil, fmt.Errorf("failed to create chat completion client: %w", err)
	}
	
	kernel := &Kernel{
		config:     agentConfig,
		chatClient: chatClient,
		plugins:    make(map[string]types.Plugin),
		functions:  make(map[string]types.KernelFunction),
	}
	
	for _, pluginName := range agentConfig.Plugins {
		err := kb.loadPlugin(ctx, kernel, pluginName)
		if err != nil {
			logger.Error("Failed to load plugin", "plugin", pluginName, "error", err.Error())
			return nil, fmt.Errorf("failed to load plugin %s: %w", pluginName, err)
		}
	}
	
	if len(agentConfig.RemotePlugins) > 0 {
		err := kb.loadRemotePlugins(ctx, kernel, agentConfig.RemotePlugins)
		if err != nil {
			logger.Error("Failed to load remote plugins", "error", err.Error())
			return nil, fmt.Errorf("failed to load remote plugins: %w", err)
		}
	}
	
	logger.Info("Kernel built successfully", "agent", agentConfig.Name, "plugins", len(agentConfig.Plugins), "remote_plugins", len(agentConfig.RemotePlugins))
	return kernel, nil
}

func (kb *KernelBuilder) loadPlugin(ctx context.Context, kernel types.Kernel, pluginName string) error {
	logger := logging.WithContext(ctx)
	
	plugin, err := kb.pluginRegistry.Create(ctx, pluginName, "", nil)
	if err != nil {
		logger.Error("Plugin creation failed", "plugin", pluginName, "error", err.Error())
		return fmt.Errorf("failed to create plugin %s: %w", pluginName, err)
	}
	
	err = kernel.AddPlugin(ctx, plugin)
	if err != nil {
		logging.LogPluginLoad(ctx, pluginName, err)
		return fmt.Errorf("failed to add plugin %s to kernel: %w", pluginName, err)
	}
	
	logging.LogPluginLoad(ctx, pluginName, nil)
	return nil
}

func (kb *KernelBuilder) loadRemotePlugins(ctx context.Context, kernel types.Kernel, remotePlugins []string) error {
	if kb.pluginCatalog == nil {
		return fmt.Errorf("plugin catalog not initialized")
	}
	
	for _, pluginName := range remotePlugins {
		plugin, err := kb.pluginCatalog.LoadPlugin(ctx, pluginName)
		if err != nil {
			logging.LogPluginLoad(ctx, pluginName, err)
			return fmt.Errorf("failed to load remote plugin %s: %w", pluginName, err)
		}
		
		err = kernel.AddPlugin(ctx, plugin)
		if err != nil {
			logging.LogPluginLoad(ctx, pluginName, err)
			return fmt.Errorf("failed to add remote plugin %s: %w", pluginName, err)
		}
		
		logging.LogPluginLoad(ctx, pluginName, nil)
	}
	
	return nil
}

func (kb *KernelBuilder) AddPlugins(ctx context.Context, kernel types.Kernel, pluginNames []string) error {
	logger := logging.WithContext(ctx)
	logger.Info("Adding plugins to kernel", "plugins", pluginNames)
	
	for _, pluginName := range pluginNames {
		err := kb.loadPlugin(ctx, kernel, pluginName)
		if err != nil {
			return err
		}
	}
	
	return nil
}

func (kb *KernelBuilder) SetPluginCatalog(catalog interface{}) {
	if c, ok := catalog.(*remote.PluginCatalog); ok {
		kb.pluginCatalog = c
	}
}
