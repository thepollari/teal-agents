*** Settings ***
Documentation    Keywords for University Agent service lifecycle management
Library          Process
Library          RequestsLibrary
Library          OperatingSystem
Library          String

*** Keywords ***
Setup Test Environment
    [Documentation]    Initialize complete test environment
    Set Environment Variables
    Start University Agent Service
    Start Streamlit UI Service
    Wait For Services Ready

Start University Agent Service
    [Documentation]    Start University Agent FastAPI service
    
    # Kill any existing processes on the port first
    Run Process    pkill    -f    uvicorn.*${AGENT_PORT}    shell=True
    Sleep    2s    # Allow process to fully terminate
    
    Set Environment Variable    GEMINI_API_KEY                              test_gemini_api_key
    Set Environment Variable    TA_API_KEY                                  test_teal_agents_key
    Set Environment Variable    TA_SERVICE_CONFIG                           /home/ubuntu/repos/teal-agents/src/sk-agents/tests/e2e/configs/test_university_config.yaml
    Set Environment Variable    TA_PLUGIN_MODULE                            /home/ubuntu/repos/teal-agents/src/orchestrators/assistant-orchestrator/example/university/custom_plugins.py
    Set Environment Variable    TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE    /home/ubuntu/repos/teal-agents/src/sk-agents/tests/e2e/libraries/MockGeminiFactory.py
    Set Environment Variable    TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS_NAME    MockGeminiChatCompletionFactory
    
    ${agent_process}=    Start Process    uv    run    uvicorn    sk_agents.app:app    --host    0.0.0.0    --port    ${AGENT_PORT}
    ...    cwd=/home/ubuntu/repos/teal-agents/src/sk-agents    alias=university_agent    stdout=agent.log    stderr=agent.log
    Set Suite Variable    ${AGENT_PROCESS}    ${agent_process}
    
    Wait For University Agent Health    ${AGENT_ENDPOINT}/openapi.json    timeout=60s

Start Streamlit UI Service
    [Documentation]    Start Streamlit UI service
    
    # Kill any existing processes on the port first
    Run Process    pkill    -f    streamlit.*${UI_PORT}    shell=True
    Sleep    2s    # Allow process to fully terminate
    
    ${ui_process}=    Start Process    uv    run    streamlit    run    streamlit_ui.py    --server.port    ${UI_PORT}    --server.headless    true
    ...    cwd=/home/ubuntu/repos/teal-agents/src/orchestrators/assistant-orchestrator/example/university    alias=streamlit_ui    stdout=ui.log    stderr=ui.log
    Set Suite Variable    ${UI_PROCESS}    ${ui_process}
    
    Wait For Streamlit UI Ready    ${UI_BASE_URL}    timeout=30s

Wait For University Agent Health
    [Arguments]    ${health_url}    ${timeout}=60s
    Wait Until Keyword Succeeds    ${timeout}    2s    Check University Agent Health    ${health_url}
    Sleep    2s    # Additional wait to ensure agent is fully ready

Check University Agent Health
    [Arguments]    ${health_url}
    ${response}=    GET    ${health_url}
    Should Be Equal As Strings    ${response.status_code}    200
    Log    University Agent health check successful: ${health_url}

Wait For Streamlit UI Ready
    [Arguments]    ${ui_url}    ${timeout}=30s
    Wait Until Keyword Succeeds    ${timeout}    2s    Check Streamlit UI Health    ${ui_url}
    Sleep    3s    # Additional wait to ensure UI is fully loaded

Check Streamlit UI Health
    [Arguments]    ${ui_url}
    ${response}=    GET    ${ui_url}
    Should Be Equal As Strings    ${response.status_code}    200

Cleanup Test Environment
    [Documentation]    Clean up all test services and processes
    
    # Close browsers first to prevent window not found errors
    Run Keyword And Ignore Error    Close All Browsers
    Sleep    2s
    
    # Terminate processes with better error handling
    ${agent_process}=    Get Variable Value    ${AGENT_PROCESS}    ${NONE}
    Run Keyword If    "${agent_process}" != "None"    Run Keyword And Ignore Error    Terminate Process    ${agent_process}
    
    ${ui_process}=    Get Variable Value    ${UI_PROCESS}    ${NONE}
    Run Keyword If    "${ui_process}" != "None"    Run Keyword And Ignore Error    Terminate Process    ${ui_process}
    
    # More aggressive cleanup with better error handling
    Run Keyword And Ignore Error    Run Process    pkill    -9    -f    uvicorn.*8001    shell=True
    Run Keyword And Ignore Error    Run Process    pkill    -9    -f    streamlit.*8501    shell=True
    Run Keyword And Ignore Error    Run Process    fuser    -k    8001/tcp    shell=True
    Run Keyword And Ignore Error    Run Process    fuser    -k    8501/tcp    shell=True
    Sleep    5s
    
    # Clean up Chrome user data directories and processes
    Run Keyword And Ignore Error    Run Process    rm    -rf    /tmp/chrome-test-*    shell=True
    Run Keyword And Ignore Error    Run Process    pkill    -f    chrome    shell=True
    Run Keyword And Ignore Error    Run Process    pkill    -f    chromedriver    shell=True

Set Environment Variables
    [Documentation]    Set required environment variables for testing
    Set Environment Variable    GEMINI_API_KEY    test_gemini_api_key
    Set Environment Variable    TA_API_KEY        test_teal_agents_key

Wait For Services Ready
    [Documentation]    Wait for all services to be ready
    Log    All services started successfully

Verify University Agent Health
    [Arguments]    ${health_url}
    ${response}=    GET    ${health_url}
    Should Be Equal As Strings    ${response.status_code}    200
    Log    University Agent health verified: ${health_url}
