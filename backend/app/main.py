from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
import inspect

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from openai import AsyncOpenAI
from redis.asyncio import Redis

from app.api.router import api_router
from app.core.errors import ApplicationError
from app.core.config import get_settings
from app.core.resources import AppResources
from app.db.session import DatabaseSessionManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    db = DatabaseSessionManager(settings)
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    openai = AsyncOpenAI(api_key=settings.openai_api_key)
    background_tasks: set[asyncio.Task[None]] = set()

    await db.open()

    app.state.resources = AppResources(
        db=db,
        redis=redis,
        openai=openai,
        background_tasks=background_tasks,
    )
    try:
        yield
    finally:
        pending_tasks = {task for task in background_tasks if not task.done()}
        for task in pending_tasks:
            task.cancel()
        if pending_tasks:
            await asyncio.gather(*pending_tasks, return_exceptions=True)
        close = getattr(openai, "close", None)
        if callable(close):
            result = close()
            if inspect.isawaitable(result):
                await result
        await redis.aclose()
        await db.close()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )

    @app.exception_handler(ApplicationError)
    async def handle_application_error(_: Request, exc: ApplicationError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
