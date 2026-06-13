# Test Guide

This folder contains the automated tests for the Riverside Books chatbot.

The tests are small, but they are chosen to show the most important decisions in the project.

## How To Run The Tests

From the project root:

```bash
pytest
```

## What The Tests Are Trying To Prove

The tests are mainly checking four things:

- the chatbot runs
- the semantic matcher behaves sensibly
- the fallback matcher behaves safely
- clearly unrelated questions are rejected

## Test Files

### `test_cli.py`

This file checks the command-line flow.

It tests things like:

- welcome and exit behavior
- empty input handling
- known answer handling
- fallback message handling

### `test_matchers.py`

This file checks the matcher internals.

It covers things like:

- FAQ embeddings are cached instead of recomputed every time
- close, unsafe matches can be rejected
- lexical fallback is used if the semantic model fails
- the `LlmMatcher` placeholder clearly says it is not implemented

### `test_evals.py`

This file acts like a tiny evaluation set.

It checks:

- a small number of paraphrases that should match correctly
- a small number of questions that should be rejected

This is not meant to be a production-grade benchmark. It is a lightweight “is the behavior roughly sensible?” safety net.

## Why The Tests Are Small

This project is a short take-home task, not a large production system.

The tests are intentionally compact because the goal is to show:

- good judgment
- clear failure handling
- enough automated coverage to make the behavior trustworthy

without drowning the repository in test scaffolding.
