import json
from typing import List

import requests
from pydantic import BaseModel, ConfigDict
from langchain_core.tools import tool
from pydantic import BaseModel


class University(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    name: str
    web_pages: List[str]
    domains: List[str]
    country: str
    state_province: str | None = None
    alpha_two_code: str


class UniversitySearchResult(BaseModel):
    message: str
    universities: List[University]
    error: str | None = None


class UniversityPlugin:
    @staticmethod
    def _get_universities_url(name: str = None, country: str = None) -> str:
        base_url = "http://universities.hipolabs.com/search"
        params = []
        if name:
            params.append(f"name={name}")
        if country:
            params.append(f"country={country}")
        
        if params:
            return f"{base_url}?{'&'.join(params)}"
        return base_url

    @staticmethod
    @tool
    def search_universities(query: str) -> UniversitySearchResult:
        """Search for universities by name and/or country"""
        try:
            url = UniversityPlugin._get_universities_url(name=query)
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            universities_data = response.json()
            if not universities_data:
                return UniversitySearchResult(
                    message=f"No universities found for query: {query}",
                    universities=[]
                )
            
            universities = []
            for uni_data in universities_data[:10]:
                university = University(
                    name=uni_data.get("name", ""),
                    web_pages=uni_data.get("web_pages", []),
                    domains=uni_data.get("domains", []),
                    country=uni_data.get("country", ""),
                    state_province=uni_data.get("state-province"),
                    alpha_two_code=uni_data.get("alpha_two_code", "")
                )
                universities.append(university)
            
            return UniversitySearchResult(
                message=f"Found {len(universities)} universities for query: {query}",
                universities=universities
            )
            
        except requests.RequestException as e:
            return UniversitySearchResult(
                message="Failed to fetch universities",
                universities=[],
                error=f"Failed to fetch universities: {str(e)}"
            )
        except Exception as e:
            return UniversitySearchResult(
                message="Unexpected error occurred",
                universities=[],
                error=f"Unexpected error: {str(e)}"
            )

    @staticmethod
    @tool
    def get_universities_by_country(country: str) -> UniversitySearchResult:
        """Find universities in a specific country"""
        try:
            url = UniversityPlugin._get_universities_url(country=country)
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            universities_data = response.json()
            if not universities_data:
                return UniversitySearchResult(
                    message=f"No universities found in country: {country}",
                    universities=[]
                )
            
            universities = []
            for uni_data in universities_data[:20]:
                university = University(
                    name=uni_data.get("name", ""),
                    web_pages=uni_data.get("web_pages", []),
                    domains=uni_data.get("domains", []),
                    country=uni_data.get("country", ""),
                    state_province=uni_data.get("state-province"),
                    alpha_two_code=uni_data.get("alpha_two_code", "")
                )
                universities.append(university)
            
            return UniversitySearchResult(
                message=f"Found {len(universities)} universities in {country}",
                universities=universities
            )
            
        except requests.RequestException as e:
            return UniversitySearchResult(
                message="Failed to fetch universities",
                universities=[],
                error=f"Failed to fetch universities: {str(e)}"
            )
        except Exception as e:
            return UniversitySearchResult(
                message="Unexpected error occurred", 
                universities=[],
                error=f"Unexpected error: {str(e)}"
            )
