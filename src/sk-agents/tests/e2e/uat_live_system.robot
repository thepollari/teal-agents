*** Settings ***
Documentation    UAT test suite for testing against a running University Agent system
...              This suite assumes the University Agent and Streamlit UI are already running
...              and performs real-world user acceptance testing scenarios.
Library          SeleniumLibrary
Library          RequestsLibrary
Library          Collections
Library          String
Resource         keywords/streamlit_automation.robot
Resource         keywords/university_data_validation.robot
Test Timeout     5 minutes

*** Variables ***
${AGENT_PORT}           8001
${UI_PORT}              8501
${AGENT_BASE_URL}       http://localhost:${AGENT_PORT}
${UI_BASE_URL}          http://localhost:${UI_PORT}
${AGENT_ENDPOINT}       ${AGENT_BASE_URL}/UniversityAgent/0.1

*** Test Cases ***
UAT Health Check - Verify Services Are Running
    [Documentation]    Verify that both University Agent and Streamlit UI are accessible
    [Tags]    uat    health-check    smoke
    
    # Verify University Agent is running
    ${agent_response}=    GET    ${AGENT_ENDPOINT}/openapi.json
    Should Be Equal As Strings    ${agent_response.status_code}    200
    Should Contain    ${agent_response.text}    UniversityAgent
    Log    ✅ University Agent is running on ${AGENT_BASE_URL}
    
    # Verify Streamlit UI is accessible
    ${ui_response}=    GET    ${UI_BASE_URL}
    Should Be Equal As Strings    ${ui_response.status_code}    200
    Should Contain    ${ui_response.text}    Streamlit
    Log    ✅ Streamlit UI is running on ${UI_BASE_URL}

UAT Scenario 1 - Basic University Search via API
    [Documentation]    Test direct API calls to the University Agent for basic university searches
    [Tags]    uat    api    university-search
    
    # Test Finland university search
    @{chat_history}=    Create List
    ${request_body}=    Create Dictionary    
    ...    chat_history=${chat_history}
    
    ${response}=    POST    ${AGENT_ENDPOINT}    json=${request_body}
    Should Be Equal As Strings    ${response.status_code}    200
    
    ${response_data}=    Set Variable    ${response.json()}
    Should Contain    ${response_data}[output_raw]    Finland
    Should Match Regexp    ${response_data}[output_raw]    (University|Aalto|Helsinki)
    Log    ✅ Finland university search successful via API

UAT Scenario 2 - Specific University Search via API
    [Documentation]    Test searching for specific universities via direct API calls
    [Tags]    uat    api    specific-search
    
    # Test Harvard University search
    @{chat_history}=    Create List
    ${request_body}=    Create Dictionary    
    ...    chat_history=${chat_history}
    
    ${response}=    POST    ${AGENT_ENDPOINT}    json=${request_body}
    Should Be Equal As Strings    ${response.status_code}    200
    
    ${response_data}=    Set Variable    ${response.json()}
    Should Contain    ${response_data}[output_raw]    Harvard
    Should Match Regexp    ${response_data}[output_raw]    (University|United States|harvard.edu)
    Log    ✅ Harvard University search successful via API

UAT Scenario 3 - Complete User Journey via Streamlit UI
    [Documentation]    Test the complete user experience through the Streamlit interface
    [Tags]    uat    ui    user-journey
    
    # Open the Streamlit UI
    Open Browser    ${UI_BASE_URL}    browser=chrome    options=add_argument("--headless");add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage")
    Set Window Size    1920    1080
    
    # Wait for UI to load
    Wait Until Page Contains    🎓 University Agent Chat    timeout=30s
    Wait Until Page Contains    Agent Status    timeout=20s
    Sleep    5s    # Allow UI to fully render
    
    # Verify agent status shows as running
    Page Should Contain    Agent Status
    
    # Test chat interaction - Finland universities
    ${chat_input_found}=    Run Keyword And Return Status    
    ...    Wait Until Element Is Visible    css:[data-testid="stChatInput"] textarea    timeout=15s
    
    Run Keyword If    ${chat_input_found}    Input Text    css:[data-testid="stChatInput"] textarea    Find universities in Finland
    Run Keyword If    ${chat_input_found}    Press Keys    css:[data-testid="stChatInput"] textarea    RETURN
    Run Keyword If    ${chat_input_found}    Sleep    10s
    Run Keyword If    ${chat_input_found}    Page Should Contain    Finland
    
    # Test example query buttons if available
    ${example_buttons}=    Get WebElements    css:button
    ${button_count}=    Get Length    ${example_buttons}
    Run Keyword If    ${button_count} > 0    Log    Found ${button_count} interactive buttons in UI
    
    Close Browser
    Log    ✅ Complete user journey test completed

