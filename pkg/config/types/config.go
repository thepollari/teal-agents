package types

type ConfigSkill struct {
	ID          string   `json:"id" yaml:"id"`
	Name        string   `json:"name" yaml:"name"`
	Description string   `json:"description" yaml:"description"`
	Tags        []string `json:"tags" yaml:"tags"`
	Examples    []string `json:"examples,omitempty" yaml:"examples,omitempty"`
	InputModes  []string `json:"input_modes,omitempty" yaml:"input_modes,omitempty"`
	OutputModes []string `json:"output_modes,omitempty" yaml:"output_modes,omitempty"`
}

type ConfigMetadata struct {
	Description      string        `json:"description" yaml:"description"`
	Skills           []ConfigSkill `json:"skills" yaml:"skills"`
	DocumentationURL *string       `json:"documentation_url,omitempty" yaml:"documentation_url,omitempty"`
}

type BaseConfig struct {
	APIVersion  string          `json:"apiVersion" yaml:"apiVersion" validate:"required"`
	Kind        *string         `json:"kind,omitempty" yaml:"kind,omitempty"`
	Name        *string         `json:"name,omitempty" yaml:"name,omitempty"`
	ServiceName *string         `json:"service_name,omitempty" yaml:"service_name,omitempty"`
	Version     any             `json:"version" yaml:"version" validate:"required"`
	Description *string         `json:"description,omitempty" yaml:"description,omitempty"`
	Metadata    *ConfigMetadata `json:"metadata,omitempty" yaml:"metadata,omitempty"`
	InputType   *string         `json:"input_type,omitempty" yaml:"input_type,omitempty"`
	OutputType  *string         `json:"output_type,omitempty" yaml:"output_type,omitempty"`
}

type AgentConfig struct {
	Name          string   `json:"name" yaml:"name" validate:"required"`
	Role          *string  `json:"role,omitempty" yaml:"role,omitempty"`
	Model         string   `json:"model" yaml:"model" validate:"required"`
	SystemPrompt  string   `json:"system_prompt" yaml:"system_prompt" validate:"required"`
	Temperature   *float64 `json:"temperature,omitempty" yaml:"temperature,omitempty" validate:"omitempty,gte=0,lte=1"`
	Plugins       []string `json:"plugins,omitempty" yaml:"plugins,omitempty"`
	RemotePlugins []string `json:"remote_plugins,omitempty" yaml:"remote_plugins,omitempty"`
}

type TaskConfig struct {
	Name         string `json:"name" yaml:"name" validate:"required"`
	TaskNo       int    `json:"task_no" yaml:"task_no" validate:"required"`
	Description  string `json:"description" yaml:"description" validate:"required"`
	Instructions string `json:"instructions" yaml:"instructions" validate:"required"`
	Agent        string `json:"agent" yaml:"agent" validate:"required"`
}

type SequentialSpec struct {
	Agents []AgentConfig `json:"agents" yaml:"agents" validate:"required,dive"`
	Tasks  []TaskConfig  `json:"tasks" yaml:"tasks" validate:"required,dive"`
}

type SequentialConfig struct {
	BaseConfig `yaml:",inline"`
	Spec       SequentialSpec `json:"spec" yaml:"spec" validate:"required"`
}

type ChatSpec struct {
	Agent AgentConfig `json:"agent" yaml:"agent" validate:"required"`
}

type ChatConfig struct {
	BaseConfig `yaml:",inline"`
	Spec       ChatSpec `json:"spec" yaml:"spec" validate:"required"`
}

type TeamOrchestratorSpec struct {
	MaxRounds    int      `json:"max_rounds" yaml:"max_rounds" validate:"required"`
	ManagerAgent string   `json:"manager_agent" yaml:"manager_agent" validate:"required"`
	Agents       []string `json:"agents" yaml:"agents" validate:"required"`
}

type TeamOrchestratorConfig struct {
	BaseConfig `yaml:",inline"`
	Spec       TeamOrchestratorSpec `json:"spec" yaml:"spec" validate:"required"`
}

type PlanningOrchestratorSpec struct {
	PlanningAgent  string   `json:"planning_agent" yaml:"planning_agent" validate:"required"`
	Agents         []string `json:"agents" yaml:"agents" validate:"required"`
	HumanInTheLoop bool     `json:"human_in_the_loop" yaml:"human_in_the_loop"`
	HitlTimeout    int      `json:"hitl_timeout,omitempty" yaml:"hitl_timeout,omitempty"`
}

type PlanningOrchestratorConfig struct {
	BaseConfig `yaml:",inline"`
	Spec       PlanningOrchestratorSpec `json:"spec" yaml:"spec" validate:"required"`
}

type AssistantOrchestratorSpec struct {
	FallbackAgent string   `json:"fallback_agent" yaml:"fallback_agent" validate:"required"`
	AgentChooser  string   `json:"agent_chooser" yaml:"agent_chooser" validate:"required"`
	Agents        []string `json:"agents" yaml:"agents" validate:"required"`
}

type AssistantOrchestratorConfig struct {
	BaseConfig `yaml:",inline"`
	Spec       AssistantOrchestratorSpec `json:"spec" yaml:"spec" validate:"required"`
}
