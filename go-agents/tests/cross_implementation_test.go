package tests

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const (
	pythonPort = "8001"
	goPort     = "8002"
	pythonURL  = "http://localhost:" + pythonPort
	goURL      = "http://localhost:" + goPort
)

type ServerResponse struct {
	StatusCode int
	Headers    map[string]string
	Body       map[string]interface{}
	RawBody    string
}

type TestServer struct {
	cmd    *exec.Cmd
	port   string
	name   string
	ready  bool
}

func TestCrossImplementationCompatibility(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping cross-implementation tests in short mode")
	}

	pythonServer := startPythonServer(t)
	defer stopServer(t, pythonServer)
	
	time.Sleep(5 * time.Second)

	goServer := startGoServer(t)
	defer stopServer(t, goServer)

	waitForServer(t, pythonURL, "Python")
	waitForServer(t, goURL, "Go")

	t.Run("Agent Invocation", func(t *testing.T) {
		testAgentInvocation(t)
	})

	t.Run("Error Handling", func(t *testing.T) {
		testErrorHandling(t)
	})

	t.Run("URL Routing", func(t *testing.T) {
		testURLRouting(t)
	})

	t.Run("Response Headers", func(t *testing.T) {
		testResponseHeaders(t)
	})

	t.Run("Health Endpoints", func(t *testing.T) {
		testHealthEndpoints(t)
	})
}

func startPythonServer(t *testing.T) *TestServer {
	pythonDir := "../../src/sk-agents"
	configPath := filepath.Join(pythonDir, "docs/demos/01_getting_started/config.yaml")

	env := os.Environ()
	env = append(env, "TA_SERVICE_CONFIG="+configPath)
	env = append(env, "OTEL_ENABLED=false") // Disable telemetry for cleaner comparison
	
	if os.Getenv("TA_API_KEY") == "" {
		env = append(env, "TA_API_KEY=sk-1234567890abcdefghijklmnopqrstuvwxyz1234567890")
	}

	cmd := exec.Command("uv", "run", "--", "fastapi", "run", "src/sk_agents/app.py", "--port", pythonPort)
	cmd.Dir = pythonDir
	cmd.Env = env
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	err := cmd.Start()
	require.NoError(t, err, "Failed to start Python server")

	return &TestServer{
		cmd:  cmd,
		port: pythonPort,
		name: "Python",
	}
}

func startGoServer(t *testing.T) *TestServer {
	goDir := ".."
	buildCmd := exec.Command("go", "build", "-o", "teal-agent", "./cmd/agent")
	buildCmd.Dir = goDir
	err := buildCmd.Run()
	require.NoError(t, err, "Failed to build Go server")

	configPath := "examples/getting_started/config.yaml"
	
	env := os.Environ()
	env = append(env, "OTEL_ENABLED=false") // Disable telemetry for cleaner comparison
	env = append(env, "PORT="+goPort)
	
	if os.Getenv("TA_API_KEY") == "" {
		env = append(env, "TA_API_KEY=sk-1234567890abcdefghijklmnopqrstuvwxyz1234567890")
	}
	
	cmd := exec.Command("./teal-agent", configPath)
	cmd.Dir = goDir
	cmd.Env = env
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	err = cmd.Start()
	require.NoError(t, err, "Failed to start Go server")

	return &TestServer{
		cmd:  cmd,
		port: goPort,
		name: "Go",
	}
}

func stopServer(t *testing.T, server *TestServer) {
	if server.cmd != nil && server.cmd.Process != nil {
		err := server.cmd.Process.Kill()
		if err != nil {
			t.Logf("Failed to kill %s server: %v", server.name, err)
		}
		server.cmd.Wait()
	}
}

func waitForServer(t *testing.T, baseURL, name string) {
	client := &http.Client{Timeout: 5 * time.Second}
	
	invocationURL := baseURL + "/ChatBot/0.1"
	
	for i := 0; i < 60; i++ { // Wait up to 120 seconds
		resp, err := client.Post(invocationURL, "application/json", strings.NewReader("invalid json"))
		if err == nil {
			resp.Body.Close()
			if resp.StatusCode == 422 || resp.StatusCode == 500 {
				t.Logf("%s server is ready (status: %d)", name, resp.StatusCode)
				return
			}
		}
		if resp != nil {
			resp.Body.Close()
		}
		t.Logf("Waiting for %s server... (attempt %d/60)", name, i+1)
		time.Sleep(2 * time.Second)
	}
	
	t.Fatalf("%s server failed to start within timeout", name)
}

