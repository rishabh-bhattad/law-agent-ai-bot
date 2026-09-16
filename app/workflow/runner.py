from app.workflow.context import WorkflowContext, WorkflowStep
from typing import Any

class WorkflowRunner:
    def __init__(self, steps: list[WorkflowStep]):
        self.steps = steps

    async def run(self, context: WorkflowContext) -> Any:
        for step in self.steps:
            await step.execute(context=context)
        return context.scratch.get('_final_output')
