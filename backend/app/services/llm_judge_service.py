from __future__ import annotations

import re
from typing import Any

from openai import AsyncOpenAI

from app.core.config import Settings
from app.core.errors import ExternalServiceError
from app.schemas.battle import BattleJudgmentOutput
from app.services.prompt_payload import dumps_prompt_payload


class LLMJudgeService:
    SYSTEM_PROMPT = (
        "당신은 캐릭터 배틀 심판입니다. "
        "제출된 두 캐릭터 중 반드시 정확히 한 명만 승자로 선택하세요. "
        "판정 근거는 반드시 자연스러운 한국어로 작성하세요. "
        "말투는 살짝 장난스럽고 재치 있어도 되지만, 비속어 없이 읽기 쉬워야 합니다. "
        "설명은 왜 이 캐릭터가 이겼는지 납득되게 써야 하며, 영어로 답하지 마세요. "
        "마크다운, 코드블록, 이모지 없이 JSON 스키마에 맞는 값만 반환하세요."
    )

    def __init__(self, settings: Settings, client: AsyncOpenAI) -> None:
        self.settings = settings
        self.client = client

    async def judge_battle(
        self,
        *,
        left_character: dict[str, Any],
        right_character: dict[str, Any],
    ) -> BattleJudgmentOutput:
        if not self.settings.openai_api_key or self.settings.openai_api_key == "replace_me":
            raise ExternalServiceError("OPENAI_API_KEY is not configured.")

        feedback: str | None = None
        for _ in range(self.settings.llm_max_attempts):
            try:
                response = await self.client.responses.create(
                    model=self.settings.openai_model,
                    input=[
                        {
                            "role": "system",
                            "content": [
                                {
                                    "type": "input_text",
                                    "text": self.SYSTEM_PROMPT,
                                }
                            ],
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "input_text",
                                    "text": self._build_prompt(
                                        left_character=left_character,
                                        right_character=right_character,
                                        feedback=feedback,
                                    ),
                                }
                            ],
                        },
                    ],
                    text={
                        "format": {
                            "type": "json_schema",
                            "name": "battle_judgment",
                            "strict": True,
                            "schema": BattleJudgmentOutput.model_json_schema(),
                        }
                    }
                )
            except Exception as exc:
                raise ExternalServiceError(f"OpenAI battle judgment request failed: {exc}") from exc
            try:
                payload = BattleJudgmentOutput.model_validate_json(response.output_text)
            except Exception as exc:
                feedback = f"JSON schema validation failed: {exc}"
                continue

            allowed_winners = {
                left_character["id"],
                right_character["id"],
            }
            if payload.winner_character_id not in allowed_winners:
                feedback = "winner_character_id must be one of the two submitted character ids."
                continue
            if not payload.explanation.strip():
                feedback = "explanation must not be empty."
                continue
            if not self._looks_korean_explanation(payload.explanation):
                feedback = "explanation must be written in Korean."
                continue
            return payload

        raise ExternalServiceError(
            "GPT-4o did not return a valid battle judgment within the allowed retry limit."
        )

    @staticmethod
    def _build_prompt(
        *,
        left_character: dict[str, Any],
        right_character: dict[str, Any],
        feedback: str | None,
    ) -> str:
        payload = {
            "rules": [
                "Return exactly one winner.",
                "The winner must be one of the submitted character ids.",
                "Do not invent a third option or a draw.",
                "Write the explanation in Korean.",
                "Use a lightly playful tone, but keep it readable and concise.",
            ],
            "left_character": left_character,
            "right_character": right_character,
            "previous_validation_feedback": feedback,
        }
        return dumps_prompt_payload(payload)

    @staticmethod
    def _looks_korean_explanation(explanation: str) -> bool:
        hangul_matches = re.findall(r"[가-힣]", explanation)
        latin_matches = re.findall(r"[A-Za-z]", explanation)
        return len(hangul_matches) >= 8 and len(hangul_matches) >= len(latin_matches)
