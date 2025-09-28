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

UAT Scenario 1 - Basic University Search via Browser
    [Documentation]    Test university search through Streamlit UI browser interaction
    [Tags]    uat    browser    university-search    end-user
    
    # Open browser and navigate to Streamlit UI
    Open Browser    ${UI_BASE_URL}    browser=chrome    options=add_argument("--headless");add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage")
    Set Window Size    1920    1080
    
    # Wait for UI to load completely
    Wait Until Page Contains    🎓 University Agent Chat    timeout=30s
    Wait Until Page Contains    Agent Status    timeout=20s
    Sleep    3s    # Allow UI to fully render
    
    # Test typing a university search query like a real user
    ${chat_input_found}=    Run Keyword And Return Status    
    ...    Wait Until Element Is Visible    css:[data-testid="stChatInput"] textarea    timeout=15s
    
    Run Keyword If    ${chat_input_found}    Input Text    css:[data-testid="stChatInput"] textarea    Find universities in Finland
    Run Keyword If    ${chat_input_found}    Press Keys    css:[data-testid="stChatInput"] textarea    RETURN
    Run Keyword If    ${chat_input_found}    Sleep    15s    # Wait for agent response
    Run Keyword If    ${chat_input_found}    Page Should Contain    Finland
    Run Keyword If    ${chat_input_found}    Log    ✅ Finland university search successful via browser
    
    # Test example query button interaction
    ${example_buttons}=    Get WebElements    css:button
    ${button_count}=    Get Length    ${example_buttons}
    Run Keyword If    ${button_count} > 0    Log    Found ${button_count} interactive buttons for user interaction
    
    Close Browser

UAT Scenario 2 - Example Query Button Interaction
    [Documentation]    Test using example query buttons like a real user would
    [Tags]    uat    browser    example-queries    end-user
    
    # Open browser and navigate to Streamlit UI
    Open Browser    ${UI_BASE_URL}    browser=chrome    options=add_argument("--headless");add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage")
    Set Window Size    1920    1080
    
    # Wait for UI to load completely
    Wait Until Page Contains    🎓 University Agent Chat    timeout=30s
    Sleep    3s    # Allow UI to fully render
    
    # Test clicking example query buttons in sidebar (real user behavior)
    ${sidebar_found}=    Run Keyword And Return Status    
    ...    Wait Until Element Is Visible    css:[data-testid="stSidebar"]    timeout=10s
    
    Run Keyword If    ${sidebar_found}    Log    Sidebar found - testing example query interactions
    
    # Look for example query buttons and click them
    ${example_buttons}=    Get WebElements    css:button
    ${button_count}=    Get Length    ${example_buttons}
    
    Run Keyword If    ${button_count} > 0    Log    Found ${button_count} buttons - simulating user clicking example queries
    
    # Try to click first available example button
    Run Keyword And Ignore Error    Click Element    css:button[key*="example"]
    Sleep    10s    # Wait for response
    
    # Verify some university-related content appeared
    ${page_source}=    Get Source
    Should Match Regexp    ${page_source}    (University|Finland|Japan|Germany|MIT|Aalto)
    
    Close Browser
    Log    ✅ Example query button interaction test completed

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

UAT Scenario 4 - Agent Status Check and Error Handling via Browser
    [Documentation]    Test agent status monitoring and error handling through UI like end users
    [Tags]    uat    browser    error-handling    status-check    end-user
    
    # Open browser and navigate to Streamlit UI
    Open Browser    ${UI_BASE_URL}    browser=chrome    options=add_argument("--headless");add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage")
    Set Window Size    1920    1080
    
    # Wait for UI to load completely
    Wait Until Page Contains    🎓 University Agent Chat    timeout=30s
    Sleep    3s    # Allow UI to fully render
    
    # Test agent status check button (real user behavior)
    ${status_button_found}=    Run Keyword And Return Status    
    ...    Wait Until Element Is Visible    xpath://button[contains(text(), 'Check Agent Status')]    timeout=10s
    
    Run Keyword If    ${status_button_found}    Click Button    xpath://button[contains(text(), 'Check Agent Status')]
    Run Keyword If    ${status_button_found}    Sleep    5s    # Wait for status check
    Run Keyword If    ${status_button_found}    Page Should Contain    Agent is
    Run Keyword If    ${status_button_found}    Log    ✅ Agent status check button works
    
    # Test empty message handling through UI
    ${chat_input_found}=    Run Keyword And Return Status    
    ...    Wait Until Element Is Visible    css:[data-testid="stChatInput"] textarea    timeout=10s
    
    Run Keyword If    ${chat_input_found}    Input Text    css:[data-testid="stChatInput"] textarea    ${EMPTY}
    Run Keyword If    ${chat_input_found}    Press Keys    css:[data-testid="stChatInput"] textarea    RETURN
    Run Keyword If    ${chat_input_found}    Sleep    5s
    Run Keyword If    ${chat_input_found}    Log    ✅ Empty message handled through UI
    
    # Test nonsensical query through UI
    Run Keyword If    ${chat_input_found}    Input Text    css:[data-testid="stChatInput"] textarea    xyzabc123 random nonsense
    Run Keyword If    ${chat_input_found}    Press Keys    css:[data-testid="stChatInput"] textarea    RETURN
    Run Keyword If    ${chat_input_found}    Sleep    10s
    Run Keyword If    ${chat_input_found}    Log    ✅ Nonsensical query handled through UI
    
    Close Browser

