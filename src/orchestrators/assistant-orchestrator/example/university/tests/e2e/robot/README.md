# Robot Framework E2E Tests for University Agent

This directory contains end-to-end tests for the University Agent using Robot Framework.

## Test Structure

- **`api_tests.robot`** - Tests for the University Agent REST API endpoints
- **`ui_tests.robot`** - Tests for the Streamlit UI interface
- **`resources/keywords.robot`** - Reusable custom keywords for service management and testing
- **`resources/variables.robot`** - Common variables and configuration
- **`fixtures/test_data.json`** - Test data fixtures

## Prerequisites

1. Install dependencies:
```bash
cd ~/repos/teal-agents/src/orchestrators/assistant-orchestrator/orchestrator
uv sync --all-packages --group dev
```

2. Initialize Robot Framework Browser Library:
```bash
uv run rfbrowser init
```

3. Set required environment variable:
```bash
export GEMINI_API_KEY="your_google_gemini_api_key"
```

## Running Tests

### Run All Tests
```bash
cd ~/repos/teal-agents/src/orchestrators/assistant-orchestrator/example/university
uv run robot tests/e2e/robot/
```

### Run Specific Test Suite
```bash
uv run robot tests/e2e/robot/api_tests.robot
uv run robot tests/e2e/robot/ui_tests.robot
```

### Run with Tags
```bash
uv run robot --include api tests/e2e/robot/
```

## Test Reports

After running tests, Robot Framework generates three files in the current directory:

- **`log.html`** - Detailed execution log with timestamps and keywords
- **`report.html`** - High-level test results summary
- **`output.xml`** - Machine-readable XML output for CI/CD integration

## Test Coverage

### API Tests (7 test cases)
1. Agent Endpoint Health Check - Verifies `/UniversityAgent/0.1/docs` is accessible
2. Search Universities By Country - Tests country-based search (Finland)
3. Search Universities By Name - Tests name-based search (Aalto University)
4. Invalid Query Handling - Tests empty query handling
5. Response Structure - Verifies `output_raw` field exists
6. Connection Error Handling - Tests behavior when agent is unreachable
7. Timeout Error Handling - Verifies timeout is respected (<30s)

### UI Tests (8 test cases)
1. Streamlit UI Loads Successfully - Verifies page loads at http://localhost:8502
2. Page Title Displays Correctly - Checks for "🎓 University Agent Chat"
3. Check Agent Status Button Works - Tests status check functionality
4. All Example Query Buttons Present - Verifies 5 example buttons exist
5. Example Query Button Clickable - Tests button click functionality
6. Chat Input Accepts User Queries - Tests text input and submission
7. Agent Responses Display In Chat History - Verifies responses appear
8. Clear Conversation Button Resets Chat - Tests chat clearing
9. Agent URL Configuration Can Be Modified - Tests sidebar configuration

## Service Management

The tests automatically manage service lifecycle:

- **Agent Service**: Started on port 8001 with 10-second startup wait
- **Streamlit UI**: Started on port 8502 with 5-second startup wait
- **Suite Teardown**: Both services are gracefully terminated after tests complete

## Environment Variables

Required environment variables (automatically configured by test keywords):

- `GEMINI_API_KEY` - Your Google Gemini API key (must be set manually)
- `TA_SERVICE_CONFIG` - Path to config.yaml
- `TA_PLUGIN_MODULE` - Path to custom_plugins.py
- `TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE` - Gemini factory module path
- `TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS_NAME` - Factory class name

## Troubleshooting

### Port Already in Use
If you see errors about ports 8001 or 8502 being in use:
```bash
lsof -ti:8001 | xargs kill -9
lsof -ti:8502 | xargs kill -9
```

### Browser Library Not Initialized
If Browser Library tests fail:
```bash
cd ~/repos/teal-agents/src/orchestrators/assistant-orchestrator/orchestrator
uv run rfbrowser init
```

### Missing GEMINI_API_KEY
Ensure the environment variable is set:
```bash
export GEMINI_API_KEY="your_api_key_here"
```

## Integration with CI/CD

These tests are integrated into the GitHub Actions workflow in `.github/workflows/check.yaml`. The workflow:

1. Installs dependencies via `uv sync`
2. Initializes Browser Library with `rfbrowser init`
3. Runs tests with environment variables from secrets
4. Uploads test reports as artifacts

## Development

When adding new tests:

1. Add test cases to the appropriate `.robot` file
2. Create reusable keywords in `resources/keywords.robot` if needed
3. Update variables in `resources/variables.robot` if needed
4. Add test data to `fixtures/test_data.json` if needed
5. Run tests locally before committing
6. Ensure lint passes: `cd ~/repos/teal-agents/src/sk-agents && uv run ruff check .`
