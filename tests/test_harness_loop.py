from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from harness_starter.context_manager import ProjectMemory
from harness_starter.harness_loop import HarnessExecutionError, run_harness_loop
from harness_starter.models import AgentResponse, Citation, ContextChunk


class FlakyWorker:
    def __init__(self) -> None:
        self.calls = 0

    def answer(
        self,
        task: str,
        context: list[ContextChunk],
        constraints: list[str],
        last_error: str | None = None,
    ) -> AgentResponse:
        self.calls += 1
        if self.calls == 1:
            return AgentResponse(answer="Missing citation", confidence=0.4)
        return AgentResponse(
            answer="Grounded answer",
            citations=[
                Citation(
                    source=context[0].source,
                    snippet="Harness retries after validation failure.",
                )
            ],
            confidence=0.7,
        )


class BrokenWorker:
    def answer(
        self,
        task: str,
        context: list[ContextChunk],
        constraints: list[str],
        last_error: str | None = None,
    ) -> AgentResponse:
        return AgentResponse(answer="", confidence=1.4)


class HarnessLoopTests(unittest.TestCase):
    def test_retries_until_validation_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs_root = Path(temp_dir)
            (docs_root / "rules.md").write_text(
                "Harness retries after validation failure.", encoding="utf-8"
            )
            memory = ProjectMemory(docs_root=docs_root)
            worker = FlakyWorker()

            response = run_harness_loop(
                task="Explain the retry rule",
                memory=memory,
                worker=worker,
                constraints=["cite your sources"],
                max_attempts=3,
            )

            self.assertEqual(worker.calls, 2)
            self.assertEqual(response.citations[0].source, "rules.md")

    def test_raises_when_max_attempts_are_exhausted(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs_root = Path(temp_dir)
            (docs_root / "rules.md").write_text(
                "Harness retries after validation failure.", encoding="utf-8"
            )
            memory = ProjectMemory(docs_root=docs_root)

            with self.assertRaises(HarnessExecutionError):
                run_harness_loop(
                    task="Explain the retry rule",
                    memory=memory,
                    worker=BrokenWorker(),
                    constraints=["cite your sources"],
                    max_attempts=2,
                )


if __name__ == "__main__":
    unittest.main()
