package types

import (
	"fmt"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

func (tl *TypeLoader) LoadCustomTypesFromFile(typesModulePath string) error {
	if typesModulePath == "" {
		return nil
	}
	
	if _, err := os.Stat(typesModulePath); os.IsNotExist(err) {
		return fmt.Errorf("custom types file not found: %s", typesModulePath)
	}
	
	log.Printf("Loading custom types from: %s", typesModulePath)
	
	return tl.compileAndLoadAsPlugin(typesModulePath)
}

func (tl *TypeLoader) compileAndLoadAsPlugin(sourcePath string) error {
	dir := filepath.Dir(sourcePath)
	filename := filepath.Base(sourcePath)
	nameWithoutExt := strings.TrimSuffix(filename, ".go")
	
	pluginPath := filepath.Join(dir, nameWithoutExt+".so")
	
	log.Printf("Compiling %s to plugin %s", sourcePath, pluginPath)
	
	cmd := exec.Command("go", "build", "-buildmode=plugin", "-o", pluginPath, sourcePath)
	cmd.Dir = dir
	
	output, err := cmd.CombinedOutput()
	if err != nil {
		log.Printf("Failed to compile plugin: %s", string(output))
		return fmt.Errorf("failed to compile custom types plugin: %w", err)
	}
	
	log.Printf("Successfully compiled plugin: %s", pluginPath)
	
	return tl.loadPluginTypes(pluginPath)
}
