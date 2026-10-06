from app.integrations.llm import LLMProvider
from app.integrations.courtlistener import CourtListenerClient
from app.workflow.context import WorkflowStep
from app.workflow.briefing_steps import (
    SearchCourtListenerStep,
    AnalyzeLegalIssuesStep,
    DraftBriefStep,
    QAReviewStep
)

def get_briefing_workflow(llm: LLMProvider, court: CourtListenerClient) -> list[WorkflowStep]:
    """Returns the ordered list of workflow steps for legal briefing."""
    listener, analyzer, drafter, reviewer = SearchCourtListenerStep(court), AnalyzeLegalIssuesStep(llm), DraftBriefStep(llm), QAReviewStep(llm)
    return [listener, analyzer, drafter, reviewer]