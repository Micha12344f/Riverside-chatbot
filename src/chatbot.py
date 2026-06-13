# src/chatbot.py
# Entry-point for the Riverside Books FAQ chatbot.
# Handles user input, loads FAQ data, and prints the best-matched answer.

import json
from pathlib import Path

# Import our local modules from the same package
from .types import FAQ          # dataclass that holds question + answer
from .matcher import find_best_match  # semantic-similarity search function

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Resolve the path to faqs.json relative to this file's location.
# We go up one directory (src/) into the project root where faqs.json lives.
FAQS_FILE = Path(__file__).parent.parent / "faqs.json"


def load_faqs() -> list[FAQ]:
    """
    Load FAQ entries from the JSON file on disk.

    Returns:
        A list of FAQ objects, each containing a 'question' and 'answer'.
    """
    with open(FAQS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)               # Parse raw JSON into Python dicts/lists
    # Convert each dictionary into a strongly-typed FAQ dataclass instance
    return [FAQ(**item) for item in data]


def main() -> None:
    """
    Run the interactive command-line chatbot loop.

    Steps:
      1. Display a welcome banner.
      2. Load FAQ data from disk.
      3. Repeatedly prompt the user for input.
      4. Use semantic search to find the best matching FAQ.
      5. Print the answer or a fallback message.
    """
    # ---- Welcome banner ----------------------------------------------------
    print("=" * 50)
    print("  Welcome to Riverside Books!")
    print("  Ask me anything — type 'quit' or 'exit' to leave.")
    print("=" * 50)

    # ---- Load knowledge base -----------------------------------------------
    faqs = load_faqs()                    # Read and parse faqs.json
    print(f"  Loaded {len(faqs)} FAQs")   # Confirm how many entries we have
    print("=" * 50)

    # ---- Main interaction loop -----------------------------------------------
    while True:
        # Prompt the user and strip surrounding whitespace
        user_input = input("\nYou: ").strip()

        # ---- Exit commands -------------------------------------------------
        # Allow the user to leave gracefully with 'quit' or 'exit'
        if user_input.lower() in ("quit", "exit"):
            print("\nBot: Goodbye! Thanks for visiting Riverside Books.")
            break                         # Break out of the while loop

        # ---- Empty input guard ---------------------------------------------
        # If the user hits Enter without typing anything, ask again politely
        if not user_input:
            print("Bot: Please ask a question.")
            continue                      # Skip to the next loop iteration

        # ---- Semantic matching ---------------------------------------------
        # Pass the user's question and the full FAQ list to the matcher.
        # It returns a MatchResult (or None if nothing is close enough).
        result = find_best_match(user_input, faqs)

        # ---- Output answer or fallback -------------------------------------
        if result:
            # A good match was found — display the stored answer
            print(f"Bot: {result.faq.answer}")
        else:
            # Similarity fell below the confidence threshold
            print("Bot: Sorry, I don't know that one — please ask a member of staff.")


# ---------------------------------------------------------------------------
# Script entry guard
# ---------------------------------------------------------------------------
# Ensures main() only runs when this file is executed directly,
# not when it is imported as a module by another script.
if __name__ == "__main__":
    main()