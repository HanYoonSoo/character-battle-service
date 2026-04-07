from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.battle import Battle
from app.services.battle_status import (
    PRACTICE_COMPLETED_STATUS,
    PRACTICE_FAILED_STATUS,
    PRACTICE_PENDING_STATUS,
    RANKED_COMPLETED_STATUS,
)


class BattleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        requested_by_user_id: uuid.UUID,
        status: str,
        left_character_id: uuid.UUID,
        right_character_id: uuid.UUID,
        left_character_name_snapshot: str,
        right_character_name_snapshot: str,
        left_character_description_snapshot: str,
        right_character_description_snapshot: str,
        winner_character_id: uuid.UUID | None,
        explanation: str | None,
        created_at: datetime,
        winner_recorded_at: datetime | None,
    ) -> Battle:
        entity = Battle(
            requested_by_user_id=requested_by_user_id,
            status=status,
            left_character_id=left_character_id,
            right_character_id=right_character_id,
            left_character_name_snapshot=left_character_name_snapshot,
            right_character_name_snapshot=right_character_name_snapshot,
            left_character_description_snapshot=left_character_description_snapshot,
            right_character_description_snapshot=right_character_description_snapshot,
            winner_character_id=winner_character_id,
            explanation=explanation,
            created_at=created_at,
            winner_recorded_at=winner_recorded_at,
        )
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def get_by_id(self, battle_id: uuid.UUID) -> Battle | None:
        result = await self.session.execute(
            select(Battle).where(Battle.id == battle_id)
        )
        return result.scalar_one_or_none()

    async def list_public(self, limit: int = 100) -> list[Battle]:
        result = await self.session.execute(
            select(Battle)
            .where(
                or_(
                    Battle.status == RANKED_COMPLETED_STATUS,
                    Battle.status == "completed",
                )
            )
            .order_by(Battle.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_practice_by_requester(
        self,
        requested_by_user_id: uuid.UUID,
        limit: int = 20,
    ) -> list[Battle]:
        result = await self.session.execute(
            select(Battle)
            .where(
                Battle.requested_by_user_id == requested_by_user_id,
                Battle.status.in_(
                    (
                        PRACTICE_PENDING_STATUS,
                        PRACTICE_COMPLETED_STATUS,
                        PRACTICE_FAILED_STATUS,
                    )
                ),
            )
            .order_by(Battle.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
