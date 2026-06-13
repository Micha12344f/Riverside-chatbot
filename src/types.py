# src/types.py
# Shared data structures for the Riverside Books FAQ chatbot.
# Keeping types in one place makes the rest of the code easier to read and test.

from dataclasses import dataclass


@dataclass
class FAQ:
    """
    Represents a single FAQ entry.

    Attributes:
        question: The canonical question text (e.g. "What are your opening hours?").
        answer:   The official answer shown to the user.
    """
    question: str
    answer: str


@dataclass
class MatchResult:
    """
    Holds the outcome of a semantic similarity search.

    Attributes:
        faq:        The best-matching FAQ object.
        similarity: Cosine-similarity score between 0.0 and 1.0 (higher is better).
    """
    faq: FAQ
    similarity: float