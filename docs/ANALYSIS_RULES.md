# Analysis Rules, Calibration & Limitations

## 1. Indicator Catalog

The system screens submissions against a transparent catalog of empirical risk indicators documented in securities regulatory warnings (SEC Investor Bulletins, FCA ScamSmart, FINRA Investor Alerts).

### Text Indicators
| Rule ID | Title | Category | Severity | Description |
|---|---|---|---|---|
| `text_guaranteed_profit` | Guaranteed Returns or Profit Promise | Financial Promise | Critical | Promises of guaranteed profit; legitimate investments always carry market risk. |
| `text_unrealistic_rate` | Unrealistically High Periodic Return | Financial Promise | Critical | Claims of 1%+ daily or 10%+ weekly returns (mathematically unsustainable compound interest). |
| `text_capital_multiplier` | Rapid Wealth Multiplier Claim | Financial Promise | High | Promises to double or triple capital in days/hours. |
| `text_zero_risk` | Claim of Zero or No Risk | Risk Claim | High | Deceptive claims that losses are impossible or capital is 100% immune from loss. |
| `text_urgency_pressure` | Urgency & Artificial Scarcity | Urgency / Scarcity | Medium | Fabricating tight deadlines, limited slots, or FOMO pressure. |
| `text_recruitment_incentive` | Recruitment & Referral Incentives | Recruitment / MLM | High | Heavy emphasis on downlines, binary trees, and member referral bonuses over product value. |
| `text_vague_algorithm` | Vague or Mythical Trading Algorithm | Vague Mechanism | Medium | References to secret quantum AI bots or money-printing trading loopholes. |
| `text_irreversible_payment` | Direct Irreversible Crypto / Wire Payment | Payment Method | High | Demanding direct USDT TRC-20, Bitcoin wallet transfers, or gift cards. |
| `text_celebrity_media` | Celebrity Endorsement / Media Impersonation | Authority Endorsement | High | Fabricated claims of endorsement by Elon Musk, BBC, Shark Tank, etc. |
| `text_lifestyle_promise` | Extreme Lifestyle / Overnight Wealth | Financial Promise | Low | Emotional appeals to quit jobs or become millionaires overnight. |

---

### URL & Domain Indicators
| Rule ID | Title | Category | Severity | Description |
|---|---|---|---|---|
| `url_ip_as_hostname` | Raw IP Hostname | Domain Reputation | Critical | Direct IP addresses (e.g. `198.51.100.24`) instead of registered domains. |
| `url_brand_impersonation` | Brand Impersonation / Lookalike | Domain Reputation | Critical | Domain containing major exchange or bank brand on unauthorized TLDs. |
| `url_credentials_embedded` | Embedded Credentials in URL | Lexical Anomaly | Critical | Phishing syntax embedding username/token in host string. |
| `url_punycode_homoglyph` | Punycode / Homograph Attack | Domain Reputation | High | `xn--` internationalized domains mimicking Latin brand spellings. |
| `url_typosquatting` | Typosquatting / Edit Distance | Domain Reputation | High | Domain label 1-2 edit distance away from recognized financial institutions. |
| `url_suspicious_path` | Suspicious Path Pattern | Lexical Anomaly | High | Paths such as `/claim-airdrop`, `/double-btc`, `/connect-wallet`. |
| `url_shortener_used` | URL Shortener | Lexical Anomaly | Medium | Known link shortener (e.g., bit.ly) masking true destination. |
| `url_high_abuse_tld` | High-Abuse / Cheap TLD | Domain Reputation | Medium | Domains using `.xyz`, `.top`, `.click`, `.buzz`, `.cfd`, etc. |
| `url_excessive_subdomains` | Excessive Subdomain Stacking | Lexical Anomaly | Medium | 4+ nested subdomains used to mislead mobile displays. |
| `url_insecure_http` | Insecure HTTP Protocol | Network Security | Medium | Plaintext HTTP used for financial interactions instead of TLS. |
| `url_ssrf_forbidden_destination`| Blocked Internal / Reserved Destination | Network Security | Critical | URL resolves to loopback, private RFC1918, or cloud metadata IP. |

---

## 2. Risk Score & Categorization Methodology

### Scoring Weights
- **Critical:** 0.40
- **High:** 0.25
- **Medium:** 0.12
- **Low:** 0.05

The raw indicator weights are summed and mapped through an asymptotic diminishing-returns curve:
$$\text{Risk Score} = 1.0 - \frac{1.0}{1.0 + (\text{Raw Weight} \times 1.5)}$$

### Category Thresholds
1. **Insufficient Information:**
   - No text and no URL provided; OR
   - Text is shorter than 8 words with no URL and no detected pattern.
2. **Elevated Concern:**
   - Any `Critical` severity finding (e.g., guaranteed profit, lookalike domain, direct IP host); OR
   - 2 or more `High` severity findings; OR
   - Aggregated risk score $\ge 0.48$.
3. **Needs Review:**
   - 1 `High` severity finding; OR
   - 2 or more `Medium` severity findings; OR
   - Aggregated risk score $\ge 0.20$.
4. **Lower Concern:**
   - No critical or high indicators detected, and risk score $< 0.20$.

---

## 3. Uncertainty Calibration

Uncertainty is explicitly evaluated along three tiers:
- **Low Uncertainty:** Both substantive promotional text ($\ge 50$ words) and a reachable, verified public URL were analyzed.
- **Medium Uncertainty:** Partial information was provided (e.g., text only without a link, or link only with limited page text).
- **High Uncertainty:** Sparse input was submitted ($< 30$ words or unresolvable URL).

---

## 4. Known Limitations

1. **Not a Definite Fraud Detector:** Rule-based matching detects recognizable linguistic and syntactic patterns. Fraudsters can compose polished copy with zero trigger words.
2. **Absence of Proof is Not Proof of Safety:** A **Lower Concern** rating must never be interpreted as an official endorsement or safety guarantee.
3. **Registry Boundaries:** Automated checks do not query official national regulatory databases directly; users must perform official register checks (SEC, FINRA, FCA, ASIC, SEBI) as suggested in the verification checklist.
