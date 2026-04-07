from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from redis.asyncio import Redis

from app.core.config import Settings
from app.repositories.character_repository import CharacterRepository
from app.schemas.leaderboard import LeaderboardEntry, LeaderboardResponse

logger = logging.getLogger(__name__)


class LeaderboardService:
    def __init__(
        self,
        settings: Settings,
        redis: Redis,
        character_repository: CharacterRepository,
    ) -> None:
        self.settings = settings
        self.redis = redis
        self.character_repository = character_repository

    async def record_win(self, character_id: uuid.UUID, won_at: datetime) -> None:
        member = str(character_id)
        await self.redis.zincrby(
            self.settings.leaderboard_zset_key,
            self.settings.leaderboard_win_points,
            member,
        )
        await self.redis.hset(
            self.settings.leaderboard_last_win_key,
            member,
            won_at.isoformat(),
        )

    async def remove_character(self, character_id: uuid.UUID) -> None:
        member = str(character_id)
        await self.redis.zrem(self.settings.leaderboard_zset_key, member)
        await self.redis.hdel(self.settings.leaderboard_last_win_key, member)

    async def list_leaderboard(self, limit: int = 100) -> LeaderboardResponse:
        raw_items = await self.redis.zrevrange(
            self.settings.leaderboard_zset_key,
            0,
            max(limit - 1, 0),
            withscores=True,
        )
        if not raw_items:
            return LeaderboardResponse(items=[])

        character_ids = [uuid.UUID(member) for member, _ in raw_items]
        last_win_values = await self.redis.hmget(
            self.settings.leaderboard_last_win_key,
            *[str(character_id) for character_id in character_ids],
        )
        characters = await self.character_repository.get_active_by_ids(character_ids)
        characters_by_id = {character.id: character for character in characters}

        entries: list[LeaderboardEntry] = []
        for (member, score), last_win_raw in zip(raw_items, last_win_values):
            character_id = uuid.UUID(member)
            character = characters_by_id.get(character_id)
            if character is None:
                continue
            last_win_at = datetime.fromisoformat(last_win_raw) if last_win_raw else None
            entries.append(
                LeaderboardEntry(
                    character_id=character_id,
                    name=character.name,
                    score=int(score),
                    win_count=int(score),
                    last_win_at=last_win_at,
                )
            )

        entries.sort(
            key=lambda item: (
                -item.score,
                item.last_win_at or datetime.max.replace(tzinfo=timezone.utc),
            )
        )
        return LeaderboardResponse(items=entries[:limit])
