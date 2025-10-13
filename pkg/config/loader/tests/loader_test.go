package tests

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/thepollari/teal-agents/pkg/config/loader"
	"github.com/thepollari/teal-agents/pkg/config/types"
)

func TestLoadEnvConfig(t *testing.T) {
	os.Setenv("TA_API_KEY", "test-api-key")
	defer os.Unsetenv("TA_API_KEY")

	cl := loader.NewConfigLoader()
	config, err := cl.LoadEnvConfig()

	require.NoError(t, err)
	assert.NotNil(t, config)
	assert.Equal(t, "test-api-key", config.APIKey)
	assert.Equal(t, "agents/config.yaml", config.ServiceConfig)
	assert.Equal(t, "false", config.A2AEnabled)
}

func TestLoadEnvConfigWithJSONStore(t *testing.T) {
	os.Setenv("TA_API_KEY", "test-api-key")
	os.Setenv("TA_ENV_STORE", `{"CUSTOM_VAR": "custom_value"}`)
	defer os.Unsetenv("TA_API_KEY")
	defer os.Unsetenv("TA_ENV_STORE")
	defer os.Unsetenv("CUSTOM_VAR")

	cl := loader.NewConfigLoader()
	_, err := cl.LoadEnvConfig()

	require.NoError(t, err)
	assert.Equal(t, "custom_value", os.Getenv("CUSTOM_VAR"))
}

func TestLoadSequentialConfig(t *testing.T) {
	configContent := `apiVersion: skagents/v1
kind: Sequential
service_name: TestAgent
version: 0.1
spec:
  agents:
    - name: default
      model: gpt-4o-mini
      system_prompt: "Test prompt"
  tasks:
    - name: test_task
      task_no: 1
      description: "Test description"
      instructions: "Test instructions"
      agent: default
`

	tmpDir := t.TempDir()
	configPath := filepath.Join(tmpDir, "config.yaml")
	err := os.WriteFile(configPath, []byte(configContent), 0644)
	require.NoError(t, err)

	cl := loader.NewConfigLoader()
	config, err := cl.LoadSequentialConfig(configPath)

	require.NoError(t, err)
	assert.NotNil(t, config)
	assert.Equal(t, "skagents/v1", config.APIVersion)
	assert.Equal(t, "TestAgent", *config.ServiceName)
	assert.Len(t, config.Spec.Agents, 1)
	assert.Len(t, config.Spec.Tasks, 1)
	assert.Equal(t, "default", config.Spec.Agents[0].Name)
}

func TestLoadChatConfig(t *testing.T) {
	configContent := `apiVersion: skagents/v1
kind: Chat
service_name: ChatBot
version: 0.1
spec:
  agent:
    name: default
    model: gpt-4o
    system_prompt: "Test prompt"
    plugins:
      - TestPlugin
`

	tmpDir := t.TempDir()
	configPath := filepath.Join(tmpDir, "config.yaml")
	err := os.WriteFile(configPath, []byte(configContent), 0644)
	require.NoError(t, err)

	cl := loader.NewConfigLoader()
	config, err := cl.LoadChatConfig(configPath)

	require.NoError(t, err)
	assert.NotNil(t, config)
	assert.Equal(t, "ChatBot", *config.ServiceName)
	assert.Equal(t, "default", config.Spec.Agent.Name)
	assert.Len(t, config.Spec.Agent.Plugins, 1)
}

func TestLoadTeamOrchestratorConfig(t *testing.T) {
	configContent := `apiVersion: skagents/v1
kind: TeamOrchestrator
service_name: TeamOrch
version: 0.1
spec:
  max_rounds: 10
  manager_agent: ManagerAgent:0.1
  agents:
    - Agent1:0.1
    - Agent2:0.1
`

	tmpDir := t.TempDir()
	configPath := filepath.Join(tmpDir, "config.yaml")
	err := os.WriteFile(configPath, []byte(configContent), 0644)
	require.NoError(t, err)

	cl := loader.NewConfigLoader()
	config, err := cl.LoadTeamOrchestratorConfig(configPath)

	require.NoError(t, err)
	assert.NotNil(t, config)
	assert.Equal(t, 10, config.Spec.MaxRounds)
	assert.Equal(t, "ManagerAgent:0.1", config.Spec.ManagerAgent)
	assert.Len(t, config.Spec.Agents, 2)
}

func TestValidationFailsOnInvalidTemperature(t *testing.T) {
	configContent := `apiVersion: skagents/v1
kind: Sequential
service_name: TestAgent
version: 0.1
spec:
  agents:
    - name: default
      model: gpt-4o-mini
      system_prompt: "Test"
      temperature: 1.5
  tasks:
    - name: test
      task_no: 1
      description: "Test"
      instructions: "Test"
      agent: default
`

	tmpDir := t.TempDir()
	configPath := filepath.Join(tmpDir, "config.yaml")
	err := os.WriteFile(configPath, []byte(configContent), 0644)
	require.NoError(t, err)

	cl := loader.NewConfigLoader()
	_, err = cl.LoadSequentialConfig(configPath)

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "validation failed")
}

func TestLoadConfigByKind(t *testing.T) {
	tests := []struct {
		name     string
		kind     string
		expected interface{}
	}{
		{
			name:     "Sequential",
			kind:     "Sequential",
			expected: &types.SequentialConfig{},
		},
		{
			name:     "Chat",
			kind:     "Chat",
			expected: &types.ChatConfig{},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			var configContent string
			switch tt.kind {
			case "Sequential":
				configContent = `apiVersion: skagents/v1
kind: Sequential
service_name: Test
version: 0.1
spec:
  agents:
    - name: default
      model: gpt-4o
      system_prompt: "Test"
  tasks:
    - name: test
      task_no: 1
      description: "Test"
      instructions: "Test"
      agent: default
`
			case "Chat":
				configContent = `apiVersion: skagents/v1
kind: Chat
service_name: Test
version: 0.1
spec:
  agent:
    name: default
    model: gpt-4o
    system_prompt: "Test"
`
			}

			tmpDir := t.TempDir()
			configPath := filepath.Join(tmpDir, "config.yaml")
			err := os.WriteFile(configPath, []byte(configContent), 0644)
			require.NoError(t, err)

			cl := loader.NewConfigLoader()
			config, err := cl.LoadConfigByKind(configPath)

			require.NoError(t, err)
			assert.IsType(t, tt.expected, config)
		})
	}
}
