"""
Test structured output with LangChain.

Tests that models can return structured Pydantic outputs.
"""
import asyncio
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
import os


class WeatherInfo(BaseModel):
    """Weather information for a location."""
    location: str = Field(description="City or location name")
    temperature: float = Field(description="Temperature in Fahrenheit")
    conditions: str = Field(description="Weather conditions (sunny, cloudy, rainy, etc.)")
    humidity: int = Field(description="Humidity percentage")


class PersonInfo(BaseModel):
    """Information about a person."""
    name: str = Field(description="Person's full name")
    age: int = Field(description="Person's age in years")
    occupation: str = Field(description="Person's job or occupation")


async def test_structured_output():
    print("Testing structured output with Gemini...")
    
    # Gemini 2.0 Flash supports structured output
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        google_api_key=os.getenv('GOOGLE_API_KEY')
    )
    
    # Test 1: Weather extraction
    print("\n=== Test 1: Extract Weather Info ===")
    structured_model = model.with_structured_output(WeatherInfo)
    
    result = await structured_model.ainvoke(
        "The weather in San Francisco is 65 degrees and sunny with 45% humidity."
    )
    
    print(f"Type: {type(result)}")
    print(f"Result: {result}")
    print(f"Location: {result.location}")
    print(f"Temperature: {result.temperature}°F")
    print(f"Conditions: {result.conditions}")
    print(f"Humidity: {result.humidity}%")
    
    # Test 2: Person extraction
    print("\n=== Test 2: Extract Person Info ===")
    person_model = model.with_structured_output(PersonInfo)
    
    result2 = await person_model.ainvoke(
        "John Smith is a 35-year-old software engineer."
    )
    
    print(f"Type: {type(result2)}")
    print(f"Name: {result2.name}")
    print(f"Age: {result2.age}")
    print(f"Occupation: {result2.occupation}")
    
    print("\n✅ Structured output validation successful!")
    return True


if __name__ == "__main__":
    asyncio.run(test_structured_output())
