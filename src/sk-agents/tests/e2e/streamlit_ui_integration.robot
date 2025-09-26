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
    
    # Get the agent process from the suite variable and stop it
    ${agent_process}=    Get Variable Value    ${AGENT_PROCESS}    ${NONE}
    Run Keyword If    "${agent_process}" != "None"    Run Keyword And Ignore Error    Terminate Process    ${agent_process}
    
    # Make sure agent is not running
    Run Keyword And Ignore Error    Run Process    pkill    -9    -f    uvicorn.*${AGENT_PORT}    shell=True
    Run Keyword And Ignore Error    Run Process    fuser    -k    ${AGENT_PORT}/tcp    shell=True
    Sleep    5s    # Allow processes to fully terminate
    
    Open University Agent UI        ${UI_BASE_URL}
    
    # Try multiple times to click the status button
    Wait Until Keyword Succeeds    3x    5s    Click Agent Status Check Button
    Verify Agent Status Shows      ❌ Agent is not responding
    
    # Try to send a message
    Run Keyword And Ignore Error    Enter Chat Message    Find universities in Finland
    Sleep    5s
    Page Should Contain    Agent is not responding
