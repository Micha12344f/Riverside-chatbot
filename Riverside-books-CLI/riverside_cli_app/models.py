from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FAQ:
    id: int
    question: str
    answer: str


@dataclass(frozen=True)
class MatchCandidate:
    faq: FAQ
    score: float


@dataclass(frozen=True)
class MatchResult:
    faq: FAQ
    score: float
    margin: float
    matcher_name: str
    used_fallback: bool = False
    candidates: tuple[MatchCandidate, ...] = field(default_factory=tuple)
