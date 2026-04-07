from __future__ import annotations

import json
import os
from typing import Protocol

from harness_starter.models import AgentResponse, Citation, ContextChunk


class HarnessWorker(Protocol):
    def answer(
        self,
        task: str,
        context: list[ContextChunk],
        constraints: list[str],
        last_error: str | None = None,
    ) -> AgentResponse:
        ...


class RulesBasedWorker:
    def answer(
        self,
        task: str,
        context: list[ContextChunk],
        constraints: list[str],
        last_error: str | None = None,
    ) -> AgentResponse:
        if not context:
            return AgentResponse(
                answer="I need more grounded project documents before I can answer safely.",
                citations=[],
                confidence=0.2,
                needs_followup=True,
            )

        citations: list[Citation] = []
        summary_lines: list[str] = []
        for chunk in context[:2]:
            snippet = _first_sentence(chunk.text)
            citations.append(Citation(source=chunk.source, snippet=snippet))
            summary_lines.append(f"{chunk.source}: {snippet}")

        answer = "Grounded summary: " + " ".join(summary_lines)
        if last_error:
            answer += f" Corrected after verification error: {last_error}"

        return AgentResponse(
            answer=answer,
            citations=citations,
            confidence=min(0.85, 0.4 + 0.2 * len(citations)),
            needs_followup=False,
        )


class OpenAIWorker:
    def __init__(self, model: str = "gpt-4.1-mini") -> None:
        self.model = model

    def answer(
        self,
        task: str,
        context: list[ContextChunk],
        constraints: list[str],
        last_error: str | None = None,
    ) -> AgentResponse:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is not set.")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install the optional 'openai' dependency first.") from exc

        client = OpenAI()
        context_block = "\n\n".join(
            f"[{chunk.source}]\n{chunk.text}" for chunk in context
        )
        error_block = last_error or "none"
        prompt = (
            "Return JSON with keys: answer, citations, confidence, needs_followup.\n"
            "Each citation item must include source and snippet.\n"
            "Use only the provided context.\n"
            f"Task: {task}\n"
            f"Constraints: {constraints}\n"
            f"Previous verification error: {error_block}\n"
            f"Context:\n{context_block}"
        )

        response = client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": "You are a constrained harness worker. Return JSON only.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        payload = json.loads(response.output_text)
        citations = [
            Citation(source=item["source"], snippet=item["snippet"])
            for item in payload.get("citations", [])
        ]
        return AgentResponse(
            answer=payload["answer"],
            citations=citations,
            confidence=float(payload.get("confidence", 0.0)),
            needs_followup=bool(payload.get("needs_followup", False)),
        )


def build_worker(kind: str) -> HarnessWorker:
    if kind == "rules":
        return RulesBasedWorker()
    if kind == "openai":
        return OpenAIWorker()
    raise ValueError(f"Unknown worker kind: {kind}")


def _first_sentence(text: str, limit: int = 160) -> str:
    compact = " ".join(text.split())
    return compact[:limit].rstrip()
