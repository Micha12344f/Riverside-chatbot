# Notebook Guide

This folder contains notebook files that help explain and inspect the Riverside Books chatbot.

These notebooks are not the main application. They are support material.

## What Is Here

### `riverside_function_breakdown.ipynb`

Purpose:

- explain the chatbot code piece by piece
- keep the language very simple
- make the logic easier to follow for someone who wants a teaching-style walkthrough

Use this notebook when you want to understand:

- what each function does
- why the project is split into separate files
- how the matching flow works in plain English

### `riverside_live_test.ipynb`

Purpose:

- give you an interactive notebook where you can type a question
- show the prepared form of that question
- show the rank table for the closest FAQ matches
- show the final safe answer if one is accepted

Use this notebook when you want to:

- demo the chatbot
- inspect ranking behavior
- understand why a question matched a specific FAQ
- see what happens when the chatbot refuses to answer

## How To Use The Live Test Notebook

The normal flow is:

1. run the setup cell
2. let it check or install `sentence-transformers` if needed
3. run the FAQ loading cell
4. run the matcher setup cell
5. type a question into the input cell
6. run the match cell
7. inspect the rank table

## Why These Notebooks Exist

The core chatbot is intentionally small. That is good for code clarity, but it means some of the matching behavior is easy to miss if you only look at the normal CLI.

The notebooks make that behavior visible by showing:

- question preparation
- candidate ranking
- threshold behavior
- final answer selection

## Important Boundary

These notebooks are useful for explanation and demos, but the main implementation still lives in `src/`.

If you want to change the real application logic, edit:

- `src/matchers.py`
- `src/chatbot.py`
- `src/live_test.py`

not just the notebooks.
