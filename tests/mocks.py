from typing import Type
from app.integrations.llm import LLMProvider, T
from app.schemas.brief import CaseBrief, LegalAnalysis


class FakeLLMProvider(LLMProvider):
    """Mock LLM Provider returning dummy Pydantic model instances."""

    async def complete_with_json_schema(self, prompt: str, schema: Type[T]) -> T:
        if schema == CaseBrief:
            return CaseBrief(
                case_name="CBDummyCaseName",
                holding="CBDummyHolding",
                reasoning="CBDummyReasoning",
                citation=["CBDummyCitation"],
            )
        elif schema == LegalAnalysis:
            return LegalAnalysis(
                primary_issue="LADummyPrimaryIsuue",
                material_facts=["LAdummyMatrialFact"],
                court_reasoning="LAdummyCourtReasoning",
            )
        raise ValueError(f"FakeLLMProvider does not support schema: {schema}")


class FakeCourtListenerClient:
    """Mock CourtListener client returning simulated search results."""

    async def search_opinions(self, query: str) -> list[str]:
        return ["DummyOpinion"]