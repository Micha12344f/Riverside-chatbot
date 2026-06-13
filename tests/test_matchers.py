from __future__ import annotations

import numpy as np

from src.matchers import LlmMatcher, LexicalMatcher, SemanticMatcher, build_faq_document
from src.models import FAQ


class FakeSemanticModel:
    def __init__(self, document_vectors: dict[str, list[float]], query_vectors: dict[str, list[float]]) -> None:
        self.document_vectors = document_vectors
        self.query_vectors = query_vectors
        self.document_calls = 0
        self.query_calls = 0

    def encode_document(self, documents: list[str], convert_to_numpy: bool = True) -> np.ndarray:
        self.document_calls += 1
        return np.asarray([self.document_vectors[document] for document in documents], dtype=float)

    def encode_query(self, query: str, convert_to_numpy: bool = True) -> np.ndarray:
        self.query_calls += 1
        return np.asarray(self.query_vectors[query], dtype=float)


def sample_faqs() -> list[FAQ]:
    return [
        FAQ(id=1, question="What are your opening hours?", answer="We are open 9am to 6pm."),
        FAQ(id=2, question="Is there parking nearby?", answer="There is a public car park nearby."),
        FAQ(id=3, question="Do you offer click and collect?", answer="Yes, usually the same day."),
    ]


def test_semantic_matcher_caches_document_embeddings() -> None:
    faqs = sample_faqs()
    document_vectors = {
        build_faq_document(faqs[0]): [1.0, 0.0],
        build_faq_document(faqs[1]): [0.0, 1.0],
        build_faq_document(faqs[2]): [0.5, 0.5],
    }
    query_vectors = {
        "when are you open?": [1.0, 0.0],
        "where can I park?": [0.0, 1.0],
    }
    model = FakeSemanticModel(document_vectors=document_vectors, query_vectors=query_vectors)
    matcher = SemanticMatcher(model=model)

    first = matcher.match("when are you open?", faqs)
    second = matcher.match("where can I park?", faqs)

    assert first is not None
    assert first.faq.id == 1
    assert second is not None
    assert second.faq.id == 2
    assert model.document_calls == 1
    assert model.query_calls == 2


def test_semantic_matcher_rejects_close_call_when_margin_is_too_small() -> None:
    faqs = sample_faqs()[:2]
    document_vectors = {
        build_faq_document(faqs[0]): [1.0, 0.0],
        build_faq_document(faqs[1]): [0.98, 0.2],
    }
    query_vectors = {
        "tell me your hours": [1.0, 0.0],
    }
    model = FakeSemanticModel(document_vectors=document_vectors, query_vectors=query_vectors)
    matcher = SemanticMatcher(model=model, min_score=0.5, min_margin=0.1)

    assert matcher.match("tell me your hours", faqs) is None


def test_semantic_matcher_uses_lexical_fallback_when_embeddings_fail() -> None:
    faqs = sample_faqs()

    class BrokenModel:
        def encode_document(self, documents: list[str], convert_to_numpy: bool = True) -> np.ndarray:
            raise RuntimeError("model unavailable")

    matcher = SemanticMatcher(model=BrokenModel())
    result = matcher.match("is there somewhere to park?", faqs)

    assert result is not None
    assert result.faq.id == 2
    assert result.matcher_name == "lexical"
    assert result.used_fallback is True


def test_lexical_matcher_rejects_unrelated_questions() -> None:
    result = LexicalMatcher().match("what is your phone number?", sample_faqs())
    assert result is None


def test_llm_matcher_stub_is_explicit() -> None:
    try:
        LlmMatcher().match("hello", sample_faqs())
    except NotImplementedError as exc:
        assert "not implemented" in str(exc).lower()
    else:
        raise AssertionError("Expected LlmMatcher to raise NotImplementedError")
