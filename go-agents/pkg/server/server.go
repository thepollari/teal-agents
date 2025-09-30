package server

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
	
	"github.com/thepollari/teal-agents/go-agents/pkg/config"
	"github.com/thepollari/teal-agents/go-agents/pkg/logging"
	"github.com/thepollari/teal-agents/go-agents/pkg/types"
)

type Server struct {
	config  *config.BaseConfig
	handler types.Handler
	router  *gin.Engine
}

func NewServer(cfg *config.BaseConfig, handler types.Handler) *Server {
	router := gin.New()
	
	server := &Server{
		config:  cfg,
		handler: handler,
		router:  router,
	}
	
	server.setupMiddleware()
	server.setupRoutes()
	
	return server
}

func (s *Server) setupMiddleware() {
	s.router.Use(RequestLoggingMiddleware())
	s.router.Use(CORSMiddleware())
	s.router.Use(AuthorizationMiddleware())
	s.router.Use(TelemetryMiddleware())
	s.router.Use(ErrorHandlingMiddleware())
}

func (s *Server) setupRoutes() {
	s.router.GET("/health", s.handleHealth)
	s.router.GET("/health/ready", s.handleHealthReady)
	
	v1 := s.router.Group(fmt.Sprintf("/%s/%s", s.config.ServiceName, s.config.Version))
	
	v1.GET("/health", s.handleHealth)
	v1.GET("/health/ready", s.handleHealthReady)
	
	v1.POST("", s.handleInvoke)
	v1.GET("/sse", s.handleInvokeSSE)
	v1.GET("/ws", s.handleWebSocket)
}

func (s *Server) handleHealth(c *gin.Context) {
	logger := logging.WithContext(c.Request.Context())
	logger.Info("Health check requested")
	
	c.JSON(http.StatusOK, gin.H{
		"status":     "healthy",
		"service":    s.config.ServiceName,
		"version":    s.config.Version,
		"request_id": c.GetHeader("X-Request-ID"),
	})
}

func (s *Server) handleHealthReady(c *gin.Context) {
	logger := logging.WithContext(c.Request.Context())
	logger.Info("Readiness check requested")
	
	c.JSON(http.StatusOK, gin.H{
		"status":     "ready",
		"service":    s.config.ServiceName,
		"version":    s.config.Version,
		"request_id": c.GetHeader("X-Request-ID"),
	})
}

func (s *Server) Start(addr string) error {
	logger := logging.GetLogger()
	logger.Info("Starting server", "address", addr, "service", s.config.ServiceName)
	return s.router.Run(addr)
}

func (s *Server) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	s.router.ServeHTTP(w, r)
}

func (s *Server) handleInvoke(c *gin.Context) {
	logger := logging.WithContext(c.Request.Context())
	
	var inputs map[string]interface{}
	if err := c.ShouldBindJSON(&inputs); err != nil {
		logger.Error("Invalid JSON in invoke request", "error", err.Error())
		c.JSON(http.StatusBadRequest, gin.H{
			"error":      fmt.Sprintf("invalid request body: %v", err),
			"request_id": c.GetHeader("X-Request-ID"),
		})
		return
	}
	
	logger.Info("Processing invoke request", "request", inputs)
	
	ctx, cancel := context.WithTimeout(c.Request.Context(), 60*time.Second)
	defer cancel()
	
	response, err := s.handler.Invoke(ctx, inputs)
	if err != nil {
		logger.Error("Handler invoke failed", "error", err.Error())
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":      fmt.Sprintf("invocation failed: %v", err),
			"request_id": c.GetHeader("X-Request-ID"),
		})
		return
	}
	
	logger.Info("Invoke request completed successfully")
	c.JSON(http.StatusOK, response)
}

func (s *Server) handleInvokeSSE(c *gin.Context) {
	inputs := make(map[string]interface{})
	
	for key, values := range c.Request.URL.Query() {
		if len(values) > 0 {
			inputs[key] = values[0]
		}
	}
	
	if len(inputs) == 0 {
		if err := c.ShouldBindJSON(&inputs); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{
				"error": fmt.Sprintf("invalid request body: %v", err),
			})
			return
		}
	}
	
	c.Header("Content-Type", "text/event-stream")
	c.Header("Cache-Control", "no-cache")
	c.Header("Connection", "keep-alive")
	c.Header("Transfer-Encoding", "chunked")
	c.Header("Access-Control-Allow-Origin", "*")
	c.Header("Access-Control-Allow-Headers", "Cache-Control")
	
	ctx, cancel := context.WithTimeout(c.Request.Context(), 5*time.Minute)
	defer cancel()
	
	responseChan, err := s.handler.InvokeStream(ctx, inputs)
	if err != nil {
		event := fmt.Sprintf("event: error\ndata: %s\n\n", err.Error())
		c.Writer.Write([]byte(event))
		c.Writer.Flush()
		return
	}
	
	for response := range responseChan {
		data, err := json.Marshal(response)
		if err != nil {
			event := fmt.Sprintf("event: error\ndata: %s\n\n", err.Error())
			c.Writer.Write([]byte(event))
			c.Writer.Flush()
			continue
		}
		
		event := fmt.Sprintf("event: message\ndata: %s\n\n", string(data))
		c.Writer.Write([]byte(event))
		c.Writer.Flush()
		
		if response.Done {
			break
		}
	}
}

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin: func(r *http.Request) bool {
		return true // Allow all origins
	},
}

func (s *Server) handleWebSocket(c *gin.Context) {
	conn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": fmt.Sprintf("failed to upgrade connection: %v", err),
		})
		return
	}
	defer conn.Close()
	
	_, message, err := conn.ReadMessage()
	if err != nil {
		conn.WriteJSON(gin.H{
			"error": fmt.Sprintf("failed to read message: %v", err),
		})
		return
	}
	
	var inputs map[string]interface{}
	if err := json.Unmarshal(message, &inputs); err != nil {
		conn.WriteJSON(gin.H{
			"error": fmt.Sprintf("invalid message: %v", err),
		})
		return
	}
	
	ctx, cancel := context.WithTimeout(c.Request.Context(), 5*time.Minute)
	defer cancel()
	
	responseChan, err := s.handler.InvokeStream(ctx, inputs)
	if err != nil {
		conn.WriteJSON(gin.H{
			"error": fmt.Sprintf("invocation failed: %v", err),
		})
		return
	}
	
	for response := range responseChan {
		err := conn.WriteJSON(response)
		if err != nil {
			break
		}
		
		if response.Done {
			break
		}
	}
}
