from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import replace
from difflib import SequenceMatcher
from typing import Any, Callable

import numpy as np

from .models import FAQ, MatchCandidate, MatchResult

MODEL_NAME = "sentence-transformers/multi-qa-MiniLM-L6-cos-v1"
DEFAULT_MIN_SCORE = 0.55
DEFAULT_MIN_MARGIN = 0.04
DEFAULT_LEXICAL_THRESHOLD = 0.3
DEFAULT_LEXICAL_MARGIN = 0.03
QUESTION_HINT_WEIGHT = 0.2
STOPWORDS = {
    "a",
    "all",
    "am",
    "an",
    "and",
    "any",
    "are",
    "at",
    "be",
    "bring",
    "can",
    "do",
    "for",
    "have",
    "how",
    "i",
    "in",
    "into",
    "is",
    "it",
    "me",
    "my",
    "of",
    "on",
    "or",
    "s",
    "store",
    "the",
    "there",
    "today",
    "to",
    "we",
    "what",
    "where",
    "you",
    "your",
}
TOKEN_ALIASES = {
    "cafe": {"coffee", "tea"},
    "coffee": {"cafe", "tea"},
    "friendly": {"accessible"},
    "open": {"hours"},
    "park": {"parking"},
    "parking": {"park"},
    "pickup": {"collect"},
    "site": {"website", "online"},
    "voucher": {"gift"},
    "vouchers": {"gift"},
    "website": {"online", "site"},
    "wheelchair": {"accessible"},
}


def build_faq_document(faq: FAQ) -> str:
    """Combine the question and answer into one searchable document."""

    return f"Question: {faq.question}\nAnswer: {faq.answer}"


def _normalize_text(text: str) -> str:
    lowered = text.lower()
    lowered = lowered.replace("wi-fi", "wifi")
    lowered = lowered.replace("children's", "children")
    lowered = lowered.replace("click-and-collect", "click and collect")
    return lowered


def _tokenize(text: str) -> list[str]:
    base_tokens = re.findall(r"[a-z0-9]+", _normalize_text(text))
    expanded_tokens: list[str] = []
    for token in base_tokens:
        if token in STOPWORDS:
            continue
        expanded_tokens.append(token)
        expanded_tokens.extend(sorted(TOKEN_ALIASES.get(token, ())))
    return expanded_tokens


def _prepare_query(query: str) -> str:
    lowered = _normalize_text(query)
    expansions: list[str] = []

    if "shop" in lowered and any(term in lowered for term in ("where", "address", "located")):
        expansions.append("location address located")
    if "site" in lowered:
        expansions.append("website online")
    if ("pick up" in lowered or "pickup" in lowered or "collect" in lowered) and (
        "online" in lowered or "order" in lowered
    ):
        expansions.append("click and collect")
    if "coffee" in lowered:
        expansions.append("cafe")
    if "wheelchair friendly" in lowered:
        expansions.append("wheelchair accessible")
    if "open" in lowered and "time" in lowered:
        expansions.append("opening hours")

    if not expansions:
        return query
    return f"{query} {' '.join(expansions)}"


