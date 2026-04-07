from __future__ import annotations


PRACTICE_PENDING_STATUS = "practice_pending"
PRACTICE_COMPLETED_STATUS = "practice_completed"
PRACTICE_FAILED_STATUS = "practice_failed"

RANKED_PENDING_STATUS = "ranked_pending"
RANKED_COMPLETED_STATUS = "ranked_completed"
RANKED_FAILED_STATUS = "ranked_failed"

LEGACY_COMPLETED_STATUS = "completed"

PENDING_STATUSES = {
    PRACTICE_PENDING_STATUS,
    RANKED_PENDING_STATUS,
}

TERMINAL_STATUSES = {
    PRACTICE_COMPLETED_STATUS,
    PRACTICE_FAILED_STATUS,
    RANKED_COMPLETED_STATUS,
    RANKED_FAILED_STATUS,
    LEGACY_COMPLETED_STATUS,
}


def battle_mode_from_status(status: str) -> str:
    return "practice" if status.startswith("practice_") else "ranked"


def score_applies_for_status(status: str) -> bool:
    return battle_mode_from_status(status) == "ranked"


def is_pending_status(status: str) -> bool:
    return status in PENDING_STATUSES


def is_public_visible_status(status: str) -> bool:
    return status in {
        RANKED_COMPLETED_STATUS,
        LEGACY_COMPLETED_STATUS,
    }


def is_terminal_status(status: str) -> bool:
    return status in TERMINAL_STATUSES


def completion_status_for(status: str) -> str:
    if status == PRACTICE_PENDING_STATUS:
        return PRACTICE_COMPLETED_STATUS
    if status == RANKED_PENDING_STATUS:
        return RANKED_COMPLETED_STATUS
    return status


def failure_status_for(status: str) -> str:
    if status == PRACTICE_PENDING_STATUS:
        return PRACTICE_FAILED_STATUS
    if status == RANKED_PENDING_STATUS:
        return RANKED_FAILED_STATUS
    return status
