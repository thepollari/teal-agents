package main

import (
	"context"
	"fmt"
	"log"

	"github.com/thepollari/teal-agents-go/pkg/agents"
	"github.com/thepollari/teal-agents-go/pkg/kernel"
	"github.com/thepollari/teal-agents-go/pkg/types"
)

func main() {
	fmt.Println("Testing Golang Semantic Kernel Implementation...")

	appConfig := kernel.NewSimpleAppConfig()
	appConfig.Set("OPENAI_API_KEY", "test-key")

	agentConfig := types.AgentConfig{
		ModelName: "gpt-3.5-turbo",
		ServiceID: "openai",
		Plugins:   []types.PluginConfig{},
		Settings: map[string]interface{}{
			"temperature": 0.7,
		},
	}

	agentBuilder := agents.NewAgentBuilder(appConfig)
	extraDataCollector := agents.NewExtraDataCollector()

	fmt.Println("Building agent...")
	skAgent, err := agentBuilder.BuildAgent(agentConfig, extraDataCollector)
	if err != nil {
		log.Fatalf("Failed to build agent: %v", err)
	}

	fmt.Println("Creating chat agent...")
	chatAgent := agents.NewChatAgents(skAgent, extraDataCollector)

	fmt.Println("Testing agent invocation...")
	inputs := map[string]interface{}{
		"chat_history": []types.HistoryMessage{
			{Role: "user", Content: "Hello, how are you?"},
		},
	}

	ctx := context.Background()
	response, err := chatAgent.Invoke(ctx, inputs)
	if err != nil {
		log.Fatalf("Failed to invoke agent: %v", err)
	}

	fmt.Printf("✅ Agent invocation successful!\n")
	fmt.Printf("Response: %s\n", *response.OutputRaw)
	fmt.Printf("Token usage: %+v\n", response.TokenUsage)

	fmt.Println("Testing streaming invocation...")
	responseChan, err := chatAgent.InvokeStream(ctx, inputs)
	if err != nil {
		log.Fatalf("Failed to start streaming: %v", err)
	}

	fmt.Print("Streaming response: ")
	for partialResponse := range responseChan {
		fmt.Print(partialResponse.OutputPartial)
	}
	fmt.Println()

	fmt.Println("✅ All tests passed! Semantic kernel implementation is working correctly.")
}
