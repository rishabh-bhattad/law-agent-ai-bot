import httpx

from app.core.config import settings

class CourtListenerClient:
    def __init__(self):
        self.url = settings.COURTLISTENER_BASE_URL
        self.headers = {
            "Authorization": f"Token {settings.COURTLISTENER_API_KEY}",
            "Accept": "application/json"
        }

    async def search_opinions(self, query: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=f"{self.url}/search/",
                headers=self.headers,
                params={
                    "q": query
                }
            )
            response.raise_for_status()

            return response.json()
