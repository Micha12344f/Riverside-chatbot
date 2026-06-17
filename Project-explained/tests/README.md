# Tests

Back to the main hub: [../../README.md](../../README.md)

Project overview: [../README.md](../README.md)

This folder contains focused tests around the matching behavior and CLI flow.

## Files

- `test_matchers.py`: matcher behavior and confidence rules
- `test_evals.py`: evaluation-style checks
- `test_cli.py`: CLI-level behavior
- `conftest.py`: shared pytest fixtures and helpers

## Running tests

From the repository root:

```powershell
pytest Project-explained/tests
```

Or run a narrower slice:

```powershell
pytest Project-explained/tests/test_matchers.py
```

## Why this folder exists

The runtime code is intentionally simple, so the tests help protect the most important behavior:

- the right FAQ should be returned for strong matches
- weak or ambiguous matches should be rejected
- the user should see the fallback answer when confidence is too low

## See also

- [../Data and requirements/README.md](../Data%20and%20requirements/README.md)
- [../../AWS-deployed-backend/app/README.md](../../AWS-deployed-backend/app/README.md)
