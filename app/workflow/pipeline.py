from app.integrations.llm import LLMProvider
from app.integrations.courtlistener import CourtListenerClient
from app.core.guardrails import check_for_injection
from app.workflow.context import WorkflowContext
from app.workflow.runner import WorkflowRunner
from app.workflow.registry import get_briefing_workflow
from app.schemas.brief import CaseBrief


class BriefingPipeline:
    def __init__(self, llm_client: LLMProvider, court_client: CourtListenerClient):
        self.llm = llm_client
        self.court = court_client


    async def execute(self, query: str) -> CaseBrief:
        check_for_injection(query)

        briefing_steps = get_briefing_workflow(llm=self.llm, court=self.court)
        context = WorkflowContext(request=query)
        runner = WorkflowRunner(briefing_steps)
        await runner.run(context=context)
        return context.scratch['_final_output']
        