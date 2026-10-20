from app.workflow.context import WorkflowContext, WorkflowStep, WorkflowBudgetExceededError
from typing import Any
import json
import logging
from collections.abc import AsyncGenerator
import asyncio

logger = logging.getLogger("law_bot.workflow")

class WorkflowRunner:
    """Executes a list of workflow steps sequentially."""

    def __init__(self, steps: list[WorkflowStep]) -> None:
        self.steps = steps

    async def run(self, context: WorkflowContext) -> Any:
        """Runs all steps in order and returns the output in context.scratch['_final_output']."""
        async with asyncio.timeout(context.budget.timeout_seconds):
            for idx, step in enumerate(self.steps, 1):
                context.budget.record_step()
                logger.info(">>> [Step %d/%d START]: %s", idx, len(self.steps), step.name)
                await step.execute(context=context)
                logger.info("<<< [Step %d/%d FINISHED]: %s (Cumulative Tokens: %d)", idx, len(self.steps), step.name, context.budget.tokens_used)
        return context.scratch.get('_final_output')

    async def run_stream(self, context: WorkflowContext) -> AsyncGenerator[str, None]:
        """Runs steps sequentially and yields SSE data events for each stage."""
        try:
            async with asyncio.timeout(context.budget.timeout_seconds):
                for idx, step in enumerate(self.steps, 1):
                    context.budget.record_step()
                    logger.info(">>> [Stream Step %d/%d START]: %s", idx, len(self.steps), step.name)
                    yield f"data: {json.dumps({'event': 'step_start', 'step': step.name})}\n\n"
                    await step.execute(context=context)
                    logger.info("<<< [Stream Step %d/%d FINISHED]: %s (Cumulative Tokens: %d)", idx, len(self.steps), step.name, context.budget.tokens_used)
                    yield f"data: {json.dumps({'event': 'step_complete', 'step': step.name})}\n\n"
            final_output = context.scratch.get('_final_output')
            yield f"data: {json.dumps({'event': 'complete', 'result': final_output.model_dump(by_alias=True)})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'event': 'error', 'detail': str(e)})}\n\n"