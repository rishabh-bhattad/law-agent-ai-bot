from app.integrations.courtlistener import CourtListenerClient
from app.integrations.llm import LLMProvider
from app.schemas.brief import CaseBrief
from app.prompts import build_schema_prompt


class BriefingService:
    def __init__(self, llm_client: LLMProvider, court_client: CourtListenerClient):
        self.llm = llm_client
        self.court = court_client


    async def generate_brief(self, query: str) -> CaseBrief:
        cases = str(await self.court.search_opinions(query=query))
        formatted_prompt = build_schema_prompt(
            template_name="briefing.md",
            schema=CaseBrief,
            case_text=cases
        )
        response = await self.llm.complete_with_json_schema(formatted_prompt, schema=CaseBrief)
        return response
