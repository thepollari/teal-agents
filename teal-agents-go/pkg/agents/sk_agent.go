package agents

import (
	"context"

	"github.com/thepollari/teal-agents-go/pkg/kernel"
	"github.com/thepollari/teal-agents-go/pkg/types"
)

type SKAgent struct {
	kernel                   *kernel.Kernel
	modelType                types.ModelType
	supportsStructuredOutput bool
	extraDataCollector       *ExtraDataCollector
	executionSettings        map[string]interface{}
}

func (ska *SKAgent) GetKernel() *kernel.Kernel {
	return ska.kernel
}

func (ska *SKAgent) GetModelType() types.ModelType {
	return ska.modelType
}

func (ska *SKAgent) SupportsStructuredOutput() bool {
	return ska.supportsStructuredOutput
}

func (ska *SKAgent) GetExtraDataCollector() *ExtraDataCollector {
	return ska.extraDataCollector
}

func (ska *SKAgent) GetExecutionSettings() map[string]interface{} {
	return ska.executionSettings
}

func (ska *SKAgent) InvokeFunction(ctx context.Context, functionName string, arguments map[string]interface{}) (interface{}, error) {
	return ska.kernel.InvokeFunction(ctx, functionName, arguments)
}

func (ska *SKAgent) GetChatCompletion(ctx context.Context, chatHistory types.ChatHistory, arguments map[string]interface{}) ([]types.ChatMessageContent, error) {
	chatCompletion, settings, err := ska.kernel.SelectAIService(arguments)
	if err != nil {
		return nil, err
	}

	return chatCompletion.GetChatMessageContents(ctx, chatHistory, settings, ska.kernel, arguments)
}
