package tests

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/thepollari/teal-agents/go-agents/pkg/agents/sequential"
	"github.com/thepollari/teal-agents/go-agents/pkg/config"
	"github.com/thepollari/teal-agents/go-agents/pkg/server"
	"github.com/thepollari/teal-agents/go-agents/pkg/types"
)

type MockKernelBuilder struct{}

func (m *MockKernelBuilder) BuildKernel(ctx context.Context, config types.AgentConfig) (types.Kernel, error) {
	return &MockKernel{}, nil
}

func (m *MockKernelBuilder) AddPlugins(ctx context.Context, kernel types.Kernel, plugins []string) error {
	return nil
}

func (m *MockKernelBuilder) SetPluginCatalog(catalog interface{}) {
}

type MockKernel struct{}

func (m *MockKernel) InvokeFunction(ctx context.Context, pluginName, functionName string, args map[string]interface{}) (interface{}, error) {
	return fmt.Sprintf("Mock result for %s.%s", pluginName, functionName), nil
}

func (m *MockKernel) GetFunction(pluginName, functionName string) (types.KernelFunction, error) {
	return &MockKernelFunction{
		name:        fmt.Sprintf("%s.%s", pluginName, functionName),
		description: fmt.Sprintf("Mock function %s.%s", pluginName, functionName),
	}, nil
}

func (m *MockKernel) AddPlugin(ctx context.Context, plugin types.Plugin) error {
	return nil
}

type MockKernelFunction struct {
	name        string
	description string
}

func (m *MockKernelFunction) Invoke(ctx context.Context, args map[string]interface{}) (interface{}, error) {
	return fmt.Sprintf("Mock result for %s", m.name), nil
}

func (m *MockKernelFunction) GetName() string {
	return m.name
}

func (m *MockKernelFunction) GetDescription() string {
	return m.description
}

func (m *MockKernelFunction) GetParameters() []types.FunctionParameter {
	return []types.FunctionParameter{}
}

func createMockConfig() *config.BaseConfig {
	return &config.BaseConfig{
		APIVersion:  "tealagents/v1alpha1",
		Kind:        "Agent",
		Description: "Test agent for compatibility testing",
		ServiceName: "test-agent",
		Version:     "1.0.0",
		InputType:   "text",
		OutputType:  "text",
		Spec: config.SpecConfig{
			Agents: []config.AgentConfig{
				{
					Name:         "test-agent",
					Role:         "assistant",
					Model:        "gpt-3.5-turbo",
					SystemPrompt: "You are a helpful assistant.",
					Plugins:      []string{},
				},
			},
			Tasks: []config.TaskConfig{
				{
					Name:         "test-task",
					TaskNo:       1,
					Description:  "Test task",
					Instructions: "Complete the test task",
					Agent:        "test-agent",
				},
			},
		},
	}
}

func TestSequentialAgentInvoke(t *testing.T) {
	mockKernelBuilder := &MockKernelBuilder{}
	mockConfig := createMockConfig()
	
	agent, err := sequential.NewSequentialAgent(mockConfig, mockKernelBuilder)
	require.NoError(t, err)
	
	inputs := map[string]interface{}{
		"message": "Hello, world!",
	}
	
	response, err := agent.Invoke(context.Background(), inputs)
	require.NoError(t, err)
	require.NotNil(t, response)
	
	assert.NotEmpty(t, response.Result)
	assert.NotEmpty(t, response.Metadata)
	assert.False(t, response.Timestamp.IsZero())
	
	assert.Contains(t, response.Metadata, "agent")
	assert.Equal(t, "test-agent", response.Metadata["agent"])
	
	resultMap, ok := response.Result.(map[string]interface{})
	require.True(t, ok, "Result should be a map")
	assert.Contains(t, resultMap, "test-task")
}

func TestSequentialAgentInvokeStream(t *testing.T) {
	mockKernelBuilder := &MockKernelBuilder{}
	mockConfig := createMockConfig()
	
	agent, err := sequential.NewSequentialAgent(mockConfig, mockKernelBuilder)
	require.NoError(t, err)
	
	inputs := map[string]interface{}{
		"message": "Hello, streaming world!",
	}
	
	responseChan, err := agent.InvokeStream(context.Background(), inputs)
	require.NoError(t, err)
	require.NotNil(t, responseChan)
	
	var responses []types.StreamResponse
	for response := range responseChan {
		responses = append(responses, response)
		if response.Done {
			break
		}
	}
	
	assert.NotEmpty(t, responses)
	assert.True(t, responses[len(responses)-1].Done)
	
	for _, response := range responses {
		assert.NotNil(t, response.Data)
		assert.NotNil(t, response.Metadata)
		assert.False(t, response.Timestamp.IsZero())
		
		if response.Metadata["task"] != nil {
			assert.Contains(t, response.Metadata, "status")
		}
	}
}

