from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import Type

# Import retry tools
from tenacity import retry, wait_exponential, stop_after_attempt

from app.core.config import settings
from app.integrations.llm.base import LLMProvider, T

class GeminiLLMProvider(LLMProvider):
    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )
        self.model_name = "gemini-2.5-flash"

    @retry(
            wait=wait_exponential(multiplier=1, min=2, max=10),
            stop=stop_after_attempt(5)
    )
    async def complete_with_json_schema(self, prompt: str, schema: Type[T]) -> T:
        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema
            )
        )

        return response.parsed