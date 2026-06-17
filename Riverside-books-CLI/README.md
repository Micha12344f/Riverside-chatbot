# CLI and TUI

Back to the main hub: [../README.md](../README.md)

This folder contains the local-first interface for the Riverside chatbot project.

## What lives here

```text
Riverside-books-CLI/
├── main.py
├── pyproject.toml
├── requirements.txt
├── riverside-chatbot.cmd
├── riverside-chatbot.ps1
└── riverside_cli_app/
```

Inside `riverside_cli_app/` you will find:

- `cli.py`: CLI entry behavior
- `tui.py`: Textual app
- `tui.tcss`: Textual styling
- `chatbot.py`: local chatbot loop
- `matchers.py`: local matching logic
- `runtime_assets/faqs.json`: CLI-side FAQ data

## Run locally

```powershell
cd Riverside-books-CLI
pip install -r requirements.txt
python main.py
```

## Why this folder matters

This is the fastest way to run the project locally and the easiest place to inspect the semantic matcher behavior without deploying anything.

## Relationship to the backend

The CLI and the AWS backend are related but not identical:

- the CLI path uses the semantic matcher for richer local behavior
- the Lambda path uses the lexical matcher for lightweight deployment

That split is documented in [../AWS-deployed-backend/app/README.md](../AWS-deployed-backend/app/README.md).

## See also

- [../AWS-deployed-backend/app/README.md](../AWS-deployed-backend/app/README.md)
- [../Project-explained/README.md](../Project-explained/README.md)
