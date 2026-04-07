from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Response, status

from app.api.deps import get_character_service, get_current_anonymous_user_id
from app.schemas.character import (
    CharacterCreateRequest,
    CharacterListResponse,
    CharacterResponse,
    CharacterUpdateRequest,
)
from app.services.character_service import CharacterService

router = APIRouter()


@router.get("/me", response_model=CharacterListResponse)
async def list_my_characters(
    anonymous_user_id: uuid.UUID = Depends(get_current_anonymous_user_id),
    service: CharacterService = Depends(get_character_service),
) -> CharacterListResponse:
    return await service.list_my_characters(anonymous_user_id)


@router.get("/public", response_model=CharacterListResponse)
async def list_public_characters(
    service: CharacterService = Depends(get_character_service),
) -> CharacterListResponse:
    return await service.list_public_characters()


@router.post("", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
async def create_character(
    payload: CharacterCreateRequest,
    anonymous_user_id: uuid.UUID = Depends(get_current_anonymous_user_id),
    service: CharacterService = Depends(get_character_service),
) -> CharacterResponse:
    return await service.create_character(anonymous_user_id, payload)


@router.patch("/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: uuid.UUID,
    payload: CharacterUpdateRequest,
    anonymous_user_id: uuid.UUID = Depends(get_current_anonymous_user_id),
    service: CharacterService = Depends(get_character_service),
) -> CharacterResponse:
    return await service.update_character(anonymous_user_id, character_id, payload)


@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(
    character_id: uuid.UUID,
    anonymous_user_id: uuid.UUID = Depends(get_current_anonymous_user_id),
    service: CharacterService = Depends(get_character_service),
) -> None:
    await service.delete_character(anonymous_user_id, character_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
