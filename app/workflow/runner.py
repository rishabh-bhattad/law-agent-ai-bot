from app.workflow.context import WorkflowContext, WorkflowStep
from typing import Any

class WorkflowRunner:
    """Executes a list of workflow steps sequentially."""

    def __init__(self, steps: list[WorkflowStep]) -> None:
        self.steps = steps

    async def run(self, context: WorkflowContext) -> Any:
        """Runs all steps in order and returns the output in context.scratch['_final_output']."""
        for step in self.steps:
            await step.execute(context=context)
        return context.scratch.get('_final_output')
