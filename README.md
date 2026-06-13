# Riverside Books Chatbot

This repository contains a small but deliberately thoughtful FAQ chatbot for the fictional independent bookshop **Riverside Books**. The core deliverable is a command-line chatbot that answers questions from a fixed FAQ file without relying on a hosted model or an API key.

The project is built around one idea:

- for a tiny, closed set of 20 FAQs, a local semantic retriever is a better default than an LLM

That choice keeps the project:

- cheap to run
- easy to explain
- easy to test
- much less likely to hallucinate

The repository also contains notebook-based teaching material and an interactive inspection tool so the matching logic is visible instead of hidden.

## What Is In This Repository

At a high level, the repository has five main parts:

- `main.py`
  - small command-line entrypoint for the production-style chatbot
- `src/`
  - the real Python code: FAQ loading, matching logic, CLI logic, and the live test helper
- `tests/`
  - automated checks for matching, CLI flow, fallback behavior, and evaluation cases
- `src/Jupyter Notebooks/`
  - notebooks for explanation and interactive exploration
- `website/`
  - a website scaffold that is present in the repository but not used by the main solution

## Quick Start

If you just want to run the chatbot:

```bash
python -m pip install -r requirements.txt
python main.py
```

If you want the more educational, table-based interactive flow:

```bash
python -m src.live_test
```

If you want to run tests:

```bash
pytest
```

## Recommended Run Order

If you are opening this repository for the first time, the easiest order is:

1. Read this root README.
2. Run `python main.py` once.
3. Run `python -m src.live_test` once.
4. Open `src/Jupyter Notebooks/riverside_live_test.ipynb`.
5. Read `src/README.md` if you want the code walkthrough.
6. Read `tests/README.md` if you want to understand the test strategy.

## Why Python Was The Right Choice Here

The original brief said the team works mainly in Node and TypeScript, but for this exact problem Python is the cleaner tool.

Why:

- the `sentence-transformers` library is mature and straightforward in Python
- the local embedding workflow is simpler in Python than in Node
- the project already contained a partial Python scaffold
- the time-box favored finishing a strong solution over changing stacks

This means the submission optimizes for:

- correctness
- clarity
- speed of implementation
- low setup friction for someone reviewing the repository

## What The Bot Actually Does

The chatbot reads FAQ entries from `faqs.json`. Each entry has:

- an `id`
- a `question`
- an `answer`

The bot then:

1. loads those FAQs into Python objects
2. turns each FAQ into a searchable text block
3. creates embeddings for those FAQ blocks once
4. turns the user question into an embedding
5. compares the user question against every FAQ
6. ranks the FAQs from best to worst
7. answers only if the top match looks safe enough

If the top match does not look safe enough, the bot declines to answer and says:

`Sorry, I don't know that one — please ask a member of staff.`

## Matching Strategy

The main matcher uses the model:

- `sentence-transformers/multi-qa-MiniLM-L6-cos-v1`

Each FAQ is embedded as:

```text
Question: ...
Answer: ...
```

That is important because many user questions are short or casual. Sometimes the FAQ answer contains useful wording that is not present in the FAQ question.

Example idea:

- user asks: `where's the shop?`
- location-related clues appear in the FAQ answer as well as the question

The matcher also adds a small question-fit bonus after the main semantic score. That helps short everyday phrasing land on the FAQ whose question most closely matches what the user seems to mean.

## Safety Rules

The bot does not answer every time it sees something “sort of close”.

It uses two safety checks:

- the best match must clear a minimum score
- the best match must be clearly ahead of second place

This is important because a chatbot that refuses sometimes is often better than a chatbot that sounds confident and gives the wrong answer.

There is also a special rejection rule for very specific event-date questions. The FAQ data only says to check the noticeboard, so the bot is designed not to pretend it knows the next exact event date.

## Fallback Mode

If the embedding model cannot load, the bot does not crash. It falls back to a simpler lexical matcher.

That fallback matcher:

- compares important words
- removes common filler words
- adds a few helpful word aliases
- still uses safety thresholds

This is weaker than the semantic matcher, but it is much better than a hard crash in a fresh environment.

## Why This Approach Makes Sense For 20 FAQs

For a tiny closed FAQ file, this local retrieval approach is a good default because it is:

- inexpensive
- fast after warm-up
- deterministic
- grounded in the source answers
- easy to debug
- easy to test

An LLM could answer some questions well, but it would also add:

- API cost
- extra latency
- prompt design complexity
- more failure modes
- a higher chance of fluent wrong answers

That tradeoff is usually not worth it for 20 fixed FAQ entries.

## How To Run The Main CLI

From the project root:

```bash
python main.py
```

Optional flags:

```bash
python main.py --debug
python main.py --faq-path ./faqs.json
```

What the flags mean:

- `--debug`
  - prints candidate ranking information while matching
- `--faq-path`
  - lets you point the chatbot at a different FAQ file

## How To Run The Interactive Live Test

The repository includes a second interactive runner designed for visibility rather than minimalism:

```bash
python -m src.live_test
```

This runner:

