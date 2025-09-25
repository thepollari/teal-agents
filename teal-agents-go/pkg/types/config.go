package types

type BaseConfig struct {
	APIVersion  string          `yaml:"apiVersion" json:"apiVersion"`
	Name        *string         `yaml:"name,omitempty" json:"name,omitempty"`
	ServiceName *string         `yaml:"service_name,omitempty" json:"service_name,omitempty"`
	Version     interface{}     `yaml:"version" json:"version"` // Can be string, float, or int
	Description *string         `yaml:"description,omitempty" json:"description,omitempty"`
	Metadata    *ConfigMetadata `yaml:"metadata,omitempty" json:"metadata,omitempty"`
	InputType   *string         `yaml:"input_type,omitempty" json:"input_type,omitempty"`
	OutputType  *string         `yaml:"output_type,omitempty" json:"output_type,omitempty"`
	Spec        interface{}     `yaml:"spec,omitempty" json:"spec,omitempty"`
}

type ConfigMetadata struct {
	Description      string        `yaml:"description" json:"description"`
	Skills           []ConfigSkill `yaml:"skills" json:"skills"`
	DocumentationURL *string       `yaml:"documentation_url,omitempty" json:"documentation_url,omitempty"`
}

type ConfigSkill struct {
	ID          string   `yaml:"id" json:"id"`
	Name        string   `yaml:"name" json:"name"`
	Description string   `yaml:"description" json:"description"`
	Tags        []string `yaml:"tags" json:"tags"`
	Examples    []string `yaml:"examples,omitempty" json:"examples,omitempty"`
	InputModes  []string `yaml:"input_modes,omitempty" json:"input_modes,omitempty"`
	OutputModes []string `yaml:"output_modes,omitempty" json:"output_modes,omitempty"`
}

type AgentConfig struct {
	ModelName string                 `yaml:"model_name" json:"model_name"`
	ServiceID string                 `yaml:"service_id" json:"service_id"`
	Plugins   []PluginConfig         `yaml:"plugins,omitempty" json:"plugins,omitempty"`
	Settings  map[string]interface{} `yaml:"settings,omitempty" json:"settings,omitempty"`
}

type PluginConfig struct {
	Name     string                 `yaml:"name" json:"name"`
	Type     string                 `yaml:"type" json:"type"` // "local" or "remote"
	Path     *string                `yaml:"path,omitempty" json:"path,omitempty"`
	URL      *string                `yaml:"url,omitempty" json:"url,omitempty"`
	Settings map[string]interface{} `yaml:"settings,omitempty" json:"settings,omitempty"`
}