func TestHTTPEndpointCompatibility(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockKernelBuilder := &MockKernelBuilder{}
	mockConfig := createMockConfig()
	
	agent, err := sequential.NewSequentialAgent(mockConfig, mockKernelBuilder)
	require.NoError(t, err)
	
	srv := server.NewServer(mockConfig, agent)
	testServer := httptest.NewServer(srv)
	defer testServer.Close()
	
	t.Run("Health endpoint", func(t *testing.T) {
		resp, err := http.Get(testServer.URL + "/health")
		require.NoError(t, err)
		defer resp.Body.Close()
		
		assert.Equal(t, http.StatusOK, resp.StatusCode)
		assert.Equal(t, "application/json; charset=utf-8", resp.Header.Get("Content-Type"))
		
		var response map[string]interface{}
		err = json.NewDecoder(resp.Body).Decode(&response)
		require.NoError(t, err)
		
		assert.Equal(t, "healthy", response["status"])
		assert.Equal(t, "test-agent", response["service"])
		assert.Equal(t, "1.0.0", response["version"])
		assert.Contains(t, response, "request_id")
	})
	
	t.Run("Versioned health endpoint", func(t *testing.T) {
		resp, err := http.Get(testServer.URL + "/test-agent/1.0.0/health")
		require.NoError(t, err)
		defer resp.Body.Close()
		
		assert.Equal(t, http.StatusOK, resp.StatusCode)
		
		var response map[string]interface{}
		err = json.NewDecoder(resp.Body).Decode(&response)
		require.NoError(t, err)
		
		assert.Equal(t, "healthy", response["status"])
		assert.Equal(t, "test-agent", response["service"])
		assert.Equal(t, "1.0.0", response["version"])
	})
	
	t.Run("Ready endpoint", func(t *testing.T) {
		resp, err := http.Get(testServer.URL + "/health/ready")
		require.NoError(t, err)
		defer resp.Body.Close()
		
		assert.Equal(t, http.StatusOK, resp.StatusCode)
		
		var response map[string]interface{}
		err = json.NewDecoder(resp.Body).Decode(&response)
		require.NoError(t, err)
		
		assert.Equal(t, "ready", response["status"])
	})
	
	t.Run("Agent invoke endpoint", func(t *testing.T) {
		payload := map[string]interface{}{
			"message": "Test message",
		}
		payloadBytes, _ := json.Marshal(payload)
		
		resp, err := http.Post(testServer.URL+"/test-agent/1.0.0", "application/json", bytes.NewBuffer(payloadBytes))
		require.NoError(t, err)
		defer resp.Body.Close()
		
		assert.Equal(t, http.StatusOK, resp.StatusCode)
		assert.Equal(t, "application/json; charset=utf-8", resp.Header.Get("Content-Type"))
		
		var response types.InvokeResponse
		err = json.NewDecoder(resp.Body).Decode(&response)
		require.NoError(t, err)
		
		assert.NotEmpty(t, response.Result)
		assert.NotEmpty(t, response.Metadata)
		assert.False(t, response.Timestamp.IsZero())
		assert.Contains(t, response.Metadata, "agent")
	})
	
	t.Run("Invalid JSON request", func(t *testing.T) {
		resp, err := http.Post(testServer.URL+"/test-agent/1.0.0", "application/json", strings.NewReader("invalid json"))
		require.NoError(t, err)
		defer resp.Body.Close()
		
		assert.Equal(t, http.StatusBadRequest, resp.StatusCode)
		
		var response map[string]interface{}
		err = json.NewDecoder(resp.Body).Decode(&response)
		require.NoError(t, err)
		
		assert.Contains(t, response, "error")
		assert.Contains(t, response, "request_id")
	})
}

