from openai import AsyncOpenAI
from pydantic import BaseModel
from typing import Type
from collections.abc import Callable
from app.workflow.context import WorkflowBudgetExceededError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_not_exception_type
from app.core.config import get_settings
from app.integrations.llm import LLMProvider, T

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
        response = await self.client.beta.chat.completions.parse(
            model=target_model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format=schema
        )

        message = response.choices[0].message
        if message.parsed is None:
            raise ValueError("Failed to parse structured output from OpenAI response.")

        if on_token_usage and response.usage:
            on_token_usage(response.usage.total_tokens)

        return message.parsed
