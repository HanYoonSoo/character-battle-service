from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_leaderboard_service
from app.schemas.leaderboard import LeaderboardResponse
from app.services.leaderboard_service import LeaderboardService

router = APIRouter()


@router.get("", response_model=LeaderboardResponse)
async def get_leaderboard(
    service: LeaderboardService = Depends(get_leaderboard_service),
) -> LeaderboardResponse:
    return await service.list_leaderboard()
