package types

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
	"plugin"
	"reflect"
	"strings"
	"sync"
)

type TypeLoader struct {
	mu          sync.RWMutex
	baseTypes   map[string]reflect.Type
	typesModule string
	agentsPath  string
}

func NewTypeLoader(typesModule string, agentsPath string) *TypeLoader {
	tl := &TypeLoader{
		baseTypes:   make(map[string]reflect.Type),
		typesModule: typesModule,
		agentsPath:  agentsPath,
	}

	tl.initStandardTypes()

	if typesModule == "" && agentsPath != "" {
		customTypesPath := filepath.Join(agentsPath, "custom_types.go")
		if _, err := os.Stat(customTypesPath); err == nil {
			typesModule = customTypesPath
			tl.typesModule = typesModule
		}
	}

	if typesModule != "" {
		if err := tl.setTypesModule(typesModule); err != nil {
			log.Printf("Warning: Could not load custom types module '%s': %v", typesModule, err)
		}
	}
	
	tl.ApplyRegistrations()

	return tl
}

func (tl *TypeLoader) initStandardTypes() {
	tl.baseTypes["BaseInput"] = reflect.TypeOf(BaseInput{})
	tl.baseTypes["InvokeResponse"] = reflect.TypeOf(InvokeResponse{})
	tl.baseTypes["PartialResponse"] = reflect.TypeOf(PartialResponse{})
	tl.baseTypes["HistoryMessage"] = reflect.TypeOf(HistoryMessage{})
	tl.baseTypes["TokenUsage"] = reflect.TypeOf(TokenUsage{})
}

func (tl *TypeLoader) setTypesModule(typesModule string) error {
	tl.mu.Lock()
	defer tl.mu.Unlock()

	if typesModule == "" {
		return nil
	}

	if _, err := os.Stat(typesModule); os.IsNotExist(err) {
		return fmt.Errorf("types module file not found: %s", typesModule)
	}

	log.Printf("Custom types module specified: %s", typesModule)
	
	if strings.HasSuffix(typesModule, ".so") {
		log.Printf("Loading .so plugin: %s", typesModule)
		return tl.loadPluginTypes(typesModule)
	}
	
	if strings.HasSuffix(typesModule, ".go") {
		log.Printf("Loading .go file via source parsing: %s", typesModule)
		return tl.LoadCustomTypesFromFile(typesModule)
	}
	
	log.Printf("Unsupported types module format: %s", typesModule)
	return fmt.Errorf("unsupported types module format: %s", typesModule)
}

func (tl *TypeLoader) loadPluginTypes(pluginPath string) error {
	p, err := plugin.Open(pluginPath)
	if err != nil {
		return fmt.Errorf("failed to open plugin %s: %w", pluginPath, err)
	}
	
	registerFunc, err := p.Lookup("RegisterCustomTypes")
	if err != nil {
		return fmt.Errorf("RegisterCustomTypes function not found in plugin: %w", err)
	}
	
	if regFunc, ok := registerFunc.(func(*TypeLoader)); ok {
		regFunc(tl)
		log.Printf("Successfully loaded custom types from plugin: %s", pluginPath)
	} else {
		return fmt.Errorf("RegisterCustomTypes function has wrong signature")
	}
	
	return nil
}

func (tl *TypeLoader) GetType(typeName string) (reflect.Type, error) {
	tl.mu.RLock()
	defer tl.mu.RUnlock()

	if standardType, exists := tl.baseTypes[typeName]; exists {
		return standardType, nil
	}

	return nil, fmt.Errorf("type %s not found in standard types or custom module", typeName)
}

func (tl *TypeLoader) RegisterType(typeName string, typeInstance interface{}) {
	tl.mu.Lock()
	defer tl.mu.Unlock()

	tl.baseTypes[typeName] = reflect.TypeOf(typeInstance)
}

func (tl *TypeLoader) GetStandardType(typeName string) (reflect.Type, bool) {
	tl.mu.RLock()
	defer tl.mu.RUnlock()

	standardType, exists := tl.baseTypes[typeName]
	return standardType, exists
}

var globalTypeLoader *TypeLoader
var typeLoaderOnce sync.Once

func GetTypeLoader() *TypeLoader {
	typeLoaderOnce.Do(func() {
		typesModule := os.Getenv("TA_TYPES_MODULE")
		globalTypeLoader = NewTypeLoader(typesModule, "")
	})
	return globalTypeLoader
}

func InitializeTypeLoader(typesModule, agentsPath string) {
	typeLoaderOnce.Do(func() {
		globalTypeLoader = NewTypeLoader(typesModule, agentsPath)
	})
}

func GetTypeLoaderWithPath(typesModule, agentsPath string) *TypeLoader {
	return NewTypeLoader(typesModule, agentsPath)
}

func (tl *TypeLoader) AddTypeRegistrationFunc(registrationFunc func(*TypeLoader)) {
	registrationFunc(tl)
}

func (tl *TypeLoader) CreateInstance(typeName string) (interface{}, error) {
	typeRef, err := tl.GetType(typeName)
	if err != nil {
		return nil, err
	}

	if typeRef.Kind() == reflect.Ptr {
		instance := reflect.New(typeRef.Elem()).Interface()
		return instance, nil
	} else {
		instance := reflect.New(typeRef).Elem().Interface()
		return instance, nil
	}
}
