from fastapi import Depends

from app.integrations.llm import llm_provider, LLMProvider
from app.integrations.courtlistener import CourtListenerClient
from app.services.briefing import BriefingService


def get_courtlistener() -> CourtListenerClient:
    """Dependency that returns a fresh CourtListener client."""
    return CourtListenerClient()


def get_llm() -> LLMProvider:
    """Dependency that uses our factory to return the correct LLM."""
    return llm_provider()


def get_briefing_service(
        court: CourtListenerClient = Depends(get_courtlistener),
        llm: LLMProvider = Depends(get_llm)
) -> BriefingService:
    """Dependency that returns a fully constructed BriefingService."""
    return BriefingService(llm_client=llm, court_client=court)

