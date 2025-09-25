package agents

import (
	"fmt"

	"github.com/thepollari/teal-agents-go/pkg/kernel"
	"github.com/thepollari/teal-agents-go/pkg/types"
)

type AgentBuilder struct {
	kernelBuilder *kernel.KernelBuilder
}

func NewAgentBuilder(appConfig types.AppConfig) *AgentBuilder {
	return &AgentBuilder{
		kernelBuilder: kernel.NewKernelBuilder(appConfig),
	}
}

func (ab *AgentBuilder) BuildAgent(config types.AgentConfig, extraDataCollector *ExtraDataCollector) (*SKAgent, error) {
	var plugins []types.Plugin

	localPlugins, err := ab.kernelBuilder.LoadLocalPlugins(config.Plugins)
	if err != nil {
		return nil, fmt.Errorf("failed to load local plugins: %w", err)
	}
	plugins = append(plugins, localPlugins...)

	remotePlugins, err := ab.kernelBuilder.LoadRemotePlugins(config.Plugins)
	if err != nil {
		return nil, fmt.Errorf("failed to load remote plugins: %w", err)
	}
	plugins = append(plugins, remotePlugins...)

	kernel, err := ab.kernelBuilder.Build(config.ModelName, config.ServiceID, plugins)
	if err != nil {
		return nil, fmt.Errorf("failed to build kernel: %w", err)
	}

	supportsStructuredOutput := ab.kernelBuilder.ModelSupportsStructuredOutput(config.ModelName)

	modelType := ab.kernelBuilder.GetModelType(config.ModelName)

	agent := &SKAgent{
		kernel:                   kernel,
		modelType:                modelType,
		supportsStructuredOutput: supportsStructuredOutput,
		extraDataCollector:       extraDataCollector,
		executionSettings:        config.Settings,
	}

	return agent, nil
}

func (ab *AgentBuilder) GetModelType(modelName string) types.ModelType {
	return ab.kernelBuilder.GetModelType(modelName)
}

func (ab *AgentBuilder) ModelSupportsStructuredOutput(modelName string) bool {
	return ab.kernelBuilder.ModelSupportsStructuredOutput(modelName)
}

type ExtraDataCollector struct {
	extraData map[string]interface{}
}

func NewExtraDataCollector() *ExtraDataCollector {
	return &ExtraDataCollector{
		extraData: make(map[string]interface{}),
	}
}

func (edc *ExtraDataCollector) AddExtraData(key string, value interface{}) {
	edc.extraData[key] = value
}

func (edc *ExtraDataCollector) AddExtraDataItems(items map[string]interface{}) {
	for key, value := range items {
		edc.extraData[key] = value
	}
}

func (edc *ExtraDataCollector) GetExtraData() map[string]interface{} {
	return edc.extraData
}

func (edc *ExtraDataCollector) Clear() {
	edc.extraData = make(map[string]interface{})
}
