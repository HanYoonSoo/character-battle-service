from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status

from app.api.deps import (
    get_app_settings,
    get_battle_service,
    get_current_anonymous_user_id,
    get_resources,
)
from app.core.config import Settings
from app.core.resources import AppResources
from app.schemas.battle import (
    BattleCreateRequest,
    BattleListResponse,
    RankedBattleCreateRequest,
    BattleResponse,
)
from app.services.battle_job_runner import BattleJobRunner
from app.services.battle_service import BattleService

router = APIRouter()


@router.get("", response_model=BattleListResponse)
async def list_public_battles(
    service: BattleService = Depends(get_battle_service),
) -> BattleListResponse:
    return await service.list_public_battles()


@router.get("/practice/mine", response_model=BattleListResponse)
async def list_my_practice_battles(
    anonymous_user_id: uuid.UUID = Depends(get_current_anonymous_user_id),
    service: BattleService = Depends(get_battle_service),
) -> BattleListResponse:
    return await service.list_my_practice_battles(anonymous_user_id)


@router.get("/{battle_id}", response_model=BattleResponse)
async def get_battle(
    battle_id: uuid.UUID,
    anonymous_user_id: uuid.UUID = Depends(get_current_anonymous_user_id),
    service: BattleService = Depends(get_battle_service),
) -> BattleResponse:
    return await service.get_battle(battle_id, anonymous_user_id)


@router.post("/practice", response_model=BattleResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_practice_battle(
    payload: BattleCreateRequest,
    anonymous_user_id: uuid.UUID = Depends(get_current_anonymous_user_id),
    service: BattleService = Depends(get_battle_service),
    resources: AppResources = Depends(get_resources),
    settings: Settings = Depends(get_app_settings),
) -> BattleResponse:
    battle = await service.create_practice_battle(anonymous_user_id, payload)
    BattleJobRunner(settings, resources).dispatch(battle.battle_id)
    return battle


@router.post("/ranked-random", response_model=BattleResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_ranked_random_battle(
    payload: RankedBattleCreateRequest,
    anonymous_user_id: uuid.UUID = Depends(get_current_anonymous_user_id),
    service: BattleService = Depends(get_battle_service),
    resources: AppResources = Depends(get_resources),
    settings: Settings = Depends(get_app_settings),
) -> BattleResponse:
    battle = await service.create_ranked_random_battle(anonymous_user_id, payload)
    BattleJobRunner(settings, resources).dispatch(battle.battle_id)
    return battle
