# University Agent E2E Tests

Comprehensive end-to-end tests for the University Agent system using Robot Framework with Streamlit UI integration.

## Test Structure

```
tests/e2e/
├── university_agent_system.robot           # Main E2E test suite
├── streamlit_ui_integration.robot          # Streamlit-specific UI tests
├── keywords/
│   ├── service_management.robot            # University Agent service start/stop/health
│   ├── streamlit_automation.robot          # Streamlit UI automation keywords
│   ├── api_workflow.robot                  # HTTP request/response testing
│   ├── external_mocking.robot              # Network-level mocking setup
│   └── university_data_validation.robot    # University data format validation
├── resources/
│   ├── aalto_university_response.json      # Mock universities.hipolabs.com data
│   ├── university_assistant_responses.json # Mock Gemini API responses
│   └── test_data.json                      # Additional test data
├── libraries/
│   ├── UniversityAgentLibrary.py           # Custom Python test helpers
│   ├── StreamlitTestLibrary.py             # Streamlit browser automation
│   ├── UniversityAPIMockLibrary.py         # Advanced mocking utilities
│   └── MockGeminiFactory.py               # Mock Gemini completion factory
└── configs/
    └── test_university_config.yaml         # Test-specific agent configuration
```

## Prerequisites

1. **Environment Setup**:
   ```bash
   cd src/sk-agents
   uv sync --dev
   ```

2. **Required Environment Variables**:
   ```bash
   export GEMINI_API_KEY="test_gemini_api_key"
   export TA_API_KEY="test_teal_agents_key"
   ```

## Running Tests

### Run All E2E Tests
```bash
cd src/sk-agents
uv run robot tests/e2e/
```

### Run Specific Test Suite
```bash
cd src/sk-agents
uv run robot tests/e2e/university_agent_system.robot
uv run robot tests/e2e/streamlit_ui_integration.robot
```

### Run Tests with Tags
```bash
cd src/sk-agents
uv run robot --include complete-workflow tests/e2e/
uv run robot --include ui tests/e2e/
uv run robot --include error-handling tests/e2e/
```

### Generate Test Reports
```bash
cd src/sk-agents
uv run robot --outputdir results tests/e2e/
```

## Test Coverage

### Service Lifecycle Testing
- [x] University Agent service startup with Gemini completion factory
- [x] Service health endpoints verification
- [x] Graceful service shutdown and cleanup
- [x] Service restart and recovery scenarios

### Streamlit UI Integration Testing
- [x] UI startup and connection to University Agent endpoints
- [x] Complete chat workflow testing
- [x] Example query buttons functionality
- [x] Conversation history management
- [x] Agent status monitoring
- [x] UI error handling when agent is unavailable

### Complete API Workflow Testing
- [x] HTTP request/response cycle through University Agent
- [x] Agent configuration loading with custom Gemini completion factory
- [x] Error propagation through complete system
- [x] Response formatting for structured university data
- [x] Server-Sent Events (SSE) streaming testing

### External API Integration Testing
- [x] Network-level mocking for universities.hipolabs.com API
- [x] Mock Google Gemini API endpoints
- [x] Error handling for external API failures
- [x] Automatic fallback to mock university data
- [x] Timeout and retry behavior testing

## Troubleshooting

### Common Issues

1. **Chrome/Selenium Issues**:
   ```bash
   sudo apt-get update
   sudo apt-get install -y chromium-browser chromium-chromedriver
   ```

2. **Port Conflicts**:
   - Tests use ports 8001 (agent) and 8501 (UI)
   - Ensure these ports are available before running tests

3. **Service Startup Timeouts**:
   - Increase timeout values in service_management.robot if needed
   - Check service logs in agent.log and ui.log

### Debug Mode
```bash
cd src/sk-agents
uv run robot --loglevel DEBUG tests/e2e/
```
