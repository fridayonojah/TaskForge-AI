from tavily import TavilyClient
from tenacity import retry, stop_after_attempt, wait_exponential


class TavilyWebSearchTool:
    def __init__(self, api_key: str) -> None:
        self._client = TavilyClient(api_key=api_key)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def search(self, query: str, max_results: int = 5) -> list[dict]:
        results = self._client.search(query, max_results=max_results)
        return results.get("results", [])

    def format_results(self, results: list[dict], max_snippet: int = 400) -> str:
        lines: list[str] = []
        for i, r in enumerate(results, 1):
            snippet = (r.get("content") or "")[:max_snippet]
            lines.append(f"{i}. {r.get('title', 'N/A')}\n   {r.get('url', '')}\n   {snippet}")
        return "\n\n".join(lines) if lines else "No results found."
