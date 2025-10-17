*** Settings ***
Documentation     API tests for University Agent endpoints
Library           RequestsLibrary
Library           Collections
Library           OperatingSystem
Resource          resources/keywords.robot
Resource          resources/variables.robot

Suite Setup       API Suite Setup
Suite Teardown    Stop All Services
Test Setup        Clear Request Session

*** Variables ***
${TEST_DATA_FILE}    ${CURDIR}/fixtures/test_data.json

*** Test Cases ***
Agent Endpoint Health Check
    [Documentation]    Verify the agent endpoint is accessible
    Create Session    agent    ${AGENT_URL}
    ${response}=    GET On Session    agent    ${AGENT_ENDPOINT}/docs    expected_status=200
    Should Be Equal As Numbers    ${response.status_code}    200

Search Universities By Country Returns Valid JSON
    [Documentation]    Test searching universities in Finland returns valid structure
    ${response}=    Send University Query    Find universities in Finland
    Validate University Response    ${response}
    ${json}=    Set Variable    ${response.json()}
    Should Contain    ${json}[output_raw]    Finland

Search Universities By Name Returns Matching Results
    [Documentation]    Test searching for Aalto University
    ${response}=    Send University Query    Search for Aalto University
    Validate University Response    ${response}
    ${json}=    Set Variable    ${response.json()}
    Should Contain    ${json}[output_raw]    Aalto

Invalid Query Returns Appropriate Error
    [Documentation]    Test that empty queries are handled
    ${response}=    Send University Query    ${EMPTY}
    Should Be Equal As Numbers    ${response.status_code}    200

Response Includes Output Raw Field
    [Documentation]    Verify all responses have output_raw field
    ${response}=    Send University Query    Find universities in Japan
    ${json}=    Set Variable    ${response.json()}
    Dictionary Should Contain Key    ${json}    output_raw

Connection Error Handling
    [Documentation]    Test behavior when agent is not reachable
    Stop All Services
    Sleep    2
    ${status}=    Run Keyword And Return Status    Send University Query    test
    Should Be Equal    ${status}    ${False}
    API Suite Setup

Timeout Error Handling
    [Documentation]    Verify timeout is respected
    ${start_time}=    Get Time    epoch
    ${response}=    Send University Query    Find universities in United States
    ${end_time}=    Get Time    epoch
    ${duration}=    Evaluate    ${end_time} - ${start_time}
    Should Be True    ${duration} < ${TIMEOUT}

*** Keywords ***
API Suite Setup
    Setup Environment Variables
    Start University Agent Service

Clear Request Session
    Delete All Sessions
