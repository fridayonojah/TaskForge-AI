from tavily import TavilyClient
from tenacity import retry, stop_after_attempt, wait_exponential
from ports.tools.hotel_search_tool import HotelSearchTool


class TavilyHotelTool(HotelSearchTool):
    def __init__(self, api_key: str) -> None:
        self._client = TavilyClient(api_key=api_key)

    def search(self, query: str) -> str:
        try:
            results = self._fetch_hotel_results(query)
        except Exception:
            return "Hotel data temporarily unavailable. Please try again later."
        lines: list[str] = []
        for i, r in enumerate(results.get("results", []), 1):
            snippet = (r.get("content") or "")[:300]
            lines.append(
                f"{i}. {r.get('title', 'N/A')}\n"
                f"   URL: {r.get('url', 'N/A')}\n"
                f"   {snippet}"
            )
        return "\n\n".join(lines) if lines else "No hotel results found."

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _fetch_hotel_results(self, query: str) -> dict:
        return self._client.search(f"Best hotels for {query}", max_results=5)