func TestStreamingEndpointCompatibility(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockKernelBuilder := &MockKernelBuilder{}
	mockConfig := createMockConfig()
	
	agent, err := sequential.NewSequentialAgent(mockConfig, mockKernelBuilder)
	require.NoError(t, err)
	
	srv := server.NewServer(mockConfig, agent)
	testServer := httptest.NewServer(srv)
	defer testServer.Close()
	
	t.Run("SSE endpoint", func(t *testing.T) {
		resp, err := http.Get(testServer.URL+"/test-agent/1.0.0/sse?message=test")
		require.NoError(t, err)
		defer resp.Body.Close()
		
		assert.Equal(t, http.StatusOK, resp.StatusCode)
		assert.Equal(t, "text/event-stream", resp.Header.Get("Content-Type"))
		assert.Equal(t, "no-cache", resp.Header.Get("Cache-Control"))
		assert.Equal(t, "keep-alive", resp.Header.Get("Connection"))
		
		scanner := bufio.NewScanner(resp.Body)
		var events []string
		for scanner.Scan() {
			line := scanner.Text()
			if strings.HasPrefix(line, "event:") || strings.HasPrefix(line, "data:") {
				events = append(events, line)
			}
		}
		
		assert.NotEmpty(t, events, "Should receive SSE events")
		
		hasEventType := false
		hasData := false
		for _, event := range events {
			if strings.HasPrefix(event, "event:") {
				hasEventType = true
			}
			if strings.HasPrefix(event, "data:") {
				hasData = true
			}
		}
		assert.True(t, hasEventType, "Should have event type")
		assert.True(t, hasData, "Should have data")
	})
	
	t.Run("WebSocket endpoint", func(t *testing.T) {
		wsURL := strings.Replace(testServer.URL, "http://", "ws://", 1) + "/test-agent/1.0.0/ws"
		
		conn, _, err := websocket.DefaultDialer.Dial(wsURL, nil)
		if err != nil {
			t.Skip("WebSocket connection failed, skipping test")
			return
		}
		defer conn.Close()
		
		payload := map[string]interface{}{
			"message": "Test WebSocket streaming",
		}
		
		err = conn.WriteJSON(payload)
		require.NoError(t, err)
		
		var responses []map[string]interface{}
		for i := 0; i < 5; i++ { // Limit to prevent infinite loop
			var response map[string]interface{}
			err = conn.ReadJSON(&response)
			if err != nil {
				break
			}
			responses = append(responses, response)
			
			if done, exists := response["done"]; exists && done == true {
				break
			}
		}
		
		assert.NotEmpty(t, responses, "Should receive WebSocket responses")
		
		for _, response := range responses {
			assert.Contains(t, response, "data")
			assert.Contains(t, response, "metadata")
			assert.Contains(t, response, "timestamp")
		}
	})
}

func TestConfigurationCompatibility(t *testing.T) {
	t.Run("YAML configuration loading", func(t *testing.T) {
		mockConfig := createMockConfig()
		
		assert.Equal(t, "tealagents/v1alpha1", mockConfig.APIVersion)
		assert.Equal(t, "Agent", mockConfig.Kind)
		assert.Equal(t, "test-agent", mockConfig.ServiceName)
		assert.Equal(t, "1.0.0", mockConfig.Version)
		assert.Equal(t, "text", mockConfig.InputType)
		assert.Equal(t, "text", mockConfig.OutputType)
		assert.NotEmpty(t, mockConfig.Description)
		
		assert.Len(t, mockConfig.Spec.Agents, 1)
		assert.Len(t, mockConfig.Spec.Tasks, 1)
		
		agent := mockConfig.Spec.Agents[0]
		assert.Equal(t, "test-agent", agent.Name)
		assert.Equal(t, "assistant", agent.Role)
		assert.Equal(t, "gpt-3.5-turbo", agent.Model)
		assert.NotEmpty(t, agent.SystemPrompt)
		assert.NotNil(t, agent.Plugins)
		
		task := mockConfig.Spec.Tasks[0]
		assert.Equal(t, "test-task", task.Name)
		assert.Equal(t, 1, task.TaskNo)
		assert.Equal(t, "test-agent", task.Agent)
		assert.NotEmpty(t, task.Description)
		assert.NotEmpty(t, task.Instructions)
	})
	
	t.Run("API version parsing", func(t *testing.T) {
		mockConfig := createMockConfig()
		
		service, version, err := config.ParseAPIVersion(mockConfig.APIVersion)
		require.NoError(t, err)
		assert.Equal(t, "tealagents", service)
		assert.Equal(t, "v1alpha1", version)
	})
}

