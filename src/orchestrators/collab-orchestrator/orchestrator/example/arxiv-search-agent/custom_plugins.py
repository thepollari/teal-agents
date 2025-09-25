from langchain_core.tools import tool
from pydantic import BaseModel


class ArxivSearchPlugin:
    @staticmethod
    @tool
    def arxiv_search(query: str, max_results: int = 2) -> list:  # type: ignore[type-arg]
        """
        Search Arxiv for papers and return the results including abstracts.
        """
        import arxiv

        client = arxiv.Client()
        search = arxiv.Search(
            query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance
        )

        results = []
        for paper in client.results(search):
            results.append(
                {
                    "title": paper.title,
                    "authors": [author.name for author in paper.authors],
                    "published": paper.published.strftime("%Y-%m-%d"),
                    "abstract": paper.summary,
                    "pdf_url": paper.pdf_url,
                }
            )

        # # Write results to a file
        # with open('arxiv_search_results.json', 'w') as f:
        #     json.dump(results, f, indent=2)

        return results
