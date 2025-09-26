package university

import (
	"reflect"
	
	"github.com/thepollari/teal-agents/go-agents/pkg/plugins"
)

func init() {
	registry := plugins.NewPluginRegistry()
	registry.Register("university", reflect.TypeOf(&UniversityPlugin{}))
}

func GetGlobalRegistry() *plugins.PluginRegistry {
	registry := plugins.NewPluginRegistry()
	registry.Register("university", reflect.TypeOf(&UniversityPlugin{}))
	return registry
}
