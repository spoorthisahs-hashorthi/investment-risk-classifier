# System architecture

The current workflow is:

```text
Browser → Next.js App Router and TypeScript → FastAPI and Python rules
```

Next.js owns the form, sample-case loading, loading/error state, evidence display, and verification guidance. Its rewrite sends browser requests to FastAPI. Python validates requests, runs the text and URL lexical analyzers, combines distinct indicator types, and returns an uncertainty-aware response.

## API

- `POST /api/v1/analyze`: accepts optional `text` (up to 20,000 characters) and optional `url` (up to 2,048 characters); at least one nonblank input is required. URL schemes are limited to HTTP and HTTPS, and embedded credentials are rejected. A compatibility `enable_network_check` field is accepted but does not enable retrieval.
- `GET /api/v1/sample-cases`: returns hand-authored educational examples.
- `POST /api/v1/feedback`: stores optional feedback in the legacy SQLite repository. It is not currently wired into the main page.
- `GET /health`: reports service health and that live URL fetch is disabled.

The response includes separate text and URL findings, severity, evidence, explanation, result category, a heuristic score, uncertainty, check statuses, disclaimer, and suggested verification steps. OpenAPI documentation is available from FastAPI when the service is running.

## Persistence and integrations

Analysis requests are processed in memory and do not save reports. No Supabase or PostgreSQL connection is used by the current workflow. `backend/data/local_store.db` and the repository implementation remain for legacy feedback storage. The Supabase migration is a draft and is not applied automatically.

Automated regulator/register lookup, domain-age lookup, reputation feeds, and fetched page text are not integrated. No jurisdiction was selected, and no external credentials are configured.

## URL retrieval boundary

The API route does not perform DNS lookup, HTTP requests, redirect following, TLS inspection, or page extraction. A legacy `NetworkInspector` module is present but is not called by the route. Do not enable or reconnect it for public use without a pinned-destination transport, redirect revalidation, response limits, and security testing. Its existence does not mean live URL checks are active.

## Development

Setup and commands are documented in the repository root `README.md`. The basic text/URL analysis path requires no external service credentials.
