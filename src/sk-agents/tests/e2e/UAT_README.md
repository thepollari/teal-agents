# UAT Test Suite for Running University Agent System

This test suite is designed for **User Acceptance Testing (UAT)** scenarios where the University Agent and Streamlit UI are already running in a production-like environment.

## Purpose

Unlike the main E2E test suite that starts and stops services automatically, this UAT suite assumes:
- ✅ University Agent service is already running on port 8001
- ✅ Streamlit UI is already running on port 8501  
- ✅ Real API keys are configured (GEMINI_API_KEY, TA_API_KEY)
- ✅ Production or staging environment is set up

## Prerequisites

### 1. Start the University Agent Service
```bash
cd src/orchestrators/assistant-orchestrator/example/university
export GEMINI_API_KEY="your_real_gemini_api_key"
export TA_API_KEY="your_real_ta_api_key"
uv run uvicorn sk_agents.app:app --host 0.0.0.0 --port 8001
```

### 2. Start the Streamlit UI
```bash
cd src/orchestrators/assistant-orchestrator/example/university
uv run streamlit run streamlit_ui.py --server.port 8501 --server.headless true
```

### 3. Verify Services Are Running
```bash
# Check University Agent
curl http://localhost:8001/UniversityAgent/0.1/openapi.json

# Check Streamlit UI  
curl http://localhost:8501
```

## Running UAT Tests

### Run All UAT Tests
```bash
cd src/sk-agents
uv run robot tests/e2e/uat_live_system.robot
```

### Run Specific UAT Scenarios
```bash
cd src/sk-agents

# Health checks only
uv run robot --include health-check tests/e2e/uat_live_system.robot

# API testing only
uv run robot --include api tests/e2e/uat_live_system.robot

# UI testing only  
uv run robot --include ui tests/e2e/uat_live_system.robot

# Performance testing
uv run robot --include performance tests/e2e/uat_live_system.robot
```

## UAT Test Scenarios

### 1. **Health Check** (`UAT Health Check - Verify Services Are Running`)
- Verifies University Agent API is accessible
- Verifies Streamlit UI is accessible
- Confirms services are responding correctly

### 2. **Basic API Testing** (`UAT Scenario 1 - Basic University Search via API`)
- Tests direct API calls to University Agent
- Validates university search functionality
- Uses real external API calls (no mocks)

### 3. **Specific Search Testing** (`UAT Scenario 2 - Specific University Search via API`)
- Tests searching for specific universities
- Validates response quality and accuracy
- Confirms real data integration

### 4. **Complete User Journey** (`UAT Scenario 3 - Complete User Journey via Streamlit UI`)
- Tests full user experience through Streamlit interface
- Validates chat functionality and UI responsiveness
- Tests example query buttons and interactions

### 5. **Error Handling** (`UAT Scenario 4 - Error Handling and Edge Cases`)
- Tests system behavior with edge cases
- Validates graceful error handling
- Tests empty and nonsensical queries

### 6. **Performance Testing** (`UAT Scenario 5 - Performance and Response Time`)
- Measures API response times
- Validates performance under normal load
- Ensures responses complete within acceptable timeframes

### 7. **Data Quality Validation** (`UAT Scenario 6 - Data Quality and Format Validation`)
- Validates university data quality and format
- Ensures responses contain expected information
- Checks for data consistency and completeness

## Key Differences from E2E Tests

| Aspect | E2E Tests | UAT Tests |
|--------|-----------|-----------|
| **Service Management** | Automatically starts/stops services | Assumes services are already running |
| **API Integration** | Uses MockGeminiFactory | Uses real Gemini API with actual keys |
| **External APIs** | Mocked universities.hipolabs.com | Real external API calls |
| **Environment** | Test environment with mocks | Production-like environment |
| **Purpose** | Development testing | User acceptance testing |
| **Data** | Predictable mock responses | Real, dynamic data |

## Configuration

### Environment Variables (Required for UAT)
```bash
export GEMINI_API_KEY="your_actual_gemini_api_key"
export TA_API_KEY="your_actual_ta_api_key"
export TA_SERVICE_CONFIG="/path/to/production/config.yaml"
```

### Port Configuration
Update these variables in `uat_live_system.robot` if your services run on different ports:
```robot
${AGENT_PORT}           8001    # University Agent service port
${UI_PORT}              8501    # Streamlit UI service port
```

## Troubleshooting

### Services Not Running
```bash
# Check if services are running
ss -tlnp | grep -E ':(8001|8501)'

# Start University Agent if not running
cd src/orchestrators/assistant-orchestrator/example/university
uv run uvicorn sk_agents.app:app --host 0.0.0.0 --port 8001

# Start Streamlit UI if not running  
uv run streamlit run streamlit_ui.py --server.port 8501
```

### API Key Issues
- Ensure `GEMINI_API_KEY` is set with a valid Google Gemini API key
- Ensure `TA_API_KEY` is set with a valid Teal Agents API key
- Check API key permissions and quotas

### Network Issues
- Verify firewall settings allow connections to ports 8001 and 8501
- Check if services are bound to correct interfaces (0.0.0.0 vs localhost)
- Ensure no proxy or VPN issues interfering with local connections

## Expected Results

**All 6 UAT scenarios should pass** when:
- ✅ Services are running correctly
- ✅ API keys are valid and have sufficient quota
- ✅ Network connectivity is working
- ✅ External APIs (universities.hipolabs.com, Gemini) are accessible

This UAT suite provides comprehensive validation that the University Agent system works correctly in a real-world deployment scenario.
