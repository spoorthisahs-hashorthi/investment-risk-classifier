"""SSRF-protected network inspector for safe probing of target URLs."""

import socket
import ipaddress
import logging
from urllib.parse import urlparse, urljoin
from typing import Tuple, List, Optional, Dict, Any

import httpx
from bs4 import BeautifulSoup

from app.models.schemas import FindingItem, FindingCategory, SeverityLevel, CheckStatusItem
from app.config import settings

logger = logging.getLogger(__name__)

# Disallowed IP networks according to IANA and cloud security standards
DISALLOWED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),          # Current network (RFC 1122)
    ipaddress.ip_network("10.0.0.0/8"),         # Private-Use (RFC 1918)
    ipaddress.ip_network("127.0.0.0/8"),        # Loopback (RFC 1122)
    ipaddress.ip_network("100.64.0.0/10"),      # Shared Address Space / CGNAT (RFC 6598)
    ipaddress.ip_network("169.254.0.0/16"),     # Link Local (RFC 3927) - includes AWS/GCP/Azure 169.254.169.254
    ipaddress.ip_network("172.16.0.0/12"),      # Private-Use (RFC 1918)
    ipaddress.ip_network("192.0.0.0/24"),       # IETF Protocol Assignments
    ipaddress.ip_network("192.0.2.0/24"),       # TEST-NET-1 (RFC 5737)
    ipaddress.ip_network("192.88.99.0/24"),     # 6to4 Relay Anycast (RFC 7526)
    ipaddress.ip_network("192.168.0.0/16"),     # Private-Use (RFC 1918)
    ipaddress.ip_network("198.18.0.0/15"),      # Network Interconnect Benchmarking (RFC 2544)
    ipaddress.ip_network("198.51.100.0/24"),    # TEST-NET-2 (RFC 5737)
    ipaddress.ip_network("203.0.113.0/24"),     # TEST-NET-3 (RFC 5737)
    ipaddress.ip_network("224.0.0.0/4"),        # Multicast (RFC 5771)
    ipaddress.ip_network("240.0.0.0/4"),        # Reserved for Future Use (RFC 1112)
    ipaddress.ip_network("255.255.255.255/32"), # Limited Broadcast (RFC 919)
    # IPv6 Disallowed
    ipaddress.ip_network("::/128"),             # Unspecified
    ipaddress.ip_network("::1/128"),           # Loopback
    ipaddress.ip_network("::ffff:0:0/96"),      # IPv4-mapped IPv6
    ipaddress.ip_network("100::/64"),           # Discard prefix (RFC 6666)
    ipaddress.ip_network("2001:db8::/32"),      # Documentation (RFC 3849)
    ipaddress.ip_network("fc00::/7"),           # Unique Local Address (ULA)
    ipaddress.ip_network("fe80::/10"),          # Link-Local Unicast
    ipaddress.ip_network("ff00::/8"),           # Multicast
]


