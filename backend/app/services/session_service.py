from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timezone

from fastapi import Response
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.errors import UnauthorizedError
from app.repositories.anonymous_user_repository import AnonymousUserRepository
from app.schemas.session import SessionBootstrapResponse


class SessionService:
    def __init__(
        self,
        settings: Settings,
        user_repository: AnonymousUserRepository,
        redis: Redis,
        session: AsyncSession,
    ) -> None:
        self.settings = settings
        self.user_repository = user_repository
        self.redis = redis
        self.session = session

    async def bootstrap(
        self,
        response: Response,
        existing_session_token: str | None,
    ) -> SessionBootstrapResponse:
        if existing_session_token:
            payload = await self._get_session_payload(existing_session_token)
            if payload:
                anonymous_user_id = uuid.UUID(payload["anonymous_user_id"])
                existing_user = await self.user_repository.get_by_id(anonymous_user_id)
                if existing_user is None:
                    await self.redis.delete(self._session_key(existing_session_token))
                else:
                    now = self._utcnow()
                    await self.user_repository.touch_last_seen(anonymous_user_id, now)
                    await self.session.commit()
                    await self._write_session_payload(
                        existing_session_token,
                        anonymous_user_id=anonymous_user_id,
                        created_at=payload["created_at"],
                        last_seen_at=now.isoformat(),
                    )
                    self._set_cookie(response, existing_session_token)
                    return SessionBootstrapResponse(
                        visitor_id=anonymous_user_id,
                        is_new=False,
                    )

        now = self._utcnow()
        anonymous_user = await self.user_repository.create(now)
        await self.session.commit()

        session_token = secrets.token_urlsafe(32)
        await self._write_session_payload(
            session_token,
            anonymous_user_id=anonymous_user.id,
            created_at=now.isoformat(),
            last_seen_at=now.isoformat(),
        )
        self._set_cookie(response, session_token)
        return SessionBootstrapResponse(visitor_id=anonymous_user.id, is_new=True)

    async def resolve_anonymous_user_id(self, session_token: str) -> uuid.UUID:
        payload = await self._get_session_payload(session_token)
        if not payload:
            raise UnauthorizedError("Anonymous session is invalid or expired.")
        anonymous_user_id = uuid.UUID(payload["anonymous_user_id"])
        existing_user = await self.user_repository.get_by_id(anonymous_user_id)
        if existing_user is None:
            await self.redis.delete(self._session_key(session_token))
            raise UnauthorizedError("Anonymous session user could not be resolved.")

        key = self._session_key(session_token)
        await self.redis.hset(key, "last_seen_at", self._utcnow().isoformat())
        await self.redis.expire(key, self.settings.session_ttl_seconds)
        return anonymous_user_id

    async def _get_session_payload(self, session_token: str) -> dict[str, str]:
        return await self.redis.hgetall(self._session_key(session_token))

    async def _write_session_payload(
        self,
        session_token: str,
        *,
        anonymous_user_id: uuid.UUID,
        created_at: str,
        last_seen_at: str,
    ) -> None:
        key = self._session_key(session_token)
        await self.redis.hset(
            key,
            mapping={
                "anonymous_user_id": str(anonymous_user_id),
                "created_at": created_at,
                "last_seen_at": last_seen_at,
                "session_version": "1",
            },
        )
        await self.redis.expire(key, self.settings.session_ttl_seconds)

    def _set_cookie(self, response: Response, session_token: str) -> None:
        response.set_cookie(
            key=self.settings.session_cookie_name,
            value=session_token,
            httponly=True,
            secure=self.settings.session_cookie_secure,
            samesite="lax",
            max_age=self.settings.session_ttl_seconds,
            path="/",
        )

    def _session_key(self, session_token: str) -> str:
        return f"anon_session:{session_token}"

    @staticmethod
    def _utcnow() -> datetime:
        return datetime.now(timezone.utc)
