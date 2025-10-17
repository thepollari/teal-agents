*** Settings ***
Library           Process
Library           OperatingSystem
Library           RequestsLibrary
Library           Browser

*** Variables ***
${AGENT_PROCESS}       None
${STREAMLIT_PROCESS}   None

*** Keywords ***
Setup Environment Variables
    Set Environment Variable    GEMINI_API_KEY                                    %{GEMINI_API_KEY}
    Set Environment Variable    TA_SERVICE_CONFIG                                 ${CURDIR}/../../config.yaml
    Set Environment Variable    TA_PLUGIN_MODULE                                  ${CURDIR}/../../custom_plugins.py
    Set Environment Variable    TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE          src.sk_agents.chat_completion.custom.gemini_chat_completion_factory
    Set Environment Variable    TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS_NAME      GeminiChatCompletionFactory

Start University Agent Service
    [Documentation]    Start the University Agent FastAPI service on port 8001
    ${result}=    Start Process    uv    run    uvicorn    sk_agents.app:app    --host    0.0.0.0    --port    8001
    ...    cwd=${EXECDIR}/../../../sk-agents
    ...    alias=agent_service
    Set Suite Variable    ${AGENT_PROCESS}    ${result}
    Sleep    ${AGENT_STARTUP_WAIT}
    Verify Agent Is Running

Start Streamlit UI Service
    [Documentation]    Start the Streamlit UI on port 8502
    ${result}=    Start Process    uv    run    streamlit    run    streamlit_ui.py    --server.port    8502
    ...    cwd=${CURDIR}/../..
    ...    alias=streamlit_service
    Set Suite Variable    ${STREAMLIT_PROCESS}    ${result}
    Sleep    ${STREAMLIT_STARTUP_WAIT}

Stop All Services
    [Documentation]    Gracefully shutdown both services
    Run Keyword If    '${AGENT_PROCESS}' != 'None'        Terminate Process    agent_service
    Run Keyword If    '${STREAMLIT_PROCESS}' != 'None'    Terminate Process    streamlit_service

Verify Agent Is Running
    [Documentation]    Check that the agent is responding to health checks
    Create Session    agent    ${AGENT_URL}
    ${response}=    GET On Session    agent    ${AGENT_ENDPOINT}/docs    expected_status=200
    Should Be Equal As Numbers    ${response.status_code}    200

Send University Query
    [Arguments]    ${query}
    [Documentation]    Send a query to the University Agent
    Create Session    agent    ${AGENT_URL}
    ${chat_history}=    Create List
    ${message}=    Create Dictionary    role=user    content=${query}
    Append To List    ${chat_history}    ${message}
    ${payload}=    Create Dictionary    chat_history=${chat_history}
    ${response}=    POST On Session    agent    ${AGENT_ENDPOINT}    json=${payload}    timeout=${TIMEOUT}    expected_status=200
    RETURN    ${response}

Validate University Response
    [Arguments]    ${response}
    [Documentation]    Validate the structure of a university response
    Should Be Equal As Numbers    ${response.status_code}    200
    ${json}=    Set Variable    ${response.json()}
    Dictionary Should Contain Key    ${json}    output_raw
