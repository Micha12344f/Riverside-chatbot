# src/matcher.py
# Semantic-search engine for the Riverside Books FAQ chatbot.
# Uses sentence-transformers to turn text into dense vectors,
# then finds the FAQ whose question vector is closest to the user's query.

import numpy as np
from sentence_transformers import SentenceTransformer

from .types import FAQ, MatchResult

# ---------------------------------------------------------------------------
# Model configuration
# ---------------------------------------------------------------------------
# all-MiniLM-L6-v2 is a small, fast transformer that produces 384-dimensional
# embeddings. It runs entirely on CPU and is ~80 MB to download.
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Similarity threshold: anything below this is considered "no match".
# 0.6 is a sensible starting point; tune it if you get too many false positives.
SIMILARITY_THRESHOLD = 0.6

# Lazy-load the model once and reuse it (avoids reloading on every call).
_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    """
    Return a cached SentenceTransformer instance.

    The model is downloaded on first use and kept in memory for the lifetime
    of the process, which keeps response times fast.
    """
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Compute the cosine similarity between two 1-D vectors.

    Cosine similarity measures the cosine of the angle between vectors,
    ignoring their magnitude. Range: -1 (opposite) to +1 (identical).
    For text embeddings we typically see 0.0 – 1.0.
    """
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def find_best_match(query: str, faqs: list[FAQ]) -> MatchResult | None:
    """
    Find the FAQ entry whose question is most similar to the user's query.

    Args:
        query: The raw text typed by the user.
        faqs:  A list of FAQ objects loaded from faqs.json.

    Returns:
        A MatchResult containing the best FAQ and its similarity score,
        or None if no FAQ meets the confidence threshold.
    """
    # Edge case: empty knowledge base
    if not faqs:
        return None

    model = _get_model()

    # Encode the user's question into a dense vector
    query_embedding = model.encode(query, convert_to_numpy=True)

    # Extract the canonical questions from every FAQ and batch-encode them.
    # Batch encoding is much faster than encoding one-by-one.
    questions = [faq.question for faq in faqs]
    faq_embeddings = model.encode(questions, convert_to_numpy=True)

    # Compare the query vector against every FAQ vector
    best_index = 0
    best_score = _cosine_similarity(query_embedding, faq_embeddings[0])

    for i in range(1, len(faq_embeddings)):
        score = _cosine_similarity(query_embedding, faq_embeddings[i])
        if score > best_score:
            best_score = score
            best_index = i

    # Only return a result if the top match is confident enough
    if best_score >= SIMILARITY_THRESHOLD:
        return MatchResult(faq=faqs[best_index], similarity=best_score)

    return None