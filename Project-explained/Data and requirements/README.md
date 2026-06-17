# Data and Requirements

Back to the main hub: [../../README.md](../../README.md)

Project overview: [../README.md](../README.md)

This folder holds the compact inputs that support the project explanation layer.

## Files

- `.env.example`: example environment file only
- `faqs.json`: FAQ dataset used for experimentation and explanation
- `requirements.txt`: notebook and analysis dependencies

## Security note

`.env.example` should stay an example file only. Do not place real secrets, live API URLs, AWS credentials, or production identifiers in it.

## FAQ data

The FAQ JSON is the backbone of the retrieval demo. It should stay:

- small
- explicit
- grounded in known answers

If you change the FAQ set here, also review the runtime FAQ copies used by:

- [../../AWS-deployed-backend/app/runtime_assets/faqs.json](../../AWS-deployed-backend/app/runtime_assets/faqs.json)
- [../../Riverside-books-CLI/riverside_cli_app/runtime_assets/faqs.json](../../Riverside-books-CLI/riverside_cli_app/runtime_assets/faqs.json)

## See also

- [../Notebooks/README.md](../Notebooks/README.md)
- [../tests/README.md](../tests/README.md)
