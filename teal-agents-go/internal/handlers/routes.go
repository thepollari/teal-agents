package handlers

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"

	"github.com/thepollari/teal-agents-go/pkg/agents"
	"github.com/thepollari/teal-agents-go/pkg/types"
)

type Routes struct {
	appConfig types.AppConfig
}

func NewRoutes(appConfig types.AppConfig) *Routes {
	return &Routes{
		appConfig: appConfig,
	}
}

func (r *Routes) GetRestRoutes(name, version, description string, config types.BaseConfig) *http.ServeMux {
	mux := http.NewServeMux()

	mux.HandleFunc("POST /", r.addCORSHeaders(r.handleInvoke(config)))

	mux.HandleFunc("POST /sse", r.addCORSHeaders(r.handleInvokeSSE(config)))

	mux.HandleFunc("GET /health", r.addCORSHeaders(r.handleHealth()))

	mux.HandleFunc("GET /agent-card", r.addCORSHeaders(r.handleAgentCard(name, version, description, config)))

	mux.HandleFunc("OPTIONS /", r.handleOptions())
	mux.HandleFunc("OPTIONS /sse", r.handleOptions())
	mux.HandleFunc("OPTIONS /health", r.handleOptions())
	mux.HandleFunc("OPTIONS /agent-card", r.handleOptions())

	return mux
}

func (r *Routes) handleInvoke(config types.BaseConfig) http.HandlerFunc {
	return func(w http.ResponseWriter, req *http.Request) {
		var inputs map[string]interface{}
		if err := json.NewDecoder(req.Body).Decode(&inputs); err != nil {
			http.Error(w, fmt.Sprintf("Invalid JSON: %v", err), http.StatusBadRequest)
			return
		}

		handler, err := r.createHandler(config)
		if err != nil {
			http.Error(w, fmt.Sprintf("Failed to create handler: %v", err), http.StatusInternalServerError)
			return
		}

		response, err := handler.Invoke(req.Context(), inputs)
		if err != nil {
			http.Error(w, fmt.Sprintf("Handler invocation failed: %v", err), http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		if err := json.NewEncoder(w).Encode(response); err != nil {
			log.Printf("Failed to encode response: %v", err)
		}
	}
}

func (r *Routes) handleInvokeSSE(config types.BaseConfig) http.HandlerFunc {
	return func(w http.ResponseWriter, req *http.Request) {
		w.Header().Set("Content-Type", "text/event-stream")
		w.Header().Set("Cache-Control", "no-cache")
		w.Header().Set("Connection", "keep-alive")
		w.Header().Set("Access-Control-Allow-Origin", "*")

		var inputs map[string]interface{}
		if err := json.NewDecoder(req.Body).Decode(&inputs); err != nil {
			fmt.Fprintf(w, "event: error\ndata: Invalid JSON: %v\n\n", err)
			return
		}

		handler, err := r.createHandler(config)
		if err != nil {
			fmt.Fprintf(w, "event: error\ndata: Failed to create handler: %v\n\n", err)
			return
		}

		responseChan, err := handler.InvokeStream(req.Context(), inputs)
		if err != nil {
			fmt.Fprintf(w, "event: error\ndata: Handler stream failed: %v\n\n", err)
			return
		}

		flusher, ok := w.(http.Flusher)
		if !ok {
			http.Error(w, "Streaming unsupported", http.StatusInternalServerError)
			return
		}

		for partialResponse := range responseChan {
			data, _ := json.Marshal(partialResponse)
			fmt.Fprintf(w, "event: partial\ndata: %s\n\n", data)
			flusher.Flush()
		}

		fmt.Fprintf(w, "event: done\ndata: {}\n\n")
		flusher.Flush()
	}
}

func (r *Routes) handleHealth() http.HandlerFunc {
	return func(w http.ResponseWriter, req *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]string{
			"status":  "healthy",
			"service": "teal-agents-go",
		})
	}
}

func (r *Routes) handleAgentCard(name, version, description string, config types.BaseConfig) http.HandlerFunc {
	return func(w http.ResponseWriter, req *http.Request) {
		agentCard := map[string]interface{}{
			"name":         name,
			"version":      version,
			"description":  description,
			"apiVersion":   config.APIVersion,
			"capabilities": []string{"invoke", "stream", "sse"},
			"inputType":    config.InputType,
			"outputType":   config.OutputType,
		}

		if config.Metadata != nil {
			agentCard["metadata"] = config.Metadata
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(agentCard)
	}
}

func (r *Routes) createHandler(config types.BaseConfig) (types.BaseHandler, error) {
	agentConfig := types.AgentConfig{
		ModelName: "gpt-3.5-turbo", // Default model
		ServiceID: "openai",        // Default service
		Plugins:   []types.PluginConfig{},
		Settings:  make(map[string]interface{}),
	}

	if spec, ok := config.Spec.(map[string]interface{}); ok {
		if modelName, ok := spec["model_name"].(string); ok {
			agentConfig.ModelName = modelName
		}
		if serviceID, ok := spec["service_id"].(string); ok {
			agentConfig.ServiceID = serviceID
		}
		if settings, ok := spec["settings"].(map[string]interface{}); ok {
			agentConfig.Settings = settings
		}
	}

	agentBuilder := agents.NewAgentBuilder(r.appConfig)
	extraDataCollector := agents.NewExtraDataCollector()

	skAgent, err := agentBuilder.BuildAgent(agentConfig, extraDataCollector)
	if err != nil {
		return nil, fmt.Errorf("failed to build agent: %w", err)
	}

	handlerType := "chat" // Default to chat handler
	if config.Name != nil {
		name := strings.ToLower(*config.Name)
		if strings.Contains(name, "sequential") {
			handlerType = "sequential"
		}
	}

	switch handlerType {
	case "sequential":
		tasks := []agents.Task{
			{
				TaskNo:   1,
				TaskName: "main_task",
				Agent:    skAgent,
				Settings: agentConfig.Settings,
			},
		}
		return agents.NewSequentialSkagents(tasks, extraDataCollector), nil
	case "chat":
		return agents.NewChatAgents(skAgent, extraDataCollector), nil
	default:
		return agents.NewChatAgents(skAgent, extraDataCollector), nil
	}
}

func (r *Routes) addCORSHeaders(handler http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, req *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

		handler(w, req)
	}
}

func (r *Routes) handleOptions() http.HandlerFunc {
	return func(w http.ResponseWriter, req *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
		w.WriteHeader(http.StatusOK)
	}
}
