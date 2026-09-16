from app.workflow.context import WorkflowContext, WorkflowStep
from app.integrations.courtlistener import CourtListenerClient
from app.integrations.llm import LLMProvider
from app.prompts import build_schema_prompt
from app.schemas.brief import LegalAnalysis, CaseBrief

class SearchCourtListenerStep(WorkflowStep):
    name = "Searching CourtListener Database."

    def __init__(self, client: CourtListenerClient):
        self.client = client

    async def execute(self, context: WorkflowContext) -> None:
        query = context.request
        cases = await self.client.search_opinions(query=query)
        formatted_str = ""
        for case in cases:
            formatted_str += str(case)
        context.scratch['raw_cases'] = formatted_str


class AnalyzeLegalIssuesStep(WorkflowStep):
    name = "Analyzing Legal Issues."

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def execute(self, context: WorkflowContext):
        raw_cases = context.scratch['raw_cases']
        formatted_prompt = build_schema_prompt("analyze.md", schema=LegalAnalysis, raw_cases=raw_cases)
        context.scratch['outline'] = await self.llm.complete_with_json_schema(
            prompt=formatted_prompt,
            schema=LegalAnalysis)


class DraftBriefStep(WorkflowStep):
    name = "Drafting Briefing for the query."

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def execute(self, context: WorkflowContext):
        outline = context.scratch['outline']
        formatted_prompt = build_schema_prompt("briefing.md", schema=CaseBrief, case_text=outline)
        context.scratch['draft_brief'] = await self.llm.complete_with_json_schema(prompt=formatted_prompt, schema=CaseBrief)


class QAReviewStep(WorkflowStep):
    name = "Running Quality Analysis"

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def execute(self, context: WorkflowContext):
        draft_brief = context.scratch['draft_brief']
        raw_cases = context.scratch['raw_cases']
        formatted_prompt = build_schema_prompt("qa_review.md", schema=CaseBrief, draft_brief=draft_brief, raw_cases=raw_cases)
        context.scratch['_final_output'] = await self.llm.complete_with_json_schema(prompt=formatted_prompt, schema=CaseBrief)
