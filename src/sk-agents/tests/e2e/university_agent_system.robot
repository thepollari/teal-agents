*** Settings ***
Documentation    E2E test suite for University Agent system with service management
...              This suite starts and stops services automatically using MockGeminiFactory
...              for predictable testing without external API dependencies.

Library          RequestsLibrary
Library          Collections
Resource         keywords/service_management.robot

Suite Setup      Setup Test Environment
Suite Teardown   Teardown Test Environment

*** Variables ***
${AGENT_BASE_URL}     http://localhost:8001
${STREAMLIT_URL}      http://localhost:8502
${AGENT_ENDPOINT}     ${AGENT_BASE_URL}/UniversityAgent/0.1

*** Keywords ***
Setup Test Environment
    [Documentation]    Start services with MockGeminiFactory before running tests
    Log    Starting University Agent with MockGeminiFactory
    Start University Agent Service    use_mock=${True}
    Wait For Agent To Be Ready
    
    Log    Starting Streamlit UI
    Start Streamlit UI
    Check Streamlit Health

Teardown Test Environment
    [Documentation]    Stop all services after tests complete
    Log    Stopping services
    Stop Streamlit UI
    Stop University Agent Service

*** Test Cases ***
Agent Service Starts Successfully
    [Documentation]    Verify the agent service started with MockGeminiFactory
    [Tags]    smoke
    ${response}=    GET    ${AGENT_ENDPOINT}/docs    expected_status=200
    Should Be Equal As Strings    ${response.status_code}    200

Streamlit UI Starts Successfully
    [Documentation]    Verify the Streamlit UI started successfully
    [Tags]    smoke
    ${response}=    GET    ${STREAMLIT_URL}/_stcore/health    expected_status=200
    Should Be Equal As Strings    ${response.status_code}    200

API Endpoint Returns Valid Response
    [Documentation]    Test basic API call with mock backend
    [Tags]    api
    
    ${payload}=    Create Dictionary
    ${chat_history}=    Create List
    ${user_msg}=    Create Dictionary    role=user    content=Hello
    Append To List    ${chat_history}    ${user_msg}
    Set To Dictionary    ${payload}    chat_history=${chat_history}
    
    ${response}=    POST    ${AGENT_ENDPOINT}    json=${payload}    expected_status=200
    Should Be Equal As Strings    ${response.status_code}    200
    
    ${json}=    Set Variable    ${response.json()}
    Dictionary Should Contain Key    ${json}    output_raw
    Dictionary Should Contain Key    ${json}    token_usage

Response Has Correct Format
    [Documentation]    Verify response structure matches expectations
    [Tags]    api    validation
    
    ${payload}=    Create Dictionary
    ${chat_history}=    Create List
    ${user_msg}=    Create Dictionary    role=user    content=Test query
    Append To List    ${chat_history}    ${user_msg}
    Set To Dictionary    ${payload}    chat_history=${chat_history}
    
    ${response}=    POST    ${AGENT_ENDPOINT}    json=${payload}    expected_status=200
    ${json}=    Set Variable    ${response.json()}
    
    Dictionary Should Contain Key    ${json}    output_raw
    Dictionary Should Not Contain Key    ${json}    choices
    
    ${output}=    Get From Dictionary    ${json}    output_raw
    ${output_type}=    Evaluate    type($output).__name__
    Should Be Equal    ${output_type}    str
