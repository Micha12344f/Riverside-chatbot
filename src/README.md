# Source Code Guide

This folder contains the real Python implementation for the Riverside Books chatbot.

If the root `README.md` explains the project at a high level, this file explains how the code inside `src/` is organized and how the parts fit together.

## What Lives In `src/`

Current Python modules:

- `__init__.py`
  - package exports
- `chatbot.py`
  - the main command-line chat loop
- `data.py`
  - loading FAQs from disk
- `live_test.py`
  - a more visible interactive runner with ranked table output
- `matchers.py`
  - semantic retrieval, lexical fallback, scoring helpers, and the future LLM stub
- `models.py`
  - shared data objects

## The Main Flow

The normal production-style flow is:

1. `main.py` calls into `src.chatbot`
2. `src.chatbot` loads FAQs through `src.data`
3. `src.chatbot` builds a matcher through `src.matchers`
4. the matcher ranks the FAQs
5. the CLI prints a safe answer or a safe fallback

The inspection-friendly flow is:

1. `python -m src.live_test`
2. environment check
3. optional package install
4. FAQ load
5. matcher warm-up
6. user enters question
7. ranked table is shown

## File-By-File Walkthrough

### `models.py`

This file contains the shared data shapes:

- `FAQ`
  - one FAQ row from `faqs.json`
- `MatchCandidate`
  - one possible ranked answer
- `MatchResult`
  - the accepted result returned to the CLI

This keeps the rest of the code cleaner because the same shapes are reused in matching, CLI code, and tests.

### `data.py`

This file is small on purpose.

Its only real job is to:

- find the FAQ file
- load the JSON
- convert each raw item into an `FAQ` object

Keeping data loading separate makes the rest of the code easier to test.

### `matchers.py`

This is the heart of the project.

It contains:

- helper functions for cleaning and preparing text
- helper functions for lexical comparison
- the abstract matcher interface
- the lexical fallback matcher
- the semantic matcher
- the future `LlmMatcher` stub

Important ideas in this file:

- FAQ question and answer are embedded together
- semantic score is the main signal
- a small question-fit bonus helps short natural phrasing
- score and margin thresholds protect against weak guesses
- a backup lexical matcher prevents crashes when embeddings are unavailable

### `chatbot.py`

This file contains the standard command-line loop.

It is intentionally simple:

- print welcome text
- read user input
- stop on `quit` or `exit`
- reject empty input politely
- call the matcher
- print the answer or fallback message

This keeps the production path neat and easy to review.

### `live_test.py`

This file is the notebook-like runner turned into plain Python.

It is more verbose than `chatbot.py` on purpose.

It is designed to help with:

- debugging
- demos
- explaining ranking behavior
- seeing why one FAQ won over another

Key difference from the main CLI:

- it always shows the rank table for the nearest candidates
- even if the final safe threshold says “do not answer”

That makes it useful for inspecting borderline questions.

## How The Matchers Relate To Each Other

There are three matcher concepts in the code:

### `Matcher`

This is the common interface.

It means every matcher should expose:

- `match(question, faqs) -> result or None`

### `SemanticMatcher`

This is the main implementation.

It is the real answer to the assignment.

It:

- loads the sentence-transformers model
- encodes FAQs once
- encodes user questions
- ranks results
- applies threshold checks
- falls back safely if the model stack is unavailable

### `LexicalMatcher`

This is the backup plan.

It is simpler and weaker, but still useful.

It:

- compares important words
- uses a few alias expansions
- avoids answering when confidence is low

### `LlmMatcher`

This is intentionally not implemented.

It exists to show where a future scaled architecture would plug in.

## Why The Source Code Is Split This Way

The split is mainly about clarity:

- data loading stays separate from matching
- matching stays separate from terminal I/O
- tests can import the matching logic directly
- the live test view can reuse the core matcher without duplicating the actual model logic

## Common Entry Points

Normal chatbot:

```bash
python main.py
```

Interactive rank-table runner:

```bash
python -m src.live_test
```

## If You Want To Modify The Behavior

Here is the simplest map:

- want to change the fallback sentence:
  - edit `src/chatbot.py`
- want to change threshold behavior:
  - edit constants or logic in `src/matchers.py`
- want to add more notebook-like interactivity:
  - edit `src/live_test.py`
- want to change the FAQ data:
  - edit `faqs.json`

## Relationship To The Notebooks

The notebook files in `src/Jupyter Notebooks/` are not separate implementations of the matcher.

They are:

- an explanation layer
- a teaching layer
- an inspection layer

The real reusable code is still in `src/`.
