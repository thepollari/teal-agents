package tests

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/thepollari/teal-agents/pkg/config/loader"
)

func TestBackwardCompatibilityWithExistingConfigs(t *testing.T) {
	repoRoot := filepath.Join("..", "..", "..", "..")

	tests := []struct {
		name       string
		configPath string
		kind       string
	}{
		{
			name:       "Getting Started Sequential",
			configPath: filepath.Join(repoRoot, "src/sk-agents/docs/demos/01_getting_started/config.yaml"),
			kind:       "Sequential",
		},
		{
			name:       "Chat with Plugins",
			configPath: filepath.Join(repoRoot, "src/sk-agents/docs/demos/10_chat_plugins/config.yaml"),
			kind:       "Chat",
		},
		{
			name:       "Team Orchestrator",
			configPath: filepath.Join(repoRoot, "src/orchestrators/collab-orchestrator/orchestrator/conf/config_team.yaml"),
			kind:       "TeamOrchestrator",
		},
		{
			name:       "Planning Orchestrator",
			configPath: filepath.Join(repoRoot, "src/orchestrators/collab-orchestrator/orchestrator/conf/config_planning.yaml"),
			kind:       "PlanningOrchestrator",
		},
		{
			name:       "Assistant Orchestrator",
			configPath: filepath.Join(repoRoot, "src/orchestrators/assistant-orchestrator/orchestrator/conf/config.yaml"),
			kind:       "AssistantOrchestrator",
		},
	}

	cl := loader.NewConfigLoader()

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if _, err := os.Stat(tt.configPath); os.IsNotExist(err) {
				t.Skipf("Config file not found: %s", tt.configPath)
				return
			}

			config, err := cl.LoadConfigByKind(tt.configPath)
			require.NoError(t, err, "Failed to load config: %s", tt.configPath)
			assert.NotNil(t, config)

			t.Logf("Successfully loaded %s config from %s", tt.kind, tt.configPath)
		})
	}
}
