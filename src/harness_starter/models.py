from dataclasses import dataclass, field


@dataclass(frozen=True)
class Intent:
    raw: str
    is_actionable: bool
    is_ambiguous: bool


@dataclass(frozen=True)
class Citation:
    source: str
    snippet: str


@dataclass(frozen=True)
class ContextChunk:
    source: str
    text: str
    score: int


@dataclass
class AgentResponse:
    answer: str
    citations: list[Citation] = field(default_factory=list)
    confidence: float = 0.0
    needs_followup: bool = False


@dataclass(frozen=True)
class VerificationResult:
    passed: bool
    errors: list[str] = field(default_factory=list)

