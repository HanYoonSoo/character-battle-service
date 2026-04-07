from __future__ import annotations

import json
import uuid
from typing import Any


def dumps_prompt_payload(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, default=_json_default)


def _json_default(value: Any) -> str:
    if isinstance(value, uuid.UUID):
        return str(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")
