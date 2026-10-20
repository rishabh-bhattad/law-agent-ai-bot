from app.integrations.llm import LLMProvider
from app.integrations.courtlistener import CourtListenerClient
from app.core.guardrails import check_for_injection
from app.workflow.context import WorkflowContext
from app.workflow.runner import WorkflowRunner
from app.workflow.registry import get_briefing_workflow, get_repair_workflow
from app.schemas.brief import CaseBrief, RepairBriefRequest, SingleFieldRepair
from app.prompts import build_schema_prompt
from app.core.config import get_settings
from collections.abc import AsyncGenerator


class BriefingPipeline:
    """Orchestrates the briefing workflow from query input to final brief output."""

    def __init__(self, llm_client: LLMProvider, court_client: CourtListenerClient) -> None:
        self.llm = llm_client
        self.court = court_client


    async def execute(self, query: str) -> CaseBrief:
        """Runs security checks and executes the briefing workflow steps."""
        check_for_injection(query)

        briefing_steps = get_briefing_workflow(llm=self.llm, court=self.court)
        context = WorkflowContext(request=query)
        runner = WorkflowRunner(briefing_steps)
        await runner.run(context=context)
        return context.scratch['_final_output']

    async def stream(self, query: str) -> AsyncGenerator[str, None]:
        """Runs security checks and streams SSE events for each workflow step"""
        check_for_injection(query)

        briefing_steps = get_briefing_workflow(llm=self.llm, court=self.court)
        ctx = WorkflowContext(request=query)
        runner = WorkflowRunner(steps=briefing_steps)
        async for event in runner.run_stream(context=ctx):
            yield event

    async def repair(self, request: RepairBriefRequest) -> CaseBrief:
        """Refines a single field of an existing brief using the fast LLM tier."""
        check_for_injection(request.instruction)

        repair_steps = get_repair_workflow(llm=self.llm)
        context = WorkflowContext(request=request)
        runner = WorkflowRunner(repair_steps)
        await runner.run(context=context)

        return context.scratch['_final_output']