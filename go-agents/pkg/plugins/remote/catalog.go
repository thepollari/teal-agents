package remote

import (
	"context"
	"fmt"
	"os"

	"gopkg.in/yaml.v3"
	
	"github.com/thepollari/teal-agents/go-agents/pkg/types"
)

type PluginCatalog struct {
	plugins map[string]RemotePluginConfig
	loader  *RemotePluginLoader
}

type RemotePluginConfig struct {
	PluginName     string `yaml:"plugin_name"`
	OpenAPIPath    string `yaml:"openapi_json_path"`
	ServerURL      string `yaml:"server_url,omitempty"`
	Description    string `yaml:"description,omitempty"`
	Version        string `yaml:"version,omitempty"`
	Authentication string `yaml:"authentication,omitempty"`
}

func NewPluginCatalog(catalogPath string) (*PluginCatalog, error) {
	data, err := os.ReadFile(catalogPath)
	if err != nil {
		return nil, fmt.Errorf("failed to read catalog file: %w", err)
	}
	
	var plugins map[string]RemotePluginConfig
	err = yaml.Unmarshal(data, &plugins)
	if err != nil {
		return nil, fmt.Errorf("failed to parse catalog: %w", err)
	}
	
	return &PluginCatalog{
		plugins: plugins,
		loader:  &RemotePluginLoader{},
	}, nil
}

func (c *PluginCatalog) LoadPlugin(ctx context.Context, pluginName string) (types.Plugin, error) {
	config, exists := c.plugins[pluginName]
	if !exists {
		return nil, fmt.Errorf("plugin %s not found in catalog", pluginName)
	}
	
	spec, err := c.loader.loadOpenAPISpec(ctx, RemotePlugin{
		PluginName:  config.PluginName,
		OpenAPIPath: config.OpenAPIPath,
		ServerURL:   config.ServerURL,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to load OpenAPI spec for %s: %w", pluginName, err)
	}
	
	plugin, err := NewOpenAPIPlugin(config.PluginName, spec, config.ServerURL)
	if err != nil {
		return nil, fmt.Errorf("failed to create plugin %s: %w", pluginName, err)
	}
	
	return plugin, nil
}

func (c *PluginCatalog) LoadPlugins(ctx context.Context, pluginNames []string) ([]types.Plugin, error) {
	plugins := make([]types.Plugin, 0, len(pluginNames))
	
	for _, name := range pluginNames {
		plugin, err := c.LoadPlugin(ctx, name)
		if err != nil {
			return nil, fmt.Errorf("failed to load plugin %s: %w", name, err)
		}
		plugins = append(plugins, plugin)
	}
	
	return plugins, nil
}

func (c *PluginCatalog) ListAvailablePlugins() []string {
	names := make([]string, 0, len(c.plugins))
	for name := range c.plugins {
		names = append(names, name)
	}
	return names
}

func (c *PluginCatalog) GetPluginInfo(pluginName string) (*RemotePluginConfig, error) {
	config, exists := c.plugins[pluginName]
	if !exists {
		return nil, fmt.Errorf("plugin %s not found in catalog", pluginName)
	}
	return &config, nil
}

/*
weather_api:
  plugin_name: "weather_api"
  openapi_json_path: "https://api.weather.com/openapi.json"
  server_url: "https://api.weather.com"
  description: "Weather information API"
  version: "1.0"
  authentication: "api_key"

university_search:
  plugin_name: "university_search"
  openapi_json_path: "/path/to/local/university-openapi.json"
  server_url: "https://university-api.example.com"
  description: "University search and information API"
  version: "2.1"
  authentication: "bearer"

github_api:
  plugin_name: "github_api"
  openapi_json_path: "https://raw.githubusercontent.com/github/rest-api-description/main/descriptions/api.github.com/api.github.com.json"
  server_url: "https://api.github.com"
  description: "GitHub REST API"
  version: "3.0"
  authentication: "token"
*/
