from __future__ import annotations

import json
import os
from pathlib import Path

from app.data import load_faqs
from app.matchers import LexicalMatcher

# Load FAQs once at cold start
_APP_ROOT = Path(__file__).resolve().parent
_FAQS = load_faqs(_APP_ROOT / "app" / "runtime_assets" / "faqs.json")
_MATCHER = LexicalMatcher()

FALLBACK_MESSAGE = "Sorry, I don't know that one — please ask a member of staff."


def lambda_handler(event: dict, context: object) -> dict:
    """API Gateway HTTP API v2 handler.

    Expects: {"query": "user question"}
    Returns: {"answer": "...", "matched": true/false}
    """
    # Handle CORS preflight
    if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return _response(200, {"ok": True})

    # Parse the incoming request
    body = event.get("body", "{}")
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            body = {}

    query = (body.get("query") or "").strip()
    if not query:
        return _response(400, {"answer": "Please ask a question.", "matched": False})

    # Match against FAQs
    result = _MATCHER.match(query, _FAQS)
    if result is None:
        return _response(200, {"answer": FALLBACK_MESSAGE, "matched": False})

    return _response(200, {"answer": result.faq.answer, "matched": True})


def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
        },
        "body": json.dumps(body),
    }
