*** Settings ***
Documentation     UI tests for Streamlit University Agent interface
Library           Browser
Resource          resources/keywords.robot
Resource          resources/variables.robot

Suite Setup       UI Suite Setup
Suite Teardown    UI Suite Teardown
Test Setup        Go To Streamlit

*** Test Cases ***
Streamlit UI Loads Successfully
    [Documentation]    Verify the Streamlit UI loads at correct URL
    ${title}=    Get Title
    Should Contain    ${title}    University Agent

Page Title Displays Correctly
    [Documentation]    Check the page title shows "🎓 University Agent Chat"
    ${heading}=    Get Text    h1
    Should Contain    ${heading}    🎓 University Agent Chat

Check Agent Status Button Works
    [Documentation]    Test the "Check Agent Status" button functionality
    Click    text=Check Agent Status
    Sleep    2
    Get Text    body    contains    Agent is running

All Example Query Buttons Present
    [Documentation]    Verify all 5 example query buttons are present
    ${buttons}=    Get Elements    button >> text=/Find universities|Search for|What universities|Tell me about|Universities in/
    ${count}=    Get Length    ${buttons}
    Should Be Equal As Numbers    ${count}    5

Example Query Button Clickable
    [Documentation]    Test clicking an example query button
    Click    button >> text=Find universities in Finland
    Sleep    1
    ${messages}=    Get Elements    .stChatMessage
    Should Not Be Empty    ${messages}

Chat Input Accepts User Queries
    [Documentation]    Test typing in the chat input
    ${input}=    Get Element    textarea[data-testid="stChatInput"]
    Fill Text    ${input}    Tell me about MIT
    Keyboard Key    press    Enter
    Sleep    3
    ${messages}=    Get Elements    .stChatMessage
    Should Not Be Empty    ${messages}

Agent Responses Display In Chat History
    [Documentation]    Verify agent responses appear in chat
    ${input}=    Get Element    textarea[data-testid="stChatInput"]
    Fill Text    ${input}    Find universities in Japan
    Keyboard Key    press    Enter
    Sleep    5
    ${response}=    Get Text    .stChatMessage >> nth=-1
    Should Not Be Empty    ${response}

Clear Conversation Button Resets Chat
    [Documentation]    Test the clear conversation functionality
    ${input}=    Get Element    textarea[data-testid="stChatInput"]
    Fill Text    ${input}    Test message
    Keyboard Key    press    Enter
    Sleep    2
    Click    text=🗑️ Clear Conversation
    Sleep    1
    ${messages}=    Get Elements    .stChatMessage
    Should Be Empty    ${messages}

Agent URL Configuration Can Be Modified
    [Documentation]    Test changing agent URL in sidebar
    ${url_input}=    Get Element    input[value="http://localhost:8001"]
    Fill Text    ${url_input}    http://localhost:9999
    ${value}=    Get Property    ${url_input}    value
    Should Be Equal    ${value}    http://localhost:9999

*** Keywords ***
UI Suite Setup
    Setup Environment Variables
    Start University Agent Service
    Start Streamlit UI Service
    New Browser    chromium    headless=True
    New Context    viewport={'width': 1920, 'height': 1080}
    New Page    ${STREAMLIT_URL}

UI Suite Teardown
    Close Browser
    Stop All Services

Go To Streamlit
    Go To    ${STREAMLIT_URL}
    Sleep    2
