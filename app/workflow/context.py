from dataclasses import dataclass, field
from typing import Any, Protocol

class WorkflowBudgetExceededError(Exception):
    """Raised when the workflow exceeds its allocated execution or resource budget."""
    pass

@dataclass
class WorkflowBudget:
    """Tracks resource consumption and enforces hard execution ceilings."""
    max_steps: int = 10
    max_tokens: int = 150_000
    timeout_seconds: float = 120.0
    steps_executed: int = 0
    tokens_used: int = 0
    def record_step(self) -> None:
        """Increments steps_executed and raises WorkflowBudgetExceededError if it exceeds max_steps."""
        self.steps_executed += 1
        if self.steps_executed > self.max_steps:
            raise WorkflowBudgetExceededError("Steps exceeded Max steps allowed")
    def record_tokens(self, count: int) -> None:
        """Increments tokens_used and raises WorkflowBudgetExceededError if it exceeds max_tokens."""
        self.tokens_used += count
        if self.tokens_used > self.max_tokens:
            raise WorkflowBudgetExceededError("Tokens exceeded max token allowed")
        pass

@dataclass
class WorkflowContext:
    """The shared memory passed between every step in the pipeline."""
    request: Any
    scratch: dict[str, Any] = field(default_factory=dict)
    budget: WorkflowBudget = field(default_factory=WorkflowBudget)


class WorkflowStep(Protocol):
    """The interface that every agent/step MUST implement."""
    name: str

    async def execute(self, context: WorkflowContext) -> None:
        """Executes the step and mutates context.scratch in-place."""
        ...