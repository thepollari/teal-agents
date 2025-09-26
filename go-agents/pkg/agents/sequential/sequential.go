package sequential

import (
	"context"
	"fmt"
	"sync"
	"time"

	"github.com/thepollari/teal-agents/go-agents/pkg/config"
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
		agentConfig, exists := agentMap[taskConfig.Agent]
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
		kernel, err := s.kernelBuilder.BuildKernel(ctx, agentConfig)
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
	s.mu.RLock()
	tasks := s.tasks
	s.mu.RUnlock()
	
	agents, err := s.initializeAgents(ctx, s.config.Spec.Agents)
	if err != nil {
		return nil, fmt.Errorf("failed to initialize agents: %w", err)
	}
	
	results := make(map[string]interface{})
	for _, task := range tasks {
		agent, exists := agents[task.AgentName]
		if !exists {
			return nil, fmt.Errorf("agent %s not found for task %s", task.AgentName, task.Name)
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
		
		
		results[task.Name] = fmt.Sprintf("Result for task %s", task.Name)
	}
	
	return &types.InvokeResponse{
		Result:    results,
		Metadata:  map[string]interface{}{"agent": s.name},
		Timestamp: time.Now(),
	}, nil
}

func (s *SequentialAgent) InvokeStream(ctx context.Context, inputs map[string]interface{}) (<-chan types.StreamResponse, error) {
	responseChan := make(chan types.StreamResponse)
	
	go func() {
		defer close(responseChan)
		
		s.mu.RLock()
		tasks := s.tasks
		s.mu.RUnlock()
		
		agents, err := s.initializeAgents(ctx, s.config.Spec.Agents)
		if err != nil {
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
			agent, exists := agents[task.AgentName]
			if !exists {
				responseChan <- types.StreamResponse{
					Data:      nil,
					Metadata:  map[string]interface{}{"error": fmt.Sprintf("agent %s not found for task %s", task.AgentName, task.Name)},
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
			
			responseChan <- types.StreamResponse{
				Data:      fmt.Sprintf("Starting task %s", task.Name),
				Metadata:  map[string]interface{}{"task": task.Name, "status": "started"},
				Timestamp: time.Now(),
				Done:      false,
			}
			
			
			taskResult := fmt.Sprintf("Result for task %s", task.Name)
			results[task.Name] = taskResult
			
			responseChan <- types.StreamResponse{
				Data:      taskResult,
				Metadata:  map[string]interface{}{"task": task.Name, "status": "completed"},
				Timestamp: time.Now(),
				Done:      i == len(tasks)-1,
			}
		}
	}()
	
	return responseChan, nil
}
