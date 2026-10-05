"""Tests for text indicator analysis and offset extraction."""

import pytest
from app.analyzers.text_analyzer import TextAnalyzer
from app.models.schemas import FindingCategory, SeverityLevel


@pytest.fixture
def analyzer():
    return TextAnalyzer()


def test_empty_text(analyzer):
    findings, meta = analyzer.analyze("")
    assert findings == []
    assert meta["word_count"] == 0
    assert not meta["is_sufficient"]


def test_guaranteed_return_detection(analyzer):
    text = "We offer 100% guaranteed profit on all invested capital without delay."
    findings, meta = analyzer.analyze(text)
    
    assert len(findings) >= 1
    guaranteed_finding = next((f for f in findings if f.id == "text_guaranteed_profit"), None)
    assert guaranteed_finding is not None
    assert guaranteed_finding.severity == SeverityLevel.CRITICAL
    assert guaranteed_finding.category == FindingCategory.FINANCIAL_PROMISE
    assert "guaranteed profit" in guaranteed_finding.evidence.lower()
    assert guaranteed_finding.start_offset is not None
    assert guaranteed_finding.end_offset is not None
    assert text[guaranteed_finding.start_offset : guaranteed_finding.end_offset] == guaranteed_finding.evidence


def test_unrealistic_rate_detection(analyzer):
    text = "Join our trading pool for 2.5% daily returns compounded every 24 hours."
    findings, meta = analyzer.analyze(text)
    
    rate_finding = next((f for f in findings if f.id == "text_unrealistic_rate"), None)
    assert rate_finding is not None
    assert rate_finding.severity == SeverityLevel.CRITICAL
    assert "2.5% daily" in rate_finding.evidence.lower()


def test_zero_risk_claim(analyzer):
    text = "Our unique hedge structure ensures zero risk to all participants."
    findings, _ = analyzer.analyze(text)
    
    zero_risk_finding = next((f for f in findings if f.id == "text_zero_risk"), None)
    assert zero_risk_finding is not None
    assert zero_risk_finding.severity == SeverityLevel.HIGH


def test_urgency_and_scarcity(analyzer):
    text = "Act now! Only 5 spots left before the special deposit window closes."
    findings, _ = analyzer.analyze(text)
    
    urgency_finding = next((f for f in findings if f.id == "text_urgency_pressure"), None)
    assert urgency_finding is not None
    assert urgency_finding.severity == SeverityLevel.MEDIUM


def test_recruitment_bonus(analyzer):
    text = "Invite friends and earn a 10% referral bonus on their downline deposits."
    findings, _ = analyzer.analyze(text)
    
    mlm_finding = next((f for f in findings if f.id == "text_recruitment_incentive"), None)
    assert mlm_finding is not None
    assert mlm_finding.severity == SeverityLevel.HIGH


def test_crypto_deposit_pressure(analyzer):
    text = "To activate your account, send USDT TRC-20 directly to our automated address."
    findings, _ = analyzer.analyze(text)
    
    payment_finding = next((f for f in findings if f.id == "text_irreversible_payment"), None)
    assert payment_finding is not None
    assert payment_finding.severity == SeverityLevel.HIGH


def test_legitimate_financial_disclosure(analyzer):
    text = (
        "Mutual fund investments are subject to market risks. Please read all scheme-related "
        "documents carefully before investing. Historical performance may not be repeated in the future."
    )
    findings, meta = analyzer.analyze(text)
    assert len(findings) == 0
    assert meta["is_sufficient"] is True
