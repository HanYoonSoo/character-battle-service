from __future__ import annotations

from datetime import datetime
from uuid import UUID

from app.schemas.base import ApiSchema


class LeaderboardEntry(ApiSchema):
    character_id: UUID
    name: str
    score: int
    win_count: int
    last_win_at: datetime | None = None


class LeaderboardResponse(ApiSchema):
    items: list[LeaderboardEntry]