- prints environment information
- checks whether the embedding package exists
- installs it if needed
- warms the model early so the later question step is cleaner
- asks you for a question
- prints a rank table of the best candidates
- prints the winning answer only if the safe threshold is met

This mirrors what the notebook demo is doing and is useful when you want to inspect the ranking behavior instead of only seeing the final answer.

## Notebook Guide

There are two notebook files in `src/Jupyter Notebooks/`:

- `riverside_function_breakdown.ipynb`
  - a teaching notebook that explains the code in very plain English
- `riverside_live_test.ipynb`
  - a small interactive notebook that lets you type a question and inspect the ranking table

If you want the notebook tour, start with:

- `src/Jupyter Notebooks/riverside_live_test.ipynb`

If you want the code explanation, open:

- `src/Jupyter Notebooks/riverside_function_breakdown.ipynb`

## Example CLI Interaction

Example:

```text
You: when can I come in?
Bot: We're open 9am to 6pm Monday to Saturday, and 11am to 4pm on Sundays.

You: what is your phone number?
Bot: Sorry, I don't know that one — please ask a member of staff.
```

Example from the live test view:

```text
User question:
where's the shop?

Rank table:
Rank   FAQ ID   Score    Question
--------------------------------------------------------------------------------
1      2        0.551    Where are you located?
2      7        0.480    Is there parking nearby?
3      17       0.418    Is the shop wheelchair accessible?
```

## Installation Notes

Basic installation:

```bash
python -m pip install -r requirements.txt
```

Packages currently listed:

- `numpy`
- `sentence-transformers`
- `pytest`

First-run note:

- the first semantic run may download the model from Hugging Face

If the model or package cannot be loaded:

- the CLI still works in lexical fallback mode
- the live test runner tries to install `sentence-transformers` automatically

## File Guide

Important files:

- `main.py`
  - root entrypoint for the production-style CLI
- `faqs.json`
  - the knowledge base
- `requirements.txt`
  - Python dependencies
- `src/chatbot.py`
  - the main CLI loop
- `src/data.py`
  - FAQ loading
- `src/matchers.py`
  - local semantic matching, lexical fallback, and the LLM stub
- `src/models.py`
  - data structures used across the app
- `src/live_test.py`
  - notebook-style live inspection runner
- `tests/`
  - automated tests

## Testing

Run all tests:

```bash
pytest
```

What the tests cover:

- FAQ loading and CLI flow
- semantic matcher caching behavior
- safety rejection behavior
- lexical fallback behavior
- expected paraphrase matches
- expected no-match cases
- the intentionally unimplemented `LlmMatcher`

The evaluation tests are intentionally small. They are there to show judgment, not to pretend this repository contains a full production evaluation suite.

## Tradeoffs

Things this project does well:

- stays grounded in the provided FAQ answers
- avoids API dependency in the main path
- makes ranking behavior inspectable
- handles missing-model conditions gracefully
- keeps the code short enough to reason about quickly

Things this project does not try to do yet:

- answer from multiple sources
- maintain chat memory
- rewrite answers in a friendly prose style
- support live content editing by non-engineers
- provide analytics, tracing, or production observability

## How I Would Scale This Beyond 20 FAQs

The local semantic matcher is the right default now, but I would not keep the architecture frozen forever.

I would move toward a retrieval-first LLM setup when:

- the FAQ set becomes much larger
- answers overlap heavily
- answers need synthesis from multiple documents
- the team wants experimentation, analytics, or better observability

### Scaled Architecture

The scaling path I would choose is:

1. keep retrieval as the first step
2. retrieve the top few candidates
3. return a stored answer directly when the winner is obvious
4. call an LLM only when the question is ambiguous or needs synthesis
5. still refuse to answer when the evidence is weak

### Why Retrieval First Still Matters

Even in the LLM future version, retrieval should remain first because it:

- keeps answers grounded
- reduces hallucination risk
- reduces prompt size
- lowers cost
- gives clearer debugging signals

### Plausible Future Modes

- retrieval + LLM reranker
  - good when final answers should remain canonical stored answers
- retrieval-augmented generation
  - good when several documents must be combined
- hybrid routing
  - good when cheap local retrieval should answer easy questions and the LLM should only handle the hard ones

### Future LLM Contract

The `LlmMatcher` placeholder in this repository exists to show where that future work would fit.

The future return shape should include things like:

- chosen FAQ id
- confidence label
- `no_match`
- optional internal reasoning for logs only

## Why There Is A Website Folder

The `website/` folder exists as a scaffold, not as a finished part of the submission.

It is currently not part of the main chatbot path and should be treated as future-facing or optional.

See `website/README.md` for details.

## Extra Documentation In This Repo

This repository now includes several README files on purpose:

- `README.md`
  - top-level project overview
- `src/README.md`
  - source-code walkthrough
- `src/Jupyter Notebooks/README.md`
  - notebook guide
- `tests/README.md`
  - testing guide
- `website/README.md`
  - website scaffold notes
- `assets/README.md`
  - asset-folder notes

That may be more documentation than a tiny task strictly needs, but it makes the repository easier to review quickly and easier to maintain later.
