*** Settings ***
Documentation    Keywords for Streamlit UI browser automation
Library          SeleniumLibrary
Library          String

*** Keywords ***
Open University Agent UI
    [Arguments]    ${url}
    Open Browser    ${url}    browser=chrome    options=add_argument("--headless");add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage")
    Set Window Size    1920    1080
    Wait Until Page Contains    🎓 University Agent Chat    timeout=15s
    Wait Until Page Contains    Agent Status                timeout=10s

Enter Chat Message
    [Arguments]    ${message}
    Wait Until Element Is Visible    css:textarea[data-testid="stChatInputTextArea"]    timeout=10s
    Clear Element Text    css:textarea[data-testid="stChatInputTextArea"]
    Input Text    css:textarea[data-testid="stChatInputTextArea"]    ${message}
    Press Keys    css:textarea[data-testid="stChatInputTextArea"]    RETURN
    Log    Entered chat message: ${message}

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
    # Wait for sidebar to load and find buttons with devinid
    Wait Until Element Is Visible    css:button[devinid]    timeout=15s
    Sleep    2s    # Allow UI to fully render
    
    # Find all buttons with devinid and click the one with matching text
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
    Log    Clicked example query: ${query_text}

Click Agent Status Check Button
    [Documentation]    Click the Check Agent Status button to trigger status check
    Wait Until Element Is Visible    xpath://button[contains(., 'Check Agent Status')]    timeout=10s
    Click Button    xpath://button[contains(., 'Check Agent Status')]
    Sleep    2s    # Allow status check to complete
    Log    Clicked Check Agent Status button

Verify Agent Status Shows
    [Arguments]    ${expected_status}
    Wait Until Page Contains    ${expected_status}    timeout=10s
    Log    Agent status verified: ${expected_status}

Verify Chat History Updated
    [Arguments]    ${message_count}
    ${messages}=    Get WebElements    css:div[data-testid="stChatMessage"]
    ${actual_count}=    Get Length    ${messages}
    Should Be Equal As Numbers    ${actual_count}    ${message_count}

Verify Page Title Contains
    [Arguments]    ${expected_title}
    Wait Until Page Contains    ${expected_title}    timeout=10s
