*** Settings ***
Documentation    Keywords for Streamlit UI browser automation
Library          SeleniumLibrary
Library          String
Library          Process

*** Keywords ***
Open University Agent UI
    [Arguments]    ${url}
    # Use more robust browser options for headless Chrome
    ${chrome_options}=    Create List    --headless=new    --no-sandbox    --disable-dev-shm-usage    --disable-gpu    --window-size=1920,1080    --disable-web-security    --disable-features=VizDisplayCompositor
    Open Browser    ${url}    browser=chrome    options=add_argument("${chrome_options[0]}");add_argument("${chrome_options[1]}");add_argument("${chrome_options[2]}");add_argument("${chrome_options[3]}");add_argument("${chrome_options[4]}");add_argument("${chrome_options[5]}");add_argument("${chrome_options[6]}")
    Set Window Size    1920    1080
    
    # Wait for Streamlit to fully load with extended timeout and multiple checks
    Wait Until Keyword Succeeds    60s    2s    Page Should Contain    🎓 University Agent Chat
    Wait Until Keyword Succeeds    30s    2s    Page Should Contain    Agent Status
    Sleep    10s    # Extended wait for all UI elements to render
    
    # Verify page is fully loaded
    Wait Until Page Contains Element    css:[data-testid="stApp"]    timeout=30s
    Log    Streamlit UI opened successfully

Enter Chat Message
    [Arguments]    ${message}
    
    # Wait for main content area to be loaded
    Wait Until Page Contains Element    css:[data-testid="stMain"]    timeout=30s
    Sleep    5s    # Allow chat interface to render
    
    # Try multiple approaches to find the chat input
    ${input_found}=    Set Variable    False
    
    # Approach 1: Try devinid selector
    ${status}=    Run Keyword And Return Status    Wait Until Element Is Visible    css:textarea[devinid="15"]    timeout=15s
    Run Keyword If    ${status}    Input Text    css:textarea[devinid="15"]    ${message}
    Run Keyword If    ${status}    Press Keys    css:textarea[devinid="15"]    RETURN
    Run Keyword If    ${status}    Set Variable    ${input_found}    True
    
    # Approach 2: Try Streamlit chat input selector
    Run Keyword Unless    ${input_found}    Run Keyword And Ignore Error    Wait Until Element Is Visible    css:[data-testid="stChatInput"] textarea    timeout=15s
    Run Keyword Unless    ${input_found}    Run Keyword And Ignore Error    Input Text    css:[data-testid="stChatInput"] textarea    ${message}
    Run Keyword Unless    ${input_found}    Run Keyword And Ignore Error    Press Keys    css:[data-testid="stChatInput"] textarea    RETURN
    Run Keyword Unless    ${input_found}    Set Variable    ${input_found}    True
    
    # Approach 3: Try any textarea in main area
    Run Keyword Unless    ${input_found}    Run Keyword And Ignore Error    Wait Until Element Is Visible    css:[data-testid="stMain"] textarea    timeout=15s
    Run Keyword Unless    ${input_found}    Run Keyword And Ignore Error    Input Text    css:[data-testid="stMain"] textarea    ${message}
    Run Keyword Unless    ${input_found}    Run Keyword And Ignore Error    Press Keys    css:[data-testid="stMain"] textarea    RETURN
    
    Sleep    3s    # Allow message to be processed
    Log    Attempted to enter chat message: ${message}

Wait For University Response
    [Arguments]    ${timeout}=30s
    Wait Until Page Contains Element    css:div[data-testid="stChatMessage"]    timeout=${timeout}
    Sleep    2s

Verify University Data Format
    [Arguments]    ${contains}    ${country}=${EMPTY}
    ${response_elements}=    Get WebElements    css:div[data-testid="stChatMessage"]
    ${latest_response}=    Get Text    ${response_elements}[-1]
    
    Should Contain    ${latest_response}    ${contains}
    Run Keyword If    "${country}" != ""    Should Contain    ${latest_response}    ${country}
    
    Should Match Regexp    ${latest_response}    (University|Country|Website|Domain)
    Log    University response validated: ${latest_response}

