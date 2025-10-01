*** Settings ***
Documentation    Simple service management keywords for University Agent E2E tests
Library          Process
Library          OperatingSystem
Library          RequestsLibrary

*** Variables ***
${AGENT_PORT}         8001
${STREAMLIT_PORT}     8502
${AGENT_PROCESS}      None
${STREAMLIT_PROCESS}  None

*** Keywords ***
Start University Agent Service
    [Documentation]    Start the University Agent API service
    [Arguments]    ${use_mock}=${False}
    
    ${agent_dir}=    Set Variable    ${CURDIR}/../../../
    
    IF    ${use_mock}
        Set Environment Variable    TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE    tests/e2e/mock_gemini_factory.py
        Set Environment Variable    TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS_NAME    MockGeminiFactory
    END
    
    Set Environment Variable    TA_SERVICE_CONFIG    ${CURDIR}/../../../../orchestrators/assistant-orchestrator/example/university/config.yaml
    Set Environment Variable    TA_PLUGIN_MODULE    ${CURDIR}/../../../../orchestrators/assistant-orchestrator/example/university/custom_plugins.py
    
    ${process}=    Start Process    uv    run    uvicorn    sk_agents.app:app    --host    0.0.0.0    --port    ${AGENT_PORT}
    ...    cwd=${agent_dir}    stdout=${TEMPDIR}/agent_stdout.log    stderr=${TEMPDIR}/agent_stderr.log
    
    Set Suite Variable    ${AGENT_PROCESS}    ${process}
    Sleep    5s
    Log    Agent started with PID ${process.pid}

Stop University Agent Service
    [Documentation]    Stop the University Agent API service
    IF    '${AGENT_PROCESS}' != 'None'
        Terminate Process    ${AGENT_PROCESS}
        ${result}=    Wait For Process    ${AGENT_PROCESS}    timeout=10s    on_timeout=kill
        Log    Agent stopped with return code ${result.rc}
    END

Start Streamlit UI
    [Documentation]    Start the Streamlit UI for University Agent
    ${streamlit_dir}=    Set Variable    ${CURDIR}/../../../../orchestrators/assistant-orchestrator/example/university
    
    ${process}=    Start Process    uv    run    streamlit    run    streamlit_ui.py    --server.port    ${STREAMLIT_PORT}    --server.headless    true
    ...    cwd=${streamlit_dir}    stdout=${TEMPDIR}/streamlit_stdout.log    stderr=${TEMPDIR}/streamlit_stderr.log
    
    Set Suite Variable    ${STREAMLIT_PROCESS}    ${process}
    Sleep    8s
    Log    Streamlit started with PID ${process.pid}

Stop Streamlit UI
    [Documentation]    Stop the Streamlit UI
    IF    '${STREAMLIT_PROCESS}' != 'None'
        Terminate Process    ${STREAMLIT_PROCESS}
        ${result}=    Wait For Process    ${STREAMLIT_PROCESS}    timeout=10s    on_timeout=kill
        Log    Streamlit stopped with return code ${result.rc}
    END

Wait For Agent To Be Ready
    [Documentation]    Wait for agent to be ready to accept requests
    [Arguments]    ${timeout}=30s    ${retry_interval}=2s
    Wait Until Keyword Succeeds    ${timeout}    ${retry_interval}    Check Agent Health

Check Agent Health
    [Documentation]    Check if agent API is responding
    ${response}=    GET    http://localhost:${AGENT_PORT}/UniversityAgent/0.1/docs    expected_status=200
    Should Be Equal As Strings    ${response.status_code}    200

Check Streamlit Health
    [Documentation]    Check if Streamlit UI is responding
    ${response}=    GET    http://localhost:${STREAMLIT_PORT}/_stcore/health    expected_status=200
    Should Be Equal As Strings    ${response.status_code}    200
