# Backend App Internals

Back to the main hub: [../../README.md](../../README.md)

See the deployment-facing overview first: [../README.md](../README.md)

This folder contains the source-of-truth chatbot logic used by the backend package.

## Files in this folder

```
app/
├── __init__.py
├── chatbot.py
├── data.py
├── matchers.py
├── models.py
├── requirements.txt
└── runtime_assets/
    └── faqs.json
```

## Module guide

- `data.py`: loads FAQ JSON into dataclasses
- `models.py`: shared data structures such as `FAQ`, `MatchCandidate`, and `MatchResult`
- `matchers.py`: lexical and semantic matching logic
- `chatbot.py`: local CLI orchestration around the semantic matcher
- `runtime_assets/faqs.json`: small fixed FAQ set used by the demo

## Matcher split

The repository uses two different matcher paths depending on where the code runs:

- AWS Lambda path: `LexicalMatcher`
- local CLI/TUI path: `SemanticMatcher`

That split matters because the semantic matcher depends on heavier ML tooling, while the Lambda deploy stays intentionally small and simple.

## Important behavior

### Lexical fallback

`matchers.py` is designed so that semantic matching can fail gracefully and fall back to lexical matching when dependencies are unavailable.

### Query normalization

The matcher expands some common phrasing such as:

- `open` + `time` -> `opening hours`
- `pick up` / `collect` + `online` -> `click and collect`
- `coffee` -> `cafe`

That keeps the FAQ set small while still handling paraphrases reasonably well.

### Confidence rules

The matcher does not only pick the highest score. It also requires:

- a minimum score
- a minimum margin over the next candidate

That is what makes the fallback answer possible when the best match is too weak or too ambiguous.

## Dependencies

`requirements.txt` in this folder is mainly for local development and exploration. The Lambda deployment path intentionally avoids shipping the full semantic stack.

## Security

- This folder shapes the public FAQ response behavior, but deploy-time values stay outside source control.
- Browser access is controlled in `lambda_handler.py`, while the website should call the backend through the frontend proxy.

## See also

- [../../Riverside-books-CLI/README.md](../../Riverside-books-CLI/README.md)
- [../../Project-explained/README.md](../../Project-explained/README.md)
- [../../Project-explained/Data and requirements/README.md](../../Project-explained/Data%20and%20requirements/README.md)
