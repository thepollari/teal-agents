package main

import (
	"github.com/thepollari/teal-agents-go/pkg/types"
)

type MathInput struct {
	Number1   int    `json:"number_1"`
	Number2   int    `json:"number_2"`
	Operation string `json:"operation"`
}

type MathOutput struct {
	Result int    `json:"result"`
	Error  string `json:"error,omitempty"`
}

type UserProfileInput struct {
	UserID   string            `json:"user_id"`
	Name     string            `json:"name"`
	Email    string            `json:"email"`
	Metadata map[string]string `json:"metadata,omitempty"`
}

type UserProfileOutput struct {
	UserID    string            `json:"user_id"`
	Name      string            `json:"name"`
	Email     string            `json:"email"`
	Status    string            `json:"status"`
	Metadata  map[string]string `json:"metadata,omitempty"`
	CreatedAt string            `json:"created_at"`
}

func RegisterCustomTypes(tl *types.TypeLoader) {
	tl.RegisterType("MathInput", MathInput{})
	tl.RegisterType("MathOutput", MathOutput{})
	tl.RegisterType("UserProfileInput", UserProfileInput{})
	tl.RegisterType("UserProfileOutput", UserProfileOutput{})
}

func init() {
	types.RegisterTypeRegistrationFunc(RegisterCustomTypes)
}