def is_ip_safe(ip_obj: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Check if an IP address is strictly public and safe to connect to."""
    if (
        ip_obj.is_private
        or ip_obj.is_loopback
        or ip_obj.is_link_local
        or ip_obj.is_multicast
        or ip_obj.is_reserved
        or ip_obj.is_unspecified
    ):
        return False

    for network in DISALLOWED_NETWORKS:
        if ip_obj in network:
            return False

    return True


def validate_hostname_safe(hostname: str) -> Tuple[bool, str, List[str]]:
    """
    Resolve hostname to IP addresses and ensure ALL resolved addresses are public.
    Returns: (is_safe, error_or_ip_summary, list_of_ips)
    """
    # Special hostnames for cloud metadata
    blocked_hosts = {
        "metadata.google.internal",
        "instance-data",
        "localhost",
    }
    if hostname.lower() in blocked_hosts:
        return False, f"Host '{hostname}' is a reserved internal or metadata address.", []

    try:
        addr_info = socket.getaddrinfo(hostname, None)
    except socket.gaierror as e:
        return False, f"DNS resolution failed: {str(e)}", []
    except Exception as e:
        return False, f"Resolution error: {str(e)}", []

    resolved_ips: List[str] = []
    for entry in addr_info:
        ip_str = entry[4][0]
        if ip_str not in resolved_ips:
            resolved_ips.append(ip_str)

    if not resolved_ips:
        return False, "No IP addresses resolved for hostname", []

    for ip_str in resolved_ips:
        try:
            ip_obj = ipaddress.ip_address(ip_str)
            if not is_ip_safe(ip_obj):
                return (
                    False,
                    f"Resolved IP {ip_str} falls within a disallowed, private, or loopback network range (SSRF blocked).",
                    resolved_ips,
                )
        except ValueError:
            return False, f"Invalid IP representation resolved: {ip_str}", resolved_ips

    return True, f"Resolved to public IP(s): {', '.join(resolved_ips[:2])}", resolved_ips


class NetworkInspector:
    """Safely inspects URLs via HTTP/HTTPS while strictly defending against SSRF."""

    async def inspect(
        self, target_url: str
    ) -> Tuple[List[FindingItem], CheckStatusItem, Optional[str]]:
        """
        Inspect the target URL safely.
        Returns:
            Tuple of (findings_list, check_status, extracted_page_text)
        """
        if not settings.NETWORK_INSPECTION_ENABLED:
            return (
                [],
                CheckStatusItem(
                    name="url_network_inspection",
                    display_name="Live URL Network Inspection",
                    status="skipped",
                    details="Live network inspection is disabled in server configuration.",
                ),
                None,
            )

        findings: List[FindingItem] = []
        current_url = target_url.strip()
        redirect_hops = 0
        extracted_text = None

        try:
            # Reusable client with limits
            async with httpx.AsyncClient(
                verify=True,
                follow_redirects=False,  # We handle redirects manually for SSRF safety!
                timeout=httpx.Timeout(settings.NETWORK_TIMEOUT_SECONDS),
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; RiskClassificationBot/1.0; +https://example.com/bot)"
                },
            ) as client:

                while redirect_hops <= settings.MAX_REDIRECTS:
                    parsed = urlparse(current_url)
                    if parsed.scheme.lower() not in ("http", "https"):
                        return (
                            findings,
                            CheckStatusItem(
                                name="url_network_inspection",
                                display_name="Live URL Network Inspection",
                                status="failed",
                                details=f"Probing aborted: Scheme '{parsed.scheme}' is not allowed for network requests.",
                            ),
                            None,
                        )

                    hostname = parsed.hostname
                    if not hostname:
                        return (
                            findings,
                            CheckStatusItem(
                                name="url_network_inspection",
                                display_name="Live URL Network Inspection",
                                status="failed",
                                details="Probing aborted: Invalid or missing hostname.",
                            ),
                            None,
                        )

                    # SSRF DNS Validation
                    is_safe, msg, _ = validate_hostname_safe(hostname)
                    if not is_safe:
                        findings.append(
                            FindingItem(
                                id="url_ssrf_forbidden_destination",
                                title="Blocked Internal or Reserved Destination",
                                category=FindingCategory.NETWORK_SECURITY,
                                severity=SeverityLevel.CRITICAL,
                                explanation=(
                                    f"The address resolved to an internal, private, or loopback network: {msg}. "
                                    "Legitimate public investment websites never reside on private local IPs."
                                ),
                                evidence=f"{hostname} -> {msg}",
                                source="network_inspection",
                            )
                        )
                        return (
                            findings,
                            CheckStatusItem(
                                name="url_network_inspection",
                                display_name="Live URL Network Inspection",
                                status="failed",
                                details=f"Destination rejected by SSRF security policy: {msg}",
                            ),
                            None,
                        )

                    # Perform bounded GET request
                    try:
                        resp = await client.get(current_url)
                    except httpx.ConnectTimeout:
                        return (
                            findings,
                            CheckStatusItem(
                                name="url_network_inspection",
                                display_name="Live URL Network Inspection",
                                status="unavailable",
                                details=f"Connection timed out after {settings.NETWORK_TIMEOUT_SECONDS}s. The server may be offline or blocking screening bots.",
                            ),
                            None,
                        )
                    except httpx.ConnectError as e:
                        return (
                            findings,
                            CheckStatusItem(
                                name="url_network_inspection",
                                display_name="Live URL Network Inspection",
                                status="unavailable",
                                details=f"Could not connect to host ({hostname}). Server may be inactive or down.",
                            ),
                            None,
                        )
                    except Exception as e:
                        return (
                            findings,
                            CheckStatusItem(
                                name="url_network_inspection",
                                display_name="Live URL Network Inspection",
                                status="unavailable",
                                details="Network probe could not be completed.",
                            ),
                            None,
                        )

                    # Handle Redirects
                    if resp.status_code in (301, 302, 303, 307, 308) and "location" in resp.headers:
                        redirect_hops += 1
                        next_location = resp.headers["location"]
                        next_url = urljoin(current_url, next_location)
                        
                        # Check if redirect changes domain significantly
                        next_parsed = urlparse(next_url)
                        if next_parsed.hostname and next_parsed.hostname != hostname:
                            findings.append(
                                FindingItem(
                                    id="url_cross_domain_redirect",
                                    title="Cross-Domain Redirect Detected",
                                    category=FindingCategory.LEXICAL_ANOMALY,
                                    severity=SeverityLevel.MEDIUM,
                                    explanation=f"The URL redirects visitors to a different external domain: '{next_parsed.hostname}'. Investment lures often use intermediate domains to mask target schemes.",
                                    evidence=f"{hostname} -> {next_parsed.hostname}",
                                    source="network_inspection",
                                )
                            )
                        current_url = next_url
                        continue

                    # Terminal response reached
                    content_type = resp.headers.get("content-type", "").lower()

                    # Check for HTTP 4xx or 5xx
                    if resp.status_code >= 400:
                        findings.append(
                            FindingItem(
                                id="url_http_error_response",
                                title=f"HTTP Server Error: Status {resp.status_code}",
                                category=FindingCategory.NETWORK_SECURITY,
                                severity=SeverityLevel.LOW,
                                explanation=f"The server returned an HTTP error status code ({resp.status_code}). The page may have been taken down, expired, or blocked.",
                                evidence=f"Status code: {resp.status_code}",
                                source="network_inspection",
                            )
                        )

                    # Safe page text extraction for HTML
                    if "text/html" in content_type:
                        try:
                            # Bound content reading to MAX_RESPONSE_BYTES
                            raw_body = resp.content[: settings.MAX_RESPONSE_BYTES]
                            soup = BeautifulSoup(raw_body, "html.parser")

                            # Remove script and style elements
                            for element in soup(["script", "style", "noscript", "svg", "header", "footer", "nav"]):
                                element.decompose()

                            text = soup.get_text(separator=" ", strip=True)
                            if text:
                                extracted_text = text[:3000]  # First 3,000 characters
                        except Exception as e:
                            logger.warning(f"Failed to parse HTML from {hostname}: {e}")

                    # Final check status report
                    status_details = f"Successfully contacted host (HTTP {resp.status_code}, {redirect_hops} redirects)"
                    return (
                        findings,
                        CheckStatusItem(
                            name="url_network_inspection",
                            display_name="Live URL Network Inspection",
                            status="completed",
                            details=status_details,
                        ),
                        extracted_text,
                    )

            # Redirect limit exceeded
            findings.append(
                FindingItem(
                    id="url_excessive_redirects",
                    title="Excessive Redirect Chain",
                    category=FindingCategory.LEXICAL_ANOMALY,
                    severity=SeverityLevel.HIGH,
                    explanation=f"The URL redirected more than {settings.MAX_REDIRECTS} times. Scam operations frequently use long redirect chains or cloakers to frustrate automated analysis.",
                    evidence=f"Exceeded {settings.MAX_REDIRECTS} redirects",
                    source="network_inspection",
                )
            )
            return (
                findings,
                CheckStatusItem(
                    name="url_network_inspection",
                    display_name="Live URL Network Inspection",
                    status="completed",
                    details=f"Terminated after reaching maximum allowed redirect limit ({settings.MAX_REDIRECTS}).",
                ),
                None,
            )

        except Exception as e:
            logger.exception("Unexpected error in network inspector")
            return (
                findings,
                CheckStatusItem(
                    name="url_network_inspection",
                    display_name="Live URL Network Inspection",
                    status="unavailable",
                    details="An error occurred while inspecting the destination.",
                ),
                None,
            )
