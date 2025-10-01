package remote

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"time"

	"github.com/thepollari/teal-agents/go-agents/pkg/types"
)

type OpenAPIFunction struct {
	name        string
	description string
	parameters  []types.FunctionParameter
	method      string
	path        string
	serverURL   string
	client      *http.Client
}

type OpenAPIPlugin struct {
	name         string
	description  string
	serverURL    string
	spec         map[string]interface{}
	functions    map[string]*OpenAPIFunction
	client       *http.Client
	authorization string
	dataCollector types.ExtraDataCollector
}

func NewOpenAPIPlugin(name string, spec map[string]interface{}, serverURL string) (*OpenAPIPlugin, error) {
	plugin := &OpenAPIPlugin{
		name:      name,
		serverURL: serverURL,
		spec:      spec,
		functions: make(map[string]*OpenAPIFunction),
		client:    &http.Client{Timeout: 60 * time.Second},
	}
	
	if info, ok := spec["info"].(map[string]interface{}); ok {
		if desc, ok := info["description"].(string); ok {
			plugin.description = desc
		}
	}
	
	err := plugin.parseFunctions()
	if err != nil {
		return nil, fmt.Errorf("failed to parse OpenAPI functions: %w", err)
	}
	
	return plugin, nil
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

func (p *OpenAPIPlugin) GetFunctions() map[string]*OpenAPIFunction {
	return p.functions
}

func (p *OpenAPIPlugin) InvokeFunction(ctx context.Context, functionName string, args map[string]interface{}) (interface{}, error) {
	function, exists := p.functions[functionName]
	if !exists {
		return nil, fmt.Errorf("function %s not found in plugin %s", functionName, p.name)
	}
	
	return function.Invoke(ctx, args)
}

func (p *OpenAPIPlugin) parseFunctions() error {
	paths, ok := p.spec["paths"].(map[string]interface{})
	if !ok {
		return fmt.Errorf("no paths found in OpenAPI spec")
	}
	
	if p.serverURL == "" {
		if servers, ok := p.spec["servers"].([]interface{}); ok && len(servers) > 0 {
			if server, ok := servers[0].(map[string]interface{}); ok {
				if url, ok := server["url"].(string); ok {
					p.serverURL = url
				}
			}
		}
	}
	
	for path, pathItem := range paths {
		pathObj, ok := pathItem.(map[string]interface{})
		if !ok {
			continue
		}
		
		for method, operation := range pathObj {
			if !isHTTPMethod(method) {
				continue
			}
			
			operationObj, ok := operation.(map[string]interface{})
			if !ok {
				continue
			}
			
			operationID, ok := operationObj["operationId"].(string)
			if !ok {
				continue
			}
			
			function := &OpenAPIFunction{
				name:      operationID,
				method:    strings.ToUpper(method),
				path:      path,
				serverURL: p.serverURL,
				client:    p.client,
			}
			
			if desc, ok := operationObj["description"].(string); ok {
				function.description = desc
			} else if summary, ok := operationObj["summary"].(string); ok {
				function.description = summary
			}
			
			if params, ok := operationObj["parameters"].([]interface{}); ok {
				function.parameters = p.parseParameters(params)
			}
			
			if requestBody, ok := operationObj["requestBody"].(map[string]interface{}); ok {
				bodyParams := p.parseRequestBody(requestBody)
				function.parameters = append(function.parameters, bodyParams...)
			}
			
			p.functions[operationID] = function
		}
	}
	
	return nil
}

func (p *OpenAPIPlugin) parseParameters(params []interface{}) []types.FunctionParameter {
	var parameters []types.FunctionParameter
	
	for _, param := range params {
		paramObj, ok := param.(map[string]interface{})
		if !ok {
			continue
		}
		
		name, ok := paramObj["name"].(string)
		if !ok {
			continue
		}
		
		parameter := types.FunctionParameter{
			Name: name,
		}
		
		if desc, ok := paramObj["description"].(string); ok {
			parameter.Description = desc
		}
		
		if schema, ok := paramObj["schema"].(map[string]interface{}); ok {
			if paramType, ok := schema["type"].(string); ok {
				parameter.Type = paramType
			}
		}
		
		if required, ok := paramObj["required"].(bool); ok {
			parameter.Required = required
		}
		
		parameters = append(parameters, parameter)
	}
	
	return parameters
}

func (p *OpenAPIPlugin) parseRequestBody(requestBody map[string]interface{}) []types.FunctionParameter {
	var parameters []types.FunctionParameter
	
	content, ok := requestBody["content"].(map[string]interface{})
	if !ok {
		return parameters
	}
	
	jsonContent, ok := content["application/json"].(map[string]interface{})
	if !ok {
		return parameters
	}
	
	schema, ok := jsonContent["schema"].(map[string]interface{})
	if !ok {
		return parameters
	}
	
	if properties, ok := schema["properties"].(map[string]interface{}); ok {
		for name, prop := range properties {
			propObj, ok := prop.(map[string]interface{})
			if !ok {
				continue
			}
			
			parameter := types.FunctionParameter{
				Name: name,
			}
			
			if desc, ok := propObj["description"].(string); ok {
				parameter.Description = desc
			}
			
			if paramType, ok := propObj["type"].(string); ok {
				parameter.Type = paramType
			}
			
			parameters = append(parameters, parameter)
		}
	}
	
	return parameters
}

func (f *OpenAPIFunction) Invoke(ctx context.Context, args map[string]interface{}) (interface{}, error) {
	url := f.serverURL + f.path
	queryParams := make(map[string]string)
	var requestBody interface{}
	
	for key, value := range args {
		if strings.Contains(f.path, "{"+key+"}") {
			url = strings.ReplaceAll(url, "{"+key+"}", fmt.Sprintf("%v", value))
		} else if f.method == "GET" || f.method == "DELETE" {
			queryParams[key] = fmt.Sprintf("%v", value)
		} else {
			if requestBody == nil {
				requestBody = make(map[string]interface{})
			}
			requestBody.(map[string]interface{})[key] = value
		}
	}
	
	if len(queryParams) > 0 {
		url += "?"
		first := true
		for key, value := range queryParams {
			if !first {
				url += "&"
			}
			url += fmt.Sprintf("%s=%s", key, value)
			first = false
		}
	}
	
	var req *http.Request
	var err error
	
	if requestBody != nil {
		bodyBytes, err := json.Marshal(requestBody)
		if err != nil {
			return nil, fmt.Errorf("failed to marshal request body: %w", err)
		}
		
		req, err = http.NewRequestWithContext(ctx, f.method, url, bytes.NewBuffer(bodyBytes))
		if err != nil {
			return nil, fmt.Errorf("failed to create request: %w", err)
		}
		
		req.Header.Set("Content-Type", "application/json")
	} else {
		req, err = http.NewRequestWithContext(ctx, f.method, url, nil)
		if err != nil {
			return nil, fmt.Errorf("failed to create request: %w", err)
		}
	}
	
	if f.client != nil {
	}
	
	resp, err := f.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("HTTP request failed: %w", err)
	}
	defer resp.Body.Close()
	
	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return nil, fmt.Errorf("HTTP request failed with status %d", resp.StatusCode)
	}
	
	var result interface{}
	err = json.NewDecoder(resp.Body).Decode(&result)
	if err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}
	
	return result, nil
}

func (f *OpenAPIFunction) GetName() string {
	return f.name
}

func (f *OpenAPIFunction) GetDescription() string {
	return f.description
}

func (f *OpenAPIFunction) GetParameters() []types.FunctionParameter {
	return f.parameters
}

func isHTTPMethod(method string) bool {
	httpMethods := []string{"get", "post", "put", "delete", "patch", "head", "options"}
	method = strings.ToLower(method)
	for _, m := range httpMethods {
		if method == m {
			return true
		}
	}
	return false
}
