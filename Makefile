.PHONY: all teal-agents orchestrator services

all : | teal-agents orchestrator services

teal-agents :
	@echo "Building Teal Agents..."
	@docker build ${DOCKER_FLAGS} -t teal-agents:latest -f teal-agents.Dockerfile .

orchestrator :
	@echo "Building Orchestrator..."
	@docker build ${DOCKER_FLAGS} -t jose:latest -f ao.Dockerfile .

services :
	@echo "Building Services..."
	@docker build ${DOCKER_FLAGS} -t ska-services:latest -f ao-services.Dockerfile .

clean:
	@echo "Cleaning up..."
	@docker rmi teal-agents:latest || true
	@docker rmi jose:latest || true
	@docker rmi ska-services:latest || true