package sequential

import (
	"context"
	"fmt"
	"sync"
	"time"

	"go.opentelemetry.io/otel/attribute"

	"github.com/thepollari/teal-agents/go-agents/pkg/config"
	"github.com/thepollari/teal-agents/go-agents/pkg/telemetry"
	"github.com/thepollari/teal-agents/go-agents/pkg/types"
)

type SequentialAgent struct {
	config       *config.BaseConfig
	kernelBuilder types.KernelBuilder
	tasks        []Task
	name         string
	version      string
	mu           sync.RWMutex
}

type Task struct {
	Name         string
	TaskNo       int
	Description  string
	Instructions string
	AgentName    string
	Agent        *AgentInstance
}

type AgentInstance struct {
	Config *config.AgentConfig
	Kernel types.Kernel
}

func NewSequentialAgent(cfg *config.BaseConfig, kb types.KernelBuilder) (*SequentialAgent, error) {
	agent := &SequentialAgent{
		config:        cfg,
		kernelBuilder: kb,
		name:          cfg.ServiceName,
		version:       cfg.Version,
	}
	
	tasks, err := agent.buildTasks(cfg.Spec.Tasks, cfg.Spec.Agents)
	if err != nil {
		return nil, fmt.Errorf("failed to build tasks: %w", err)
	}
	agent.tasks = tasks
	
	return agent, nil
}

func (s *SequentialAgent) buildTasks(taskConfigs []config.TaskConfig, agentConfigs []config.AgentConfig) ([]Task, error) {
	agentMap := make(map[string]config.AgentConfig)
	for _, agent := range agentConfigs {
		agentMap[agent.Name] = agent
	}
	
	tasks := make([]Task, len(taskConfigs))
	for i, taskConfig := range taskConfigs {
		_, exists := agentMap[taskConfig.Agent]
		if !exists {
			return nil, fmt.Errorf("agent %s not found for task %s", taskConfig.Agent, taskConfig.Name)
		}
		
		tasks[i] = Task{
			Name:         taskConfig.Name,
			TaskNo:       taskConfig.TaskNo,
			Description:  taskConfig.Description,
			Instructions: taskConfig.Instructions,
			AgentName:    taskConfig.Agent,
		}
	}
	
	return tasks, nil
}

func (s *SequentialAgent) initializeAgents(ctx context.Context, agentConfigs []config.AgentConfig) (map[string]*AgentInstance, error) {
	agents := make(map[string]*AgentInstance)
	
	for _, agentConfig := range agentConfigs {
		typesAgentConfig := types.AgentConfig{
			Name:          agentConfig.Name,
			Role:          agentConfig.Role,
			Model:         agentConfig.Model,
			SystemPrompt:  agentConfig.SystemPrompt,
			Plugins:       agentConfig.Plugins,
			RemotePlugins: agentConfig.RemotePlugins,
			MaxTokens:     agentConfig.MaxTokens,
		}
		
		kernel, err := s.kernelBuilder.BuildKernel(ctx, typesAgentConfig)
		if err != nil {
			return nil, fmt.Errorf("failed to build kernel for agent %s: %w", agentConfig.Name, err)
		}
		
		if len(agentConfig.Plugins) > 0 {
			err = s.kernelBuilder.AddPlugins(ctx, kernel, agentConfig.Plugins)
			if err != nil {
				return nil, fmt.Errorf("failed to add plugins for agent %s: %w", agentConfig.Name, err)
			}
		}
		
		agents[agentConfig.Name] = &AgentInstance{
			Config: &agentConfig,
			Kernel: kernel,
		}
	}
	
	return agents, nil
}

