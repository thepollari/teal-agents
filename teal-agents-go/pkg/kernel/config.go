package kernel

import (
	"os"
	"sync"

	"github.com/thepollari/teal-agents-go/pkg/types"
)

type SimpleAppConfig struct {
	mu     sync.RWMutex
	values map[string]string
}

func NewSimpleAppConfig() *SimpleAppConfig {
	return &SimpleAppConfig{
		values: make(map[string]string),
	}
}

func (sac *SimpleAppConfig) Get(key string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}

	sac.mu.RLock()
	defer sac.mu.RUnlock()
	return sac.values[key]
}

func (sac *SimpleAppConfig) Set(key, value string) {
	sac.mu.Lock()
	defer sac.mu.Unlock()
	sac.values[key] = value
}

func (sac *SimpleAppConfig) AddConfigs(configs []types.Config) {
	sac.mu.Lock()
	defer sac.mu.Unlock()

	for _, config := range configs {
		if _, exists := sac.values[config.EnvName]; !exists {
			sac.values[config.EnvName] = config.DefaultValue
		}
	}
}

func (sac *SimpleAppConfig) LoadFromEnvironment() {
	sac.mu.Lock()
	defer sac.mu.Unlock()

	for _, env := range os.Environ() {
		for i, char := range env {
			if char == '=' {
				key := env[:i]
				value := env[i+1:]
				sac.values[key] = value
				break
			}
		}
	}

	sac.setDefaultIfEmpty("TA_TYPES_MODULE", "")
	sac.setDefaultIfEmpty("TA_PLUGIN_MODULE", "")
	sac.setDefaultIfEmpty("TA_SERVICE_CONFIG", "config.yaml")
}

func (sac *SimpleAppConfig) setDefaultIfEmpty(key, defaultValue string) {
	if _, exists := sac.values[key]; !exists {
		sac.values[key] = defaultValue
	}
}
