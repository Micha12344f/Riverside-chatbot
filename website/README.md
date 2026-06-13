# Website Folder

This folder is present as a scaffold, not as a finished part of the Riverside Books chatbot submission.

The main deliverable for this project is the Python CLI chatbot in the root project and `src/`.

## Current Status

Right now, the `website/` folder should be treated as:

- optional
- incomplete
- not part of the main run path

In other words:

- the chatbot does not need this folder to work
- the tests do not depend on this folder
- the main README and Python code are the real submission

## Why The Folder Exists

This folder likely exists because the original scaffold left space for an optional front end or documentation site.

That is a reasonable future direction, but it was not the best use of time for the core task. The main value of this submission is in:

- matching judgment
- safe fallback behavior
- a clean CLI
- clear testing
- visible ranking logic

## What Is Inside

There are placeholders and scaffold-style files such as:

- `package.json`
- `docusaurus.config.js`
- `babel.config.js`
- `sidebars.js`
- `docs/`
- `src/`
- `static/`

At the moment, these files are not the focus of the project and may be empty or only partially configured.

## Recommendation

If you are reviewing this repository for the chatbot itself:

- read the root `README.md`
- inspect `src/`
- run `python main.py`
- run `python -m src.live_test`

If you later decide to add a front end, this folder is where that work should happen.

## If This Folder Is Expanded Later

A sensible future direction would be:

1. create a tiny interface with one input box
2. show the chatbot answer
3. optionally show the rank table behind a debug toggle
4. reuse the same matching logic from the Python backend or port the same behavior carefully

Until then, treat `website/` as a placeholder rather than a core part of the chatbot.
