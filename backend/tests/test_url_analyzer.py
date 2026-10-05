"""Tests for lexical URL analysis and domain impersonation checks."""

import pytest
from app.analyzers.url_analyzer import URLAnalyzer
from app.models.schemas import SeverityLevel


@pytest.fixture
def analyzer():
    return URLAnalyzer()


def test_ip_address_host(analyzer):
    findings, meta = analyzer.analyze("http://198.51.100.24/invest")
    assert meta["is_valid"] is True
    ip_finding = next((f for f in findings if f.id == "url_ip_as_hostname"), None)
    assert ip_finding is not None
    assert ip_finding.severity == SeverityLevel.CRITICAL


def test_url_shortener(analyzer):
    findings, meta = analyzer.analyze("https://bit.ly/guaranteed-crypto")
    assert meta["is_valid"] is True
    short_finding = next((f for f in findings if f.id == "url_shortener_used"), None)
    assert short_finding is not None
    assert short_finding.severity == SeverityLevel.MEDIUM


def test_brand_impersonation(analyzer):
    findings, meta = analyzer.analyze("https://binance-trade-portal.xyz/login")
    assert meta["is_valid"] is True
    impersonation = next((f for f in findings if f.id == "url_brand_impersonation"), None)
    assert impersonation is not None
    assert impersonation.severity == SeverityLevel.CRITICAL
    assert "binance" in impersonation.title.lower()


def test_suspicious_tld(analyzer):
    findings, meta = analyzer.analyze("https://quick-wealth-investments.top")
    assert meta["is_valid"] is True
    tld_finding = next((f for f in findings if f.id == "url_high_abuse_tld"), None)
    assert tld_finding is not None
    assert tld_finding.severity == SeverityLevel.MEDIUM


def test_suspicious_path_pattern(analyzer):
    findings, meta = analyzer.analyze("https://crypto-reward.net/claim-airdrop")
    path_finding = next((f for f in findings if f.id == "url_suspicious_path"), None)
    assert path_finding is not None
    assert path_finding.severity == SeverityLevel.HIGH


def test_insecure_http_scheme(analyzer):
    findings, _ = analyzer.analyze("http://myinvestmentsite.org")
    http_finding = next((f for f in findings if f.id == "url_insecure_http"), None)
    assert http_finding is not None
    assert http_finding.severity == SeverityLevel.MEDIUM


def test_legitimate_url(analyzer):
    findings, meta = analyzer.analyze("https://investor.vanguard.com")
    assert meta["is_valid"] is True
    # Should have no critical or high severity findings
    high_findings = [f for f in findings if f.severity in (SeverityLevel.HIGH, SeverityLevel.CRITICAL)]
    assert len(high_findings) == 0
