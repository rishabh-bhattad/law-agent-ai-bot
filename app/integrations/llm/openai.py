from datetime import datetime, timezone
from openai import AsyncOpenAI
from pydantic import BaseModel
from typing import Type
from collections.abc import Callable
from app.workflow.context import WorkflowBudgetExceededError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_not_exception_type
from app.core.config import get_settings
from app.integrations.llm import LLMProvider, T
from app.integrations.revenium import record_revenium_metric

class OpenAILLMProvider(LLMProvider):
    """OpenAI integration conforming to LLMProvider using beta.chat.completions.parse."""

    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            api_key=get_settings().OPENAI_API_KEY
        )
        self.model_name = get_settings().LLM_MODEL_REASONING or "gpt-6.1-sol"

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
        """Generates structured content matching the provided Pydantic schema using OpenAI beta parse."""
        target_model = model or self.model_name
        start_time = datetime.now(timezone.utc)

        response = await self.client.beta.chat.completions.parse(
            model=target_model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format=schema
        )

        end_time = datetime.now(timezone.utc)
        duration_ms = max(1, int((end_time - start_time).total_seconds() * 1000))

        message = response.choices[0].message
        if message.parsed is None:
            refusal = getattr(message, "refusal", None) or "Failed to parse structured output from OpenAI response."
            raise ValueError(f"OpenAI parsing failed: {refusal}")

        if response.usage:
            prompt_tokens = response.usage.prompt_tokens or 0
            completion_tokens = response.usage.completion_tokens or 0
            total_tokens = response.usage.total_tokens or (prompt_tokens + completion_tokens)

            reasoning_tokens = getattr(getattr(response.usage, "completion_tokens_details", None), "reasoning_tokens", 0) or 0
            cache_read_tokens = getattr(getattr(response.usage, "prompt_tokens_details", None), "cached_tokens", 0) or 0

            if on_token_usage:
                on_token_usage(total_tokens)

            # Asynchronous non-blocking metering to Revenium
            record_revenium_metric(
                model=target_model,
                provider="OpenAI",
                input_tokens=prompt_tokens,
                output_tokens=completion_tokens,
                total_tokens=total_tokens,
                reasoning_tokens=reasoning_tokens,
                cache_read_tokens=cache_read_tokens,
                request_time=start_time,
                response_time=end_time,
                request_duration_ms=duration_ms,
                task_type=schema.__name__.lower() if hasattr(schema, "__name__") else "legal-brief",
            )

        return message.parsed
