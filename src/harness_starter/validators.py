from __future__ import annotations

from harness_starter.models import AgentResponse, ContextChunk, VerificationResult


def validate_response(
    response: AgentResponse,
    context_chunks: list[ContextChunk],
) -> VerificationResult:
    errors: list[str] = []

    if not response.answer.strip():
        errors.append("Answer must not be empty.")

    if not 0.0 <= response.confidence <= 1.0:
        errors.append("Confidence must be between 0.0 and 1.0.")

    available_sources = {chunk.source: chunk.text for chunk in context_chunks}

    if not response.needs_followup and not response.citations:
        errors.append("Grounded answers must include at least one citation.")

    for citation in response.citations:
        if citation.source not in available_sources:
            errors.append(f"Unknown citation source: {citation.source}")
            continue
        if _normalize_whitespace(citation.snippet) not in _normalize_whitespace(
            available_sources[citation.source]
        ):
            errors.append(
                f"Citation snippet was not found in source: {citation.source}"
            )

    return VerificationResult(passed=not errors, errors=errors)


def _normalize_whitespace(value: str) -> str:
    return " ".join(value.split())