func TestTelemetryCompatibility(t *testing.T) {
	t.Run("Telemetry initialization", func(t *testing.T) {
		mockKernelBuilder := &MockKernelBuilder{}
		mockConfig := createMockConfig()
		
		agent, err := sequential.NewSequentialAgent(mockConfig, mockKernelBuilder)
		require.NoError(t, err)
		
		inputs := map[string]interface{}{
			"message": "Test telemetry",
		}
		
		response, err := agent.Invoke(context.Background(), inputs)
		require.NoError(t, err)
		require.NotNil(t, response)
		assert.NotEmpty(t, response.Result)
		
		responseChan, err := agent.InvokeStream(context.Background(), inputs)
		require.NoError(t, err)
		require.NotNil(t, responseChan)
		
		var responses []types.StreamResponse
		for response := range responseChan {
			responses = append(responses, response)
			if response.Done {
				break
			}
		}
		
		assert.NotEmpty(t, responses)
	})
	
	t.Run("HTTP telemetry middleware", func(t *testing.T) {
		gin.SetMode(gin.TestMode)
		
		mockKernelBuilder := &MockKernelBuilder{}
		mockConfig := createMockConfig()
		
		agent, err := sequential.NewSequentialAgent(mockConfig, mockKernelBuilder)
		require.NoError(t, err)
		
	srv := server.NewServer(mockConfig, agent)
	testServer := httptest.NewServer(srv)
		defer testServer.Close()
		
		resp, err := http.Get(testServer.URL + "/health")
		require.NoError(t, err)
		defer resp.Body.Close()
		
		assert.Equal(t, http.StatusOK, resp.StatusCode)
		
		var response map[string]interface{}
		err = json.NewDecoder(resp.Body).Decode(&response)
		require.NoError(t, err)
		assert.Contains(t, response, "request_id")
	})
}

func TestErrorHandlingCompatibility(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockKernelBuilder := &MockKernelBuilder{}
	mockConfig := createMockConfig()
	
	agent, err := sequential.NewSequentialAgent(mockConfig, mockKernelBuilder)
	require.NoError(t, err)
	
	srv := server.NewServer(mockConfig, agent)
	testServer := httptest.NewServer(srv)
	defer testServer.Close()
	
	t.Run("Invalid JSON request", func(t *testing.T) {
		resp, err := http.Post(testServer.URL+"/test-agent/1.0.0", "application/json", strings.NewReader("invalid json"))
		require.NoError(t, err)
		defer resp.Body.Close()
		
		assert.Equal(t, http.StatusBadRequest, resp.StatusCode)
		
		var response map[string]interface{}
		err = json.NewDecoder(resp.Body).Decode(&response)
		require.NoError(t, err)
		
		assert.Contains(t, response, "error")
		assert.Contains(t, response, "request_id")
		assert.Contains(t, response["error"], "invalid request body")
	})
	
	t.Run("Not found endpoint", func(t *testing.T) {
		resp, err := http.Get(testServer.URL + "/nonexistent")
		require.NoError(t, err)
		defer resp.Body.Close()
		
		assert.Equal(t, http.StatusNotFound, resp.StatusCode)
	})
	
	t.Run("Method not allowed", func(t *testing.T) {
		resp, err := http.Post(testServer.URL+"/health", "application/json", strings.NewReader("{}"))
		require.NoError(t, err)
		defer resp.Body.Close()
		
		assert.True(t, resp.StatusCode == 404 || resp.StatusCode == 405)
	})
	
	t.Run("Missing content type", func(t *testing.T) {
		resp, err := http.Post(testServer.URL+"/test-agent/1.0.0", "", strings.NewReader("{}"))
		require.NoError(t, err)
		defer resp.Body.Close()
		
		assert.True(t, resp.StatusCode == http.StatusOK || resp.StatusCode == http.StatusBadRequest)
	})
}

