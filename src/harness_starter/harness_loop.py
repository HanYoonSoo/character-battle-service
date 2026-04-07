from __future__ import annotations

from harness_starter.context_manager import ProjectMemory
from harness_starter.models import AgentResponse
from harness_starter.validators import validate_response
from harness_starter.workers import HarnessWorker


class HarnessExecutionError(RuntimeError):
    """Raised when the harness cannot produce a validated answer."""


def run_harness_loop(
    task: str,
    memory: ProjectMemory,
    worker: HarnessWorker,
    constraints: list[str],
    max_attempts: int = 3,
) -> AgentResponse:
    current_task = task
    last_error: str | None = None

    for _ in range(max_attempts):
        context = memory.get_relevant_context(current_task)
        response = worker.answer(
            current_task,
            context,
            constraints,
            last_error=last_error,
        )
        verification = validate_response(response, context)
        if verification.passed:
            return response

        last_error = "; ".join(verification.errors)
        current_task = f"{task}\n\nFix the failed verification: {last_error}"

    raise HarnessExecutionError(
        f"Harness stopped after {max_attempts} attempts. Last error: {last_error}"
    )

