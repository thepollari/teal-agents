package types

import (
	"log"
)

func (tl *TypeLoader) LoadCustomTypesFromFile(typesModulePath string) error {
	log.Printf("Note: Go requires custom types to be compiled into the binary")
	log.Printf("Custom types from %s should be registered via init() functions", typesModulePath)
	log.Printf("See documentation for build-time custom type integration")
	return nil
}
