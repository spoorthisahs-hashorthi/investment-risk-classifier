# Functional backtest and feature audit

This is a deterministic regression run against the current rules, not a traditional predictive-model backtest. There is no historical, independently labeled dataset, so accuracy, precision, recall, and false-positive rates cannot be estimated from this run.

## Backtest results

The five curated sample cases were submitted through `POST /api/v1/analyze`; expected and actual categories matched **5/5** after risk aggregation was changed to count each distinct source/rule once. Additional safe API scenarios verified direct crypto payment and upfront activation-fee detection, repeated recruitment-match handling, and that URL analysis does not fetch a private address or return URL path/query tokens.

Automated regression scenarios live in `backend/tests/test_functional_backtest.py`. They use only synthetic fixtures and the in-process API transport; they do not contact websites.

## Feature coverage

| Defined feature | Current status | Audit evidence / boundary |
|---|---|---|
| Submit promotional text, URL, or both | Working | Form and `POST /api/v1/analyze`; sample cases are loaded into the form. |
| Validate required input, size, scheme, credentials | Working | Pydantic caps input sizes; empty input is rejected; only HTTP(S) is accepted; embedded URL credentials are rejected. |
| Detect claims, risk language, urgency, recruitment, vague mechanism, payments | Working with rule limits | Explicit English regular expressions; direct crypto and upfront-fee regressions included. Not a language model, no translations, and paraphrases can be missed. |
| Inspect lexical URL/domain signals | Partial | IP host, brand-name similarity, punycode, shortener list, local TLD watchlist, subdomains, path terms, and HTTP scheme are checked. Lists are hand-maintained heuristics without an authoritative source feed. |
| Show separate findings, evidence and explanations | Working | Text/URL collections are separate; text findings carry offsets; matched evidence is displayed. |
| Combine findings and express uncertainty | Working with a known limitation | Distinct rule types are counted once, while repeated evidence remains visible. There is no real-world calibration. Current API cannot reach Low uncertainty because it does not perform live inspection. |
| Report redirects, TLS, live page content, domain age | Not implemented | Live retrieval is skipped; domain-age check is unavailable. No host is contacted. |
| Regulator/register verification | Manual guidance only | No jurisdiction was selected and no registry API adapter is configured. The tool provides general verification steps, not a lookup result. |
| Report export | Working | The result UI offers copy and JSON download. |
| Sample cases | Working | Five curated sample cases; all five categories matched their authored expected category in regression. |
| Feedback | Partial | Backend endpoint and SQLite storage exist, but the feedback widget is not connected to the main page. Notes have no retention or authorization controls. |
| Persistence / history dashboard | Not implemented for analysis | Analysis requests do not save reports; Supabase migration is inactive. |
| Human review, scheme classification, evaluation dashboard | Not implemented | These were candidate later additions, not active features. |

## Validation command

From `backend/`, run `PYTHONPATH=. python -m pytest -q`. The current suite contains the deterministic regression scenarios plus analyzer, validation, synthesis, and security-module tests. Live network inspection is intentionally disabled in the API and was not tested against external websites.
