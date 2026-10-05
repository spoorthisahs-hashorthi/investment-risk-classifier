"""URL and domain lexical analysis module for detecting suspicious link characteristics."""

import re
import ipaddress
from urllib.parse import urlparse
from typing import List, Tuple, Dict, Any, Optional
from app.models.schemas import FindingItem, FindingCategory, SeverityLevel

# Well-known URL shorteners
URL_SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.me", "is.gd", "cutt.ly", "rb.gy",
    "ow.ly", "buff.ly", "rebrand.ly", "soo.gd", "shorturl.at", "t.co",
    "tiny.cc", "goo.gl", "bit.do", "bl.ink", "lnkd.in"
}

# TLDs historically over-represented in ephemeral scam campaigns and phishing
HIGH_ABUSE_TLDS = {
    "xyz", "top", "click", "buzz", "cfd", "rest", "icu", "sbs",
    "monster", "fit", "stream", "loan", "trade", "racing", "work",
    "gq", "tk", "ml", "ga", "cf", "cam", "vip", "uno"
}

# Major financial brands, brokerages, and cryptocurrency exchanges targets of impersonation
FINANCIAL_TARGET_BRANDS = [
    "binance", "coinbase", "kraken", "bybit", "kucoin", "metamask",
    "uniswap", "paxful", "bitfinex", "fidelity", "vanguard", "schwab",
    "robinhood", "blackrock", "jpmorgan", "chase", "goldmansachs",
    "morganstanley", "barclays", "hsbc", "wellsfargo", "citibank",
    "revolut", "paypal", "cashapp", "stripe", "etoro", "webull"
]

# Sensitive or suspicious path patterns
SUSPICIOUS_PATH_PATTERNS = [
    (r"\b(double[-_]?btc|double[-_]?crypto)\b", "Crypto doubling scheme in URL path"),
    (r"\b(claim[-_]?airdrop|airdrop[-_]?bonus)\b", "Unsolicited airdrop / reward claim path"),
    (r"\b(connect[-_]?wallet|seed[-_]?phrase|private[-_]?key)\b", "High-risk credential or wallet extraction path"),
    (r"\b(instant[-_]?withdraw|guaranteed[-_]?payout)\b", "Lure path promoting instant withdrawals"),
]


