"""Tests for SSRF defenses and safe IP validation in NetworkInspector."""

import ipaddress
import pytest
from app.analyzers.network_inspector import (
    is_ip_safe,
    validate_hostname_safe,
    NetworkInspector,
)
from app.models.schemas import SeverityLevel


def test_public_ips_are_safe():
    public_ips = [
        "8.8.8.8",
        "1.1.1.1",
        "104.16.132.229",
        "142.250.190.46",
        "2606:4700:4700::1111",
    ]
    for ip in public_ips:
        assert is_ip_safe(ipaddress.ip_address(ip)) is True, f"{ip} should be considered safe"


def test_private_and_reserved_ips_are_disallowed():
    dangerous_ips = [
        # Loopback
        "127.0.0.1",
        "127.0.0.254",
        "::1",
        # RFC 1918 Private
        "10.0.0.1",
        "10.255.255.255",
        "172.16.0.1",
        "172.31.255.255",
        "192.168.0.1",
        "192.168.100.50",
        # Cloud Metadata & Link-Local
        "169.254.169.254",
        "169.254.1.1",
        "fe80::1",
        # CGNAT
        "100.64.0.1",
        # Multicast
        "224.0.0.1",
    ]
    for ip in dangerous_ips:
        assert is_ip_safe(ipaddress.ip_address(ip)) is False, f"{ip} should be blocked"


def test_blocked_special_hostnames():
    special_hosts = ["metadata.google.internal", "instance-data", "localhost"]
    for host in special_hosts:
        is_safe, msg, _ = validate_hostname_safe(host)
        assert is_safe is False
        assert "reserved" in msg.lower() or "dns" in msg.lower()


@pytest.mark.asyncio
async def test_network_inspection_is_disabled_in_current_app():
    inspector = NetworkInspector()
    # The live retrieval component is intentionally disabled for the current product flow.
    findings, status_item, page_text = await inspector.inspect("http://127.0.0.1:8000/internal")

    assert status_item.status == "skipped"
    assert page_text is None
    assert findings == []
