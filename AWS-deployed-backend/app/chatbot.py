from __future__ import annotations

from pathlib import Path
from typing import Callable

from .data import load_faqs
from .matchers import Matcher, SemanticMatcher

FALLBACK_MESSAGE = "Sorry, I don't know that one — please ask a member of staff."
GOODBYE_MESSAGE = "Goodbye! Thanks for visiting Riverside Books."


def build_matcher(
    *,
    debug: bool = False,
    logger: Callable[[str], None] = print,
) -> Matcher:
    return SemanticMatcher(debug=debug, logger=logger)


def run_cli(
    *,
    faq_path: Path | None = None,
    matcher: Matcher | None = None,
    debug: bool = False,
    input_func: Callable[[str], str] = input,
    output_func: Callable[[str], None] = print,
) -> int:
    faqs = load_faqs(faq_path)
    active_matcher = matcher or build_matcher(debug=debug, logger=output_func)

    output_func("=" * 50)
    output_func("  Welcome to Riverside Books!")
    output_func("  Ask me anything - type 'quit' or 'exit' to leave.")
    output_func("=" * 50)
    output_func(f"  Loaded {len(faqs)} FAQs")
    output_func("=" * 50)

    while True:
        try:
            user_input = input_func("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            output_func(f"\nBot: {GOODBYE_MESSAGE}")
            return 0

        if user_input.lower() in {"quit", "exit"}:
            output_func(f"\nBot: {GOODBYE_MESSAGE}")
            return 0

        if not user_input:
            output_func("Bot: Please ask a question.")
            continue

        result = active_matcher.match(user_input, faqs)
        if result is None:
            output_func(f"Bot: {FALLBACK_MESSAGE}")
            continue

        output_func(f"Bot: {result.faq.answer}")


def main(*, faq_path: Path | None = None, debug: bool = False) -> int:
    return run_cli(faq_path=faq_path, debug=debug)
