from __future__ import annotations

import uuid
from collections.abc import AsyncIterator

from fastapi import Depends, Request
from openai import AsyncOpenAI
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.errors import UnauthorizedError
from app.core.resources import AppResources
from app.repositories.anonymous_user_repository import AnonymousUserRepository
from app.repositories.battle_repository import BattleRepository
from app.repositories.character_repository import CharacterRepository
from app.services.battle_service import BattleService
from app.services.character_service import CharacterService
from app.services.leaderboard_service import LeaderboardService
from app.services.llm_judge_service import LLMJudgeService
from app.services.session_service import SessionService


def get_app_settings() -> Settings:
    return get_settings()


def get_resources(request: Request) -> AppResources:
    return request.app.state.resources


async def get_db_session(
    resources: AppResources = Depends(get_resources),
) -> AsyncIterator[AsyncSession]:
    async with resources.db.session() as session:
        yield session


def get_redis(resources: AppResources = Depends(get_resources)) -> Redis:
    return resources.redis


def get_openai_client(resources: AppResources = Depends(get_resources)) -> AsyncOpenAI:
    return resources.openai


def get_anonymous_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> AnonymousUserRepository:
    return AnonymousUserRepository(session)


def get_character_repository(
    session: AsyncSession = Depends(get_db_session),
) -> CharacterRepository:
    return CharacterRepository(session)


def get_battle_repository(
    session: AsyncSession = Depends(get_db_session),
) -> BattleRepository:
    return BattleRepository(session)


def get_session_service(
    settings: Settings = Depends(get_app_settings),
    user_repository: AnonymousUserRepository = Depends(get_anonymous_user_repository),
    redis: Redis = Depends(get_redis),
    session: AsyncSession = Depends(get_db_session),
) -> SessionService:
    return SessionService(settings, user_repository, redis, session)


def get_leaderboard_service(
    settings: Settings = Depends(get_app_settings),
    redis: Redis = Depends(get_redis),
    character_repository: CharacterRepository = Depends(get_character_repository),
) -> LeaderboardService:
    return LeaderboardService(settings, redis, character_repository)


def get_character_service(
    settings: Settings = Depends(get_app_settings),
    repository: CharacterRepository = Depends(get_character_repository),
    leaderboard_service: LeaderboardService = Depends(get_leaderboard_service),
    session: AsyncSession = Depends(get_db_session),
) -> CharacterService:
    return CharacterService(settings, repository, leaderboard_service, session)


def get_llm_judge_service(
    settings: Settings = Depends(get_app_settings),
    client: AsyncOpenAI = Depends(get_openai_client),
) -> LLMJudgeService:
    return LLMJudgeService(settings, client)


def get_battle_service(
    settings: Settings = Depends(get_app_settings),
    battle_repository: BattleRepository = Depends(get_battle_repository),
    character_repository: CharacterRepository = Depends(get_character_repository),
    session: AsyncSession = Depends(get_db_session),
) -> BattleService:
    return BattleService(
        settings,
        battle_repository,
        character_repository,
        session,
    )


async def get_current_anonymous_user_id(
    request: Request,
    session_service: SessionService = Depends(get_session_service),
    settings: Settings = Depends(get_app_settings),
) -> uuid.UUID:
    session_token = request.cookies.get(settings.session_cookie_name)
    if not session_token:
        raise UnauthorizedError("Anonymous session cookie is missing.")
    return await session_service.resolve_anonymous_user_id(session_token)
