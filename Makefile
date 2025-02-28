.PHONY: all sk-agents orchestrator services

all : | sk-agents orchestrator services

sk-agents :
	@echo "Building SK agents..."
	@docker build ${DOCKER_FLAGS} -t sk-agents:latest -f sk-agents.Dockerfile .

orchestrator :
	@echo "Building Orchestrator..."
	@docker build ${DOCKER_FLAGS} -t jose:latest -f ao.Dockerfile .

services :
	@echo "Building Services..."
	@docker build ${DOCKER_FLAGS} -t ska-services:latest -f ao-services.Dockerfile .

clean:
	@echo "Cleaning up..."
	@docker rmi sk-agents:latest || true
	@docker rmi jose:latest || true
	@docker rmi ska-services:latest || true