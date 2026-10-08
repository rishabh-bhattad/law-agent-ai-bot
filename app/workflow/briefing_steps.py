from app.workflow.context import WorkflowContext, WorkflowStep
from app.integrations.courtlistener import CourtListenerClient
from app.integrations.llm import LLMProvider
from app.prompts import build_schema_prompt
from app.schemas.brief import LegalAnalysis, CaseBrief, SearchPlan


class OptimizeQueryStep(WorkflowStep):
    """Rewrites user query into targeted search keywords and jurisdiction filters."""
    name = "Optimizing Search Query."

    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    async def execute(self, context: WorkflowContext) -> None:
        user_query = context.request
        formatted_prompt = build_schema_prompt(
            "optimize_query.md",
            schema=SearchPlan,
            user_query=user_query,
        )
        context.scratch['search_plan'] = await self.llm.complete_with_json_schema(
            prompt=formatted_prompt,
            schema=SearchPlan,
        )


class SearchCourtListenerStep(WorkflowStep):
    """Searches CourtListener for opinions matching the request."""
    name = "Searching CourtListener Database."

    def __init__(self, client: CourtListenerClient) -> None:
        self.client = client

    async def execute(self, context: WorkflowContext) -> None:
        plan: SearchPlan | None = context.scratch.get('search_plan')
        query = plan.search_query if plan else context.request
        court = plan.court if plan else None

        data = await self.client.search_opinions(query=query, court=court)
        cases = data.get("results", []) if isinstance(data, dict) else data
        formatted_str = ""
        for case in cases:
            formatted_str += str(case) + "\n\n"
        context.scratch['raw_cases'] = formatted_str


class AnalyzeLegalIssuesStep(WorkflowStep):
    """Extracts primary legal issues and reasoning from raw case opinions."""
    name = "Analyzing Legal Issues."

    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    async def execute(self, context: WorkflowContext) -> None:
        raw_cases = context.scratch['raw_cases']
        formatted_prompt = build_schema_prompt("analyze.md", schema=LegalAnalysis, raw_cases=raw_cases)
        context.scratch['outline'] = await self.llm.complete_with_json_schema(
            prompt=formatted_prompt,
            schema=LegalAnalysis)


class DraftBriefStep(WorkflowStep):
    """Drafts a structured case brief from the extracted legal analysis."""
    name = "Drafting Briefing for the query."

    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    async def execute(self, context: WorkflowContext) -> None:
        outline = context.scratch['outline']
        formatted_prompt = build_schema_prompt("briefing.md", schema=CaseBrief, case_text=outline)
        context.scratch['draft_brief'] = await self.llm.complete_with_json_schema(prompt=formatted_prompt, schema=CaseBrief)


class QAReviewStep(WorkflowStep):
    """Reviews the draft brief against the original case text for accuracy."""
    name = "Running Quality Analysis"

    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    async def execute(self, context: WorkflowContext) -> None:
        draft_brief = context.scratch['draft_brief']
        raw_cases = context.scratch['raw_cases']
        formatted_prompt = build_schema_prompt("qa_review.md", schema=CaseBrief, draft_brief=draft_brief, raw_cases=raw_cases)
        context.scratch['_final_output'] = await self.llm.complete_with_json_schema(prompt=formatted_prompt, schema=CaseBrief)
