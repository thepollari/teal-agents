.PHONY: all teal-agents orchestrator services

all : | teal-agents orchestrator services

teal-agents :
	@echo "Building Teal Agents..."
	@docker build ${DOCKER_FLAGS} -t teal-agents:latest -f teal-agents.Dockerfile .

orchestrator :
	@echo "Building Orchestrator..."
	@docker build ${DOCKER_FLAGS} -t ao:latest -f ao.Dockerfile .

services :
	@echo "Building Services..."
	@docker build ${DOCKER_FLAGS} -t ao-services:latest -f ao-services.Dockerfile .

clean:
	@echo "Cleaning up..."
	@docker rmi teal-agents:latest || true
	@docker rmi ao:latest || true
	@docker rmi ao-services:latest || true