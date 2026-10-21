import httpx
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception
import logging

from app.core.config import get_settings

logger = logging.getLogger("law_bot.courtlistener")

def is_retryable_courtlistener_error(exception: BaseException) -> bool:
    """Retries on HTTP 429 (Rate Limit), 5xx server errors, or transient network timeouts."""
    if isinstance(exception, httpx.HTTPStatusError):
        return exception.response.status_code in (429, 500, 502, 503, 504)
    if isinstance(exception, (httpx.TimeoutException, httpx.NetworkError)):
        return True
    return False

class CourtListenerClient:
    """Client for querying the CourtListener REST API."""

    def __init__(self) -> None:
        self.url = get_settings().COURTLISTENER_BASE_URL
        self.headers = {
            "Authorization": f"Token {get_settings().COURTLISTENER_API_KEY}",
            "Accept": "application/json"
        }

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=15),
        stop=stop_after_attempt(4),
        retry=retry_if_exception(is_retryable_courtlistener_error)
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

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                url=f"{self.url}/search/",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=15),
        stop=stop_after_attempt(4),
        retry=retry_if_exception(is_retryable_courtlistener_error)
    )
    async def get_opinion(self, opinion_id: int | str) -> dict:
        """Fetches the full opinion record (plain_text and html_with_citations) by opinion ID."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                url=f"{self.url}/opinions/{opinion_id}/",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
