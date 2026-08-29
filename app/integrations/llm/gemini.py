from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import Type

from app.core.config import settings
from app.integrations.llm.base import LLMProvider, T

class GeminiLLMProvider(LLMProvider):
    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )
        self.model_name = "gemini-2.5-flash"


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