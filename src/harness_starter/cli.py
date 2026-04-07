from __future__ import annotations

import argparse
import json
from pathlib import Path

from harness_starter.context_manager import ProjectMemory
from harness_starter.router import handle_user_input
from harness_starter.workers import build_worker

DEFAULT_CONSTRAINTS = [
    "Use only the approved local docs directory as context.",
    "Do not guess when the docs do not support an answer.",
    "Return at least one citation for grounded answers.",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the harness starter.")
    parser.add_argument("prompt", help="User request to send through the harness.")
    parser.add_argument(
        "--docs-root",
        default="docs",
        help="Directory containing approved source documents.",
    )
    parser.add_argument(
        "--worker",
        default="rules",
        choices=("rules", "openai"),
        help="Worker implementation to use.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    memory = ProjectMemory(
        docs_root=Path(args.docs_root),
        global_constraints=DEFAULT_CONSTRAINTS,
    )
    worker = build_worker(args.worker)
    response = handle_user_input(
        user_prompt=args.prompt,
        memory=memory,
        worker=worker,
        constraints=memory.get_global_constraints(),
    )

    payload = {
        "answer": response.answer,
        "citations": [citation.__dict__ for citation in response.citations],
        "confidence": response.confidence,
        "needs_followup": response.needs_followup,
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