func makeRequest(method, url string, body interface{}) (*ServerResponse, error) {
	var reqBody io.Reader
	if body != nil {
		jsonBody, err := json.Marshal(body)
		if err != nil {
			return nil, err
		}
		reqBody = bytes.NewBuffer(jsonBody)
	}

	req, err := http.NewRequest(method, url, reqBody)
	if err != nil {
		return nil, err
	}

	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}

	client := &http.Client{Timeout: 30 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	rawBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	headers := make(map[string]string)
	for key, values := range resp.Header {
		if len(values) > 0 {
			headers[key] = values[0]
		}
	}

	response := &ServerResponse{
		StatusCode: resp.StatusCode,
		Headers:    headers,
		RawBody:    string(rawBody),
	}

	if len(rawBody) > 0 && strings.Contains(resp.Header.Get("Content-Type"), "application/json") {
		var jsonBody map[string]interface{}
		if err := json.Unmarshal(rawBody, &jsonBody); err == nil {
			response.Body = jsonBody
		}
	}

	return response, nil
}


func testAgentInvocation(t *testing.T) {
	endpoint := "/ChatBot/0.1"
	payload := map[string]interface{}{
		"message": "Hello, test agent!",
		"task":    "respond",
	}

	pythonResp, err := makeRequest("POST", pythonURL+endpoint, payload)
	require.NoError(t, err, "Python request failed")

	goResp, err := makeRequest("POST", goURL+endpoint, payload)
	require.NoError(t, err, "Go request failed")

	assert.Equal(t, pythonResp.StatusCode, goResp.StatusCode, 
		"Status codes don't match for agent invocation")

	assert.Equal(t, 500, pythonResp.StatusCode, "Python should return 500 for missing API key")
	assert.Equal(t, 500, goResp.StatusCode, "Go should return 500 for missing API key")

	if pythonResp.Body != nil && goResp.Body != nil {
		assert.Contains(t, pythonResp.Body, "error", "Python response missing error field")
		assert.Contains(t, goResp.Body, "error", "Go response missing error field")
		
		pythonError := pythonResp.Body["error"].(string)
		goError := goResp.Body["error"].(string)
		
		pythonErrorLower := strings.ToLower(pythonError)
		goErrorLower := strings.ToLower(goError)
		
		assert.True(t, strings.Contains(pythonErrorLower, "api") || strings.Contains(pythonErrorLower, "auth") || strings.Contains(pythonErrorLower, "key"), 
			"Python error should mention API/auth/key: %s", pythonError)
		assert.True(t, strings.Contains(goErrorLower, "api") || strings.Contains(goErrorLower, "auth") || strings.Contains(goErrorLower, "key"), 
			"Go error should mention API/auth/key: %s", goError)
	}
}

