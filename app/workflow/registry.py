from app.integrations.llm import LLMProvider
from app.integrations.courtlistener import CourtListenerClient
from app.workflow.context import WorkflowStep
from app.workflow.briefing_steps import (
    OptimizeQueryStep,
    SearchCourtListenerStep,
    AnalyzeLegalIssuesStep,
    DraftBriefStep,
    QAReviewStep
)

def get_briefing_workflow(llm: LLMProvider, court: CourtListenerClient) -> list[WorkflowStep]:
    """Returns the ordered list of workflow steps for legal briefing."""
    optimizer = OptimizeQueryStep(llm)
    listener = SearchCourtListenerStep(court)
    analyzer = AnalyzeLegalIssuesStep(llm)
    drafter = DraftBriefStep(llm)
    reviewer = QAReviewStep(llm)
    return [optimizer, listener, analyzer, drafter, reviewer]