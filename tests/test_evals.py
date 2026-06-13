from __future__ import annotations

import pytest

from src.data import load_faqs
from src.matchers import SemanticMatcher

pytest.importorskip("sentence_transformers")

FAQS = load_faqs()
MATCHER = SemanticMatcher()


@pytest.mark.parametrize(
    ("query", "expected_id"),
    [
        ("what time do you open?", 1),
        ("where's the shop?", 2),
        ("is there somewhere to park?", 7),
        ("can I pick up an online order today?", 12),
        ("can I buy books on your site?", 11),
        ("do you sell vouchers?", 9),
        ("is the shop wheelchair friendly?", 17),
        ("do you have coffee?", 16),
    ],
)
def test_known_questions_map_to_expected_faqs(query: str, expected_id: int) -> None:
    result = MATCHER.match(query, FAQS)
    assert result is not None
    assert result.faq.id == expected_id


@pytest.mark.parametrize(
    "query",
    [
        "what is your phone number?",
        "do you ship internationally?",
        "can I bring my dog into the store?",
        "do you have free wifi?",
        "what date is the next author event?",
    ],
)
def test_unknown_questions_are_rejected(query: str) -> None:
    assert MATCHER.match(query, FAQS) is None
