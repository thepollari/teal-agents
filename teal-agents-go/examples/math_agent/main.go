package main

import (
	"log"

	"github.com/thepollari/teal-agents-go/pkg/types"
)

func main() {
	log.Println("Starting Math Agent with Custom Types...")

	typeLoader := types.GetTypeLoader()
	RegisterCustomTypes(typeLoader)

	log.Println("Custom types registered successfully:")
	log.Println("- MathInput")
	log.Println("- MathOutput")
	log.Println("- UserProfileInput")
	log.Println("- UserProfileOutput")

	testTypeCreation(typeLoader)

	log.Println("Math Agent initialization complete!")
}

func testTypeCreation(typeLoader *types.TypeLoader) {
	mathInput, err := typeLoader.CreateInstance("MathInput")
	if err != nil {
		log.Printf("Error creating MathInput: %v", err)
		return
	}
	log.Printf("Successfully created MathInput instance: %T", mathInput)

	mathOutput, err := typeLoader.CreateInstance("MathOutput")
	if err != nil {
		log.Printf("Error creating MathOutput: %v", err)
		return
	}
	log.Printf("Successfully created MathOutput instance: %T", mathOutput)

	mathInputType, err := typeLoader.GetType("MathInput")
	if err != nil {
		log.Printf("Error getting MathInput type: %v", err)
		return
	}
	log.Printf("MathInput type: %v", mathInputType)
}
