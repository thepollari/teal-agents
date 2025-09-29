package handlers

import "github.com/gin-gonic/gin"

type HandlerAdapter struct {
	handlerFunc func(c *gin.Context)
}

func NewHandlerAdapter(handlerFunc func(c *gin.Context)) *HandlerAdapter {
	return &HandlerAdapter{
		handlerFunc: handlerFunc,
	}
}

func (ha *HandlerAdapter) Handle(c *gin.Context) error {
	ha.handlerFunc(c)
	return nil
}
