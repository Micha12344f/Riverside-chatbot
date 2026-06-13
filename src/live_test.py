from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

from .data import load_faqs
from .matchers import SemanticMatcher, _prepare_query


def ensure_embedding_package() -> bool:
    """Install sentence-transformers into the current environment if needed."""

    if importlib.util.find_spec("sentence_transformers") is not None:
        return True

    print("Embedding package status:")
    print("sentence_transformers is NOT installed in this Python environment.")
    print("Installing it now...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "sentence-transformers"])
    return importlib.util.find_spec("sentence_transformers") is not None


def print_rank_table(result) -> None:
    print("Rank table (closest matches first):")
    print(f"{'Rank':<6} {'FAQ ID':<8} {'Score':<8} Question")
    print("-" * 80)
    for index, candidate in enumerate(result.candidates, start=1):
        print(f"{index:<6} {candidate.faq.id:<8} {candidate.score:<8.3f} {candidate.faq.question}")


def show_question_result(question: str, matcher: SemanticMatcher, faqs) -> object | None:
    print("User question:")
    print(question)
    print("Prepared version used by the matcher:")
    print(_prepare_query(question))
    print()

    result = matcher.match(question, faqs)

    original_min_score = matcher.min_score
    original_min_margin = matcher.min_margin
    original_debug = matcher.debug
    matcher.min_score = 0.0
    matcher.min_margin = 0.0
    matcher.debug = False
    full_result = matcher.match(question, faqs)
    matcher.min_score = original_min_score
    matcher.min_margin = original_min_margin
    matcher.debug = original_debug

    if full_result is None:
        print("No candidates found.")
        return result

    print_rank_table(full_result)
    print()

    if result is None:
        print("No safe match was found (score or margin below threshold).")
        print("Sorry I cannot confidently answer your question. Shall I connect you to a member of staff?")
        return None

    print("Winning FAQ id:")
    print(result.faq.id)
    print("Winning FAQ question:")
    print(result.faq.question)
    print("Answer shown to the user:")
    print(result.faq.answer)
    print("Final score:")
    print(round(result.score, 3))
    print("Gap over second place:")
    print(round(result.margin, 3))
    print()
    print(result.faq.answer)
    return result


def run_live_test(*, faq_path: Path | None = None) -> int:
    print("Project root found:")
    project_root = Path(__file__).resolve().parent.parent
    print(project_root)
    print()
    print("Python executable:")
    print(sys.executable)
    print()

    embeddings_available = ensure_embedding_package()
    print()
    if embeddings_available:
        print("Embedding package status:")
        print("sentence_transformers is installed. The semantic matcher can run.")
    else:
        print("Embedding package status:")
        print("sentence_transformers still is not available. The chatbot may fall back to lexical matching.")
    print()

    faqs = load_faqs(faq_path)
    print(f"Loaded {len(faqs)} FAQs")
    print("First FAQ question:")
    print(faqs[0].question)
    print("First FAQ answer:")
    print(faqs[0].answer)
    print()

    matcher = SemanticMatcher(debug=True, logger=print)
    print("Matcher created:")
    print(type(matcher).__name__)
    print()
    if embeddings_available:
        print("Mode:")
        print("Semantic matcher is ready. It should use embeddings.")
        print("Loading the embedding model now so later questions stay cleaner...")
        matcher._load_model()
        matcher._ensure_embeddings(faqs)
        print("Embedding model loaded and FAQ embeddings are ready.")
    else:
        print("Mode:")
        print("Embeddings are missing, so the chatbot will fall back to lexical matching.")
    print()

    while True:
        try:
            query = input("Type your Riverside Books question here: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return 0

        if query.lower() in {"quit", "exit"}:
            print("Goodbye!")
            return 0

        if not query:
            print("Please type a question, or type 'quit' to leave.")
            print()
            continue

        show_question_result(query, matcher, faqs)
        print()


def main() -> int:
    return run_live_test()


if __name__ == "__main__":
    raise SystemExit(main())
