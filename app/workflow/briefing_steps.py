from app.workflow.context import WorkflowContext, WorkflowStep
from app.integrations.courtlistener import CourtListenerClient
from app.integrations.llm import LLMProvider
from app.prompts import build_schema_prompt
from app.schemas.brief import LegalAnalysis, CaseBrief, SearchPlan
from app.core.config import get_settings
from app.core.citations import enrich_brief_citations
import logging

logger = logging.getLogger("law_bot.workflow")


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
        plan: SearchPlan = await self.llm.complete_with_json_schema(
            prompt=formatted_prompt,
            schema=SearchPlan,
            model=get_settings().LLM_MODEL_FAST,
            on_token_usage=context.budget.record_tokens
        )
        context.scratch['search_plan'] = plan
        logger.info(
            "\n%s\n[STAGE 1/5 OUTPUT] Optimizing Search Query -> Schema: SearchPlan\n%s\n%s",
            "=" * 70,
            plan.model_dump_json(indent=2),
            "=" * 70
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
        logger.info(
            "\n%s\n[STAGE 2/5 OUTPUT] CourtListener Search -> Retrieved %d raw opinion(s)\n%s",
            "=" * 70,
            len(cases),
            "=" * 70
        )


class AnalyzeLegalIssuesStep(WorkflowStep):
    """Extracts primary legal issues and reasoning from raw case opinions."""
    name = "Analyzing Legal Issues."

    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    async def execute(self, context: WorkflowContext) -> None:
        raw_cases = context.scratch['raw_cases']
        formatted_prompt = build_schema_prompt("analyze.md", schema=LegalAnalysis, raw_cases=raw_cases)
        analysis: LegalAnalysis = await self.llm.complete_with_json_schema(
            prompt=formatted_prompt,
            schema=LegalAnalysis,
            model=get_settings().LLM_MODEL_REASONING,
            on_token_usage=context.budget.record_tokens
        )
        context.scratch['outline'] = analysis
        logger.info(
            "\n%s\n[STAGE 3/5 OUTPUT] Analyzing Legal Issues -> Schema: LegalAnalysis\n%s\n%s",
            "=" * 70,
            analysis.model_dump_json(indent=2),
            "=" * 70
        )


class DraftBriefStep(WorkflowStep):
    """Drafts a structured case brief from the extracted legal analysis."""
    name = "Drafting Briefing for the query."

    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    async def execute(self, context: WorkflowContext) -> None:
        outline = context.scratch['outline']
        formatted_prompt = build_schema_prompt("briefing.md", schema=CaseBrief, case_text=outline)
        draft: CaseBrief = await self.llm.complete_with_json_schema(
            prompt=formatted_prompt,
            schema=CaseBrief,
            model=get_settings().LLM_MODEL_FAST,
            on_token_usage=context.budget.record_tokens
        )
        context.scratch['draft_brief'] = draft
        logger.info(
            "\n%s\n[STAGE 4/5 OUTPUT] Drafting Brief -> Schema: CaseBrief (Draft)\n%s\n%s",
            "=" * 70,
            draft.model_dump_json(indent=2, by_alias=True),
            "=" * 70
        )


class QAReviewStep(WorkflowStep):
    """Reviews the draft brief against the original case text for accuracy."""
    name = "Running Quality Analysis"

    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    async def execute(self, context: WorkflowContext) -> None:
        draft_brief = context.scratch['draft_brief']
        raw_cases = context.scratch['raw_cases']
        formatted_prompt = build_schema_prompt("qa_review.md", schema=CaseBrief, draft_brief=draft_brief, raw_cases=raw_cases)
        brief = await self.llm.complete_with_json_schema(
            prompt=formatted_prompt,
            schema=CaseBrief,
            model=get_settings().LLM_MODEL_REASONING,
            on_token_usage=context.budget.record_tokens
        )
        final_brief = enrich_brief_citations(brief=brief)
        context.scratch['_final_output'] = final_brief
        logger.info(
            "\n%s\n[STAGE 5/5 OUTPUT] QA Review & Enrichment -> Schema: CaseBrief (Final Verified)\n%s\n%s",
            "=" * 70,
            final_brief.model_dump_json(indent=2, by_alias=True),
            "=" * 70
        )
