package api

import (
	"context"
	"fmt"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"

	"github.com/merck-gen/teal-agents-go/pkg/config"
	"github.com/merck-gen/teal-agents-go/pkg/kernel"
)

type Server struct {
	engine   *gin.Engine
	config   *config.BaseConfig
	kernel   kernel.Kernel
	logger   *logrus.Logger
	handlers map[string]Handler
}

func (s *Server) GetEngine() *gin.Engine {
	return s.engine
}

type Handler interface {
	Handle(c *gin.Context) error
}

type ServerConfig struct {
	Host         string
	Port         int
	ReadTimeout  time.Duration
	WriteTimeout time.Duration
	IdleTimeout  time.Duration
}

func NewServer(cfg *config.BaseConfig, k kernel.Kernel, logger *logrus.Logger) *Server {
	gin.SetMode(gin.ReleaseMode)
	engine := gin.New()

	engine.Use(gin.Recovery())
	engine.Use(LoggerMiddleware(logger))
	engine.Use(CORSMiddleware())

	return &Server{
		engine:   engine,
		config:   cfg,
		kernel:   k,
		logger:   logger,
		handlers: make(map[string]Handler),
	}
}

func (s *Server) RegisterHandler(path string, handler Handler) {
	s.handlers[path] = handler
}

func (s *Server) SetupRoutes() {
	s.engine.GET("/health", s.healthCheck)

	v1 := s.engine.Group(fmt.Sprintf("/%s/%v", s.config.Name, s.config.Version))
	{
		v1.POST("/invoke", s.handleInvoke)
		v1.POST("/invoke-stream", s.handleInvokeStream)
		v1.GET("/agent-card", s.handleAgentCard)

		v1.GET("/ws", s.handleWebSocket)

		a2a := v1.Group("/a2a")
		{
			a2a.POST("/invoke", s.handleA2AInvoke)
			a2a.GET("/agent-card", s.handleA2AAgentCard)
		}

		v1.POST("/chat", s.handleStatefulChat)
		v1.POST("/resume", s.handleResume)
	}
}

func (s *Server) Start(serverConfig ServerConfig) error {
	s.SetupRoutes()

	server := &http.Server{
		Addr:         fmt.Sprintf("%s:%d", serverConfig.Host, serverConfig.Port),
		Handler:      s.engine,
		ReadTimeout:  serverConfig.ReadTimeout,
		WriteTimeout: serverConfig.WriteTimeout,
		IdleTimeout:  serverConfig.IdleTimeout,
	}

	s.logger.Infof("Starting server on %s:%d", serverConfig.Host, serverConfig.Port)
	return server.ListenAndServe()
}

func (s *Server) StartWithContext(ctx context.Context, serverConfig ServerConfig) error {
	s.SetupRoutes()

	server := &http.Server{
		Addr:         fmt.Sprintf("%s:%d", serverConfig.Host, serverConfig.Port),
		Handler:      s.engine,
		ReadTimeout:  serverConfig.ReadTimeout,
		WriteTimeout: serverConfig.WriteTimeout,
		IdleTimeout:  serverConfig.IdleTimeout,
	}

	go func() {
		s.logger.Infof("Starting server on %s:%d", serverConfig.Host, serverConfig.Port)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			s.logger.Fatalf("Server failed to start: %v", err)
		}
	}()

	<-ctx.Done()

	s.logger.Info("Shutting down server...")
	shutdownCtx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	return server.Shutdown(shutdownCtx)
}

func (s *Server) healthCheck(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":    "healthy",
		"timestamp": time.Now().UTC(),
		"service":   s.config.Name,
		"version":   s.config.Version,
	})
}

func (s *Server) handleInvoke(c *gin.Context) {
	if handler, exists := s.handlers["invoke"]; exists {
		if err := handler.Handle(c); err != nil {
			s.logger.Errorf("Handler error: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		}
	} else {
		c.JSON(http.StatusNotImplemented, gin.H{"error": "invoke handler not registered"})
	}
}

func (s *Server) handleInvokeStream(c *gin.Context) {
	if handler, exists := s.handlers["invoke-stream"]; exists {
		if err := handler.Handle(c); err != nil {
			s.logger.Errorf("Handler error: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		}
	} else {
		c.JSON(http.StatusNotImplemented, gin.H{"error": "invoke-stream handler not registered"})
	}
}

func (s *Server) handleAgentCard(c *gin.Context) {
	if handler, exists := s.handlers["agent-card"]; exists {
		if err := handler.Handle(c); err != nil {
			s.logger.Errorf("Handler error: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		}
	} else {
		c.JSON(http.StatusNotImplemented, gin.H{"error": "agent-card handler not registered"})
	}
}

func (s *Server) handleWebSocket(c *gin.Context) {
	c.JSON(http.StatusNotImplemented, gin.H{"error": "WebSocket not implemented yet"})
}

func (s *Server) handleA2AInvoke(c *gin.Context) {
	if handler, exists := s.handlers["a2a-invoke"]; exists {
		if err := handler.Handle(c); err != nil {
			s.logger.Errorf("Handler error: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		}
	} else {
		c.JSON(http.StatusNotImplemented, gin.H{"error": "a2a-invoke handler not registered"})
	}
}

func (s *Server) handleA2AAgentCard(c *gin.Context) {
	if handler, exists := s.handlers["a2a-agent-card"]; exists {
		if err := handler.Handle(c); err != nil {
			s.logger.Errorf("Handler error: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		}
	} else {
		c.JSON(http.StatusNotImplemented, gin.H{"error": "a2a-agent-card handler not registered"})
	}
}

func (s *Server) handleStatefulChat(c *gin.Context) {
	c.JSON(http.StatusNotImplemented, gin.H{"error": "Stateful chat not implemented yet"})
}

func (s *Server) handleResume(c *gin.Context) {
	c.JSON(http.StatusNotImplemented, gin.H{"error": "Resume not implemented yet"})
}
