package university

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/go-resty/resty/v2"

	"github.com/merck-gen/teal-agents-go/pkg/kernel"
	"github.com/merck-gen/teal-agents-go/pkg/plugins"
)

type University struct {
	Name           string   `json:"name"`
	WebPages       []string `json:"web_pages"`
	Domains        []string `json:"domains"`
	Country        string   `json:"country"`
	StateProvince  *string  `json:"state_province,omitempty"`
	AlphaTwoCode   string   `json:"alpha_two_code"`
}

type UniversitySearchResult struct {
	Message      string       `json:"message"`
	Universities []University `json:"universities"`
	Error        *string      `json:"error,omitempty"`
}

type UniversityPlugin struct {
	*plugins.BasePlugin
	client *resty.Client
}

func NewUniversityPlugin() *UniversityPlugin {
	basePlugin := plugins.NewBasePlugin("UniversityPlugin", "Search for universities by name and/or country")
	
	client := resty.New().
		SetTimeout(10 * time.Second).
		SetRetryCount(3).
		SetRetryWaitTime(1 * time.Second)

	plugin := &UniversityPlugin{
		BasePlugin: basePlugin,
		client:     client,
	}

	searchFunction := plugins.NewBaseFunction(
		"search_universities",
		"Search for universities by name and/or country",
		plugin.searchUniversitiesExecutor,
	)
	searchFunction.AddParameter(kernel.FunctionParameter{
		Name:        "query",
		Description: "University name to search for",
		Required:    true,
		Type:        "string",
	})
	plugin.AddFunction(searchFunction)

	countryFunction := plugins.NewBaseFunction(
		"get_universities_by_country",
		"Find universities in a specific country",
		plugin.getUniversitiesByCountryExecutor,
	)
	countryFunction.AddParameter(kernel.FunctionParameter{
		Name:        "country",
		Description: "Country name to search universities in",
		Required:    true,
		Type:        "string",
	})
	plugin.AddFunction(countryFunction)

	return plugin
}

func (up *UniversityPlugin) getUniversitiesURL(name, country string) string {
	baseURL := "http://universities.hipolabs.com/search"
	
	if name == "" && country == "" {
		return baseURL
	}

	params := make([]string, 0)
	if name != "" {
		params = append(params, fmt.Sprintf("name=%s", name))
	}
	if country != "" {
		params = append(params, fmt.Sprintf("country=%s", country))
	}

	if len(params) > 0 {
		return fmt.Sprintf("%s?%s", baseURL, joinParams(params))
	}

	return baseURL
}

func joinParams(params []string) string {
	if len(params) == 0 {
		return ""
	}
	
	result := params[0]
	for i := 1; i < len(params); i++ {
		result += "&" + params[i]
	}
	return result
}

func (up *UniversityPlugin) searchUniversitiesExecutor(ctx context.Context, input kernel.FunctionInput) (kernel.FunctionResult, error) {
	query, exists := input.GetValue("query")
	if !exists {
		return kernel.NewFunctionResult(nil, fmt.Errorf("query parameter is required")), fmt.Errorf("query parameter is required")
	}

	queryStr, ok := query.(string)
	if !ok {
		return kernel.NewFunctionResult(nil, fmt.Errorf("query must be a string")), fmt.Errorf("query must be a string")
	}

	result := up.searchUniversities(ctx, queryStr, "")
	return kernel.NewFunctionResult(result, nil), nil
}

func (up *UniversityPlugin) getUniversitiesByCountryExecutor(ctx context.Context, input kernel.FunctionInput) (kernel.FunctionResult, error) {
	country, exists := input.GetValue("country")
	if !exists {
		return kernel.NewFunctionResult(nil, fmt.Errorf("country parameter is required")), fmt.Errorf("country parameter is required")
	}

	countryStr, ok := country.(string)
	if !ok {
		return kernel.NewFunctionResult(nil, fmt.Errorf("country must be a string")), fmt.Errorf("country must be a string")
	}

	result := up.searchUniversities(ctx, "", countryStr)
	return kernel.NewFunctionResult(result, nil), nil
}

func (up *UniversityPlugin) searchUniversities(ctx context.Context, name, country string) *UniversitySearchResult {
	url := up.getUniversitiesURL(name, country)
	
	resp, err := up.client.R().
		SetContext(ctx).
		Get(url)

	if err != nil {
		errorMsg := fmt.Sprintf("Failed to fetch universities: %s", err.Error())
		return &UniversitySearchResult{
			Message:      "Failed to fetch universities",
			Universities: []University{},
			Error:        &errorMsg,
		}
	}

	if resp.StatusCode() != http.StatusOK {
		errorMsg := fmt.Sprintf("HTTP error: %d", resp.StatusCode())
		return &UniversitySearchResult{
			Message:      "Failed to fetch universities",
			Universities: []University{},
			Error:        &errorMsg,
		}
	}

	var universitiesData []map[string]interface{}
	if err := json.Unmarshal(resp.Body(), &universitiesData); err != nil {
		errorMsg := fmt.Sprintf("Failed to parse response: %s", err.Error())
		return &UniversitySearchResult{
			Message:      "Failed to parse universities data",
			Universities: []University{},
			Error:        &errorMsg,
		}
	}

	if len(universitiesData) == 0 {
		searchTerm := name
		if country != "" {
			if name != "" {
				searchTerm = fmt.Sprintf("%s in %s", name, country)
			} else {
				searchTerm = country
			}
		}
		return &UniversitySearchResult{
			Message:      fmt.Sprintf("No universities found for query: %s", searchTerm),
			Universities: []University{},
		}
	}

	limit := 10
	if name == "" && country != "" {
		limit = 20
	}
	if len(universitiesData) > limit {
		universitiesData = universitiesData[:limit]
	}

	universities := make([]University, 0, len(universitiesData))
	for _, uniData := range universitiesData {
		university := University{
			Name:         getStringValue(uniData, "name"),
			WebPages:     getStringSliceValue(uniData, "web_pages"),
			Domains:      getStringSliceValue(uniData, "domains"),
			Country:      getStringValue(uniData, "country"),
			AlphaTwoCode: getStringValue(uniData, "alpha_two_code"),
		}

		if stateProvince := getStringValue(uniData, "state-province"); stateProvince != "" {
			university.StateProvince = &stateProvince
		}

		universities = append(universities, university)
	}

	searchTerm := name
	if country != "" {
		if name != "" {
			searchTerm = fmt.Sprintf("%s in %s", name, country)
		} else {
			searchTerm = country
		}
	}

	return &UniversitySearchResult{
		Message:      fmt.Sprintf("Found %d universities for query: %s", len(universities), searchTerm),
		Universities: universities,
	}
}

func getStringValue(data map[string]interface{}, key string) string {
	if value, exists := data[key]; exists {
		if str, ok := value.(string); ok {
			return str
		}
	}
	return ""
}

func getStringSliceValue(data map[string]interface{}, key string) []string {
	if value, exists := data[key]; exists {
		if slice, ok := value.([]interface{}); ok {
			result := make([]string, 0, len(slice))
			for _, item := range slice {
				if str, ok := item.(string); ok {
					result = append(result, str)
				}
			}
			return result
		}
	}
	return []string{}
}
