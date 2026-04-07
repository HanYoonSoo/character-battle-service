from __future__ import annotations

import unittest

from app.services.battle_status import (
    PRACTICE_PENDING_STATUS,
    RANKED_PENDING_STATUS,
    battle_mode_from_status,
    completion_status_for,
    failure_status_for,
    is_pending_status,
    is_public_visible_status,
    score_applies_for_status,
)


class BattleStatusTests(unittest.TestCase):
    def test_practice_pending_maps_to_practice_mode(self) -> None:
        self.assertEqual(battle_mode_from_status(PRACTICE_PENDING_STATUS), "practice")
        self.assertTrue(is_pending_status(PRACTICE_PENDING_STATUS))
        self.assertFalse(score_applies_for_status(PRACTICE_PENDING_STATUS))

    def test_ranked_pending_maps_to_ranked_mode(self) -> None:
        self.assertEqual(battle_mode_from_status(RANKED_PENDING_STATUS), "ranked")
        self.assertTrue(is_pending_status(RANKED_PENDING_STATUS))
        self.assertTrue(score_applies_for_status(RANKED_PENDING_STATUS))

    def test_status_transitions_are_stable(self) -> None:
        self.assertEqual(completion_status_for(PRACTICE_PENDING_STATUS), "practice_completed")
        self.assertEqual(failure_status_for(PRACTICE_PENDING_STATUS), "practice_failed")
        self.assertEqual(completion_status_for(RANKED_PENDING_STATUS), "ranked_completed")
        self.assertEqual(failure_status_for(RANKED_PENDING_STATUS), "ranked_failed")
        self.assertTrue(is_public_visible_status("ranked_completed"))
        self.assertFalse(is_public_visible_status("ranked_pending"))


if __name__ == "__main__":
    unittest.main()
