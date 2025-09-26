package university

import (
	"context"
	"testing"
	"time"
)

func TestUniversityPlugin_SearchUniversities(t *testing.T) {
	plugin := NewUniversityPlugin()
	
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	
	result, err := plugin.searchUniversities(ctx, "MIT")
	if err != nil {
		t.Fatalf("searchUniversities failed: %v", err)
	}
	
	if result == nil {
		t.Fatal("result is nil")
	}
	
	if result.Error != nil {
		t.Fatalf("API returned error: %s", *result.Error)
	}
	
	if len(result.Universities) == 0 {
		t.Fatal("no universities found")
	}
	
	t.Logf("Found %d universities for MIT search", len(result.Universities))
	for i, uni := range result.Universities {
		if i >= 3 {
			break
		}
		t.Logf("University %d: %s (%s)", i+1, uni.Name, uni.Country)
	}
}

func TestUniversityPlugin_GetUniversitiesByCountry(t *testing.T) {
	plugin := NewUniversityPlugin()
	
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	
	result, err := plugin.getUniversitiesByCountry(ctx, "United States")
	if err != nil {
		t.Fatalf("getUniversitiesByCountry failed: %v", err)
	}
	
	if result == nil {
		t.Fatal("result is nil")
	}
	
	if result.Error != nil {
		t.Fatalf("API returned error: %s", *result.Error)
	}
	
	if len(result.Universities) == 0 {
		t.Fatal("no universities found")
	}
	
	t.Logf("Found %d universities in United States", len(result.Universities))
	for i, uni := range result.Universities {
		if i >= 3 {
			break
		}
		t.Logf("University %d: %s", i+1, uni.Name)
	}
}

func TestUniversityFunction_Invoke(t *testing.T) {
	plugin := NewUniversityPlugin()
	functions := plugin.GetFunctions()
	
	if len(functions) != 2 {
		t.Fatalf("expected 2 functions, got %d", len(functions))
	}
	
	searchFunc := functions[0]
	if searchFunc.GetName() != "search_universities" {
		t.Fatalf("expected search_universities, got %s", searchFunc.GetName())
	}
	
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	
	args := map[string]interface{}{
		"query": "Stanford",
	}
	
	result, err := searchFunc.Invoke(ctx, args)
	if err != nil {
		t.Fatalf("function invoke failed: %v", err)
	}
	
	searchResult, ok := result.(*UniversitySearchResult)
	if !ok {
		t.Fatalf("expected UniversitySearchResult, got %T", result)
	}
	
	if searchResult.Error != nil {
		t.Fatalf("function returned error: %s", *searchResult.Error)
	}
	
	if len(searchResult.Universities) == 0 {
		t.Fatal("no universities found")
	}
	
	t.Logf("Function invoke successful: %s", searchResult.Message)
}
