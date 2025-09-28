*** Settings ***
Documentation    Keywords for validating university data format and content
Library          String
Library          Collections

*** Keywords ***
Validate University Response Format
    [Arguments]    ${response_text}
    [Documentation]    Validate that university response contains required fields
    
    Should Match Regexp    ${response_text}    (?i)(university|name)
    Should Match Regexp    ${response_text}    (?i)(country|location)
    Should Match Regexp    ${response_text}    (?i)(website|domain|url)
    
    Log    University response format validated

Validate University Data Structure
    [Arguments]    ${university_data}
    [Documentation]    Validate university data structure from API response
    
    Dictionary Should Contain Key    ${university_data}    name
    Dictionary Should Contain Key    ${university_data}    country
    Dictionary Should Contain Key    ${university_data}    web_pages
    Dictionary Should Contain Key    ${university_data}    domains
    
    Should Not Be Empty    ${university_data}[name]
    Should Not Be Empty    ${university_data}[country]
    
    Log    University data structure validated

Validate Multiple Universities Response
    [Arguments]    ${universities_list}    ${min_count}=1
    [Documentation]    Validate response containing multiple universities
    
    ${count}=    Get Length    ${universities_list}
    Should Be True    ${count} >= ${min_count}
    
    FOR    ${university}    IN    @{universities_list}
        Validate University Data Structure    ${university}
    END
    
    Log    Multiple universities response validated: ${count} universities
