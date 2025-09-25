import aiohttp
from pydantic import BaseModel
from langchain_core.tools import tool
from pydantic import BaseModel


class SearchResultPage(BaseModel):
    page_key: str
    title: str
    excerpt: str
    description: str


class Page(BaseModel):
    page_key: str
    title: str
    content: str


class WikipediaPlugin:
    @staticmethod
    @tool
    async def search(search_query: str, num_results: int = 2) -> list[SearchResultPage]:
        """Search for Wikipedia pages related to a given query and return the results."""
        search_url = f"https://api.wikimedia.org/core/v1/wikipedia/en/search/page?q={search_query}&limit={num_results}"
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url) as response:
                response.raise_for_status()
                data = await response.json()
                pages = [
                    SearchResultPage(
                        page_key=page["key"],
                        title=page["title"],
                        excerpt=page["excerpt"],
                        description=page["description"],
                    )
                    for page in data["pages"]
                ]
                return pages

    @staticmethod
    @tool
    async def get_page_content(page_key: str) -> Page:
        """Retrieve a Wikipedia page's content"""
        page_url = f"https://api.wikimedia.org/core/v1/wikipedia/en/page/{page_key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(page_url) as response:
                response.raise_for_status()
                data = await response.json()
                return Page(page_key=data["key"], title=data["title"], content=data["source"])
