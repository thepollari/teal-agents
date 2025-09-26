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
	"github.com/thepollari/teal-agents/go-agents/pkg/types"
)

type Server struct {
	config  *config.BaseConfig
	handler types.Handler
	router  *gin.Engine
}

func NewServer(cfg *config.BaseConfig, handler types.Handler) *Server {
	router := gin.Default()
	
	server := &Server{
		config:  cfg,
		handler: handler,
		router:  router,
	}
	
	server.setupRoutes()
	
	return server
}

func (s *Server) setupRoutes() {
	s.router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status": "ok",
			"service": s.config.ServiceName,
			"version": s.config.Version,
		})
	})
	
	v1 := s.router.Group(fmt.Sprintf("/%s/%s", s.config.ServiceName, s.config.Version))
	
	v1.POST("", s.handleInvoke)
	
	v1.GET("/sse", s.handleInvokeSSE)
	
	v1.GET("/ws", s.handleWebSocket)
}

func (s *Server) Start(addr string) error {
	return s.router.Run(addr)
}

func (s *Server) handleInvoke(c *gin.Context) {
	var inputs map[string]interface{}
	if err := c.ShouldBindJSON(&inputs); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": fmt.Sprintf("invalid request body: %v", err),
		})
		return
	}
	
	ctx, cancel := context.WithTimeout(c.Request.Context(), 60*time.Second)
	defer cancel()
	
	response, err := s.handler.Invoke(ctx, inputs)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": fmt.Sprintf("invocation failed: %v", err),
		})
		return
	}
	
	c.JSON(http.StatusOK, response)
}

func (s *Server) handleInvokeSSE(c *gin.Context) {
	var inputs map[string]interface{}
	if err := c.ShouldBindJSON(&inputs); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": fmt.Sprintf("invalid request body: %v", err),
		})
		return
	}
	
	c.Writer.Header().Set("Content-Type", "text/event-stream")
	c.Writer.Header().Set("Cache-Control", "no-cache")
	c.Writer.Header().Set("Connection", "keep-alive")
	c.Writer.Header().Set("Transfer-Encoding", "chunked")
	
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