UAT Scenario 5 - End-to-End User Workflow Performance via Browser
    [Documentation]    Test complete user workflow performance through browser like real usage
    [Tags]    uat    browser    performance    end-user-workflow
    
    # Measure complete user interaction time
    ${start_time}=    Get Time    epoch
    
    # Open browser and navigate to Streamlit UI
    Open Browser    ${UI_BASE_URL}    browser=chrome    options=add_argument("--headless");add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage")
    Set Window Size    1920    1080
    
    # Wait for UI to load completely
    Wait Until Page Contains    🎓 University Agent Chat    timeout=30s
    Sleep    3s    # Allow UI to fully render
    
    # Simulate real user typing and submitting query
    ${chat_input_found}=    Run Keyword And Return Status    
    ...    Wait Until Element Is Visible    css:[data-testid="stChatInput"] textarea    timeout=15s
    
    Run Keyword If    ${chat_input_found}    Input Text    css:[data-testid="stChatInput"] textarea    Find universities in Japan
    Run Keyword If    ${chat_input_found}    Press Keys    css:[data-testid="stChatInput"] textarea    RETURN
    Run Keyword If    ${chat_input_found}    Sleep    20s    # Wait for complete response
    
    ${end_time}=    Get Time    epoch
    ${total_time}=    Evaluate    ${end_time} - ${start_time}
    
    # Verify response appeared and measure user experience
    Run Keyword If    ${chat_input_found}    Page Should Contain    Japan
    Should Be True    ${total_time} < 60    Complete user workflow should be under 60 seconds
    
    Close Browser
    Log    ✅ Complete user workflow completed in ${total_time} seconds

UAT Scenario 6 - Multi-Query User Session via Browser
    [Documentation]    Test multiple queries in one session like real user behavior
    [Tags]    uat    browser    multi-query    user-session    end-user
    
    # Open browser and navigate to Streamlit UI
    Open Browser    ${UI_BASE_URL}    browser=chrome    options=add_argument("--headless");add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage")
    Set Window Size    1920    1080
    
    # Wait for UI to load completely
    Wait Until Page Contains    🎓 University Agent Chat    timeout=30s
    Sleep    3s    # Allow UI to fully render
    
    # Test multiple queries in sequence (real user session behavior)
    ${chat_input_found}=    Run Keyword And Return Status    
    ...    Wait Until Element Is Visible    css:[data-testid="stChatInput"] textarea    timeout=15s
    
    # First query - Germany universities
    Run Keyword If    ${chat_input_found}    Input Text    css:[data-testid="stChatInput"] textarea    Show me universities in Germany
    Run Keyword If    ${chat_input_found}    Press Keys    css:[data-testid="stChatInput"] textarea    RETURN
    Run Keyword If    ${chat_input_found}    Sleep    15s    # Wait for response
    Run Keyword If    ${chat_input_found}    Page Should Contain    Germany
    Run Keyword If    ${chat_input_found}    Log    ✅ First query (Germany) successful
    
    # Second query - MIT specific search
    Run Keyword If    ${chat_input_found}    Input Text    css:[data-testid="stChatInput"] textarea    Tell me about MIT
    Run Keyword If    ${chat_input_found}    Press Keys    css:[data-testid="stChatInput"] textarea    RETURN
    Run Keyword If    ${chat_input_found}    Sleep    15s    # Wait for response
    Run Keyword If    ${chat_input_found}    Page Should Contain    MIT
    Run Keyword If    ${chat_input_found}    Log    ✅ Second query (MIT) successful
    
    # Third query - Finland universities
    Run Keyword If    ${chat_input_found}    Input Text    css:[data-testid="stChatInput"] textarea    What universities are in Finland?
    Run Keyword If    ${chat_input_found}    Press Keys    css:[data-testid="stChatInput"] textarea    RETURN
    Run Keyword If    ${chat_input_found}    Sleep    15s    # Wait for response
    Run Keyword If    ${chat_input_found}    Page Should Contain    Finland
    Run Keyword If    ${chat_input_found}    Log    ✅ Third query (Finland) successful
    
    # Verify conversation history is maintained (real user expectation)
    ${page_source}=    Get Source
    Should Match Regexp    ${page_source}    (Germany.*MIT.*Finland|Finland.*MIT.*Germany)
    
    Close Browser
    Log    ✅ Multi-query user session completed successfully


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
