package types

import (
	"log"
	"sync"
)

type TypeRegistry struct {
	mu                sync.RWMutex
	registrationFuncs []func(*TypeLoader)
}

var globalRegistry = &TypeRegistry{
	registrationFuncs: make([]func(*TypeLoader), 0),
}

func RegisterTypeRegistrationFunc(regFunc func(*TypeLoader)) {
	globalRegistry.mu.Lock()
	defer globalRegistry.mu.Unlock()
	globalRegistry.registrationFuncs = append(globalRegistry.registrationFuncs, regFunc)
}

func (tl *TypeLoader) ApplyRegistrations() {
	globalRegistry.mu.RLock()
	defer globalRegistry.mu.RUnlock()
	
	for _, regFunc := range globalRegistry.registrationFuncs {
		regFunc(tl)
	}
	
	if len(globalRegistry.registrationFuncs) > 0 {
		log.Printf("Applied %d custom type registration functions", len(globalRegistry.registrationFuncs))
	}
}

func ClearRegistrations() {
	globalRegistry.mu.Lock()
	defer globalRegistry.mu.Unlock()
	globalRegistry.registrationFuncs = globalRegistry.registrationFuncs[:0]
}
