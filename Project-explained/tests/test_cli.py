from __future__ import annotations

import json
from pathlib import Path

from app.chatbot import run_cli
from app.models import FAQ, MatchResult


class StubMatcher:
    def __init__(self, result: MatchResult | None) -> None:
        self.result = result
        self.calls: list[str] = []

    def match(self, query: str, faqs: list[FAQ]) -> MatchResult | None:
        self.calls.append(query)
        return self.result


def write_temp_faqs(tmp_path: Path) -> Path:
    faq_path = tmp_path / "faqs.json"
    faq_path.write_text(
        json.dumps(
            [
                {
                    "id": 1,
                    "question": "What are your opening hours?",
                    "answer": "We are open 9am to 6pm.",
                }
            ]
        ),
        encoding="utf-8",
    )
    return faq_path


def test_run_cli_answers_then_exits(tmp_path: Path) -> None:
    faq_path = write_temp_faqs(tmp_path)
    faq = FAQ(id=1, question="What are your opening hours?", answer="We are open 9am to 6pm.")
    matcher = StubMatcher(
        MatchResult(faq=faq, score=0.9, margin=0.2, matcher_name="semantic")
    )
    prompts = iter(["hours?", "exit"])
    output: list[str] = []

    exit_code = run_cli(
        faq_path=faq_path,
        matcher=matcher,
        input_func=lambda _: next(prompts),
        output_func=output.append,
    )

    assert exit_code == 0
    assert matcher.calls == ["hours?"]
    assert any("Loaded 1 FAQs" in line for line in output)
    assert "Bot: We are open 9am to 6pm." in output
    assert output[-1].endswith("Goodbye! Thanks for visiting Riverside Books.")


def test_run_cli_handles_empty_and_unknown_question(tmp_path: Path) -> None:
    faq_path = write_temp_faqs(tmp_path)
    matcher = StubMatcher(None)
    prompts = iter(["", "phone number?", "quit"])
    output: list[str] = []

    exit_code = run_cli(
        faq_path=faq_path,
        matcher=matcher,
        input_func=lambda _: next(prompts),
        output_func=output.append,
    )

    assert exit_code == 0
    assert matcher.calls == ["phone number?"]
    assert "Bot: Please ask a question." in output
    assert "Bot: Sorry, I don't know that one — please ask a member of staff." in output
