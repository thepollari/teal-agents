package integration

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/merck-gen/teal-agents-go/internal/gemini"
	"github.com/merck-gen/teal-agents-go/internal/handlers"
	"github.com/merck-gen/teal-agents-go/internal/university"
	"github.com/merck-gen/teal-agents-go/pkg/api"
	"github.com/merck-gen/teal-agents-go/pkg/config"
	"github.com/merck-gen/teal-agents-go/pkg/kernel"
)

func TestUniversityAgentIntegration(t *testing.T) {
	if os.Getenv("GEMINI_API_KEY") == "" {
		t.Skip("Skipping integration test: GEMINI_API_KEY environment variable not set")
	}

	configLoader := config.NewConfigLoader()
	agentConfig, err := configLoader.LoadAgent("../../configs/agents/university-agent.yaml")
	require.NoError(t, err, "Failed to load agent configuration")

	k := kernel.NewKernel()
	universityPlugin := university.NewUniversityPlugin()
	err = k.RegisterPlugin(universityPlugin)
	require.NoError(t, err, "Failed to register University plugin")

	model := "gemini-1.5-flash-lite" // Default model if not specified in config
	if agentConfig.Spec != nil && len(agentConfig.Spec.Agents) > 0 {
		if agentConfig.Spec.Agents[0].Model != "" {
			model = agentConfig.Spec.Agents[0].Model
		}
	}
	geminiClient, err := gemini.NewClient(model)
	require.NoError(t, err, "Failed to create Gemini client")
	defer geminiClient.Close()

	logger := logrus.New()
	logger.SetLevel(logrus.InfoLevel)

	gin.SetMode(gin.TestMode)
	server := api.NewServer(agentConfig, k, logger)

	universityHandler := handlers.NewUniversityHandler(k, geminiClient, logger, agentConfig)
	server.RegisterHandler("invoke", handlers.NewHandlerAdapter(universityHandler.HandleInvoke))
	server.RegisterHandler("agent-card", handlers.NewHandlerAdapter(universityHandler.HandleAgentCard))

	server.SetupRoutes()

	t.Run("TestAgentCard", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", fmt.Sprintf("/%s/%v/agent-card", agentConfig.Name, agentConfig.Version), nil)
		server.GetEngine().ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		require.NoError(t, err, "Failed to unmarshal response")

		assert.Equal(t, agentConfig.Name, response["name"])
		assert.Equal(t, agentConfig.Version, response["version"])
		assert.Equal(t, agentConfig.Description, response["description"])
	})

	t.Run("TestInvoke", func(t *testing.T) {
		payload := config.BaseInput{
			ChatHistory: []config.HistoryMessage{
				{
					Role:    "user",
					Content: "Tell me about Harvard University",
				},
			},
		}

		payloadBytes, err := json.Marshal(payload)
		require.NoError(t, err, "Failed to marshal request payload")

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", fmt.Sprintf("/%s/%v/invoke", agentConfig.Name, agentConfig.Version), bytes.NewBuffer(payloadBytes))
		req.Header.Set("Content-Type", "application/json")

		ctx, cancel := context.WithTimeout(req.Context(), 30*time.Second)
		defer cancel()
		req = req.WithContext(ctx)

		server.GetEngine().ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var response config.InvokeResponse
		err = json.Unmarshal(w.Body.Bytes(), &response)
		require.NoError(t, err, "Failed to unmarshal response")

		assert.NotEmpty(t, response.SessionID)
		assert.NotEmpty(t, response.RequestID)
		assert.Equal(t, agentConfig.Name, response.Source)
		assert.NotEmpty(t, response.OutputRaw)
		assert.NotZero(t, response.TokenUsage.TotalTokens)
	})
}
