# Security & Privacy Safeguards

## 1. Threat Model & Untrusted Input Policy

All user-submitted promotional text and website URLs are treated as untrusted and potentially hostile. The application enforces defense-in-depth protections across both backend network calls and presentation rendering.

---

## 2. Server-Side Request Forgery (SSRF) Mitigations

When evaluating user-submitted website links, the system performs network probing to check TLS certificates, redirects, and HTTP status codes. To protect internal network infrastructure, cloud metadata endpoints, and internal microservices from SSRF attacks, `NetworkInspector` implements the following defenses:

### Disallowed Network Blacklist
Before establishing any socket connection, the target hostname is resolved into its constituent IP addresses. **Every single IP** returned by DNS is validated against the following disallowed CIDR blocks:
- **Loopback:** `127.0.0.0/8`, `::1/128`
- **RFC 1918 Private Ranges:**
  - `10.0.0.0/8`
  - `172.16.0.0/12`
  - `192.168.0.0/16`
- **Cloud Provider Metadata Endpoints:**
  - `169.254.169.254` (AWS, GCP, Azure, DigitalOcean)
  - `metadata.google.internal`
  - `instance-data`
- **Link-Local & Multicast:**
  - `169.254.0.0/16`, `fe80::/10`
  - `224.0.0.0/4`, `ff00::/8`
- **Carrier-Grade NAT (CGNAT):** `100.64.0.0/10`
- **IPv4-Mapped IPv6:** `::ffff:0:0/96`
- **Reserved & Future Use:** `240.0.0.0/4`, `0.0.0.0/8`

If **any** resolved IP belongs to any of these ranges, the probe is terminated immediately with a security event: `url_ssrf_forbidden_destination`.

### Revalidation on Every Redirect Hop
Attackers often use open redirects on public servers that bounce to `127.0.0.1` or private intranet targets (DNS rebinding / redirect attacks).
- The network inspector uses `follow_redirects=False` in HTTPX.
- Every HTTP redirect (`301`, `302`, `303`, `307`, `308`) is intercepted manually.
- The `Location` header is parsed, and DNS resolution + IP address validation is re-executed on the destination before making the next hop.
- Redirection count is strictly bounded to `MAX_REDIRECTS=3`.

### Strict Resource Limits
- **Connection Timeout:** Strict `4.0` second socket timeout.
- **Payload Bound:** Maximum `256 KB` body read limit (`MAX_RESPONSE_BYTES`).
- **No Script Execution:** Retrieved HTML is parsed solely as static DOM using BeautifulSoup; JavaScript is never executed, and external assets (images, stylesheets, scripts) are never downloaded.

---

## 3. Privacy & Data Minimization Policy

### Zero Retention of Raw Submitted Text
- To respect user confidentiality and protect sensitive personal communications, **raw submitted promotional text is never stored in persistent databases**.
- Only a one-way cryptographic SHA-256 hash (`text_hash`) is retained to detect duplicates or support feedback correlation.

### Sanitized URL Retention
- If a URL contains embedded credentials (`user:password@domain`), the credentials are stripped prior to storage.
- Non-sensitive domain hosts are retained solely for aggregation and abuse monitoring.

### Row Level Security (RLS)
- Supabase migrations enforce Row Level Security on `risk_analyses` and `analysis_feedback`.
- Privileged service-role keys are kept strictly on the backend and are never exposed in browser bundles.

---

## 4. UI Rendering Security & XSS Mitigation

- React's JSX safely escapes strings by default.
- Highlighted text spans are rendered through standard React text nodes (`<span>` and `<mark>`) with index-based offsets rather than dangerous `dangerouslySetInnerHTML`.
