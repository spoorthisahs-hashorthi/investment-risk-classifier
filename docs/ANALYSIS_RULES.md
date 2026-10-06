# Analysis rules and regression coverage

## What the result means

The API uses explicit lexical rules and heuristic score thresholds. It has no trained model, labeled production dataset, calibration study, or measured accuracy. Scores are not fraud probabilities. A match means only that the submitted wording or URL structure matches a rule.

## Current text rule families

The Python catalog in `backend/app/analyzers/text_analyzer.py` currently checks for guaranteed or periodic returns, rapid multiplication of money, no-risk claims, urgency/scarcity, recruitment incentives, vague algorithm claims, direct crypto/unusual payments, upfront/release fees, celebrity/media associations, and instant-wealth claims. Each match includes the literal matched phrase and character offsets.

These regular expressions are a baseline. They can miss paraphrases and languages other than English, and can flag benign context. The payment checks are lexical and cannot determine whether a fee or payment route is legitimate.

## Current URL rule families

`backend/app/analyzers/url_analyzer.py` checks numeric IP hosts, selected brand-name references and edit-distance similarities, punycode labels, URL shorteners, a local TLD watchlist, nested subdomains, selected path terms, and HTTP (unencrypted) schemes. TLD and brand lists are local heuristics, not a current reputation feed or authoritative list of official domains. TLD alone is a weak signal.

The API does not visit submitted URLs. Redirects, page contents, DNS reputation, TLS certificates, domain age, and live destination safety are not checked; those statuses are reported as skipped or unavailable. Embedded credentials and non-HTTP(S) URL schemes are rejected at request validation rather than scored as findings.

## Score and categories

Finding weights are Critical 0.40, High 0.25, Medium 0.12, and Low 0.05. Repeated occurrences of the same rule from the same source remain visible as separate evidence, but contribute only once to the combined score and category. The weighted sum is transformed with `1 - 1 / (1 + weight * 1.5)`. This is a hand-set heuristic, not statistical calibration.

- **Insufficient information:** no usable input, or fewer than eight words of text with no URL and no detected indicator.
- **Elevated concern:** any Critical indicator, at least two distinct High indicator types, or a score of at least 0.48.
- **Needs review:** at least one High indicator type, at least two Medium types, or a score of at least 0.20.
- **Lower concern:** none of the above. A single Medium or Low indicator can remain in this category; the summary names that observed signal.

No category proves an offer fraudulent or safe. The API currently reports Medium or High uncertainty for active submissions; Low uncertainty requires completed live URL inspection, which the API route does not currently perform.

## Regression “backtest”

`backend/tests/test_functional_backtest.py` runs a deterministic scenario suite over the five hand-authored API sample cases, repeated-rule scoring, and crypto/upfront-payment examples. These are regression fixtures written by the project, not independently labeled or historically collected data. Passing them checks expected behavior; it does not measure real-world precision, recall, false-positive rates, or accuracy.

## Data provenance

No external training data or reputation dataset is bundled. Sample cases are educational examples authored in the API source. No model accuracy or comparative performance claim is available.