UAT Scenario 4 - Error Handling and Edge Cases
    [Documentation]    Test how the system handles various edge cases and errors
    [Tags]    uat    error-handling    edge-cases
    
    # Test empty query
    @{chat_history}=    Create List
    ${request_body}=    Create Dictionary    
    ...    chat_history=${chat_history}
    
    ${response}=    POST    ${AGENT_ENDPOINT}    json=${request_body}
    Should Be Equal As Strings    ${response.status_code}    200
    Log    ✅ Empty query handled gracefully
    
    # Test nonsensical query
    @{chat_history}=    Create List
    ${request_body}=    Create Dictionary    
    ...    chat_history=${chat_history}
    
    ${response}=    POST    ${AGENT_ENDPOINT}    json=${request_body}
    Should Be Equal As Strings    ${response.status_code}    200
    ${response_data}=    Set Variable    ${response.json()}
    Should Not Be Empty    ${response_data}[output_raw]
    Log    ✅ Nonsensical query handled gracefully

UAT Scenario 5 - Performance and Response Time
    [Documentation]    Test system performance and response times under normal load
    [Tags]    uat    performance    response-time
    
    # Measure response time for university search
    ${start_time}=    Get Time    epoch
    
    @{chat_history}=    Create List
    ${request_body}=    Create Dictionary    
    ...    chat_history=${chat_history}
    
    ${response}=    POST    ${AGENT_ENDPOINT}    json=${request_body}
    ${end_time}=    Get Time    epoch
    ${response_time}=    Evaluate    ${end_time} - ${start_time}
    
    Should Be Equal As Strings    ${response.status_code}    200
    Should Be True    ${response_time} < 30    Response time should be under 30 seconds
    
    ${response_data}=    Set Variable    ${response.json()}
    Should Contain    ${response_data}[output_raw]    Japan
    
    Log    ✅ Japan university search completed in ${response_time} seconds

UAT Scenario 6 - Data Quality and Format Validation
    [Documentation]    Validate the quality and format of university data returned
    [Tags]    uat    data-quality    validation
    
    # Test comprehensive university search
    @{chat_history}=    Create List
    ${request_body}=    Create Dictionary    
    ...    chat_history=${chat_history}
    
    ${response}=    POST    ${AGENT_ENDPOINT}    json=${request_body}
    Should Be Equal As Strings    ${response.status_code}    200
    
    ${response_data}=    Set Variable    ${response.json()}
    ${content}=    Set Variable    ${response_data}[output_raw]
    
    # Validate response contains expected university information
    Should Contain    ${content}    Germany
    Should Match Regexp    ${content}    (University|Website|Domain|Country)
    Should Match Regexp    ${content}    (http|www|\.edu|\.de)
    
    # Validate response is well-formatted
    Should Not Contain    ${content}    null
    Should Not Contain    ${content}    undefined
    Should Not Contain    ${content}    error
    
    Log    ✅ Germany university data quality validation passed

*** Keywords ***
Verify Service Health
    [Arguments]    ${service_url}    ${service_name}
    ${response}=    GET    ${service_url}
    Should Be Equal As Strings    ${response.status_code}    200
    Log    ${service_name} is healthy at ${service_url}

Measure API Response Time
    [Arguments]    ${endpoint}    ${request_data}
    ${start_time}=    Get Time    epoch
    ${response}=    POST    ${endpoint}    json=${request_data}
    ${end_time}=    Get Time    epoch
    ${response_time}=    Evaluate    ${end_time} - ${start_time}
    RETURN    ${response}    ${response_time}
