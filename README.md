# Investment Risk Screener

An educational early-warning tool for reviewing promotional text and website URL structure for common investment risk indicators. It is a rules-based screening aid, not a fraud determination, investment recommendation, or safety guarantee.

## Architecture

- `frontend/`: Next.js App Router and TypeScript user interface.
- `backend/`: FastAPI service. Python owns the authoritative text and URL rules and result synthesis.
- `supabase/`: an initial database migration retained for future evaluation; database persistence is not used by the current analysis flow.

The browser sends requests to the Next.js rewrite at `/api/backend`, which forwards them to the Python API. Analysis is performed in memory. The analysis endpoint does not save submitted text, URLs, findings, or reports. The optional feedback endpoint stores feedback in the local SQLite database; feedback may itself contain personal or sensitive information, so do not expose that endpoint in a public deployment without adding retention and authorization controls. A legacy SQLite repository implementation and database may exist in `backend/data/`; analysis requests no longer write to it.

## Local setup

Requirements: Python 3.11 or newer and Node.js/npm compatible with the versions in `frontend/package-lock.json`.

Start the API:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

In another terminal, start the web app:

```bash
cd frontend
npm ci
npm run dev
```

Open <http://localhost:3000>. The Next.js rewrite defaults to `http://127.0.0.1:8000`; set `BACKEND_URL` for a different server. `NEXT_PUBLIC_API_URL` can override the browser API base URL. `CORS_ORIGINS` configures backend origins. Request size limits are fixed by the request schema; no secrets or external service credentials are needed for local analysis.

## Analysis coverage and interpretation

The current baseline uses explicit lexical rules, not a trained model or labeled dataset. Text checks cover guaranteed/high periodic returns, risk claims, urgency, recruitment, payment methods, and vague mechanisms. URL checks cover syntax, URL shorteners, selected TLDs, suspicious paths, brand references, and lookalike strings. Findings include observed evidence and plain-language explanations. The overall score is a heuristic indicator, not a probability.

Categories are **Lower concern**, **Needs review**, **Elevated concern**, and **Insufficient information**. They describe how the submitted material matched these rules. They do not establish whether a firm or offer is legitimate.

The current service does not visit submitted URLs, follow redirects, inspect page contents, check HTTPS certificates or domain age, or query official registers. These checks appear as skipped or unavailable where relevant. Verify the exact legal entity and offer using the relevant regulator in your jurisdiction. A register entry is not proof that a specific offer is safe.

No third-party dataset or trained model is bundled. Example cases are hand-authored educational fixtures, not evaluation data; no accuracy claim is made.

## Security and privacy

- Text is limited to 20,000 characters and URL input to 2,048 characters by the API schema.
- Only HTTP(S) URLs are accepted; URLs with embedded credentials are rejected.
- Submitted websites are not contacted, avoiding SSRF and redirect risks in this version.
- The analysis route does not persist or log submitted text or URLs. Application exception logs include request method/path only.
- Deploy behind request-size and rate limits. Configure trusted origins for production and protect/remove the optional feedback endpoint before public use.

## Validation

From `backend/`, run `PYTHONPATH=. python -m pytest -q`. From `frontend/`, run `npm run typecheck` and `npm run build`. The repository has no ESLint dependency/configuration yet; `npm run lint` invokes Next's setup prompt and is not currently a non-interactive lint check.

See [`docs/FUNCTIONAL_BACKTEST.md`](docs/FUNCTIONAL_BACKTEST.md) for the feature-by-feature audit and synthetic regression coverage. The suite is not a statistical accuracy evaluation.
