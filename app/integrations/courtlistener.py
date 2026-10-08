import httpx
from tenacity import retry, wait_exponential, stop_after_attempt

from app.core.config import get_settings

class CourtListenerClient:
    """Client for querying the CourtListener REST API."""

    def __init__(self) -> None:
        self.url = get_settings().COURTLISTENER_BASE_URL
        self.headers = {
            "Authorization": f"Token {get_settings().COURTLISTENER_API_KEY}",
            "Accept": "application/json"
        }

    @retry(
            wait=wait_exponential(multiplier=1, min=2, max=10),
            stop=stop_after_attempt(3)
    )
    async def search_opinions(self, query: str, court: str | None = None) -> dict:
        """Searches opinions matching the query with automatic retries."""
        params = {
            "q": query,
            "type": "o",
            "order_by": "score desc"
        }
        if court:
            params["court"] = court

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                url=f"{self.url}/search/",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()

            return response.json()
