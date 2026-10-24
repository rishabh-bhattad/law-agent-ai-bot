from datetime import datetime, timezone
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import Type
from collections.abc import Callable
from app.workflow.context import WorkflowBudgetExceededError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_not_exception_type
from app.core.config import get_settings
from app.integrations.llm import LLMProvider, T
from app.integrations.revenium import record_revenium_metric

class GeminiLLMProvider(LLMProvider):
    """Google Gemini integration conforming to LLMProvider."""

    def __init__(self) -> None:
        self.client = genai.Client(
            api_key=get_settings().GEMINI_API_KEY
        )
        # Default Fallback model, if none is provided, in workflow steps.
        self.model_name = get_settings().LLM_MODEL_REASONING or "gemini-3.5-flash"

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
        start_time = datetime.now(timezone.utc)

        response = await self.client.aio.models.generate_content(
            model=target_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema
            )
        )

        end_time = datetime.now(timezone.utc)
        duration_ms = max(1, int((end_time - start_time).total_seconds() * 1000))

        if response.usage_metadata:
            prompt_tokens = response.usage_metadata.prompt_token_count or 0
            candidate_tokens = response.usage_metadata.candidates_token_count or 0
            total_tokens = response.usage_metadata.total_token_count or (prompt_tokens + candidate_tokens)
            cached_tokens = getattr(response.usage_metadata, "cached_content_token_count", 0) or 0

            if on_token_usage:
                on_token_usage(total_tokens)

            # Asynchronous non-blocking metering to Revenium
            record_revenium_metric(
                model=target_model,
                provider="Google",
                input_tokens=prompt_tokens,
                output_tokens=candidate_tokens,
                total_tokens=total_tokens,
                cache_read_tokens=cached_tokens,
                request_time=start_time,
                response_time=end_time,
                request_duration_ms=duration_ms,
                task_type=schema.__name__.lower() if hasattr(schema, "__name__") else "legal-brief",
            )

        return response.parsed