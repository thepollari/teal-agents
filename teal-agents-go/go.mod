module github.com/thepollari/teal-agents-go

go 1.21.5

require gopkg.in/yaml.v3 v3.0.1

require (
	github.com/go-chi/chi/v5 v5.2.3
	github.com/thepollari/teal-agents-go/examples/math_agent v0.0.0-00010101000000-000000000000
)

replace github.com/thepollari/teal-agents-go/examples/math_agent => ./examples/math_agent