func (s *SequentialAgent) Invoke(ctx context.Context, inputs map[string]interface{}) (*types.InvokeResponse, error) {
	ctx, span := telemetry.InstrumentAgentInvocation(ctx, s.name, "sequential")
	defer span.End()
	
	telemetry.AddSpanAttributes(span,
		attribute.String("agent.type", "sequential"),
		attribute.Int("agent.task_count", len(s.tasks)),
	)
	
	s.mu.RLock()
	tasks := s.tasks
	s.mu.RUnlock()
	
	agents, err := s.initializeAgents(ctx, s.config.Spec.Agents)
	if err != nil {
		telemetry.RecordError(span, err)
		return nil, fmt.Errorf("failed to initialize agents: %w", err)
	}
	
	results := make(map[string]interface{})
	for i, task := range tasks {
		_, taskSpan := telemetry.StartSpan(ctx, fmt.Sprintf("task.%s", task.Name))
		telemetry.AddSpanAttributes(taskSpan,
			attribute.String("task.name", task.Name),
			attribute.String("task.agent", task.AgentName),
			attribute.Int("task.number", task.TaskNo),
		)
		
		agent, exists := agents[task.AgentName]
		if !exists {
			err := fmt.Errorf("agent %s not found for task %s", task.AgentName, task.Name)
			telemetry.RecordError(taskSpan, err)
			taskSpan.End()
			telemetry.RecordError(span, err)
			return nil, err
		}
		
		taskInputs := make(map[string]interface{})
		for k, v := range inputs {
			taskInputs[k] = v
		}
		
		for k, v := range results {
			taskInputs[k] = v
		}
		
		taskInputs["task"] = task.Name
		taskInputs["instructions"] = task.Instructions
		
		telemetry.AddSpanAttributes(taskSpan,
			attribute.String("agent.model", agent.Config.Model),
			attribute.String("agent.role", agent.Config.Role),
		)
		
		results[task.Name] = fmt.Sprintf("Result for task %s", task.Name)
		
		telemetry.AddSpanAttributes(taskSpan,
			attribute.String("task.status", "completed"),
		)
		taskSpan.End()
		
		telemetry.AddSpanAttributes(span,
			attribute.Int("tasks.completed", i+1),
		)
	}
	
	telemetry.AddSpanAttributes(span,
		attribute.String("invocation.status", "success"),
		attribute.Int("results.count", len(results)),
	)
	
	return &types.InvokeResponse{
		Result:    results,
		Metadata:  map[string]interface{}{"agent": s.name},
		Timestamp: time.Now(),
	}, nil
}

func (s *SequentialAgent) InvokeStream(ctx context.Context, inputs map[string]interface{}) (<-chan types.StreamResponse, error) {
	ctx, span := telemetry.InstrumentAgentInvocation(ctx, s.name, "sequential-stream")
	defer span.End()
	
	telemetry.AddSpanAttributes(span,
		attribute.String("agent.type", "sequential"),
		attribute.String("invocation.mode", "stream"),
		attribute.Int("agent.task_count", len(s.tasks)),
	)
	
	responseChan := make(chan types.StreamResponse)
	
	go func() {
		defer close(responseChan)
		
		s.mu.RLock()
		tasks := s.tasks
		s.mu.RUnlock()
		
		agents, err := s.initializeAgents(ctx, s.config.Spec.Agents)
		if err != nil {
			telemetry.RecordError(span, err)
			responseChan <- types.StreamResponse{
				Data:      nil,
				Metadata:  map[string]interface{}{"error": err.Error()},
				Timestamp: time.Now(),
				Done:      true,
			}
			return
		}
		
		results := make(map[string]interface{})
		for i, task := range tasks {
			_, taskSpan := telemetry.StartSpan(ctx, fmt.Sprintf("stream.task.%s", task.Name))
			telemetry.AddSpanAttributes(taskSpan,
				attribute.String("task.name", task.Name),
				attribute.String("task.agent", task.AgentName),
				attribute.Int("task.number", task.TaskNo),
				attribute.String("task.mode", "stream"),
			)
			
			agent, exists := agents[task.AgentName]
			if !exists {
				err := fmt.Errorf("agent %s not found for task %s", task.AgentName, task.Name)
				telemetry.RecordError(taskSpan, err)
				telemetry.RecordError(span, err)
				taskSpan.End()
				responseChan <- types.StreamResponse{
					Data:      nil,
					Metadata:  map[string]interface{}{"error": err.Error()},
					Timestamp: time.Now(),
					Done:      true,
				}
				return
			}
			
			taskInputs := make(map[string]interface{})
			for k, v := range inputs {
				taskInputs[k] = v
			}
			
			for k, v := range results {
				taskInputs[k] = v
			}
			
			taskInputs["task"] = task.Name
			taskInputs["instructions"] = task.Instructions
			
			telemetry.AddSpanAttributes(taskSpan,
				attribute.String("agent.model", agent.Config.Model),
				attribute.String("agent.role", agent.Config.Role),
			)
			
			responseChan <- types.StreamResponse{
				Data:      fmt.Sprintf("Starting task %s", task.Name),
				Metadata:  map[string]interface{}{"task": task.Name, "status": "started"},
				Timestamp: time.Now(),
				Done:      false,
			}
			
			taskResult := fmt.Sprintf("Result for task %s", task.Name)
			results[task.Name] = taskResult
			
			telemetry.AddSpanAttributes(taskSpan,
				attribute.String("task.status", "completed"),
			)
			
			responseChan <- types.StreamResponse{
				Data:      taskResult,
				Metadata:  map[string]interface{}{"task": task.Name, "status": "completed"},
				Timestamp: time.Now(),
				Done:      i == len(tasks)-1,
			}
			
			taskSpan.End()
			
			telemetry.AddSpanAttributes(span,
				attribute.Int("tasks.completed", i+1),
			)
		}
		
		telemetry.AddSpanAttributes(span,
			attribute.String("invocation.status", "success"),
			attribute.Int("results.count", len(results)),
		)
	}()
	
	return responseChan, nil
}
