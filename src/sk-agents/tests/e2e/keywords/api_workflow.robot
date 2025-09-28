*** Settings ***
Documentation    Keywords for University Agent API workflow testing
Library          RequestsLibrary
Library          Collections
Library          String

*** Keywords ***
Test University Agent HTTP Endpoint
    [Arguments]    ${query}    ${expected_contains}
    
    ${payload}=    Create Dictionary    chat_history=${EMPTY LIST}
    ${chat_message}=    Create Dictionary    role=user    content=${query}
    Append To List    ${payload}[chat_history]    ${chat_message}
    
    ${response}=    POST    ${AGENT_ENDPOINT}    json=${payload}    timeout=30
    Should Be Equal As Strings    ${response.status_code}    200
    
    ${response_json}=    Set Variable    ${response.json()}
    Should Contain    ${response_json}[output_raw]    ${expected_contains}
    
    Log    API response validated for query: ${query}

Test University Agent SSE Streaming
    [Arguments]    ${query}
    
    ${payload}=    Create Dictionary    chat_history=${EMPTY LIST}
    ${chat_message}=    Create Dictionary    role=user    content=${query}
    Append To List    ${payload}[chat_history]    ${chat_message}
    
    ${headers}=    Create Dictionary    Accept=text/event-stream
    ${response}=    POST    ${AGENT_ENDPOINT}/sse    json=${payload}    headers=${headers}    timeout=30
    Should Be Equal As Strings    ${response.status_code}    200
    Should Contain    ${response.headers}[content-type]    text/event-stream
    
    Log    SSE streaming validated for query: ${query}

Verify University Agent Endpoints
    [Arguments]    ${base_url}
    
    ${docs_response}=    GET    ${base_url}/docs
    Should Be Equal As Strings    ${docs_response.status_code}    200
    
    ${openapi_response}=    GET    ${base_url}/openapi.json
    Should Be Equal As Strings    ${openapi_response.status_code}    200
    Should Contain    ${openapi_response.text}    "UniversityAgent"
    
    Log    University Agent endpoints verified: ${base_url}
