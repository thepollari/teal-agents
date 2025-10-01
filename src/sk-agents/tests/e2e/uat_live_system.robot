*** Settings ***
Documentation    UAT test suite for University Agent system against live services
...              This suite assumes the University Agent and Streamlit UI are already running
...              with real API keys configured. Run this to validate the complete system.
...
...              Prerequisites:
...              - University Agent running on http://localhost:8001
...              - Streamlit UI running on http://localhost:8502
...              - GEMINI_API_KEY environment variable set
...
...              To start services manually:
...              Terminal 1: cd src/sk-agents && uv run uvicorn sk_agents.app:app --host 0.0.0.0 --port 8001
...              Terminal 2: cd src/orchestrators/assistant-orchestrator/example/university && uv run streamlit run streamlit_ui.py --server.port 8502

Library          RequestsLibrary
Library          Collections
Library          JSONLibrary

*** Variables ***
${AGENT_BASE_URL}     http://localhost:8001
${STREAMLIT_URL}      http://localhost:8502
${AGENT_ENDPOINT}     ${AGENT_BASE_URL}/UniversityAgent/0.1

*** Test Cases ***
Agent API Should Be Accessible
    [Documentation]    Verify the University Agent API is running and accessible
    [Tags]    smoke    api
    ${response}=    GET    ${AGENT_ENDPOINT}/docs    expected_status=200
    Should Be Equal As Strings    ${response.status_code}    200
    Log    Agent API is accessible at ${AGENT_ENDPOINT}

Streamlit UI Should Be Accessible
    [Documentation]    Verify the Streamlit UI is running and accessible
    [Tags]    smoke    ui
    ${response}=    GET    ${STREAMLIT_URL}/_stcore/health    expected_status=200
    Should Be Equal As Strings    ${response.status_code}    200
    Log    Streamlit UI is accessible at ${STREAMLIT_URL}

Search Universities By Name
    [Documentation]    Test searching for universities by name through the API
    [Tags]    api    search
    
    ${payload}=    Create Dictionary
    ${chat_history}=    Create List
    ${user_msg}=    Create Dictionary    role=user    content=Search for Aalto University
    Append To List    ${chat_history}    ${user_msg}
    Set To Dictionary    ${payload}    chat_history=${chat_history}
    
    ${response}=    POST    ${AGENT_ENDPOINT}    json=${payload}    expected_status=200
    Should Be Equal As Strings    ${response.status_code}    200
    
    ${json}=    Set Variable    ${response.json()}
    Log    Response: ${json}
    
    Dictionary Should Contain Key    ${json}    output_raw
    ${output}=    Get From Dictionary    ${json}    output_raw
    Should Contain    ${output}    Aalto    msg=Response should mention Aalto
    
    Dictionary Should Contain Key    ${json}    token_usage
    ${tokens}=    Get From Dictionary    ${json}    token_usage
    Should Be True    ${tokens['total_tokens']} > 0    msg=Should have token usage

Search Universities By Country
    [Documentation]    Test searching for universities by country through the API
    [Tags]    api    search
    
    ${payload}=    Create Dictionary
    ${chat_history}=    Create List
    ${user_msg}=    Create Dictionary    role=user    content=Find universities in Finland
    Append To List    ${chat_history}    ${user_msg}
    Set To Dictionary    ${payload}    chat_history=${chat_history}
    
    ${response}=    POST    ${AGENT_ENDPOINT}    json=${payload}    expected_status=200
    Should Be Equal As Strings    ${response.status_code}    200
    
    ${json}=    Set Variable    ${response.json()}
    Log    Response: ${json}
    
    Dictionary Should Contain Key    ${json}    output_raw
    ${output}=    Get From Dictionary    ${json}    output_raw
    Should Contain    ${output}    Finland    msg=Response should mention Finland
    Should Contain    ${output}    universities    msg=Response should mention universities

Multi-Turn Conversation
    [Documentation]    Test multi-turn conversation with chat history
    [Tags]    api    conversation
    
    ${history}=    Create List
    ${msg1}=    Create Dictionary    role=user    content=Tell me about universities in Japan
    Append To List    ${history}    ${msg1}
    
    ${payload1}=    Create Dictionary    chat_history=${history}
    ${response1}=    POST    ${AGENT_ENDPOINT}    json=${payload1}    expected_status=200
    ${json1}=    Set Variable    ${response1.json()}
    ${output1}=    Get From Dictionary    ${json1}    output_raw
    
    ${msg2}=    Create Dictionary    role=assistant    content=${output1}
    Append To List    ${history}    ${msg2}
    
    ${msg3}=    Create Dictionary    role=user    content=How many did you find?
    Append To List    ${history}    ${msg3}
    
    ${payload2}=    Create Dictionary    chat_history=${history}
    ${response2}=    POST    ${AGENT_ENDPOINT}    json=${payload2}    expected_status=200
    ${json2}=    Set Variable    ${response2.json()}
    ${output2}=    Get From Dictionary    ${json2}    output_raw
    
    Log    First response: ${output1}
    Log    Second response: ${output2}
    
    Should Not Be Empty    ${output2}    msg=Second response should not be empty

Response Format Validation
    [Documentation]    Verify the API response has the correct structure
    [Tags]    api    validation
    
    ${payload}=    Create Dictionary
    ${chat_history}=    Create List
    ${user_msg}=    Create Dictionary    role=user    content=Search for MIT
    Append To List    ${chat_history}    ${user_msg}
    Set To Dictionary    ${payload}    chat_history=${chat_history}
    
    ${response}=    POST    ${AGENT_ENDPOINT}    json=${payload}    expected_status=200
    ${json}=    Set Variable    ${response.json()}
    
    Dictionary Should Contain Key    ${json}    output_raw
    Dictionary Should Contain Key    ${json}    token_usage
    Dictionary Should Contain Key    ${json}    session_id
    Dictionary Should Contain Key    ${json}    source
    Dictionary Should Contain Key    ${json}    request_id
    
    ${tokens}=    Get From Dictionary    ${json}    token_usage
    Dictionary Should Contain Key    ${tokens}    completion_tokens
    Dictionary Should Contain Key    ${tokens}    prompt_tokens
    Dictionary Should Contain Key    ${tokens}    total_tokens
    
    ${output}=    Get From Dictionary    ${json}    output_raw
    ${output_type}=    Evaluate    type($output).__name__
    Should Be Equal    ${output_type}    str    msg=output_raw should be a string, not a dict
    Log    Response format validated successfully

Error Handling For Empty Query
    [Documentation]    Test error handling when no query is provided
    [Tags]    api    error
    
    ${payload}=    Create Dictionary
    ${chat_history}=    Create List
    Set To Dictionary    ${payload}    chat_history=${chat_history}
    
    ${response}=    POST    ${AGENT_ENDPOINT}    json=${payload}    expected_status=any
    Log    Status code: ${response.status_code}
    Log    Response: ${response.json()}
