from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class GateResult:
    name: str
    passed: bool
    summary: str
    repairable: bool = False
    command: tuple[str, ...] = ()
    returncode: int = 0
    stdout: str = ""
    stderr: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["command"] = list(self.command)
        return payload


@dataclass(frozen=True)
class HygieneFinding:
    code: str
    message: str
    path: str
    severity: str = "error"
    metadata: dict[str, Any] = field(default_factory=dict)

    def fingerprint(self) -> str:
        return f"{self.code}:{self.path}"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TextLintFinding:
    code: str
    message: str
    path: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RuleCandidate:
    code: str
    title: str
    rationale: str
    recommended_action: str
    evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RepairOutcome:
    success: bool
    attempts_used: int
    results: list[GateResult]
    applied_repairs: list[str] = field(default_factory=list)
    stopped_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "attempts_used": self.attempts_used,
            "results": [result.to_dict() for result in self.results],
            "applied_repairs": list(self.applied_repairs),
            "stopped_reason": self.stopped_reason,
        }
