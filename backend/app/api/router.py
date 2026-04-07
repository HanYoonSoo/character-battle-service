from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import battles, characters, health, leaderboard, session

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(session.router, prefix="/session", tags=["session"])
api_router.include_router(characters.router, prefix="/characters", tags=["characters"])
api_router.include_router(battles.router, prefix="/battles", tags=["battles"])
api_router.include_router(leaderboard.router, prefix="/leaderboard", tags=["leaderboard"])
