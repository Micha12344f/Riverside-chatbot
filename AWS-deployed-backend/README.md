# AWS Backend

Back to the main hub: [../README.md](../README.md)

This folder contains the AWS-facing backend structure for the Riverside Books chatbot. The production shape is an AWS Lambda behind API Gateway.

## What lives here

```
AWS-deployed-backend/
├── lambda_handler.py   # HTTP entry point for API Gateway
├── main.py             # local CLI-style smoke entry point
├── app/                # matcher, data-loading, and runtime logic
├── package/            # generated deployment bundle workspace
└── README.md
```

See the runtime internals in [app/README.md](app/README.md).

## Architecture

```
Browser or client
    -> POST /chat {"query": "..."}
API Gateway HTTP API
    -> Lambda proxy integration
Lambda handler
    -> LexicalMatcher against FAQ runtime assets
JSON response
    -> {"answer": "...", "matched": true|false}
```

The Lambda uses the lightweight lexical matcher rather than the semantic matcher so the deployable bundle stays small and does not require heavyweight ML dependencies.

## API contract

### `POST /chat`

Request:

```json
{"query": "What are your opening hours?"}
```

Matched response:

```json
{"answer": "We're open 9am to 6pm Monday to Saturday, and 11am to 4pm on Sundays.", "matched": true}
```

Fallback response:

```json
{"answer": "Sorry, I don't know that one — please ask a member of staff.", "matched": false}
```

Empty-query response:

```json
{"answer": "Please ask a question.", "matched": false}
```

## Security

- Frontend requests should arrive through the Vercel-side `/api/chat` proxy.
- Store the upstream API URL in the Vercel environment variable `RIVERSIDE_BACKEND_URL`.
- Control browser access to Lambda with the `ALLOWED_ORIGINS` environment variable.
- Keep deploy-time values such as API IDs, account IDs, ARNs, bucket names, and console links out of public docs.

## Deployment workflow

The repository already includes a GitHub Actions workflow at [../.github/workflows/deploy-backend-aws.yml](../.github/workflows/deploy-backend-aws.yml).

At a high level it:

1. packages `main.py` and `app/`
2. uploads the bundle as a workflow artifact
3. assumes an AWS role through GitHub OIDC
4. uploads the bundle to an S3 artifact location

### Secret names used by the workflow

- `AWS_ROLE_ARN`
- `AWS_BACKEND_ARTIFACT_BUCKET`
- `ALLOWED_ORIGINS`

## Local testing

Use a placeholder or environment-provided backend URL when documenting commands:

### cURL

```bash
export RIVERSIDE_API_URL="https://<api-id>.execute-api.<region>.amazonaws.com/chat"
curl -X POST "$RIVERSIDE_API_URL" \
  -H "Content-Type: application/json" \
  -d '{"query":"Where are you located?"}'
```

### PowerShell

```powershell
$env:RIVERSIDE_API_URL = "https://<api-id>.execute-api.<region>.amazonaws.com/chat"
$body = '{"query":"Do you host events?"}'
Invoke-RestMethod -Uri $env:RIVERSIDE_API_URL `
  -Method POST -Body $body -ContentType "application/json"
```

### Local frontend smoke test

```powershell
cd ..\Vercel-deployed-frontend
python -m http.server 3000
```

For production website traffic, prefer the Vercel proxy route rather than calling the API Gateway URL directly from browser code.

## Updating the Lambda bundle manually

If you need a local packaging pass:

```powershell
cd AWS-deployed-backend
Remove-Item -Recurse -Force package, lambda-release.zip -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force package | Out-Null
Copy-Item lambda_handler.py package/
Copy-Item -Recurse app package/app
Remove-Item -Recurse package/app/__pycache__ -ErrorAction SilentlyContinue
Compress-Archive -Path package\* -DestinationPath lambda-release.zip -Force
```

The generated `package/` directory and `lambda-release.zip` are build artifacts, not source-of-truth docs or code.

## FAQ knowledge base

The runtime FAQ data lives in `app/runtime_assets/faqs.json`.

To add or change answers:

1. edit the FAQ JSON
2. verify behavior locally
3. redeploy the backend bundle

For the data and matcher details, continue to [app/README.md](app/README.md) and [../Project-explained/README.md](../Project-explained/README.md).
