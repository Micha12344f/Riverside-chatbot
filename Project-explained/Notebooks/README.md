# Notebooks

Back to the main hub: [../../README.md](../../README.md)

Project overview: [../README.md](../README.md)

This folder contains exploratory notebooks used to inspect the codebase and run fuller end-to-end checks outside the main runtime entrypoints.

## Current notebooks

- `Expanded_codebase.ipynb`
- `Full_E2E_test.ipynb`

## Expectations

These notebooks are for exploration, explanation, and iteration. They are not the deployment entrypoint and they may lag behind the final runtime code if the project evolves.

## Security note

Keep notebooks free of:

- live API invoke URLs
- copied secret values
- AWS credentials
- screenshots or dumps that expose private deployment metadata

If a notebook needs configuration, prefer example values and local-only environment loading.

## See also

- [../Data and requirements/README.md](../Data%20and%20requirements/README.md)
- [../tests/README.md](../tests/README.md)
- [../../AWS-deployed-backend/app/README.md](../../AWS-deployed-backend/app/README.md)