Click Example Query
    [Arguments]    ${query_text}
    
    # Wait for sidebar and example queries section with extended timeout
    Wait Until Page Contains    Example Queries    timeout=30s
    Sleep    5s    # Allow buttons to render fully
    
    # Remove quotes from query text for matching
    ${clean_query}=    Replace String    ${query_text}    "    ${EMPTY}
    
    # Map query text to specific devinids based on the UI structure
    ${devinid}=    Set Variable    7    # Default to first example query button
    Run Keyword If    '${clean_query}' == 'Find universities in Finland'    Set Variable    ${devinid}    7
    Run Keyword If    '${clean_query}' == 'Search for Aalto University'    Set Variable    ${devinid}    8
    Run Keyword If    '${clean_query}' == 'What universities are in Japan?'    Set Variable    ${devinid}    9
    Run Keyword If    '${clean_query}' == 'Tell me about MIT'    Set Variable    ${devinid}    10
    Run Keyword If    '${clean_query}' == 'Universities in Germany'    Set Variable    ${devinid}    11
    
    # Click the button using its devinid
    Wait Until Element Is Visible    css:button[devinid="${devinid}"]    timeout=20s
    Click Element    css:button[devinid="${devinid}"]
    
    Log    Clicked example query: ${clean_query} (devinid=${devinid})

Click Example Query With Devinid
    [Arguments]    ${query_text}
    
    Wait Until Element Is Visible    css:button[devinid]    timeout=15s
    ${buttons}=    Get WebElements    css:button[devinid]
    ${clicked}=    Set Variable    False
    
    FOR    ${button}    IN    @{buttons}
        ${button_text}=    Get Text    ${button}
        ${matches}=    Run Keyword And Return Status    Should Contain    ${button_text}    ${query_text}
        Run Keyword If    ${matches}    Click Element    ${button}
        Run Keyword If    ${matches}    Set Variable    ${clicked}    True
        Run Keyword If    ${matches}    Exit For Loop
    END
    
    Should Be True    ${clicked}    Could not find button with text: ${query_text}
    Log    Clicked example query using devinid: ${query_text}

Click Agent Status Check Button
    [Documentation]    Click the Check Agent Status button to trigger status check
    
    # Wait for sidebar to be fully loaded
    Wait Until Page Contains Element    css:[data-testid="stSidebar"]    timeout=30s
    Sleep    3s    # Allow sidebar content to render
    
    # Try multiple approaches to find and click the status button
    ${clicked}=    Set Variable    False
    
    # Approach 1: Try devinid selector
    ${status}=    Run Keyword And Return Status    Wait Until Element Is Visible    css:button[devinid="6"]    timeout=15s
    Run Keyword If    ${status}    Click Element    css:button[devinid="6"]
    Run Keyword If    ${status}    Set Variable    ${clicked}    True
    
    # Approach 2: Try text-based xpath
    Run Keyword Unless    ${clicked}    Run Keyword And Ignore Error    Wait Until Element Is Visible    xpath://button[contains(text(), 'Check Agent Status')]    timeout=15s
    Run Keyword Unless    ${clicked}    Run Keyword And Ignore Error    Click Element    xpath://button[contains(text(), 'Check Agent Status')]
    Run Keyword Unless    ${clicked}    Set Variable    ${clicked}    True
    
    # Approach 3: Try any button in sidebar
    Run Keyword Unless    ${clicked}    Run Keyword And Ignore Error    Wait Until Element Is Visible    css:[data-testid="stSidebar"] button    timeout=15s
    Run Keyword Unless    ${clicked}    Run Keyword And Ignore Error    Click Element    css:[data-testid="stSidebar"] button
    
    Sleep    8s    # Extended wait for status check to complete
    Log    Attempted to click Check Agent Status button

Verify Agent Status Shows
    [Arguments]    ${expected_status}
    Wait Until Page Contains    ${expected_status}    timeout=20s
    Log    Agent status verified: ${expected_status}

Verify Chat History Updated
    [Arguments]    ${message_count}
    ${messages}=    Get WebElements    css:div[data-testid="stChatMessage"]
    ${actual_count}=    Get Length    ${messages}
    Should Be Equal As Numbers    ${actual_count}    ${message_count}

Verify Page Title Contains
    [Arguments]    ${expected_title}
    Wait Until Page Contains    ${expected_title}    timeout=10s
