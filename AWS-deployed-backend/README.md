# AWS Backend Deployment

Riverside Books FAQ chatbot — deployed as **AWS Lambda + API Gateway HTTP API**.

## Architecture

```
User Browser (Vercel frontend)
        │
        │ POST /chat {"query": "..."}
        ▼
API Gateway HTTP API (dqcxdduwwj)
  https://dqcxdduwwj.execute-api.us-east-1.amazonaws.com/chat
        │
        │ Lambda proxy integration (v2 payload)
        ▼
Lambda: riverside-chatbot
  Python 3.11 | 256 MB | 30 s timeout
  Handler: lambda_handler.lambda_handler
        │
        │ LexicalMatcher (token overlap + fuzzy string matching)
        ▼
Response: {"answer": "...", "matched": true|false}
```

## Live Resources

| Resource | ID / ARN | Console Link |
|----------|----------|-------------|
| **Lambda** | `riverside-chatbot` | [Lambda console](https://us-east-1.console.aws.amazon.com/lambda/home?region=us-east-1#/functions/riverside-chatbot) |
| **API Gateway** | `dqcxdduwwj` | [API Gateway console](https://us-east-1.console.aws.amazon.com/apigateway/main/apis/dqcxdduwwj?region=us-east-1) |
| **Invoke URL** | `https://dqcxdduwwj.execute-api.us-east-1.amazonaws.com/chat` | — |
| **IAM Role (Lambda)** | `riverside-lambda-exec` | [IAM console](https://us-east-1.console.aws.amazon.com/iam/home?region=us-east-1#/roles/riverside-lambda-exec) |
| **IAM Role (GitHub)** | `github-riverside-chatbot-deploy` | [IAM console](https://us-east-1.console.aws.amazon.com/iam/home?region=us-east-1#/roles/github-riverside-chatbot-deploy) |
| **S3 Artifacts** | `riverside-chatbot-artifacts-459100131320` | [S3 console](https://s3.console.aws.amazon.com/s3/buckets/riverside-chatbot-artifacts-459100131320?region=us-east-1) |
| **CloudWatch Logs** | `/aws/lambda/riverside-chatbot` | [Logs console](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups/log-group/$252Faws$252Flambda$252Friverside-chatbot) |

## API Reference

### `POST /chat`

**Request:**
```json
{"query": "What are your opening hours?"}
```

**Response (matched):**
```json
{"answer": "We're open 9am to 6pm Monday to Saturday, and 11am to 4pm on Sundays.", "matched": true}
```

**Response (no match):**
```json
{"answer": "Sorry, I don't know that one — please ask a member of staff.", "matched": false}
```

**Response (empty query):**
```json
HTTP 400
{"answer": "Please ask a question.", "matched": false}
```

CORS headers are included on all responses (`Access-Control-Allow-Origin: *`).

## Directory Layout

```
AWS-deployed-backend/
├── lambda_handler.py      # Lambda entry point (HTTP API v2 handler)
├── main.py                # CLI entry point (for local dev / smoke tests)
├── app/
│   ├── __init__.py        # Public API surface
│   ├── chatbot.py         # CLI loop + matcher orchestration
│   ├── data.py            # FAQ loader (JSON → FAQ dataclasses)
│   ├── matchers.py        # LexicalMatcher, SemanticMatcher, LlmMatcher
│   ├── models.py          # FAQ, MatchCandidate, MatchResult dataclasses
│   ├── requirements.txt   # numpy, sentence-transformers, pytest
│   └── runtime_assets/
│       └── faqs.json      # FAQ knowledge base (6 entries)
└── README.md
```

## Matcher Strategy

The Lambda uses **LexicalMatcher** — a pure-Python token-overlap matcher with fuzzy string comparison. It requires no ML dependencies, keeping the Lambda zip under 8 KB.

| Matcher | Dependencies | Lambda Size | Used In |
|---------|-------------|-------------|---------|
| `LexicalMatcher` | stdlib only | ~8 KB | **Lambda (production)** |
| `SemanticMatcher` | numpy, sentence-transformers, PyTorch | ~2.9 GB | CLI / local dev |
| `LlmMatcher` | not implemented | — | Future scaling path |

The `numpy` import in `matchers.py` is guarded with a `try/except ImportError` so the module loads cleanly in Lambda without numpy installed.

## GitHub Actions Workflow

`.github/workflows/deploy-backend-aws.yml`:

1. **package-backend** — Installs deps, bundles `main.py` + `app/` into `backend-release.zip`, uploads as artifact
2. **publish-bundle-to-aws** — Downloads artifact, assumes IAM role via GitHub OIDC, uploads zip to S3

Triggered on pushes to `main` touching `AWS-deployed-backend/**` or the workflow file itself.

### Required GitHub Secrets

| Secret | Value | Purpose |
|--------|-------|---------|
| `AWS_ROLE_ARN` | `arn:aws:iam::459100131320:role/github-riverside-chatbot-deploy` | OIDC role assumption |
| `AWS_BACKEND_ARTIFACT_BUCKET` | `riverside-chatbot-artifacts-459100131320` | S3 upload target |
| `VERCEL_TOKEN` | (set) | Vercel frontend deploy |

## Testing

### cURL
```bash
curl -X POST https://dqcxdduwwj.execute-api.us-east-1.amazonaws.com/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"Where are you located?"}'
```

### PowerShell
```powershell
$body = '{"query":"Do you host events?"}'
Invoke-RestMethod -Uri "https://dqcxdduwwj.execute-api.us-east-1.amazonaws.com/chat" `
  -Method POST -Body $body -ContentType "application/json"
```

### AWS Console
1. Open [Lambda console](https://us-east-1.console.aws.amazon.com/lambda/home?region=us-east-1#/functions/riverside-chatbot)
2. Click **Test** tab
3. Create event with body: `{"body": "{\"query\":\"What are your opening hours?\"}"}`
4. Click **Test**

### Local Frontend
```powershell
cd Vercel-deployed-frontend
python -m http.server 3000
# Open http://localhost:3000/index.html
# Click golden chatbot button (bottom-right)
```

## Updating the Lambda

After changing `lambda_handler.py` or `app/`:

```powershell
cd AWS-deployed-backend
Remove-Item -Recurse -Force package, lambda-release.zip -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force package | Out-Null
Copy-Item lambda_handler.py package/
Copy-Item -Recurse app package/app
Remove-Item -Recurse package/app/__pycache__ -ErrorAction SilentlyContinue
Compress-Archive -Path package\* -DestinationPath lambda-release.zip -Force

aws lambda update-function-code `
  --function-name riverside-chatbot `
  --zip-file "fileb://lambda-release.zip"
```

## IAM Setup Summary

| Role | Trust | Permissions |
|------|-------|-------------|
| `riverside-lambda-exec` | `lambda.amazonaws.com` | `AWSLambdaBasicExecutionRole` (CloudWatch logs) |
| `github-riverside-chatbot-deploy` | GitHub OIDC (`repo:Micha12344f/Riverside-books-chatbot:*`) | `s3:PutObject`, `s3:GetObject`, `s3:ListBucket` on artifact bucket |

## FAQ Knowledge Base

6 entries covering: opening hours, location, gift wrapping, book ordering, second-hand books, and events. Stored in `app/runtime_assets/faqs.json`. To add more FAQs, edit that file and redeploy the Lambda.