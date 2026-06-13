from __future__ import annotations

import json
from pathlib import Path

from .models import FAQ

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FAQS_FILE = PROJECT_ROOT / "faqs.json"


def load_faqs(path: Path | None = None) -> list[FAQ]:
    """Load FAQ entries from disk."""

    faq_path = path or DEFAULT_FAQS_FILE
    with faq_path.open("r", encoding="utf-8") as handle:
        raw_items = json.load(handle)
    return [FAQ(**item) for item in raw_items]