def _cosine_similarity(left: np.ndarray, right: np.ndarray) -> float:
    left_norm = float(np.linalg.norm(left))
    right_norm = float(np.linalg.norm(right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return float(np.dot(left, right) / (left_norm * right_norm))


def _lexical_similarity(query: str, text: str) -> float:
    query_tokens = set(_tokenize(_prepare_query(query)))
    if not query_tokens:
        return 0.0

    document_tokens = set(_tokenize(text))
    intersection = query_tokens & document_tokens
    if not intersection:
        return 0.0

    coverage = len(intersection) / len(query_tokens)
    precision = len(intersection) / len(document_tokens)
    fuzzy = SequenceMatcher(
        None,
        _normalize_text(query),
        _normalize_text(text),
    ).ratio()
    return (0.7 * coverage) + (0.2 * precision) + (0.1 * fuzzy)


def _margin_for(candidates: tuple[MatchCandidate, ...]) -> float:
    if len(candidates) < 2:
        return candidates[0].score if candidates else 0.0
    return candidates[0].score - candidates[1].score


class Matcher(ABC):
    """Contract shared by the local matcher and future LLM matcher."""

    @abstractmethod
    def match(self, query: str, faqs: list[FAQ]) -> MatchResult | None:
        raise NotImplementedError


class LexicalMatcher(Matcher):
    """Simple token-overlap fallback when embeddings are unavailable."""

    def __init__(
        self,
        min_score: float = DEFAULT_LEXICAL_THRESHOLD,
        min_margin: float = DEFAULT_LEXICAL_MARGIN,
    ) -> None:
        self.min_score = min_score
        self.min_margin = min_margin

    def _score(self, query: str, faq: FAQ) -> float:
        return _lexical_similarity(query, build_faq_document(faq))

    def match(self, query: str, faqs: list[FAQ]) -> MatchResult | None:
        if not faqs:
            return None

        candidates = tuple(
            sorted(
                (
                    MatchCandidate(faq=faq, score=self._score(query, faq))
                    for faq in faqs
                ),
                key=lambda candidate: candidate.score,
                reverse=True,
            )[:3]
        )

        if not candidates:
            return None

        margin = _margin_for(candidates)
        if candidates[0].score < self.min_score or margin < self.min_margin:
            return None

        return MatchResult(
            faq=candidates[0].faq,
            score=candidates[0].score,
            margin=margin,
            matcher_name="lexical",
            candidates=candidates,
        )


class SemanticMatcher(Matcher):
    """Sentence-transformers matcher with cached FAQ embeddings."""

    def __init__(
        self,
        model_name: str = MODEL_NAME,
        min_score: float = DEFAULT_MIN_SCORE,
        min_margin: float = DEFAULT_MIN_MARGIN,
        debug: bool = False,
        logger: Callable[[str], None] | None = None,
        model: Any | None = None,
        lexical_fallback: Matcher | None = None,
    ) -> None:
        self.model_name = model_name
        self.min_score = min_score
        self.min_margin = min_margin
        self.debug = debug
        self.logger = logger or (lambda _: None)
        self._model = model
        self._faq_signature: tuple[tuple[int, str, str], ...] | None = None
        self._faq_embeddings: np.ndarray | None = None
        self._fallback = lexical_fallback or LexicalMatcher()
        self._warned_about_fallback = False

    def _log(self, message: str) -> None:
        if self.debug:
            self.logger(message)

    def _load_model(self) -> Any:
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
        return self._model

    def _signature_for(self, faqs: list[FAQ]) -> tuple[tuple[int, str, str], ...]:
        return tuple((faq.id, faq.question, faq.answer) for faq in faqs)

    def _encode_documents(self, model: Any, documents: list[str]) -> np.ndarray:
        if hasattr(model, "encode_document"):
            return np.asarray(model.encode_document(documents, convert_to_numpy=True))
        return np.asarray(model.encode(documents, convert_to_numpy=True))

    def _encode_query(self, model: Any, query: str) -> np.ndarray:
        if hasattr(model, "encode_query"):
            return np.asarray(model.encode_query(query, convert_to_numpy=True))
        return np.asarray(model.encode(query, convert_to_numpy=True))

    def _ensure_embeddings(self, faqs: list[FAQ]) -> None:
        signature = self._signature_for(faqs)
        if self._faq_signature == signature and self._faq_embeddings is not None:
            return

        model = self._load_model()
        documents = [build_faq_document(faq) for faq in faqs]
        self._faq_embeddings = self._encode_documents(model, documents)
        self._faq_signature = signature

    def _rank(self, query: str, query_embedding: np.ndarray, faqs: list[FAQ]) -> tuple[MatchCandidate, ...]:
        assert self._faq_embeddings is not None
        candidates = []
        for faq, embedding in zip(faqs, self._faq_embeddings):
            semantic_score = _cosine_similarity(query_embedding, embedding)
            question_hint = _lexical_similarity(query, faq.question)
            final_score = min(1.0, semantic_score + (QUESTION_HINT_WEIGHT * question_hint))
            candidates.append(MatchCandidate(faq=faq, score=final_score))
        return tuple(sorted(candidates, key=lambda candidate: candidate.score, reverse=True)[:3])

    def _should_reject_specific_query(self, query: str, top_candidate: MatchCandidate) -> bool:
        lowered_query = _normalize_text(query)
        asks_for_specific_event_timing = (
            ("event" in lowered_query or "events" in lowered_query)
            and any(term in lowered_query for term in ("next", "date", "dates", "time", "when"))
        )
        answer_points_elsewhere = "noticeboard for dates" in _normalize_text(top_candidate.faq.answer)
        return asks_for_specific_event_timing and answer_points_elsewhere

    def _emit_debug_scores(self, candidates: tuple[MatchCandidate, ...]) -> None:
        if not self.debug or not candidates:
            return

        debug_parts = [
            f"{candidate.faq.id}:{candidate.score:.3f} {candidate.faq.question}"
            for candidate in candidates
        ]
        self._log("Debug top candidates -> " + " | ".join(debug_parts))

    def _fallback_match(self, query: str, faqs: list[FAQ], exc: Exception) -> MatchResult | None:
        if not self._warned_about_fallback:
            self.logger(
                "Bot: Embedding model unavailable, falling back to lexical matching."
            )
            self._warned_about_fallback = True
        self._log(f"Debug fallback reason -> {exc!r}")

        fallback_result = self._fallback.match(query, faqs)
        if fallback_result is None:
            return None
        return replace(fallback_result, used_fallback=True)

    def match(self, query: str, faqs: list[FAQ]) -> MatchResult | None:
        if not faqs:
            return None

        try:
            self._ensure_embeddings(faqs)
            model = self._load_model()
            prepared_query = _prepare_query(query)
            query_embedding = self._encode_query(model, prepared_query)
            candidates = self._rank(query, query_embedding, faqs)
        except Exception as exc:
            return self._fallback_match(query, faqs, exc)

        if not candidates:
            return None

        self._emit_debug_scores(candidates)
        margin = _margin_for(candidates)
        top_candidate = candidates[0]

        if self._should_reject_specific_query(query, top_candidate):
            self._log("Debug rejection -> top candidate lacked the requested specific detail.")
            return None

        if top_candidate.score < self.min_score or margin < self.min_margin:
            return None

        return MatchResult(
            faq=top_candidate.faq,
            score=top_candidate.score,
            margin=margin,
            matcher_name="semantic",
            candidates=candidates,
        )


class LlmMatcher(Matcher):
    """Future scaling path for retrieval-grounded LLM answering."""

    def match(self, query: str, faqs: list[FAQ]) -> MatchResult | None:
        raise NotImplementedError(
            "LlmMatcher is intentionally not implemented for the main submission. "
            "See the README for the scaling plan."
        )
