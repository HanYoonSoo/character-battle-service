from __future__ import annotations

import asyncio
from dataclasses import dataclass

from openai import AsyncOpenAI
from redis.asyncio import Redis

from app.db.session import DatabaseSessionManager


@dataclass
class AppResources:
    db: DatabaseSessionManager
    redis: Redis
    openai: AsyncOpenAI
    background_tasks: set[asyncio.Task[None]]
