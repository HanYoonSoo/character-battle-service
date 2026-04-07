from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone

from app.core.config import Settings
from app.core.resources import AppResources
from app.repositories.battle_repository import BattleRepository
from app.repositories.character_repository import CharacterRepository
from app.services.battle_status import (
    PENDING_STATUSES,
    completion_status_for,
    failure_status_for,
    score_applies_for_status,
)
from app.services.leaderboard_service import LeaderboardService
from app.services.llm_judge_service import LLMJudgeService

logger = logging.getLogger(__name__)


class BattleJobRunner:
    def __init__(self, settings: Settings, resources: AppResources) -> None:
        self.settings = settings
        self.resources = resources

    def dispatch(self, battle_id: uuid.UUID) -> None:
        task = asyncio.create_task(self.run(battle_id))
        self.resources.background_tasks.add(task)
        task.add_done_callback(self.resources.background_tasks.discard)

    async def run(self, battle_id: uuid.UUID) -> None:
        async with self.resources.db.session() as session:
            battle_repository = BattleRepository(session)
            character_repository = CharacterRepository(session)
            leaderboard_service = LeaderboardService(
                self.settings,
                self.resources.redis,
                character_repository,
            )
            judge_service = LLMJudgeService(self.settings, self.resources.openai)

            entity = await battle_repository.get_by_id(battle_id)
            if entity is None or entity.status not in PENDING_STATUSES:
                return

            try:
                judgment = await judge_service.judge_battle(
                    left_character={
                        "id": entity.left_character_id,
                        "name": entity.left_character_name_snapshot,
                        "power_description": entity.left_character_description_snapshot,
                    },
                    right_character={
                        "id": entity.right_character_id,
                        "name": entity.right_character_name_snapshot,
                        "power_description": entity.right_character_description_snapshot,
                    },
                )
                recorded_at = self._utcnow()
                entity.winner_character_id = judgment.winner_character_id
                entity.explanation = judgment.explanation.strip()
                entity.winner_recorded_at = recorded_at
                entity.status = completion_status_for(entity.status)
                await session.commit()

                if score_applies_for_status(entity.status):
                    try:
                        await leaderboard_service.record_win(
                            judgment.winner_character_id,
                            recorded_at,
                        )
                    except Exception:
                        logger.exception("Failed to update leaderboard for battle %s.", battle_id)
                return
            except Exception:
                logger.exception("Battle job failed for %s.", battle_id)

            entity.status = failure_status_for(entity.status)
            entity.explanation = "심판이 아직 판정을 마치지 못했습니다. 잠시 후 다시 시도해 주세요."
            entity.winner_recorded_at = self._utcnow()
            await session.commit()

    @staticmethod
    def _utcnow() -> datetime:
        return datetime.now(timezone.utc)
