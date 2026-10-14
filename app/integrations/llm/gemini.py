from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import Type
from collections.abc import Callable
from app.workflow.context import WorkflowBudgetExceededError

# Import retry tools
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_not_exception_type

from app.core.config import get_settings
from app.integrations.llm import LLMProvider, T

class GeminiLLMProvider(LLMProvider):
    """Google Gemini integration conforming to LLMProvider."""

    def __init__(self) -> None:
        self.client = genai.Client(
            api_key=get_settings().GEMINI_API_KEY
        )
        # Deafult Fallback model, if none is provided, in workflow steps.
        self.model_name = "gemini-3.5-flash-lite"


    @retry(
            wait=wait_exponential(multiplier=1, min=2, max=10),
            stop=stop_after_attempt(5),
            retry=retry_if_not_exception_type(WorkflowBudgetExceededError)
    )
    async def complete_with_json_schema(
        self,
        prompt: str,
        schema: Type[T],
        model: str | None = None,
        on_token_usage: Callable[[int], None] | None = None
    ) -> T:
        """Generates structured content matching the provided Pydantic schema."""
        target_model = model or self.model_name
        response = await self.client.aio.models.generate_content(
            model=target_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema
            )
        )

        if on_token_usage and response.usage_metadata:
            on_token_usage(response.usage_metadata.total_token_count)

        return response.parsed