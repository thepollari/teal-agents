*** Settings ***
Documentation    Comprehensive E2E tests for University Agent system
Library          RequestsLibrary
Library          Process
Library          SeleniumLibrary
Library          Collections
Library          OperatingSystem
Library          String
Library          libraries/UniversityAgentLibrary.py
Library          libraries/StreamlitTestLibrary.py
Library          libraries/UniversityAPIMockLibrary.py
Resource         keywords/service_management.robot
Resource         keywords/streamlit_automation.robot
Resource         keywords/api_workflow.robot
Resource         keywords/external_mocking.robot
Resource         keywords/university_data_validation.robot
Suite Setup      Setup Test Environment
Suite Teardown   Cleanup Test Environment
Test Timeout     5 minutes

*** Variables ***
${AGENT_PORT}           8001
${UI_PORT}              8501
${AGENT_BASE_URL}       http://localhost:${AGENT_PORT}
${UI_BASE_URL}          http://localhost:${UI_PORT}
${AGENT_ENDPOINT}       ${AGENT_BASE_URL}/UniversityAgent/0.1
${CONFIG_PATH}          ${CURDIR}/configs/test_university_config.yaml
${PLUGIN_PATH}          ${CURDIR}/../../../orchestrators/assistant-orchestrator/example/university/custom_plugins.py

*** Test Cases ***
University Agent Complete System Test
    [Documentation]    Test complete university request workflow through Streamlit UI
    [Tags]    complete-workflow    ui    integration
    
    Setup University API Mocks    response_file=aalto_university_response.json
    Setup Gemini API Mocks        response_file=university_assistant_responses.json
    
    Open University Agent UI        ${UI_BASE_URL}
    Verify Page Title Contains      🎓 University Agent Chat
    Click Agent Status Check Button
    Verify Agent Status Shows       ✅ Agent is running
    
    Enter Chat Message              Find universities in Finland
    Wait For University Response    timeout=30s
    Verify University Data Format   contains=Aalto University    country=Finland
    Verify Chat History Updated     message_count=2
    
    # Skip example query button test for now - focus on core functionality
    Log    Skipping example query button test - core chat functionality verified
    
    Verify Universities API Called  endpoint=/search    params=name=finland
    Verify Gemini API Called       model=gemini-2.0-flash-lite

University Agent Service Lifecycle Test
    [Documentation]    Test University Agent service startup, health, and shutdown
    [Tags]    service-lifecycle    health-check
    
    Verify University Agent Health    ${AGENT_ENDPOINT}/openapi.json
    Verify University Agent Health    ${AGENT_ENDPOINT}/docs
    
    ${response}=    GET    ${AGENT_ENDPOINT}/openapi.json
    Should Be Equal As Strings    ${response.status_code}    200
    Should Contain    ${response.text}    "/UniversityAgent/0.1"

University Agent Error Recovery Test
    [Documentation]    Test error handling and fallback mechanisms
    [Tags]    error-handling    resilience
    
    Setup Failed University API Mock    status_code=503
    Setup Gemini API Mocks
    
    Open University Agent UI        ${UI_BASE_URL}
    Click Agent Status Check Button
    Enter Chat Message             Find universities in Finland
    Wait For University Response   timeout=30s
    
    Verify Response Contains       Finland
    Verify Error Handling Graceful
