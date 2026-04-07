from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.errors import BadRequestError, NotFoundError
from app.repositories.character_repository import CharacterRepository
from app.schemas.character import CharacterCreateRequest, CharacterUpdateRequest
from app.schemas.character import CharacterListResponse, CharacterResponse
from app.services.leaderboard_service import LeaderboardService

logger = logging.getLogger(__name__)


class CharacterService:
    def __init__(
        self,
        settings: Settings,
        repository: CharacterRepository,
        leaderboard_service: LeaderboardService,
        session: AsyncSession,
    ) -> None:
        self.settings = settings
        self.repository = repository
        self.leaderboard_service = leaderboard_service
        self.session = session

    def validate_character_payload(
        self,
        payload: CharacterCreateRequest | CharacterUpdateRequest,
    ) -> None:
        if getattr(payload, "name", None) is not None:
            if not payload.name.strip():
                raise BadRequestError("Character name must not be blank.")
        if getattr(payload, "power_description", None) is not None:
            if not payload.power_description.strip():
                raise BadRequestError("Character description must not be blank.")
        if getattr(payload, "name", None) is not None and len(payload.name) > self.settings.max_character_name_length:
            raise BadRequestError("Character name length exceeds configured limit.")
        if (
            getattr(payload, "power_description", None) is not None
            and len(payload.power_description) > self.settings.max_character_description_length
        ):
            raise BadRequestError("Character description length exceeds configured limit.")

    def validate_character_limit(self, current_count: int) -> None:
        if current_count >= self.settings.max_characters_per_user:
            raise BadRequestError("Character count exceeds configured per-user limit.")

    async def list_my_characters(self, anonymous_user_id: uuid.UUID) -> CharacterListResponse:
        items = await self.repository.list_active_by_owner(anonymous_user_id)
        return CharacterListResponse(items=[self._to_response(item) for item in items])

    async def list_public_characters(self) -> CharacterListResponse:
        items = await self.repository.list_public_active()
        return CharacterListResponse(items=[self._to_response(item) for item in items])

    async def create_character(
        self,
        anonymous_user_id: uuid.UUID,
        payload: CharacterCreateRequest,
    ) -> CharacterResponse:
        self.validate_character_payload(payload)
        current_count = await self.repository.count_active_by_owner(anonymous_user_id)
        self.validate_character_limit(current_count)

        entity = await self.repository.create(
            anonymous_user_id=anonymous_user_id,
            name=payload.name.strip(),
            power_description=payload.power_description.strip(),
            now=self._utcnow(),
        )
        await self.session.commit()
        return self._to_response(entity)

    async def update_character(
        self,
        anonymous_user_id: uuid.UUID,
        character_id: uuid.UUID,
        payload: CharacterUpdateRequest,
    ) -> CharacterResponse:
        self.validate_character_payload(payload)
        entity = await self.repository.get_owned_active(character_id, anonymous_user_id)
        if entity is None:
            raise NotFoundError("Character was not found for the current anonymous user.")

        updated = await self.repository.update(
            entity,
            name=payload.name.strip() if payload.name is not None else None,
            power_description=(
                payload.power_description.strip()
                if payload.power_description is not None
                else None
            ),
            now=self._utcnow(),
        )
        await self.session.commit()
        return self._to_response(updated)

    async def delete_character(
        self,
        anonymous_user_id: uuid.UUID,
        character_id: uuid.UUID,
    ) -> None:
        entity = await self.repository.get_owned_active(character_id, anonymous_user_id)
        if entity is None:
            raise NotFoundError("Character was not found for the current anonymous user.")

        await self.repository.soft_delete(entity, self._utcnow())
        await self.session.commit()
        try:
            await self.leaderboard_service.remove_character(character_id)
        except Exception:
            logger.exception("Failed to remove soft-deleted character from leaderboard.")

    @staticmethod
    def _to_response(entity) -> CharacterResponse:
        return CharacterResponse(
            id=entity.id,
            owner_visitor_id=entity.anonymous_user_id,
            name=entity.name,
            power_description=entity.power_description,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def _utcnow() -> datetime:
        return datetime.now(timezone.utc)
