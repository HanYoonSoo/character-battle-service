from __future__ import annotations

import unittest

from harness_starter.models import AgentResponse, Citation, ContextChunk
from harness_starter.validators import validate_response


class ValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.context = [
            ContextChunk(
                source="rules.md",
                text="Harness retries after validation failure.",
                score=3,
            )
        ]

    def test_accepts_grounded_response(self) -> None:
        response = AgentResponse(
            answer="Grounded answer",
            citations=[
                Citation(
                    source="rules.md",
                    snippet="Harness retries after validation failure.",
                )
            ],
            confidence=0.8,
        )

        verification = validate_response(response, self.context)

        self.assertTrue(verification.passed)
        self.assertEqual(verification.errors, [])

    def test_rejects_unknown_citation(self) -> None:
        response = AgentResponse(
            answer="Grounded answer",
            citations=[Citation(source="missing.md", snippet="Nope")],
            confidence=0.8,
        )

        verification = validate_response(response, self.context)

        self.assertFalse(verification.passed)
        self.assertIn("Unknown citation source: missing.md", verification.errors)

    def test_rejects_empty_grounded_answer(self) -> None:
        response = AgentResponse(answer="", citations=[], confidence=0.5)

        verification = validate_response(response, self.context)

        self.assertFalse(verification.passed)
        self.assertIn("Answer must not be empty.", verification.errors)
        self.assertIn(
            "Grounded answers must include at least one citation.",
            verification.errors,
        )


if __name__ == "__main__":
    unittest.main()
