# University Agent E2E Tests

Comprehensive end-to-end test suite for the University Agent system using Robot Framework.

## Overview

This test suite provides two types of tests:

1. **UAT Suite** (`uat_live_system.robot`) - Tests against live, already-running services with real API keys (PRIMARY FOCUS)
2. **E2E Suite** (`university_agent_system.robot`) - Automated tests with service management using MockGeminiFactory

## Prerequisites

### Install Dependencies

```bash
cd ~/repos/teal-agents/src/sk-agents
uv sync --dev
```

This installs Robot Framework and required libraries:
- `robotframework` - Core test framework
- `robotframework-requests` - HTTP API testing
- `robotframework-jsonlibrary` - JSON validation

### Environment Setup

For UAT tests with real services, you need:

```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
export TA_SERVICE_CONFIG="$(pwd)/../../orchestrators/assistant-orchestrator/example/university/config.yaml"
export TA_PLUGIN_MODULE="$(pwd)/../../orchestrators/assistant-orchestrator/example/university/custom_plugins.py"
export TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE="src/sk_agents/chat_completion/custom/gemini_chat_completion_factory.py"
export TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS_NAME="GeminiChatCompletionFactory"
```

## Running Tests

### UAT Suite (Recommended for Manual Testing)

The UAT suite tests against already-running services. Start services first:

**Terminal 1 - Start Agent:**
```bash
cd ~/repos/teal-agents/src/sk-agents
uv run uvicorn sk_agents.app:app --host 0.0.0.0 --port 8001
```

**Terminal 2 - Start Streamlit:**
```bash
cd ~/repos/teal-agents/src/orchestrators/assistant-orchestrator/example/university
uv run streamlit run streamlit_ui.py --server.port 8502
```

**Terminal 3 - Run UAT Tests:**
```bash
cd ~/repos/teal-agents/src/sk-agents
uv run robot --outputdir test-results tests/e2e/uat_live_system.robot
```

### E2E Suite (Automated with Mock)

The E2E suite automatically starts/stops services with MockGeminiFactory:

```bash
cd ~/repos/teal-agents/src/sk-agents
uv run robot --outputdir test-results tests/e2e/university_agent_system.robot
```

### Run Specific Tests

Run tests with specific tags:

```bash
# Run only smoke tests
uv run robot --outputdir test-results --include smoke tests/e2e/uat_live_system.robot

# Run only API tests
uv run robot --outputdir test-results --include api tests/e2e/uat_live_system.robot

# Run only search tests
uv run robot --outputdir test-results --include search tests/e2e/uat_live_system.robot
```

## Test Structure

```
tests/e2e/
├── uat_live_system.robot           # UAT suite for live services (PRIMARY)
├── university_agent_system.robot   # E2E suite with automation
├── keywords/
│   └── service_management.robot   # Service start/stop keywords
├── mock_gemini_factory.py         # Mock factory for E2E tests
└── README.md                       # This file
```

## Test Coverage

### UAT Suite Tests

1. **Smoke Tests**
   - Agent API accessibility
   - Streamlit UI accessibility

2. **Search Functionality**
   - Search universities by name
   - Search universities by country
   - Multi-turn conversations

3. **API Validation**
   - Response format validation (output_raw field)
   - Token usage tracking
   - Error handling

### E2E Suite Tests

1. **Service Management**
   - Agent service startup with MockGeminiFactory
   - Streamlit UI startup
   - Service health checks

2. **Basic API Testing**
   - Valid response format
   - Correct field structure

## Viewing Test Results

After running tests, view the results:

```bash
# Open HTML report
open test-results/report.html

# View log file
open test-results/log.html
```

## Troubleshooting

### Services Not Starting

Check logs:
```bash
tail -f /tmp/agent_stdout.log
tail -f /tmp/streamlit_stdout.log
```

### Port Already in Use

Kill existing processes:
```bash
lsof -ti:8001 | xargs kill -9  # Agent
lsof -ti:8502 | xargs kill -9  # Streamlit
```

### Environment Variables Not Set

Verify your environment:
```bash
echo $GEMINI_API_KEY
echo $TA_SERVICE_CONFIG
echo $TA_PLUGIN_MODULE
```

## Best Practices

1. **Run UAT suite regularly** - This validates the complete system with real API
2. **Use E2E suite for CI/CD** - Automated with mocks, no API key needed
3. **Check logs on failure** - Review agent and Streamlit logs for debugging
4. **Update tests when adding features** - Keep tests in sync with functionality

## CI/CD Integration

Add to GitHub Actions:

```yaml
- name: Run E2E Tests
  run: |
    cd src/sk-agents
    uv sync --dev
    uv run robot --outputdir test-results tests/e2e/university_agent_system.robot
```

Note: UAT suite requires API keys and should be run manually or in a secure CI environment with secrets.
