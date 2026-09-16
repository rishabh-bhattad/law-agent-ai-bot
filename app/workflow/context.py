from dataclasses import dataclass, field
from typing import Any, Protocol

@dataclass
class WorkflowContext:
    """The shared memory passed between every step in the pipeline."""
    request: Any
    scratch: dict[str, Any] = field(default_factory=dict)


class WorkflowStep(Protocol):
    """The interface that every agent/step MUST implement."""
    name: str

    async def execute(self, context: WorkflowContext) -> None:
        """Executes the step and mutates context.scratch in-place."""
        ...