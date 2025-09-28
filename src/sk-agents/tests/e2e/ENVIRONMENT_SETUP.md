# E2E Test Environment Setup Guide

This guide explains how to configure the University Agent E2E tests for your specific environment.

## Required Dependencies

First, install all required dependencies including streamlit:

```bash
cd src/sk-agents
uv sync --dev
```

## Environment-Specific Configuration

### 1. File Paths Configuration

The following paths in the test configuration files need to be updated for your environment:

#### In `tests/e2e/keywords/service_management.robot`:

**Lines 16-21**: Update these absolute paths to match your repository location:

```robot
Set Environment Variable    TA_SERVICE_CONFIG                           /YOUR/PATH/TO/teal-agents/src/sk-agents/tests/e2e/configs/test_university_config.yaml
Set Environment Variable    TA_PLUGIN_MODULE                            /YOUR/PATH/TO/teal-agents/src/orchestrators/assistant-orchestrator/example/university/custom_plugins.py
Set Environment Variable    TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE    /YOUR/PATH/TO/teal-agents/src/sk-agents/tests/e2e/libraries/MockGeminiFactory.py
```

**Line 28**: Update the working directory path:
```robot
...    cwd=/YOUR/PATH/TO/teal-agents/src/sk-agents    alias=university_agent    stdout=agent.log    stderr=agent.log
```

**Line 38**: Update the Streamlit UI working directory:
```robot
...    cwd=/YOUR/PATH/TO/teal-agents/src/orchestrators/assistant-orchestrator/example/university    alias=streamlit_ui    stdout=ui.log    stderr=ui.log
```

### 2. Port Configuration

The tests use these default ports:

- **University Agent Service**: `8001`
- **Streamlit UI**: `8501`

If these ports are not available in your environment, update the following files:

#### In `tests/e2e/university_agent_system.robot` and `tests/e2e/streamlit_ui_integration.robot`:

```robot
*** Variables ***
${AGENT_PORT}           8001  # Change to your available port
${UI_PORT}              8501  # Change to your available port
```

#### In `src/orchestrators/assistant-orchestrator/example/university/streamlit_ui.py`:

Update the agent URL references (lines 61, 195, 207) to match your agent port:
```python
# Change from:
"Please ensure the agent is running on http://localhost:8001"
# To your port:
"Please ensure the agent is running on http://localhost:YOUR_AGENT_PORT"
```

### 3. Repository Structure Assumptions

The tests assume this repository structure:
```
teal-agents/
├── src/
│   ├── sk-agents/
│   │   ├── tests/e2e/          # E2E test files
│   │   └── src/sk_agents/      # Agent source code
│   └── orchestrators/
│       └── assistant-orchestrator/
│           └── example/
│               └── university/  # Streamlit UI and plugins
└── shared/
    └── ska_utils/              # Shared utilities
```

If your repository structure is different, update the relative paths in:
- `pyproject.toml` (line 34): `ska-utils = { path = "../../shared/ska_utils" }`
- Test configuration files that reference cross-directory modules

### 4. Environment Variables

The tests set these environment variables automatically, but you can customize them:

```bash
export GEMINI_API_KEY="test_gemini_api_key"                    # Mock API key for testing
export TA_API_KEY="test_teal_agents_key"                       # Mock TA API key
export TA_SERVICE_CONFIG="/path/to/test_university_config.yaml" # Test config file
export TA_PLUGIN_MODULE="/path/to/custom_plugins.py"           # University plugin
export TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE="/path/to/MockGeminiFactory.py"
export TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS_NAME="MockGeminiChatCompletionFactory"
```

## Quick Setup Script

Create a setup script for your environment:

```bash
#!/bin/bash
# setup_e2e_tests.sh

# Set your repository root path
REPO_ROOT="/path/to/your/teal-agents"

# Update service_management.robot paths
sed -i "s|/home/ubuntu/repos/teal-agents|${REPO_ROOT}|g" \
    "${REPO_ROOT}/src/sk-agents/tests/e2e/keywords/service_management.robot"

# Update streamlit_ui.py port references if needed
# sed -i "s|localhost:8001|localhost:YOUR_PORT|g" \
#     "${REPO_ROOT}/src/orchestrators/assistant-orchestrator/example/university/streamlit_ui.py"

echo "E2E test environment configured for ${REPO_ROOT}"
```

## Running the Tests

After configuration, run the tests:

```bash
cd src/sk-agents
uv run robot tests/e2e/
```

## Troubleshooting

### Port Conflicts
If you get "Address already in use" errors:
1. Change the port numbers in the test configuration
2. Kill existing processes: `pkill -f "uvicorn.*8001" && pkill -f "streamlit.*8501"`

### Path Issues
If you get "FileNotFoundError" or "ModuleNotFoundError":
1. Verify all absolute paths in `service_management.robot` are correct
2. Check that the repository structure matches expectations
3. Ensure `uv sync --dev` was run successfully

### Browser Issues
If Selenium tests fail with browser errors:
1. Ensure Chrome/Chromium is installed
2. Check that the system has sufficient resources for headless browser testing
3. Verify no other browser processes are interfering

## Test Structure Overview

- `university_agent_system.robot` - Main system integration tests
- `streamlit_ui_integration.robot` - UI-specific tests  
- `keywords/service_management.robot` - Service lifecycle management
- `keywords/streamlit_automation.robot` - Browser automation helpers
- `libraries/MockGeminiFactory.py` - Mock Gemini API for testing
- `configs/test_university_config.yaml` - Test-specific agent configuration
