"""Deterministic regression scenarios, not a statistical accuracy evaluation."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.analyzers.text_analyzer import TextAnalyzer


@pytest.mark.asyncio
async def test_curated_sample_category_regression():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        samples = (await client.get("/api/v1/sample-cases")).json()
        for sample in samples:
            response = await client.post(
                "/api/v1/analyze",
                json={
                    "text": sample["sample_text"],
                    "url": sample["sample_url"],
                    "enable_network_check": False,
                },
            )
            assert response.status_code == 200, sample["id"]
            assert response.json()["category"] == sample["expected_category"], sample["id"]


@pytest.mark.asyncio
async def test_repeated_matches_of_one_rule_do_not_multiply_risk_category():
    text = (
        "Earn a referral bonus for recruiting people, receive downline commissions, and grow a binary tree. "
        "Our investment plan offers five tiers of recruitment rewards for every new member you bring in."
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/analyze", json={"text": text})
    result = response.json()
    matching = [f for f in result["text_findings"] if f["id"] == "text_recruitment_incentive"]
    assert len(matching) > 1  # Keep each evidence occurrence visible.
    assert result["category"] == "needs_review"  # But score that indicator type once.


@pytest.mark.asyncio
async def test_single_medium_signal_is_named_even_when_category_is_lower_concern():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/analyze", json={"text": "Act now, only 3 slots left."})
    result = response.json()
    assert result["category"] == "lower_concern"
    assert "urgency and artificial scarcity tactic" in result["summary"].lower()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "text,expected_id",
    [
        (
            "To activate your account, send USDT (TRC-20) to our automated contract before trading begins.",
            "text_irreversible_payment",
        ),
        (
            "Pay an activation fee before your investment account can be opened.",
            "text_upfront_payment",
        ),
    ],
)
async def test_payment_request_scenarios_are_detected(text, expected_id):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/analyze", json={"text": text})
    assert response.status_code == 200
    assert expected_id in {finding["id"] for finding in response.json()["text_findings"]}


@pytest.mark.parametrize(
    "text,expected_id",
    [
        ("The bot guarantees returns to all participants.", "text_guaranteed_profit"),
        ("Get 2% daily returns from the pool.", "text_unrealistic_rate"),
        ("Double your money in five days.", "text_capital_multiplier"),
        ("There is zero risk and no chance of loss.", "text_zero_risk"),
        ("Act now, only 3 slots left.", "text_urgency_pressure"),
        ("Invite friends and earn a referral bonus.", "text_recruitment_incentive"),
        ("Our automated AI trading bot uses a secret algorithm.", "text_vague_algorithm"),
        ("This investment company has been endorsed by Elon Musk.", "text_celebrity_media"),
        ("Become a millionaire overnight.", "text_lifestyle_promise"),
    ],
)
def test_text_indicator_catalog_regressions(text, expected_id):
    findings, _ = TextAnalyzer().analyze(text)
    assert expected_id in {finding.id for finding in findings}
