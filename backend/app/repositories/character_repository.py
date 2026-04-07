from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.character import Character


class CharacterRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def count_active_by_owner(self, anonymous_user_id: uuid.UUID) -> int:
        result = await self.session.execute(
            select(func.count(Character.id)).where(
                Character.anonymous_user_id == anonymous_user_id,
                Character.deleted_at.is_(None),
            )
        )
        return int(result.scalar_one())

    async def create(
        self,
        anonymous_user_id: uuid.UUID,
        name: str,
        power_description: str,
        now: datetime,
    ) -> Character:
        entity = Character(
            anonymous_user_id=anonymous_user_id,
            name=name,
            power_description=power_description,
            created_at=now,
            updated_at=now,
        )
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def list_active_by_owner(self, anonymous_user_id: uuid.UUID) -> list[Character]:
        result = await self.session.execute(
            select(Character)
            .where(
                Character.anonymous_user_id == anonymous_user_id,
                Character.deleted_at.is_(None),
            )
            .order_by(Character.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_public_active(self, limit: int = 100) -> list[Character]:
        result = await self.session.execute(
            select(Character)
            .where(Character.deleted_at.is_(None))
            .order_by(Character.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_public_active_excluding_owner(
        self,
        anonymous_user_id: uuid.UUID,
        limit: int = 100,
    ) -> list[Character]:
        result = await self.session.execute(
            select(Character)
            .where(
                Character.deleted_at.is_(None),
                Character.anonymous_user_id != anonymous_user_id,
            )
            .order_by(Character.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_random_active_public_opponent(
        self,
        anonymous_user_id: uuid.UUID,
    ) -> Character | None:
        result = await self.session.execute(
            select(Character)
            .where(
                Character.deleted_at.is_(None),
                Character.anonymous_user_id != anonymous_user_id,
            )
            .order_by(func.random())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_active_by_id(self, character_id: uuid.UUID) -> Character | None:
        result = await self.session.execute(
            select(Character).where(
                Character.id == character_id,
                Character.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_owned_active(
        self,
        character_id: uuid.UUID,
        anonymous_user_id: uuid.UUID,
    ) -> Character | None:
        result = await self.session.execute(
            select(Character).where(
                Character.id == character_id,
                Character.anonymous_user_id == anonymous_user_id,
                Character.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_active_by_ids(self, character_ids: list[uuid.UUID]) -> list[Character]:
        if not character_ids:
            return []
        result = await self.session.execute(
            select(Character).where(
                Character.id.in_(character_ids),
                Character.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def update(
        self,
        entity: Character,
        *,
        name: str | None,
        power_description: str | None,
        now: datetime,
    ) -> Character:
        if name is not None:
            entity.name = name
        if power_description is not None:
            entity.power_description = power_description
        entity.updated_at = now
        await self.session.flush()
        return entity

    async def soft_delete(self, entity: Character, now: datetime) -> None:
        entity.deleted_at = now
        entity.updated_at = now
        await self.session.flush()
