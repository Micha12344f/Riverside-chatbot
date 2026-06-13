from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FAQ:
    """Represents one FAQ entry from the shop knowledge base."""

    id: int
    question: str
    answer: str


@dataclass(frozen=True)
class MatchCandidate:
    """A scored FAQ candidate returned during ranking."""

    faq: FAQ
    score: float


@dataclass(frozen=True)
class MatchResult:
    """The accepted match returned to the CLI."""

    faq: FAQ
    score: float
    margin: float
    matcher_name: str
    used_fallback: bool = False
    candidates: tuple[MatchCandidate, ...] = field(default_factory=tuple)
