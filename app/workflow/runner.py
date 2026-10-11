from app.workflow.context import WorkflowContext, WorkflowStep
from typing import Any
import json
from collections.abc import AsyncGenerator

class WorkflowRunner:
    """Executes a list of workflow steps sequentially."""

    def __init__(self, steps: list[WorkflowStep]) -> None:
        self.steps = steps

    async def run(self, context: WorkflowContext) -> Any:
        """Runs all steps in order and returns the output in context.scratch['_final_output']."""
        for step in self.steps:
            await step.execute(context=context)
        return context.scratch.get('_final_output')

    async def run_stream(self, context: WorkflowContext) -> AsyncGenerator[str, None]:
        """Runs steps sequentially and yields SSE data events for each stage."""
        for step in self.steps:
            yield f"data: {json.dumps({'event': 'step_start', 'step': step.name})}\n\n"
            await step.execute(context=context)
            yield f"data: {json.dumps({'event': 'step_complete', 'step': step.name})}\n\n"
        final_output = context.scratch.get('_final_output')
        yield f"data: {json.dumps({'event': 'complete', 'result': final_output.model_dump(by_alias=True)})}\n\n"