def levenshtein_distance(s1: str, s2: str) -> int:
    """Compute Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


class URLAnalyzer:
    """Performs lexical, structural, and brand-impersonation analysis on URLs."""

    def analyze(self, raw_url: str) -> Tuple[List[FindingItem], Dict[str, Any]]:
        """
        Analyze a raw URL for suspicious lexical features.
        Returns:
            Tuple of (findings_list, url_metadata)
        """
        findings: List[FindingItem] = []
        if not raw_url or not raw_url.strip():
            return [], {
                "is_valid": False,
                "reason": "No URL provided",
            }

        url_str = raw_url.strip()
        # Add default scheme if missing for parsing
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url_str):
            url_str = "https://" + url_str

        try:
            parsed = urlparse(url_str)
        except Exception as e:
            return [
                FindingItem(
                    id="url_malformed",
                    title="Malformed or Invalid URL Structure",
                    category=FindingCategory.LEXICAL_ANOMALY,
                    severity=SeverityLevel.HIGH,
                    explanation=f"The URL could not be parsed: {str(e)}",
                    evidence=raw_url,
                    source="url_analysis",
                )
            ], {"is_valid": False, "error": str(e)}

        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        path = parsed.path.lower()

        # Split host and port
        host = netloc
        port = None
        if ":" in netloc and not (netloc.startswith("[") and netloc.endswith("]")):
            parts = netloc.split(":")
            host = parts[0]
            try:
                port = int(parts[1])
            except ValueError:
                pass

        # 1. Check scheme
        if scheme not in ("http", "https"):
            findings.append(
                FindingItem(
                    id="url_unsupported_scheme",
                    title="Non-Standard or Unsafe URL Scheme",
                    category=FindingCategory.NETWORK_SECURITY,
                    severity=SeverityLevel.CRITICAL,
                    explanation=f"The URL uses '{scheme}://' instead of standard http or https. This may indicate an attempt to run local code, scripts, or non-web protocols.",
                    evidence=f"Scheme: {scheme}",
                    source="url_analysis",
                )
            )
        elif scheme == "http":
            findings.append(
                FindingItem(
                    id="url_insecure_http",
                    title="Insecure HTTP Protocol",
                    category=FindingCategory.NETWORK_SECURITY,
                    severity=SeverityLevel.MEDIUM,
                    explanation="The link uses unencrypted HTTP. Legitimate financial, investment, and crypto platforms require encrypted HTTPS to protect transactions and user credentials.",
                    evidence=f"Scheme: {scheme}://",
                    source="url_analysis",
                )
            )

        # 2. Check for userinfo / credentials in URL
        if parsed.username or parsed.password:
            findings.append(
                FindingItem(
                    id="url_credentials_embedded",
                    title="Credentials Embedded in URL",
                    category=FindingCategory.LEXICAL_ANOMALY,
                    severity=SeverityLevel.CRITICAL,
                    explanation="Embedding username or password tokens directly in the URL is commonly used in phishing attacks to mislead users about the true destination domain.",
                    evidence=f"{parsed.username}@{host}",
                    source="url_analysis",
                )
            )

        # 3. Check if Host is an IP address
        is_ip_host = False
        try:
            ipaddress.ip_address(host.strip("[]"))
            is_ip_host = True
            findings.append(
                FindingItem(
                    id="url_ip_as_hostname",
                    title="Raw IP Address Used Instead of Domain Name",
                    category=FindingCategory.DOMAIN_REPUTATION,
                    severity=SeverityLevel.CRITICAL,
                    explanation="Legitimate financial companies register brand domains. Direct IP address links are strongly correlated with transient, fly-by-night phishing servers or command-and-control nodes.",
                    evidence=f"Direct IP: {host}",
                    source="url_analysis",
                )
            )
        except ValueError:
            is_ip_host = False

        # 4. Non-standard port check
        if port and port not in (80, 443):
            findings.append(
                FindingItem(
                    id="url_non_standard_port",
                    title="Non-Standard Port Specified",
                    category=FindingCategory.NETWORK_SECURITY,
                    severity=SeverityLevel.MEDIUM,
                    explanation=f"The URL specifies custom port :{port}. Mainstream financial institutions operate exclusively over standard ports 80 and 443.",
                    evidence=f"Port: {port}",
                    source="url_analysis",
                )
            )

        # 5. Check URL Shorteners
        domain_parts = host.split(".")
        tld = domain_parts[-1] if len(domain_parts) > 1 else ""
        registered_domain = ".".join(domain_parts[-2:]) if len(domain_parts) >= 2 else host

        if registered_domain in URL_SHORTENERS or host in URL_SHORTENERS:
            findings.append(
                FindingItem(
                    id="url_shortener_used",
                    title="URL Shortening Service Detected",
                    category=FindingCategory.LEXICAL_ANOMALY,
                    severity=SeverityLevel.MEDIUM,
                    explanation="The link uses a URL shortener which masks the actual target website. Scammers frequently use shorteners to bypass initial domain reputation filters.",
                    evidence=f"Shortener: {host}",
                    source="url_analysis",
                )
            )

        # 6. Punycode / Homoglyph check
        if host.startswith("xn--") or ".xn--" in host:
            findings.append(
                FindingItem(
                    id="url_punycode_homoglyph",
                    title="Punycode / Internationalized Domain Name Detected",
                    category=FindingCategory.DOMAIN_REPUTATION,
                    severity=SeverityLevel.HIGH,
                    explanation="Punycode (xn--) allows characters from different alphabets (e.g. Cyrillic) that look visually identical to Latin characters (homograph attack), often mimicking legitimate brands.",
                    evidence=f"Punycode host: {host}",
                    source="url_analysis",
                )
            )

        # 7. Subdomain depth check
        if len(domain_parts) >= 4 and not is_ip_host:
            findings.append(
                FindingItem(
                    id="url_excessive_subdomains",
                    title="Excessive Subdomain Stacking",
                    category=FindingCategory.LEXICAL_ANOMALY,
                    severity=SeverityLevel.MEDIUM,
                    explanation="Using multiple nested subdomains (e.g. login.secure.target.evil.com) is often used to deceive mobile users who only see the first few words on small screens.",
                    evidence=f"Host: {host} ({len(domain_parts)} domain labels)",
                    source="url_analysis",
                )
            )

        # 8. High-abuse / Cheap TLD check
        if tld in HIGH_ABUSE_TLDS:
            findings.append(
                FindingItem(
                    id="url_high_abuse_tld",
                    title="High-Abuse Top-Level Domain (TLD)",
                    category=FindingCategory.DOMAIN_REPUTATION,
                    severity=SeverityLevel.MEDIUM,
                    explanation=f"The top-level domain '.{tld}' is frequently favored by disposable investment scam campaigns due to low registration cost and minimal identity verification.",
                    evidence=f"TLD: .{tld}",
                    source="url_analysis",
                )
            )

        # 9. Brand Spoofing / Typosquatting check
        domain_name_core = domain_parts[0] if len(domain_parts) >= 1 else ""
        if len(domain_parts) >= 2:
            domain_name_core = domain_parts[-2]

        for brand in FINANCIAL_TARGET_BRANDS:
            # Check exact match on a brand with suspicious TLD or lookalike combinations
            if brand in host:
                # If host is not the official brand domain (e.g. not binance.com or www.binance.com)
                official_domains = {f"{brand}.com", f"www.{brand}.com", f"{brand}.org", f"www.{brand}.org", f"{brand}.io"}
                if registered_domain not in official_domains and host not in official_domains:
                    findings.append(
                        FindingItem(
                            id="url_brand_impersonation",
                            title=f"Potential Brand Impersonation: '{brand.capitalize()}'",
                            category=FindingCategory.DOMAIN_REPUTATION,
                            severity=SeverityLevel.CRITICAL,
                            explanation=f"The domain contains the brand name '{brand}', but does not appear to be an official domain of {brand.capitalize()}. Scammers create lookalike domains (e.g. '{brand}-login.top') to siphon credentials and deposits.",
                            evidence=f"Host '{host}' references brand '{brand}'",
                            source="url_analysis",
                        )
                    )
                    break
            else:
                # Check for subtle typosquatting (Levenshtein distance <= 2)
                dist = levenshtein_distance(domain_name_core, brand)
                # Only flag if length is similar and distance is 1 or 2
                if 0 < dist <= 2 and abs(len(domain_name_core) - len(brand)) <= 2 and len(domain_name_core) >= 5:
                    findings.append(
                        FindingItem(
                            id="url_typosquatting",
                            title=f"Typosquatting Detected: Similar to '{brand.capitalize()}'",
                            category=FindingCategory.DOMAIN_REPUTATION,
                            severity=SeverityLevel.HIGH,
                            explanation=f"The domain '{domain_name_core}' is deceptively similar to recognized financial brand '{brand.capitalize()}' (edit distance: {dist}). This is typical of typosquatting lures.",
                            evidence=f"Domain label '{domain_name_core}' vs '{brand}'",
                            source="url_analysis",
                        )
                    )
                    break

        # 10. Suspicious path keywords
        for pattern_str, label in SUSPICIOUS_PATH_PATTERNS:
            if re.search(pattern_str, path, re.IGNORECASE):
                findings.append(
                    FindingItem(
                        id="url_suspicious_path",
                        title=f"Suspicious Path Pattern: {label}",
                        category=FindingCategory.LEXICAL_ANOMALY,
                        severity=SeverityLevel.HIGH,
                        explanation=f"The URL path contains patterns ('{path}') frequently associated with deceptive giveaways, fake airdrops, or credential harvesting.",
                        evidence=f"Path: {path}",
                        source="url_analysis",
                    )
                )

        metadata = {
            "is_valid": True,
            "normalized_url": url_str,
            "scheme": scheme,
            "host": host,
            "port": port,
            "registered_domain": registered_domain,
            "tld": tld,
            "findings_count": len(findings),
        }

        return findings, metadata
