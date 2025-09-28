*** Settings ***
Documentation    Simple test to verify Robot Framework setup
Library          Collections

*** Test Cases ***
Simple Robot Framework Test
    [Documentation]    Basic test to verify Robot Framework is working
    [Tags]    smoke
    
    ${test_dict}=    Create Dictionary    key=value
    Should Contain    ${test_dict}    key
    Log    Robot Framework is working correctly