func testErrorHandling(t *testing.T) {
	testCases := []struct {
		name     string
		endpoint string
		method   string
		body     interface{}
		expected int
	}{
		{
			name:     "Invalid JSON",
			endpoint: "/ChatBot/0.1",
			method:   "POST",
			body:     "invalid json",
			expected: 422,
		},
		{
			name:     "Not Found",
			endpoint: "/nonexistent",
			method:   "GET",
			body:     nil,
			expected: 404,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			var pythonResp, goResp *ServerResponse
			var err error

			if tc.body == "invalid json" {
				pythonReq, _ := http.NewRequest(tc.method, pythonURL+tc.endpoint, strings.NewReader("invalid json"))
				pythonReq.Header.Set("Content-Type", "application/json")
				client := &http.Client{Timeout: 30 * time.Second}
				resp, err := client.Do(pythonReq)
				require.NoError(t, err)
				defer resp.Body.Close()
				rawBody, _ := io.ReadAll(resp.Body)
				pythonResp = &ServerResponse{StatusCode: resp.StatusCode, RawBody: string(rawBody)}

				goReq, _ := http.NewRequest(tc.method, goURL+tc.endpoint, strings.NewReader("invalid json"))
				goReq.Header.Set("Content-Type", "application/json")
				resp, err = client.Do(goReq)
				require.NoError(t, err)
				defer resp.Body.Close()
				rawBody, _ = io.ReadAll(resp.Body)
				goResp = &ServerResponse{StatusCode: resp.StatusCode, RawBody: string(rawBody)}
			} else {
				pythonResp, err = makeRequest(tc.method, pythonURL+tc.endpoint, tc.body)
				require.NoError(t, err, "Python request failed")

				goResp, err = makeRequest(tc.method, goURL+tc.endpoint, tc.body)
				require.NoError(t, err, "Go request failed")
			}

			assert.Equal(t, pythonResp.StatusCode, goResp.StatusCode, 
				"Status codes don't match for %s", tc.name)

			assert.Equal(t, tc.expected, pythonResp.StatusCode, 
				"Python status code doesn't match expected for %s", tc.name)
			assert.Equal(t, tc.expected, goResp.StatusCode, 
				"Go status code doesn't match expected for %s", tc.name)
		})
	}
}

func testURLRouting(t *testing.T) {
	testCases := []struct {
		url    string
		method string
		desc   string
	}{
		{"/ChatBot/0.1", "POST", "Agent invocation endpoint"},
		{"/ChatBot/0.1/sse", "POST", "SSE endpoint"},
		{"/nonexistent", "GET", "404 endpoint"},
	}

	for _, tc := range testCases {
		t.Run(tc.desc, func(t *testing.T) {
			var body interface{}
			if tc.method == "POST" {
				body = map[string]interface{}{"message": "test"}
			}

			pythonResp, err := makeRequest(tc.method, pythonURL+tc.url, body)
			require.NoError(t, err, "Python request failed")

			goResp, err := makeRequest(tc.method, goURL+tc.url, body)
			require.NoError(t, err, "Go request failed")

			assert.Equal(t, pythonResp.StatusCode, goResp.StatusCode, 
				"URL routing behavior differs for %s %s", tc.method, tc.url)
		})
	}
}

func testResponseHeaders(t *testing.T) {
	endpoint := "/ChatBot/0.1"
	body := map[string]interface{}{"message": "test"}
	
	pythonResp, err := makeRequest("POST", pythonURL+endpoint, body)
	require.NoError(t, err, "Python request failed")

	goResp, err := makeRequest("POST", goURL+endpoint, body)
	require.NoError(t, err, "Go request failed")

	importantHeaders := []string{
		"Content-Type",
	}

	for _, header := range importantHeaders {
		pythonHeader := pythonResp.Headers[header]
		goHeader := goResp.Headers[header]
		
		if pythonHeader != "" || goHeader != "" {
			assert.Equal(t, pythonHeader, goHeader, 
				"Header %s differs: Python=%s, Go=%s", header, pythonHeader, goHeader)
		}
	}
}

func testHealthEndpoints(t *testing.T) {
	endpoints := []string{
		"/health",
		"/health/ready",
		"/ChatBot/0.1/health",
		"/ChatBot/0.1/health/ready",
	}

	for _, endpoint := range endpoints {
		t.Run("Go_"+endpoint, func(t *testing.T) {
			goResp, err := makeRequest("GET", goURL+endpoint, nil)
			require.NoError(t, err, "Go health request failed for %s", endpoint)

			assert.Equal(t, 200, goResp.StatusCode, "Go health endpoint should return 200")

			if goResp.Body != nil {
				assert.Contains(t, goResp.Body, "status", "Go health response should contain status")
			}
		})
		
		t.Run("Python_"+endpoint, func(t *testing.T) {
			pythonResp, err := makeRequest("GET", pythonURL+endpoint, nil)
			require.NoError(t, err, "Python health request failed for %s", endpoint)

			assert.Equal(t, 404, pythonResp.StatusCode, "Python server should return 404 for health endpoints")
		})
	}
}
