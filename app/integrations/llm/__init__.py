from app.core.config import Settings
from typing import Protocol, TypeVar, Type
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class LLMProvider(Protocol):
    async def complete_with_json_schema(
            self,
            prompt: str,
            schema: Type[T]
    ) -> T:
        """
        Takes a prompt string and a Pydantic schema class.
        Returns an instance of that exact Pydantic class.
        """
        ...

def llm_provider(settings: Settings) -> LLMProvider:
    llm = settings.LLM_PROVIDER
    if llm == 'gemini':
        from app.integrations.llm.gemini import GeminiLLMProvider
        return GeminiLLMProvider()
    else:
        raise ValueError("Unknown LLM provider")




