from __future__ import annotations

import argparse
from pathlib import Path

from app.chatbot import main as run_chatbot


def parse_args() -> argparse.Namespace:
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
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(run_chatbot(faq_path=args.faq_path, debug=args.debug))
