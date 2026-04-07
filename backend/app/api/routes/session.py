from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response

from app.api.deps import get_session_service
from app.schemas.session import SessionBootstrapResponse
from app.services.session_service import SessionService

router = APIRouter()


@router.post("/bootstrap", response_model=SessionBootstrapResponse)
async def bootstrap_session(
    request: Request,
    response: Response,
    service: SessionService = Depends(get_session_service),
) -> SessionBootstrapResponse:
    session_token = request.cookies.get(service.settings.session_cookie_name)
    return await service.bootstrap(response=response, existing_session_token=session_token)
