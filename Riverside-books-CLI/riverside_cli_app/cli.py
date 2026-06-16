from __future__ import annotations

import argparse
from pathlib import Path

from .chatbot import main as run_chatbot
from .tui import run_tui


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Riverside Books FAQ chatbot")
    parser.add_argument(
        "--faq-path",
        type=Path,
        default=None,
        help="Optional path to a faqs.json file.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print matcher diagnostics while answering questions.",
    )
    parser.add_argument(
        "--lexical-only",
        action="store_true",
        help="Skip embeddings and use lexical matching only.",
    )
    parser.add_argument(
        "--plain",
        action="store_true",
        help="Use the plain text CLI instead of the full-screen TUI.",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.plain:
        return run_tui(
            faq_path=args.faq_path,
            debug=args.debug,
            lexical_only=args.lexical_only,
        )
    return run_chatbot(
        faq_path=args.faq_path,
        debug=args.debug,
        lexical_only=args.lexical_only,
    )
