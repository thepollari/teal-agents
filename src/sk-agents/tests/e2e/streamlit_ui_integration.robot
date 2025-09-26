*** Settings ***
Documentation    Streamlit UI specific integration tests
Library          SeleniumLibrary
Library          RequestsLibrary
Resource         keywords/service_management.robot
Resource         keywords/streamlit_automation.robot
Resource         keywords/external_mocking.robot
Suite Setup      Setup Test Environment
Suite Teardown   Cleanup Test Environment
Test Timeout     3 minutes

*** Variables ***
${AGENT_PORT}           8001
${UI_PORT}              8501
${AGENT_BASE_URL}       http://localhost:${AGENT_PORT}
${UI_BASE_URL}          http://localhost:${UI_PORT}
${AGENT_ENDPOINT}       ${AGENT_BASE_URL}/UniversityAgent/0.1

*** Test Cases ***
Streamlit UI Startup and Connection Test
    [Documentation]    Test Streamlit UI startup and connection to University Agent
    [Tags]    ui    startup    connection
    
    Open University Agent UI        ${UI_BASE_URL}
    Verify Page Title Contains      🎓 University Agent Chat
    Verify Agent Status Shows       ✅ Agent is running
    
    Page Should Contain Element     css:[data-testid="stSidebar"]
    Page Should Contain             Configuration
    Page Should Contain             Status
    Page Should Contain             Example Queries

Streamlit Example Query Buttons Test
    [Documentation]    Test all example query buttons from the UI
    [Tags]    ui    example-queries
    
    Setup University API Mocks    response_file=aalto_university_response.json
    Setup Gemini API Mocks
    
    Open University Agent UI        ${UI_BASE_URL}
    
    Click Example Query            "Find universities in Finland"
    Wait For University Response   timeout=30s
    Verify University Data Format  contains=Finland
    
    Click Example Query            "Search for Aalto University"
    Wait For University Response   timeout=30s
    Verify University Data Format  contains=Aalto University

Streamlit Error Handling Test
    [Documentation]    Test UI error handling when agent is unavailable
    [Tags]    ui    error-handling
    
    # Make sure agent is not running with ultra-aggressive cleanup
    Run Keyword And Ignore Error    Run Process    pkill    -9    -f    uvicorn.*${AGENT_PORT}    shell=True
    Run Keyword And Ignore Error    Run Process    fuser    -k    ${AGENT_PORT}/tcp    shell=True
    Run Keyword And Ignore Error    Run Process    kill -9 $(lsof -t -i:${AGENT_PORT})    shell=True
    Sleep    10s    # Extended wait to allow processes to fully terminate
    
    # Verify agent is not running
    ${agent_check}=    Run Process    curl -s -o /dev/null -w "%{http_code}" http://localhost:${AGENT_PORT}    shell=True
    ${agent_running}=    Evaluate    "${agent_check.stdout}" == "200"
    Run Keyword If    ${agent_running}    Log    WARNING: Agent is still running despite cleanup attempts    WARN
    
    # Open UI and check status
    Open University Agent UI        ${UI_BASE_URL}
    Sleep    10s    # Allow UI to fully load
    
    # Try multiple times to click the status button with extended retries
    Wait Until Keyword Succeeds    5x    10s    Click Agent Status Check Button
    
    # Verify error status with more flexible matching
    Wait Until Page Contains    Agent is not    timeout=30s
    
    # Try to send a message
    Run Keyword And Ignore Error    Enter Chat Message    Find universities in Finland
    Sleep    10s
    Page Should Contain    Agent is not    timeout=20s
