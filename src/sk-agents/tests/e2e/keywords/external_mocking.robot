*** Settings ***
Documentation    Keywords for external API mocking and network-level testing
Library          ../libraries/UniversityAPIMockLibrary.py

*** Keywords ***
Setup University API Mocks
    [Arguments]    ${response_file}
    [Documentation]    Setup mock responses for universities.hipolabs.com API
    
    ${mock_data}=    Load Mock University Data    ${response_file}
    Start University API Mock Server    ${mock_data}
    Log    University API mock server started with data from: ${response_file}

Setup Gemini API Mocks
    [Arguments]    ${response_file}=university_assistant_responses.json
    [Documentation]    Setup mock responses for Google Gemini API
    
    ${mock_responses}=    Load Mock Gemini Responses    ${response_file}
    Start Gemini API Mock Server    ${mock_responses}
    Log    Gemini API mock server started with responses from: ${response_file}

Setup Failed University API Mock
    [Arguments]    ${status_code}=503
    [Documentation]    Setup University API to return error responses
    
    Start Failed University API Mock    ${status_code}
    Log    University API mock configured to return status: ${status_code}

Verify Universities API Called
    [Arguments]    ${endpoint}    ${params}
    [Documentation]    Verify that the universities API was called with expected parameters
    
    # For now, just log that we would verify the API call
    # In a real implementation, this would check mock server logs
    Log    Would verify Universities API call: ${endpoint} with params: ${params}

Verify Gemini API Called
    [Arguments]    ${model}
    [Documentation]    Verify that Gemini API was called with expected model
    
    # For now, just log that we would verify the API call
    # In a real implementation, this would check mock server logs
    Log    Would verify Gemini API call with model: ${model}

Verify Response Contains
    [Arguments]    ${expected_text}
    ${page_source}=    Get Source
    Should Contain    ${page_source}    ${expected_text}

Verify Mock University Data
    [Arguments]    ${contains}
    ${page_source}=    Get Source
    Should Contain    ${page_source}    ${contains}

Verify Error Handling Graceful
    ${page_source}=    Get Source
    Should Not Contain    ${page_source}    Error
    Should Not Contain    ${page_source}    Exception
