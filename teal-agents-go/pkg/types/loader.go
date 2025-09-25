package types

import (
	"fmt"
	"go/ast"
	"go/parser"
	"go/token"
	"log"
	"os"
	"reflect"
)

func (tl *TypeLoader) LoadCustomTypesFromFile(typesModulePath string) error {
	if typesModulePath == "" {
		return nil
	}
	
	if _, err := os.Stat(typesModulePath); os.IsNotExist(err) {
		return fmt.Errorf("custom types file not found: %s", typesModulePath)
	}
	
	log.Printf("Loading custom types from: %s", typesModulePath)
	
	return tl.parseAndRegisterTypes(typesModulePath)
}

func (tl *TypeLoader) parseAndRegisterTypes(sourcePath string) error {
	fset := token.NewFileSet()
	node, err := parser.ParseFile(fset, sourcePath, nil, parser.ParseComments)
	if err != nil {
		return fmt.Errorf("failed to parse Go file: %w", err)
	}
	
	typeCount := 0
	
	ast.Inspect(node, func(n ast.Node) bool {
		switch x := n.(type) {
		case *ast.TypeSpec:
			if structType, ok := x.Type.(*ast.StructType); ok {
				typeName := x.Name.Name
				
				fields := make([]reflect.StructField, 0)
				for _, field := range structType.Fields.List {
					for _, name := range field.Names {
						fieldType := tl.parseFieldType(field.Type)
						if fieldType != nil {
							tag := ""
							if field.Tag != nil {
								tag = field.Tag.Value[1 : len(field.Tag.Value)-1] // Remove backticks
							}
							fields = append(fields, reflect.StructField{
								Name: name.Name,
								Type: fieldType,
								Tag:  reflect.StructTag(tag),
							})
						}
					}
				}
				
				if len(fields) > 0 {
					structType := reflect.StructOf(fields)
					instance := reflect.New(structType).Elem().Interface()
					tl.RegisterType(typeName, instance)
					typeCount++
					log.Printf("Registered custom type: %s", typeName)
				}
			}
		}
		return true
	})
	
	if typeCount > 0 {
		log.Printf("Successfully registered %d custom types from %s", typeCount, sourcePath)
	} else {
		log.Printf("No custom types found in %s", sourcePath)
	}
	
	return nil
}

func (tl *TypeLoader) parseFieldType(expr ast.Expr) reflect.Type {
	switch t := expr.(type) {
	case *ast.Ident:
		switch t.Name {
		case "string":
			return reflect.TypeOf("")
		case "int":
			return reflect.TypeOf(0)
		case "bool":
			return reflect.TypeOf(false)
		case "float64":
			return reflect.TypeOf(0.0)
		}
	case *ast.MapType:
		keyType := tl.parseFieldType(t.Key)
		valueType := tl.parseFieldType(t.Value)
		if keyType != nil && valueType != nil {
			return reflect.MapOf(keyType, valueType)
		}
	case *ast.ArrayType:
		if t.Len == nil { // slice
			elemType := tl.parseFieldType(t.Elt)
			if elemType != nil {
				return reflect.SliceOf(elemType)
			}
		}
	}
	return nil
}
