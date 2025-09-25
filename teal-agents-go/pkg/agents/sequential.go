package agents

import (
	"context"
	"fmt"

	"github.com/thepollari/teal-agents-go/pkg/types"
)

type SequentialSkagents struct {
	tasks              []Task
	extraDataCollector *ExtraDataCollector
}

type Task struct {
	TaskNo   int
	TaskName string
	Agent    *SKAgent
	Settings map[string]interface{}
}

func NewSequentialSkagents(tasks []Task, extraDataCollector *ExtraDataCollector) *SequentialSkagents {
	return &SequentialSkagents{
		tasks:              tasks,
		extraDataCollector: extraDataCollector,
	}
}

func (ss *SequentialSkagents) Invoke(ctx context.Context, inputs map[string]interface{}) (*types.InvokeResponse, error) {
	var totalTokenUsage types.TokenUsage
	var intermediateResponses []types.IntermediateTaskResponse
	var finalOutput interface{}

	chatHistory, ok := inputs["chat_history"].(types.ChatHistory)
	if !ok {
		chatHistory = types.ChatHistory{}
	}

	currentInput := inputs

	for _, task := range ss.tasks {
		if ss.extraDataCollector != nil {
			ss.extraDataCollector.AddExtraData(fmt.Sprintf("task_%d_started", task.TaskNo), task.TaskName)
		}

		response, err := task.Agent.GetChatCompletion(ctx, chatHistory, currentInput)
		if err != nil {
			return nil, fmt.Errorf("task %d (%s) failed: %w", task.TaskNo, task.TaskName, err)
		}

		if len(response) > 0 {
			finalOutput = response[len(response)-1].Content

			chatHistory = append(chatHistory, response...)
		}

		intermediateResponse := types.IntermediateTaskResponse{
			TaskNo:   task.TaskNo,
			TaskName: task.TaskName,
			Response: &types.InvokeResponse{
				OutputRaw:  stringPtr(fmt.Sprintf("%v", finalOutput)),
				TokenUsage: types.TokenUsage{}, // Would be populated from actual LLM response
			},
		}
		intermediateResponses = append(intermediateResponses, intermediateResponse)

		currentInput = map[string]interface{}{
			"chat_history":    chatHistory,
			"previous_output": finalOutput,
		}

		if ss.extraDataCollector != nil {
			ss.extraDataCollector.AddExtraData(fmt.Sprintf("task_%d_completed", task.TaskNo), true)
		}
	}

	var extraData interface{}
	if ss.extraDataCollector != nil {
		extraData = ss.extraDataCollector.GetExtraData()
	}

	return &types.InvokeResponse{
		OutputRaw:      stringPtr(fmt.Sprintf("%v", finalOutput)),
		TokenUsage:     totalTokenUsage,
		ExtraData:      extraData,
		OutputPydantic: intermediateResponses,
	}, nil
}

func (ss *SequentialSkagents) InvokeStream(ctx context.Context, inputs map[string]interface{}) (<-chan types.PartialResponse, error) {
	responseChan := make(chan types.PartialResponse, 10)

	go func() {
		defer close(responseChan)

		response, err := ss.Invoke(ctx, inputs)
		if err != nil {
			responseChan <- types.PartialResponse{
				OutputPartial: fmt.Sprintf("Error: %v", err),
			}
			return
		}

		if response.OutputRaw != nil {
			output := *response.OutputRaw
			chunkSize := 50 // Stream in chunks of 50 characters

			for i := 0; i < len(output); i += chunkSize {
				end := i + chunkSize
				if end > len(output) {
					end = len(output)
				}

				responseChan <- types.PartialResponse{
					OutputPartial: output[i:end],
				}
			}
		}
	}()

	return responseChan, nil
}

func stringPtr(s string) *string {
	return &s
}
