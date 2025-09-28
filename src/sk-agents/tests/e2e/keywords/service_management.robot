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
    
    # Simple but effective port cleanup
    Run Keyword And Ignore Error    Run Process    pkill    -9    -f    uvicorn.*${AGENT_PORT}    shell=True
    Run Keyword And Ignore Error    Run Process    fuser    -k    ${AGENT_PORT}/tcp    shell=True
    Sleep    3s    # Allow processes to terminate
    
    # Check if port is still in use and wait if needed
    ${port_check}=    Run Process    lsof -i:${AGENT_PORT}    shell=True
    Run Keyword If    ${port_check.rc} == 0    Sleep    5s
    Run Keyword If    ${port_check.rc} == 0    Log    Port ${AGENT_PORT} cleanup completed
    
    Set Environment Variable    GEMINI_API_KEY                              test_gemini_api_key
    Set Environment Variable    TA_API_KEY                                  test_teal_agents_key
    ${CURDIR_PARENT}=    Set Variable    ${CURDIR}/../../../..
    Set Environment Variable    TA_SERVICE_CONFIG                           ${CURDIR}/configs/test_university_config.yaml
    Set Environment Variable    TA_PLUGIN_MODULE                            ${CURDIR_PARENT}/orchestrators/assistant-orchestrator/example/university/custom_plugins.py
    Set Environment Variable    TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE    ${CURDIR}/libraries/MockGeminiFactory.py
    Set Environment Variable    TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS_NAME    MockGeminiChatCompletionFactory
    
    ${agent_process}=    Start Process    uv    run    uvicorn    sk_agents.app:app    --host    0.0.0.0    --port    ${AGENT_PORT}
    ...    cwd=${CURDIR}/../../..    alias=university_agent    stdout=${CURDIR}/../../../agent.log    stderr=${CURDIR}/../../../agent.log
    Set Suite Variable    ${AGENT_PROCESS}    ${agent_process}
    
    Wait For University Agent Health    ${AGENT_ENDPOINT}/openapi.json    timeout=60s

Start Streamlit UI Service
    [Documentation]    Start Streamlit UI service
    
    # Simple but effective port cleanup
    Run Keyword And Ignore Error    Run Process    pkill    -9    -f    streamlit.*${UI_PORT}    shell=True
    Run Keyword And Ignore Error    Run Process    fuser    -k    ${UI_PORT}/tcp    shell=True
    Sleep    3s    # Allow processes to terminate
    
    # Check if port is still in use and wait if needed
    ${port_check}=    Run Process    lsof -i:${UI_PORT}    shell=True
    Run Keyword If    ${port_check.rc} == 0    Sleep    5s
    Run Keyword If    ${port_check.rc} == 0    Log    Port ${UI_PORT} cleanup completed
    
    ${ui_process}=    Start Process    uv    run    streamlit    run    streamlit_ui.py    --server.port    ${UI_PORT}    --server.headless    true
    ...    cwd=${CURDIR_PARENT}/orchestrators/assistant-orchestrator/example/university    alias=streamlit_ui    stdout=${CURDIR_PARENT}/orchestrators/assistant-orchestrator/example/university/ui.log    stderr=${CURDIR_PARENT}/orchestrators/assistant-orchestrator/example/university/ui.log
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
    
    # Close browsers first with extended cleanup and explicit session termination
    Run Keyword And Ignore Error    Execute JavaScript    window.close();
    Sleep    2s
    Run Keyword And Ignore Error    Close All Browsers
    Sleep    5s
    
    # Kill all Chrome and WebDriver processes with multiple attempts
    Run Keyword And Ignore Error    Run Process    pkill    -9    -f    chrome    shell=True
    Run Keyword And Ignore Error    Run Process    pkill    -9    -f    chromedriver    shell=True
    Run Keyword And Ignore Error    Run Process    pkill    -9    -f    chromium    shell=True
    Run Keyword And Ignore Error    Run Process    pkill    -9    -f    selenium    shell=True
    Sleep    5s    # Extended wait for processes to terminate
    
    # Second attempt to ensure all processes are terminated
    Run Keyword And Ignore Error    Run Process    pkill    -9    -f    chrome    shell=True
    Run Keyword And Ignore Error    Run Process    pkill    -9    -f    chromedriver    shell=True
    
    # Clean up Chrome user data directories and temp files
    Run Keyword And Ignore Error    Run Process    rm    -rf    /tmp/chrome-test-*    shell=True
    Run Keyword And Ignore Error    Run Process    rm    -rf    /tmp/.org.chromium.*    shell=True
    Run Keyword And Ignore Error    Run Process    rm    -rf    /tmp/scoped_dir*    shell=True
    Run Keyword And Ignore Error    Run Process    rm    -rf    /tmp/.com.google.Chrome.*    shell=True
    
    # Terminate processes with better error handling
    ${agent_process}=    Get Variable Value    ${AGENT_PROCESS}    ${NONE}
    Run Keyword If    "${agent_process}" != "None"    Run Keyword And Ignore Error    Terminate Process    ${agent_process}
    
    ${ui_process}=    Get Variable Value    ${UI_PROCESS}    ${NONE}
    Run Keyword If    "${ui_process}" != "None"    Run Keyword And Ignore Error    Terminate Process    ${ui_process}
    
    # More aggressive service cleanup
    Run Keyword And Ignore Error    Run Process    pkill    -9    -f    uvicorn.*8001    shell=True
    Run Keyword And Ignore Error    Run Process    pkill    -9    -f    streamlit.*8501    shell=True
    Run Keyword And Ignore Error    Run Process    fuser    -k    8001/tcp    shell=True
    Run Keyword And Ignore Error    Run Process    fuser    -k    8501/tcp    shell=True
    Sleep    5s
    
    # Clean up temporary files and directories
    Run Keyword And Ignore Error    Run Process    rm    -rf    /tmp/chrome-test-*    shell=True
    Run Keyword And Ignore Error    Run Process    rm    -rf    /tmp/.org.chromium.*    shell=True
    Run Keyword And Ignore Error    Run Process    rm    -rf    /tmp/scoped_dir*    shell=True
    
    Log    Test environment cleanup completed

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
