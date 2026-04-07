from __future__ import annotations

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, get_redis

router = APIRouter()


@router.get("/healthz")
async def healthcheck(
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
) -> dict[str, object]:
    await session.execute(text("SELECT 1"))
    redis_ok = await redis.ping()
    return {
        "status": "ok",
        "database": "ok",
        "redis": "ok" if redis_ok else "unhealthy",
    }
