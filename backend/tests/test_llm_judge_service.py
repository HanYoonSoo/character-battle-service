from __future__ import annotations

import unittest

from app.services.llm_judge_service import LLMJudgeService


class LLMJudgeServiceTests(unittest.TestCase):
    def test_system_prompt_requires_korean_and_playful_tone(self) -> None:
        prompt = LLMJudgeService.SYSTEM_PROMPT

        self.assertIn("한국어", prompt)
        self.assertIn("장난스럽", prompt)
        self.assertIn("영어로 답하지 마세요", prompt)

    def test_korean_explanation_validator_accepts_korean_text(self) -> None:
        explanation = "눈빛맨이 슬쩍 노려보는 순간 분위기가 끝났습니다. 결국 상대가 버티지 못하고 패배했네요."

        self.assertTrue(LLMJudgeService._looks_korean_explanation(explanation))

    def test_korean_explanation_validator_rejects_english_text(self) -> None:
        explanation = "The left character wins because the opponent cannot resist the pressure."

        self.assertFalse(LLMJudgeService._looks_korean_explanation(explanation))


if __name__ == "__main__":
    unittest.main()
