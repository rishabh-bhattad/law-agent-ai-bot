from fastapi import Depends

from functools import lru_cache

from app.core.config import Settings, get_settings
from app.integrations.llm import llm_provider, LLMProvider
from app.integrations.courtlistener import CourtListenerClient
from app.workflow.pipeline import BriefingPipeline


def get_courtlistener() -> CourtListenerClient:
    """Dependency that returns a fresh CourtListener client."""
    return CourtListenerClient()


@lru_cache
def get_llm() -> LLMProvider:
    """Dependency that uses our factory to return the correct LLM."""
    return llm_provider(get_settings())


def get_briefing_pipeline(
        court: CourtListenerClient = Depends(get_courtlistener),
        llm: LLMProvider = Depends(get_llm)
) -> BriefingPipeline:
    """Dependency that returns a fully constructed BriefingService."""
    return BriefingPipeline(llm_client=llm, court_client=court)

