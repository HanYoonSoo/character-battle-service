from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.schemas.base import ApiSchema


class BattleCreateRequest(ApiSchema):
    left_character_id: UUID
    right_character_id: UUID


class RankedBattleCreateRequest(ApiSchema):
    my_character_id: UUID


class BattleParticipantSnapshot(ApiSchema):
    character_id: UUID
    name: str
    power_description: str


class BattleResponse(ApiSchema):
    battle_id: UUID
    battle_mode: str
    score_applied: bool
    left_character: BattleParticipantSnapshot
    right_character: BattleParticipantSnapshot
    winner_character_id: UUID | None
    winner_character_name: str | None
    explanation: str | None
    status: str
    created_at: datetime
    winner_recorded_at: datetime | None


class BattleListResponse(ApiSchema):
    items: list[BattleResponse]


class BattleJudgmentOutput(ApiSchema):
    winner_character_id: UUID = Field(
        description="Must be one of the two submitted character ids."
    )
    explanation: str = Field(
        description=(
            "A Korean explanation written in a lightly playful tone. "
            "Keep it natural, concise, and focused on why the winner won."
        )
    )
