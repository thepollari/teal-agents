package main

import (
	"github.com/thepollari/teal-agents-go/pkg/types"
)

type NumbersInput struct {
	Number1 int `json:"number_1"`
	Number2 int `json:"number_2"`
}

type AddOutput struct {
	Result int `json:"result"`
}

func RegisterCustomTypes(tl *types.TypeLoader) {
	tl.RegisterType("NumbersInput", NumbersInput{})
	tl.RegisterType("AddOutput", AddOutput{})
}

func main() {
	typeLoader := types.GetTypeLoader()
	RegisterCustomTypes(typeLoader)
}
