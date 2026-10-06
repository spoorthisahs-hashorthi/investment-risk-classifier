# Security and privacy behavior

## Current analysis route

- Request models cap text at 20,000 characters and URLs at 2,048 characters.
- Only HTTP(S) URLs are accepted. URLs with embedded usernames or passwords are rejected.
- The analysis endpoint never connects to submitted hosts. It performs lexical analysis only, so no DNS, redirects, TLS, page download, or SSRF-relevant outbound fetch takes place.
- Results expose the URL origin as metadata, not its path/query/fragment. A suspicious path match may include the matched path as evidence.
- Analysis text, URLs, findings, and reports are not written to persistent storage by the analysis endpoint. Application errors are logged without request bodies.

## Persistence and feedback

The optional feedback route uses the legacy SQLite repository and can persist free-text feedback notes. It has no authentication or retention controls and is not connected to the main UI; do not expose it publicly without adding those controls or disabling the route. An existing `backend/data/local_store.db` file may contain older records; this application update does not delete or inspect those records.

The Supabase migration is inactive and denies access to client roles by omitting client policies. A future backend integration still needs narrowly scoped service policies and an ownership/retention model. Never expose a service-role key in browser code.

## Legacy network code and deployment

`backend/app/analyzers/network_inspector.py` is not called by the API. It performs a DNS validation followed by an independent HTTPX hostname connection, which can resolve again; therefore it does not pin the validated IP to the actual connection and must not be treated as production SSRF protection. Do not reconnect it without a pinned-destination transport and a reviewed redirect strategy.

The service has no application-level rate limiter or request-body limit beyond the Pydantic field limits. A public deployment needs ingress request-size limits, rate limiting, HTTPS, narrowly configured CORS, and monitoring that avoids recording sensitive request bodies. No external reputation or regulator APIs are contacted.

## UI rendering

Submitted text and result strings are rendered as React text nodes. The highlighted text view uses offsets and standard React elements; it does not inject submitted HTML.
