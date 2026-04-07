from __future__ import annotations

from harness_starter.context_manager import ProjectMemory
from harness_starter.harness_loop import run_harness_loop
from harness_starter.models import AgentResponse, Intent
from harness_starter.workers import HarnessWorker

ACTION_HINTS = {
    "build",
    "create",
    "make",
    "implement",
    "design",
    "write",
    "setup",
    "fix",
    "update",
}

AMBIGUOUS_HINTS = {
    "something",
    "anything",
    "stuff",
    "maybe",
    "somehow",
}


def extract_intent(user_prompt: str) -> Intent:
    lowered = user_prompt.lower()
    tokens = lowered.split()
    is_actionable = any(token in ACTION_HINTS for token in tokens) or len(tokens) >= 6
    is_ambiguous = len(tokens) < 4 or any(token in AMBIGUOUS_HINTS for token in tokens)
    return Intent(raw=user_prompt, is_actionable=is_actionable, is_ambiguous=is_ambiguous)


def handle_user_input(
    user_prompt: str,
    memory: ProjectMemory,
    worker: HarnessWorker,
    constraints: list[str],
) -> AgentResponse:
    intent = extract_intent(user_prompt)

    if intent.is_ambiguous:
        return AgentResponse(
            answer=(
                "Please clarify the goal, expected output, and any constraints before "
                "the harness starts the execution loop."
            ),
            citations=[],
            confidence=0.1,
            needs_followup=True,
        )

    if intent.is_actionable:
        return run_harness_loop(user_prompt, memory, worker, constraints)

    return AgentResponse(
        answer="This request does not require the controlled harness path.",
        citations=[],
        confidence=0.3,
        needs_followup=True,
    )

