package university

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"time"

	"github.com/thepollari/teal-agents/go-agents/pkg/types"
)

type University struct {
	Name           string   `json:"name"`
	WebPages       []string `json:"web_pages"`
	Domains        []string `json:"domains"`
	Country        string   `json:"country"`
	StateProvince  *string  `json:"state-province,omitempty"`
	AlphaTwoCode   string   `json:"alpha_two_code"`
}

type UniversitySearchResult struct {
	Message      string       `json:"message"`
	Universities []University `json:"universities"`
	Error        *string      `json:"error,omitempty"`
}

type UniversityPlugin struct {
	name        string
	description string
	client      *http.Client
}

func NewUniversityPlugin() *UniversityPlugin {
	return &UniversityPlugin{
		name:        "university",
		description: "Search for universities by name and country",
		client:      &http.Client{Timeout: 10 * time.Second},
	}
}

func (p *UniversityPlugin) Initialize(ctx context.Context, authorization string, extraDataCollector types.ExtraDataCollector) error {
	return nil
}

func (p *UniversityPlugin) GetName() string {
	return p.name
}

func (p *UniversityPlugin) GetDescription() string {
	return p.description
}

func (p *UniversityPlugin) GetFunctions() []types.KernelFunction {
	return []types.KernelFunction{
		&UniversityFunction{
			name:        "search_universities",
			description: "Search for universities by name and/or country",
			plugin:      p,
			funcType:    "search",
		},
		&UniversityFunction{
			name:        "get_universities_by_country",
			description: "Find universities in a specific country",
			plugin:      p,
			funcType:    "country",
		},
	}
}

func (p *UniversityPlugin) getUniversitiesURL(name, country string) string {
	baseURL := "http://universities.hipolabs.com/search"
	params := url.Values{}
	
	if name != "" {
		params.Add("name", name)
	}
	if country != "" {
		params.Add("country", country)
	}
	
	if len(params) > 0 {
		return fmt.Sprintf("%s?%s", baseURL, params.Encode())
	}
	return baseURL
}

func (p *UniversityPlugin) searchUniversities(ctx context.Context, query string) (*UniversitySearchResult, error) {
	url := p.getUniversitiesURL(query, "")
	
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return &UniversitySearchResult{
			Message:      "Failed to create request",
			Universities: []University{},
			Error:        stringPtr(fmt.Sprintf("Failed to create request: %v", err)),
		}, nil
	}
	
	resp, err := p.client.Do(req)
	if err != nil {
		return &UniversitySearchResult{
			Message:      "Failed to fetch universities",
			Universities: []University{},
			Error:        stringPtr(fmt.Sprintf("Failed to fetch universities: %v", err)),
		}, nil
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != http.StatusOK {
		return &UniversitySearchResult{
			Message:      "Failed to fetch universities",
			Universities: []University{},
			Error:        stringPtr(fmt.Sprintf("HTTP error: %d", resp.StatusCode)),
		}, nil
	}
	
	var universitiesData []University
	if err := json.NewDecoder(resp.Body).Decode(&universitiesData); err != nil {
		return &UniversitySearchResult{
			Message:      "Failed to parse response",
			Universities: []University{},
			Error:        stringPtr(fmt.Sprintf("Failed to parse response: %v", err)),
		}, nil
	}
	
	if len(universitiesData) == 0 {
		return &UniversitySearchResult{
			Message:      fmt.Sprintf("No universities found for query: %s", query),
			Universities: []University{},
		}, nil
	}
	
	if len(universitiesData) > 10 {
		universitiesData = universitiesData[:10]
	}
	
	return &UniversitySearchResult{
		Message:      fmt.Sprintf("Found %d universities for query: %s", len(universitiesData), query),
		Universities: universitiesData,
	}, nil
}

func (p *UniversityPlugin) getUniversitiesByCountry(ctx context.Context, country string) (*UniversitySearchResult, error) {
	url := p.getUniversitiesURL("", country)
	
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return &UniversitySearchResult{
			Message:      "Failed to create request",
			Universities: []University{},
			Error:        stringPtr(fmt.Sprintf("Failed to create request: %v", err)),
		}, nil
	}
	
	resp, err := p.client.Do(req)
	if err != nil {
		return &UniversitySearchResult{
			Message:      "Failed to fetch universities",
			Universities: []University{},
			Error:        stringPtr(fmt.Sprintf("Failed to fetch universities: %v", err)),
		}, nil
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != http.StatusOK {
		return &UniversitySearchResult{
			Message:      "Failed to fetch universities",
			Universities: []University{},
			Error:        stringPtr(fmt.Sprintf("HTTP error: %d", resp.StatusCode)),
		}, nil
	}
	
	var universitiesData []University
	if err := json.NewDecoder(resp.Body).Decode(&universitiesData); err != nil {
		return &UniversitySearchResult{
			Message:      "Failed to parse response",
			Universities: []University{},
			Error:        stringPtr(fmt.Sprintf("Failed to parse response: %v", err)),
		}, nil
	}
	
	if len(universitiesData) == 0 {
		return &UniversitySearchResult{
			Message:      fmt.Sprintf("No universities found in country: %s", country),
			Universities: []University{},
		}, nil
	}
	
	if len(universitiesData) > 20 {
		universitiesData = universitiesData[:20]
	}
	
	return &UniversitySearchResult{
		Message:      fmt.Sprintf("Found %d universities in %s", len(universitiesData), country),
		Universities: universitiesData,
	}, nil
}

type UniversityFunction struct {
	name        string
	description string
	plugin      *UniversityPlugin
	funcType    string
}

func (f *UniversityFunction) Invoke(ctx context.Context, args map[string]interface{}) (interface{}, error) {
	switch f.funcType {
	case "search":
		query, ok := args["query"].(string)
		if !ok {
			return nil, fmt.Errorf("query parameter is required and must be a string")
		}
		return f.plugin.searchUniversities(ctx, query)
	case "country":
		country, ok := args["country"].(string)
		if !ok {
			return nil, fmt.Errorf("country parameter is required and must be a string")
		}
		return f.plugin.getUniversitiesByCountry(ctx, country)
	default:
		return nil, fmt.Errorf("unknown function type: %s", f.funcType)
	}
}

func (f *UniversityFunction) GetName() string {
	return f.name
}

func (f *UniversityFunction) GetDescription() string {
	return f.description
}

func (f *UniversityFunction) GetParameters() []types.FunctionParameter {
	switch f.funcType {
	case "search":
		return []types.FunctionParameter{
			{
				Name:        "query",
				Type:        "string",
				Description: "University name to search for",
				Required:    true,
			},
		}
	case "country":
		return []types.FunctionParameter{
			{
				Name:        "country",
				Type:        "string",
				Description: "Country name to search universities in",
				Required:    true,
			},
		}
	default:
		return []types.FunctionParameter{}
	}
}

func stringPtr(s string) *string {
	return &s
}
