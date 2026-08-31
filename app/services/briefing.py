from app.integrations.courtlistener import CourtListenerClient
from app.integrations.llm import LLMProvider
from app.schemas.brief import CaseBrief
from app.prompts import get_prompt_template


class BriefingService:
    def __init__(self, llm_client: LLMProvider, court_client: CourtListenerClient):
        self.llm = llm_client
        self.court = court_client


    async def generate_brief(self, query: str) -> CaseBrief:
        cases = str(await self.court.search_opinions(query=query))
        prompt = get_prompt_template("briefing.md")
        formatted_prompt = prompt.format(
            case_text=cases
        )
        response = await self.llm.complete_with_json_schema(formatted_prompt, schema=CaseBrief)
        return response
