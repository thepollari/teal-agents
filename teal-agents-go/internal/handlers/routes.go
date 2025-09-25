package handlers

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"reflect"
	"strings"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
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

func (r *Routes) GetRestRoutes(name, version, description string, config types.BaseConfig) chi.Router {
	router := chi.NewRouter()

	router.Use(middleware.Logger)
	router.Use(middleware.Recoverer)
	router.Use(r.corsMiddleware)

	versionedRouter := chi.NewRouter()
	versionedRouter.Post("/", r.handleInvoke(config))
	versionedRouter.Post("/sse", r.handleInvokeSSE(config))
	versionedRouter.Get("/health", r.handleHealth())
	versionedRouter.Get("/agent-card", r.handleAgentCard(name, version, description, config))

	router.Mount(fmt.Sprintf("/%s/%s", name, version), versionedRouter)

	return router
}

func (r *Routes) handleInvoke(config types.BaseConfig) http.HandlerFunc {
	return func(w http.ResponseWriter, req *http.Request) {
		var inputs map[string]interface{}

		if config.InputType != nil && *config.InputType != "" {
			typeLoader := types.GetTypeLoader()
			inputType, err := typeLoader.GetType(*config.InputType)
			if err != nil {
				log.Printf("Warning: Could not load input type %s: %v", *config.InputType, err)
				if err := json.NewDecoder(req.Body).Decode(&inputs); err != nil {
					http.Error(w, fmt.Sprintf("Invalid JSON: %v", err), http.StatusBadRequest)
					return
				}
			} else {
				inputInstance := reflect.New(inputType).Interface()
				if err := json.NewDecoder(req.Body).Decode(inputInstance); err != nil {
					http.Error(w, fmt.Sprintf("Invalid JSON for type %s: %v", *config.InputType, err), http.StatusBadRequest)
					return
				}

				inputBytes, _ := json.Marshal(inputInstance)
				json.Unmarshal(inputBytes, &inputs)

				log.Printf("Successfully parsed custom input type: %s", *config.InputType)
			}
		} else {
			if err := json.NewDecoder(req.Body).Decode(&inputs); err != nil {
				http.Error(w, fmt.Sprintf("Invalid JSON: %v", err), http.StatusBadRequest)
				return
			}
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

		typeLoader := types.GetTypeLoader()
		if config.InputType != nil && *config.InputType != "" {
			if _, err := typeLoader.GetType(*config.InputType); err == nil {
				agentCard["customInputType"] = true
				log.Printf("Custom input type '%s' is registered", *config.InputType)
			} else {
				log.Printf("Custom input type '%s' not found: %v", *config.InputType, err)
				agentCard["customInputType"] = false
			}
		}
		if config.OutputType != nil && *config.OutputType != "" {
			if _, err := typeLoader.GetType(*config.OutputType); err == nil {
				agentCard["customOutputType"] = true
				log.Printf("Custom output type '%s' is registered", *config.OutputType)
			} else {
				log.Printf("Custom output type '%s' not found: %v", *config.OutputType, err)
				agentCard["customOutputType"] = false
			}
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

func (r *Routes) corsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, req *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

		if req.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}

		next.ServeHTTP(w, req)
	})
}
