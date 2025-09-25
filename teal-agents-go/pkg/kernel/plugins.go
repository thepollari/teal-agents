package kernel

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"

	"github.com/thepollari/teal-agents-go/pkg/types"
)

type RemotePluginLoader struct {
	httpClient *http.Client
}

func NewRemotePluginLoader() *RemotePluginLoader {
	return &RemotePluginLoader{
		httpClient: &http.Client{},
	}
}

func (rpl *RemotePluginLoader) LoadFromURL(url, name string) (types.Plugin, error) {
	resp, err := rpl.httpClient.Get(url)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch OpenAPI spec from %s: %w", url, err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("failed to fetch OpenAPI spec: HTTP %d", resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read OpenAPI spec: %w", err)
	}

	var spec map[string]interface{}
	if err := json.Unmarshal(body, &spec); err != nil {
		return nil, fmt.Errorf("failed to parse OpenAPI spec: %w", err)
	}

	plugin := &RemotePlugin{
		name:        name,
		description: getStringFromSpec(spec, "info.description", "Remote plugin"),
		baseURL:     url,
		spec:        spec,
		functions:   make([]types.Function, 0),
	}

	if paths, ok := spec["paths"].(map[string]interface{}); ok {
		for path, pathSpec := range paths {
			if pathData, ok := pathSpec.(map[string]interface{}); ok {
				for method, methodSpec := range pathData {
					if methodData, ok := methodSpec.(map[string]interface{}); ok {
						function := &RemoteFunction{
							name:        fmt.Sprintf("%s_%s", method, sanitizePath(path)),
							description: getStringFromSpec(methodData, "summary", "Remote function"),
							method:      method,
							path:        path,
							baseURL:     url,
							spec:        methodData,
						}
						plugin.functions = append(plugin.functions, function)
					}
				}
			}
		}
	}

	return plugin, nil
}

type LocalPluginLoader struct{}

func NewLocalPluginLoader() *LocalPluginLoader {
	return &LocalPluginLoader{}
}

func (lpl *LocalPluginLoader) LoadFromPath(path, name string) (types.Plugin, error) {
	if _, err := os.Stat(path); os.IsNotExist(err) {
		return nil, fmt.Errorf("plugin path does not exist: %s", path)
	}

	plugin := &LocalPlugin{
		name:        name,
		description: fmt.Sprintf("Local plugin from %s", path),
		path:        path,
		functions:   make([]types.Function, 0),
	}

	err := filepath.Walk(path, func(filePath string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if filepath.Ext(filePath) == ".json" {
			function, err := lpl.loadFunctionFromFile(filePath)
			if err == nil {
				plugin.functions = append(plugin.functions, function)
			}
		}

		return nil
	})

	if err != nil {
		return nil, fmt.Errorf("failed to scan plugin directory: %w", err)
	}

	return plugin, nil
}

func (lpl *LocalPluginLoader) loadFunctionFromFile(filePath string) (types.Function, error) {
	data, err := os.ReadFile(filePath)
	if err != nil {
		return nil, err
	}

	var spec map[string]interface{}
	if err := json.Unmarshal(data, &spec); err != nil {
		return nil, err
	}

	function := &LocalFunction{
		name:        getStringFromSpec(spec, "name", filepath.Base(filePath)),
		description: getStringFromSpec(spec, "description", "Local function"),
		spec:        spec,
	}

	return function, nil
}

type RemotePlugin struct {
	name        string
	description string
	baseURL     string
	spec        map[string]interface{}
	functions   []types.Function
}

func (rp *RemotePlugin) GetName() string                { return rp.name }
func (rp *RemotePlugin) GetDescription() string         { return rp.description }
func (rp *RemotePlugin) GetFunctions() []types.Function { return rp.functions }

type RemoteFunction struct {
	name        string
	description string
	method      string
	path        string
	baseURL     string
	spec        map[string]interface{}
}

func (rf *RemoteFunction) GetName() string        { return rf.name }
func (rf *RemoteFunction) GetDescription() string { return rf.description }

func (rf *RemoteFunction) Invoke(ctx context.Context, kernel interface{}, arguments map[string]interface{}) (interface{}, error) {
	return map[string]interface{}{
		"result": fmt.Sprintf("Called remote function %s with arguments %v", rf.name, arguments),
	}, nil
}

type LocalPlugin struct {
	name        string
	description string
	path        string
	functions   []types.Function
}

func (lp *LocalPlugin) GetName() string                { return lp.name }
func (lp *LocalPlugin) GetDescription() string         { return lp.description }
func (lp *LocalPlugin) GetFunctions() []types.Function { return lp.functions }

type LocalFunction struct {
	name        string
	description string
	spec        map[string]interface{}
}

func (lf *LocalFunction) GetName() string        { return lf.name }
func (lf *LocalFunction) GetDescription() string { return lf.description }

func (lf *LocalFunction) Invoke(ctx context.Context, kernel interface{}, arguments map[string]interface{}) (interface{}, error) {
	return map[string]interface{}{
		"result": fmt.Sprintf("Called local function %s with arguments %v", lf.name, arguments),
	}, nil
}

func getStringFromSpec(spec map[string]interface{}, path, defaultValue string) string {
	keys := []string{}
	current := ""
	for _, char := range path {
		if char == '.' {
			if current != "" {
				keys = append(keys, current)
				current = ""
			}
		} else {
			current += string(char)
		}
	}
	if current != "" {
		keys = append(keys, current)
	}

	current_map := spec
	for i, key := range keys {
		if i == len(keys)-1 {
			if value, ok := current_map[key].(string); ok {
				return value
			}
		} else {
			if next_map, ok := current_map[key].(map[string]interface{}); ok {
				current_map = next_map
			} else {
				break
			}
		}
	}

	return defaultValue
}

func sanitizePath(path string) string {
	result := ""
	for _, char := range path {
		if (char >= 'a' && char <= 'z') || (char >= 'A' && char <= 'Z') || (char >= '0' && char <= '9') {
			result += string(char)
		} else {
			result += "_"
		}
	}
	return result
}
