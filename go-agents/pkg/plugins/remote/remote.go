package remote

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"sync"

	"gopkg.in/yaml.v3"
	
	"github.com/thepollari/teal-agents/go-agents/pkg/types"
)

type RemotePlugin struct {
	PluginName     string `yaml:"plugin_name"`
	OpenAPIPath    string `yaml:"openapi_json_path"`
	ServerURL      string `yaml:"server_url,omitempty"`
}

type RemotePluginLoader struct {
	catalog map[string]RemotePlugin
	client  *http.Client
	mu      sync.RWMutex
}

func NewRemotePluginLoader(catalogPath string) (*RemotePluginLoader, error) {
	data, err := os.ReadFile(catalogPath)
	if err != nil {
		return nil, fmt.Errorf("failed to read catalog file: %w", err)
	}
	
	var catalog map[string]RemotePlugin
	err = yaml.Unmarshal(data, &catalog)
	if err != nil {
		return nil, fmt.Errorf("failed to parse catalog: %w", err)
	}
	
	return &RemotePluginLoader{
		catalog: catalog,
		client:  &http.Client{Timeout: 60 * http.Second},
	}, nil
}

func (r *RemotePluginLoader) LoadRemotePlugins(ctx context.Context, kernel types.Kernel, pluginNames []string) error {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	for _, name := range pluginNames {
		plugin, exists := r.catalog[name]
		if !exists {
			return fmt.Errorf("remote plugin %s not found in catalog", name)
		}
		
		spec, err := r.loadOpenAPISpec(ctx, plugin)
		if err != nil {
			return fmt.Errorf("failed to load OpenAPI spec for plugin %s: %w", name, err)
		}
		
		remotePlugin, err := r.createRemotePlugin(plugin, spec)
		if err != nil {
			return fmt.Errorf("failed to create remote plugin %s: %w", name, err)
		}
		
		err = kernel.AddPlugin(ctx, remotePlugin)
		if err != nil {
			return fmt.Errorf("failed to add remote plugin %s to kernel: %w", name, err)
		}
	}
	
	return nil
}

func (r *RemotePluginLoader) loadOpenAPISpec(ctx context.Context, plugin RemotePlugin) (map[string]interface{}, error) {
	if isURL(plugin.OpenAPIPath) {
		return r.loadOpenAPISpecFromURL(ctx, plugin.OpenAPIPath)
	}
	return r.loadOpenAPISpecFromFile(plugin.OpenAPIPath)
}

func (r *RemotePluginLoader) loadOpenAPISpecFromURL(ctx context.Context, url string) (map[string]interface{}, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}
	
	resp, err := r.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch OpenAPI spec: %w", err)
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("failed to fetch OpenAPI spec: status code %d", resp.StatusCode)
	}
	
	data, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response body: %w", err)
	}
	
	var spec map[string]interface{}
	err = json.Unmarshal(data, &spec)
	if err != nil {
		return nil, fmt.Errorf("failed to parse OpenAPI spec: %w", err)
	}
	
	return spec, nil
}

func (r *RemotePluginLoader) loadOpenAPISpecFromFile(path string) (map[string]interface{}, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read OpenAPI spec file: %w", err)
	}
	
	var spec map[string]interface{}
	err = json.Unmarshal(data, &spec)
	if err != nil {
		return nil, fmt.Errorf("failed to parse OpenAPI spec: %w", err)
	}
	
	return spec, nil
}

func (r *RemotePluginLoader) createRemotePlugin(config RemotePlugin, spec map[string]interface{}) (types.Plugin, error) {
	
	return &OpenAPIPlugin{
		name:        config.PluginName,
		description: fmt.Sprintf("Remote plugin %s", config.PluginName),
		serverURL:   config.ServerURL,
		spec:        spec,
	}, nil
}

func isURL(s string) bool {
	return len(s) > 8 && (s[:7] == "http://" || s[:8] == "https://")
}

type OpenAPIPlugin struct {
	name           string
	description    string
	serverURL      string
	spec           map[string]interface{}
	authorization  string
	dataCollector  types.ExtraDataCollector
}

func (p *OpenAPIPlugin) Initialize(ctx context.Context, authorization string, extraDataCollector types.ExtraDataCollector) error {
	p.authorization = authorization
	p.dataCollector = extraDataCollector
	return nil
}

func (p *OpenAPIPlugin) GetName() string {
	return p.name
}

func (p *OpenAPIPlugin) GetDescription() string {
	return p.description
}
