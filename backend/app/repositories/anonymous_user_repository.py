from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.anonymous_user import AnonymousUser


class AnonymousUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, now: datetime) -> AnonymousUser:
        entity = AnonymousUser(created_at=now, last_seen_at=now)
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def get_by_id(self, anonymous_user_id: uuid.UUID) -> AnonymousUser | None:
        result = await self.session.execute(
            select(AnonymousUser).where(AnonymousUser.id == anonymous_user_id)
        )
        return result.scalar_one_or_none()

    async def touch_last_seen(self, anonymous_user_id: uuid.UUID, now: datetime) -> None:
        await self.session.execute(
            update(AnonymousUser)
            .where(AnonymousUser.id == anonymous_user_id)
            .values(last_seen_at=now)
        )
