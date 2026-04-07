from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.errors import BadRequestError, NotFoundError
from app.repositories.battle_repository import BattleRepository
from app.repositories.character_repository import CharacterRepository
from app.schemas.battle import (
    BattleCreateRequest,
    BattleListResponse,
    BattleParticipantSnapshot,
    BattleResponse,
    RankedBattleCreateRequest,
)
from app.services.battle_status import (
    LEGACY_COMPLETED_STATUS,
    PRACTICE_PENDING_STATUS,
    RANKED_PENDING_STATUS,
    battle_mode_from_status,
    is_public_visible_status,
    score_applies_for_status,
)


class BattleService:
    def __init__(
        self,
        settings: Settings,
        battle_repository: BattleRepository,
        character_repository: CharacterRepository,
        session: AsyncSession,
    ) -> None:
        self.settings = settings
        self.battle_repository = battle_repository
        self.character_repository = character_repository
        self.session = session

    async def list_public_battles(self) -> BattleListResponse:
        items = await self.battle_repository.list_public()
        return BattleListResponse(items=[self._to_response(item) for item in items])

    async def list_my_practice_battles(
        self,
        requested_by_user_id: uuid.UUID,
    ) -> BattleListResponse:
        items = await self.battle_repository.list_practice_by_requester(requested_by_user_id)
        return BattleListResponse(items=[self._to_response(item) for item in items])

    async def get_battle(
        self,
        battle_id: uuid.UUID,
        requested_by_user_id: uuid.UUID,
    ) -> BattleResponse:
        entity = await self.battle_repository.get_by_id(battle_id)
        if entity is None:
            raise NotFoundError("Battle was not found.")
        if not is_public_visible_status(entity.status) and entity.requested_by_user_id != requested_by_user_id:
            raise NotFoundError("Battle was not found.")
        return self._to_response(entity)

    async def create_practice_battle(
        self,
        requested_by_user_id: uuid.UUID,
        payload: BattleCreateRequest,
    ) -> BattleResponse:
        if payload.left_character_id == payload.right_character_id:
            raise BadRequestError("A character cannot battle itself.")

        left_character = await self.character_repository.get_owned_active(
            payload.left_character_id,
            requested_by_user_id,
        )
        right_character = await self.character_repository.get_owned_active(
            payload.right_character_id,
            requested_by_user_id,
        )
        if left_character is None or right_character is None:
            raise NotFoundError("Practice battles require two active characters that you own.")

        entity = await self.battle_repository.create(
            requested_by_user_id=requested_by_user_id,
            status=PRACTICE_PENDING_STATUS,
            left_character_id=left_character.id,
            right_character_id=right_character.id,
            left_character_name_snapshot=left_character.name,
            right_character_name_snapshot=right_character.name,
            left_character_description_snapshot=left_character.power_description,
            right_character_description_snapshot=right_character.power_description,
            winner_character_id=None,
            explanation=None,
            created_at=self._utcnow(),
            winner_recorded_at=None,
        )
        await self.session.commit()
        return self._to_response(entity)

    async def create_ranked_random_battle(
        self,
        requested_by_user_id: uuid.UUID,
        payload: RankedBattleCreateRequest,
    ) -> BattleResponse:
        my_character = await self.character_repository.get_owned_active(
            payload.my_character_id,
            requested_by_user_id,
        )
        if my_character is None:
            raise NotFoundError("Your selected character must exist and be active.")

        random_opponent = await self.character_repository.get_random_active_public_opponent(
            requested_by_user_id
        )
        if random_opponent is None:
            raise BadRequestError("There are no active public opponents from other players yet.")

        entity = await self.battle_repository.create(
            requested_by_user_id=requested_by_user_id,
            status=RANKED_PENDING_STATUS,
            left_character_id=my_character.id,
            right_character_id=random_opponent.id,
            left_character_name_snapshot=my_character.name,
            right_character_name_snapshot=random_opponent.name,
            left_character_description_snapshot=my_character.power_description,
            right_character_description_snapshot=random_opponent.power_description,
            winner_character_id=None,
            explanation=None,
            created_at=self._utcnow(),
            winner_recorded_at=None,
        )
        await self.session.commit()
        return self._to_response(entity)

    @staticmethod
    def _to_response(entity) -> BattleResponse:
        winner_name: str | None = None
        if entity.winner_character_id == entity.left_character_id:
            winner_name = entity.left_character_name_snapshot
        elif entity.winner_character_id == entity.right_character_id:
            winner_name = entity.right_character_name_snapshot

        status = entity.status
        battle_mode = "ranked" if status == LEGACY_COMPLETED_STATUS else battle_mode_from_status(status)

        return BattleResponse(
            battle_id=entity.id,
            battle_mode=battle_mode,
            score_applied=score_applies_for_status(status),
            left_character=BattleParticipantSnapshot(
                character_id=entity.left_character_id,
                name=entity.left_character_name_snapshot,
                power_description=entity.left_character_description_snapshot,
            ),
            right_character=BattleParticipantSnapshot(
                character_id=entity.right_character_id,
                name=entity.right_character_name_snapshot,
                power_description=entity.right_character_description_snapshot,
            ),
            winner_character_id=entity.winner_character_id,
            winner_character_name=winner_name,
            explanation=entity.explanation,
            status=status,
            created_at=entity.created_at,
            winner_recorded_at=entity.winner_recorded_at,
        )

    @staticmethod
    def _utcnow() -> datetime:
        return datetime.now(timezone.utc)