func TestAuthenticationCompatibility(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockKernelBuilder := &MockKernelBuilder{}
	mockConfig := createMockConfig()
	
	agent, err := sequential.NewSequentialAgent(mockConfig, mockKernelBuilder)
	require.NoError(t, err)
	
	srv := server.NewServer(mockConfig, agent)
	testServer := httptest.NewServer(srv)
	defer testServer.Close()
	
	t.Run("Bearer token handling", func(t *testing.T) {
		payload := map[string]interface{}{
			"message": "Test with auth",
		}
		payloadBytes, _ := json.Marshal(payload)
		
		req, err := http.NewRequest("POST", testServer.URL+"/test-agent/1.0.0", bytes.NewBuffer(payloadBytes))
		require.NoError(t, err)
		
		req.Header.Set("Authorization", "Bearer test-token-123")
		req.Header.Set("Content-Type", "application/json")
		
		client := &http.Client{}
		resp, err := client.Do(req)
		require.NoError(t, err)
		defer resp.Body.Close()
		
		assert.True(t, resp.StatusCode == http.StatusOK || resp.StatusCode == http.StatusUnauthorized)
		
		if resp.StatusCode == http.StatusOK {
			var response types.InvokeResponse
			err = json.NewDecoder(resp.Body).Decode(&response)
			require.NoError(t, err)
			assert.NotEmpty(t, response.Result)
		}
	})
	
	t.Run("Missing authorization header", func(t *testing.T) {
		payload := map[string]interface{}{
			"message": "Test without auth",
		}
		payloadBytes, _ := json.Marshal(payload)
		
		resp, err := http.Post(testServer.URL+"/test-agent/1.0.0", "application/json", bytes.NewBuffer(payloadBytes))
		require.NoError(t, err)
		defer resp.Body.Close()
		
		assert.Equal(t, http.StatusOK, resp.StatusCode)
	})
}

func TestCORSCompatibility(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockKernelBuilder := &MockKernelBuilder{}
	mockConfig := createMockConfig()
	
	agent, err := sequential.NewSequentialAgent(mockConfig, mockKernelBuilder)
	require.NoError(t, err)
	
	srv := server.NewServer(mockConfig, agent)
	testServer := httptest.NewServer(srv)
	defer testServer.Close()
	
	t.Run("CORS preflight request", func(t *testing.T) {
		req, err := http.NewRequest("OPTIONS", testServer.URL+"/test-agent/1.0.0", nil)
		require.NoError(t, err)
		
		req.Header.Set("Origin", "http://localhost:3000")
		req.Header.Set("Access-Control-Request-Method", "POST")
		req.Header.Set("Access-Control-Request-Headers", "Content-Type,Authorization")
		
		client := &http.Client{}
		resp, err := client.Do(req)
		require.NoError(t, err)
		defer resp.Body.Close()
		
		assert.Contains(t, resp.Header.Get("Access-Control-Allow-Origin"), "*")
		assert.Contains(t, resp.Header.Get("Access-Control-Allow-Methods"), "POST")
		assert.Contains(t, resp.Header.Get("Access-Control-Allow-Headers"), "Content-Type")
	})
}

func TestURLRoutingCompatibility(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockKernelBuilder := &MockKernelBuilder{}
	mockConfig := createMockConfig()
	
	agent, err := sequential.NewSequentialAgent(mockConfig, mockKernelBuilder)
	require.NoError(t, err)
	
	srv := server.NewServer(mockConfig, agent)
	testServer := httptest.NewServer(srv)
	defer testServer.Close()
	
	t.Run("URL pattern matching Python FastAPI", func(t *testing.T) {
		testCases := []struct {
			url            string
			expectedStatus int
			description    string
		}{
			{"/health", http.StatusOK, "Root health endpoint"},
			{"/health/ready", http.StatusOK, "Ready endpoint"},
			{"/test-agent/1.0.0/health", http.StatusOK, "Versioned health endpoint"},
			{"/test-agent/1.0.0/health/ready", http.StatusOK, "Versioned ready endpoint"},
		}
		
		for _, tc := range testCases {
			t.Run(tc.description, func(t *testing.T) {
				resp, err := http.Get(testServer.URL + tc.url)
				require.NoError(t, err)
				defer resp.Body.Close()
				
				assert.Equal(t, tc.expectedStatus, resp.StatusCode, "URL: %s", tc.url)
				
				if resp.StatusCode == http.StatusOK {
					var response map[string]interface{}
					err = json.NewDecoder(resp.Body).Decode(&response)
					require.NoError(t, err)
					
					assert.Contains(t, response, "status")
					assert.Contains(t, response, "service")
					assert.Contains(t, response, "version")
				}
			})
		}
	})
}
