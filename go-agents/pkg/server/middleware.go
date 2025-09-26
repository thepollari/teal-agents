package server

import (
	"context"
	"fmt"
	"net/http"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/thepollari/teal-agents/go-agents/pkg/logging"
)

func RequestLoggingMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		requestID := uuid.New().String()
		
		ctx := context.WithValue(c.Request.Context(), "request_id", requestID)
		ctx = context.WithValue(ctx, "trace_id", requestID)
		c.Request = c.Request.WithContext(ctx)
		
		c.Header("X-Request-ID", requestID)
		
		c.Next()
		
		duration := time.Since(start)
		logging.LogHTTPRequest(ctx, c.Request.Method, c.Request.URL.Path, c.Writer.Status(), duration.String())
	}
}

func CORSMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Origin, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization, X-Request-ID")
		c.Header("Access-Control-Expose-Headers", "X-Request-ID")
		c.Header("Access-Control-Allow-Credentials", "true")
		
		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(http.StatusNoContent)
			return
		}
		
		c.Next()
	}
}

func AuthorizationMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.Next()
			return
		}
		
		if strings.HasPrefix(authHeader, "Bearer ") {
			token := strings.TrimPrefix(authHeader, "Bearer ")
			ctx := context.WithValue(c.Request.Context(), "auth_token", token)
			c.Request = c.Request.WithContext(ctx)
		}
		
		c.Next()
	}
}

func ErrorHandlingMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		defer func() {
			if err := recover(); err != nil {
				logger := logging.WithContext(c.Request.Context())
				logger.Error("Panic recovered",
					"error", fmt.Sprintf("%v", err),
					"path", c.Request.URL.Path,
					"method", c.Request.Method,
				)
				
				c.JSON(http.StatusInternalServerError, gin.H{
					"error": "Internal server error",
					"request_id": c.GetHeader("X-Request-ID"),
				})
				c.Abort()
			}
		}()
		
		c.Next()
		
		if len(c.Errors) > 0 {
			logger := logging.WithContext(c.Request.Context())
			for _, err := range c.Errors {
				logger.Error("Request error",
					"error", err.Error(),
					"path", c.Request.URL.Path,
					"method", c.Request.Method,
				)
			}
			
			lastError := c.Errors.Last()
			c.JSON(http.StatusInternalServerError, gin.H{
				"error": lastError.Error(),
				"request_id": c.GetHeader("X-Request-ID"),
			})
		}
	}
}

func TelemetryMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		
		c.Next()
		
		duration := time.Since(start)
		logger := logging.WithContext(c.Request.Context())
		
		logger.Info("Request telemetry",
			"method", c.Request.Method,
			"path", c.Request.URL.Path,
			"status_code", c.Writer.Status(),
			"duration_ms", duration.Milliseconds(),
			"content_length", c.Writer.Size(),
			"user_agent", c.Request.UserAgent(),
			"remote_addr", c.ClientIP(),
		)
	}
}
