from __future__ import annotations

from pathlib import Path
import json
import sys
import unittest
import uuid


BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.prompt_payload import dumps_prompt_payload  # noqa: E402


class PromptPayloadTests(unittest.TestCase):
    def test_serializes_uuid_values_for_llm_prompt_payload(self) -> None:
        character_id = uuid.uuid4()

        payload_text = dumps_prompt_payload(
            {
                "left_character": {
                    "id": character_id,
                    "name": "left",
                }
            }
        )

        payload = json.loads(payload_text)
        self.assertEqual(payload["left_character"]["id"], str(character_id))


if __name__ == "__main__":
    unittest.main()
