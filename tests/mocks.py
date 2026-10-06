from typing import Type
from app.integrations.llm import LLMProvider, T
from app.schemas.brief import CaseBrief, LegalAnalysis

class FakeLLMProvider(LLMProvider):
    async def complete_with_json_schema(self, prompt: str, schema: Type[T]):
        if schema == CaseBrief:
            return CaseBrief(case_name="CBDummyCaseName", holding="CBDummyHolding", reasoning="CBDummyReasoning", citation=["CBDummyCitation"])
        elif schema == LegalAnalysis:
            return LegalAnalysis(primary_issue="LADummyPrimaryIsuue", material_facts=["LAdummyMatrialFact"], court_reasoning="LAdummyCourtReasoning")


class FakeCourtListenerClient:
    async def search_opinions(self, query: str):
        return ["DummyOpinion"]