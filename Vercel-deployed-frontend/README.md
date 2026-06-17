# Frontend

Back to the main hub: [../README.md](../README.md)

This folder contains the static web presentation layer for the Riverside Books chatbot.

Live frontend: <https://riverside-chatbot-website.vercel.app>

## What it is

The frontend is a single-page static storefront shell with a floating chatbot trigger and an animated book-style chat overlay.

Main file:

```text
Vercel-deployed-frontend/index.html
```

Local visual assets live in:

```text
Vercel-deployed-frontend/assets/
```

## Local run

```powershell
cd Vercel-deployed-frontend
python -m http.server 3000
```

Then open:

```text
http://127.0.0.1:3000/index.html
```

## Integration point

The chatbot widget sends a `POST` request to `/api/chat`.

That route is intended to be a Vercel-side proxy, with the upstream backend URL stored in the `RIVERSIDE_BACKEND_URL` Vercel environment variable.

## Security

- Keep frontend environment values in Vercel environment variables.
- Keep the backend origin allowlist aligned with the deployed frontend domains.
- Avoid publishing live backend service URLs in the public README set.

## Notes about the current shell

- The storefront HTML is static rather than framework-driven.
- The chatbot is the project-specific interactive layer.
- The mirrored storefront depends on external CSS and JS asset hosts plus the local asset overrides in this repo.

## See also

- [../AWS-deployed-backend/README.md](../AWS-deployed-backend/README.md)
- [../assets/README.md](../assets/README.md)
