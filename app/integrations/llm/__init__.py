from app.core.config import settings
from app.integrations.llm.base import LLMProvider

def llm_provider() -> LLMProvider:
    llm = settings.LLM_PROVIDER
    if llm == 'gemini':
        from app.integrations.llm.gemini import GeminiLLMProvider
        return GeminiLLMProvider()
    else:
        raise ValueError("Unknown LLM provider")
