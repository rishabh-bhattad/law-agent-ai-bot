from collections.abc import Callable
from typing import Type
from app.integrations.llm import LLMProvider, T
from app.schemas.brief import (
    CaseBrief,
    LegalAnalysis,
    SearchPlan,
    SingleFieldRepair,
    AuditRepairResult,
)


class FakeLLMProvider(LLMProvider):
    """Mock LLM Provider returning dummy Pydantic model instances."""

    async def complete_with_json_schema(
        self,
        prompt: str,
        schema: Type[T],
        model: str | None = None,
        on_token_usage: Callable[[int], None] | None = None,
    ) -> T:
        if on_token_usage:
            on_token_usage(100)

        if schema == SearchPlan:
            return SearchPlan(
                search_query="Dummy Search Query",
                court=None
            )
        elif schema == CaseBrief:
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
        elif schema == SingleFieldRepair:
            return SingleFieldRepair(
                repaired_text="Repaired field text content."
            )
        elif schema == AuditRepairResult:
            return AuditRepairResult(
                approved=True,
                audited_text="Repaired field text content.",
                critique="The draft accurately reflects the legal principles.",
            )
        raise ValueError(f"FakeLLMProvider does not support schema: {schema}")


class FakeCourtListenerClient:
    """Mock CourtListener client returning simulated search results."""

    async def search_opinions(self, query: str, court: str | None = None) -> dict:
        return {
            "results": [
                {
                    "id": 107252,
                    "caseName": "Miranda v. Arizona",
                    "citation": ["384 U.S. 436"],
                    "citeCount": 58748,
                    "opinions": [{"id": 107252, "type": "combined-opinion"}],
                }
            ]
        }

    async def get_opinion(self, opinion_id: int | str) -> dict:
        return {
            "plain_text": "Delivered the opinion of the Court. The constitutional issue is custodial interrogation under the Fifth Amendment.",
            "html_with_citations": "<p>Delivered the opinion of the Court. The constitutional issue is custodial interrogation under the Fifth Amendment.</p>",
        }