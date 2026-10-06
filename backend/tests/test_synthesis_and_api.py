"""Tests for risk synthesis, categorization, and FastAPI endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.schemas import RiskCategory, UncertaintyLevel


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_sample_cases_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/sample-cases")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 4
        assert any(c["id"] == "sample_hyip_guarantee" for c in data)


@pytest.mark.asyncio
async def test_analyze_empty_payload_fails_validation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/analyze", json={})
        assert resp.status_code == 422
        assert set(resp.json()) == {"error", "message", "details"}


@pytest.mark.asyncio
async def test_analyze_hyip_elevated_concern():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "text": "Join now for 100% guaranteed profit of 3% daily! Act now, only 5 spots left! Send USDT TRC20.",
            "enable_network_check": False,
        }
        resp = await client.post("/api/v1/analyze", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["category"] == RiskCategory.ELEVATED_CONCERN.value
        assert data["risk_score"] > 0.4
        assert len(data["text_findings"]) >= 2
        assert len(data["verification_checklist"]) >= 2
        assert "disclaimer" in data


@pytest.mark.asyncio
async def test_analyze_insufficient_information():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "text": "Hello invest",
            "enable_network_check": False,
        }
        resp = await client.post("/api/v1/analyze", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["category"] == RiskCategory.INSUFFICIENT_INFORMATION.value
        assert data["uncertainty_level"] == UncertaintyLevel.HIGH.value


@pytest.mark.asyncio
async def test_analyze_lookalike_url_elevated():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "url": "https://binance-login-portal.xyz/claim-airdrop",
            "enable_network_check": False,
        }
        resp = await client.post("/api/v1/analyze", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["category"] == RiskCategory.ELEVATED_CONCERN.value
        assert len(data["url_findings"]) >= 2


@pytest.mark.asyncio
async def test_url_credentials_are_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/analyze", json={"url": "https://user:secret@example.org/path"})
        assert resp.status_code == 422
        assert set(resp.json()) == {"error", "message", "details"}
        assert "secret" not in resp.text


@pytest.mark.asyncio
async def test_non_web_url_scheme_is_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/analyze", json={"url": "ftp://example.org/invest"})
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_text_limit_is_enforced_by_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/analyze", json={"text": "a" * 20001})
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_url_analysis_does_not_fetch_or_return_path_and_query():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/analyze",
            json={"url": "https://127.0.0.1/private?access_token=do-not-return", "enable_network_check": True},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["inputs_analyzed"]["normalized_url"] == "https://127.0.0.1"
        assert "access_token" not in resp.text
        assert "private" not in data["inputs_analyzed"]["normalized_url"]
        statuses = {check["name"]: check["status"] for check in data["checks_unavailable"]}
        assert statuses["url_network_inspection"] == "skipped"


@pytest.mark.asyncio
async def test_feedback_submission(monkeypatch):
    from app.api.v1 import endpoints

    monkeypatch.setattr(endpoints.repository, "save_feedback", lambda feedback, timestamp: True)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # First perform an analysis
        analyze_resp = await client.post(
            "/api/v1/analyze",
            json={"text": "Guaranteed 10% daily return without risk.", "enable_network_check": False},
        )
        analysis_id = analyze_resp.json()["analysis_id"]

        # Submit feedback
        feedback_resp = await client.post(
            "/api/v1/feedback",
            json={
                "analysis_id": analysis_id,
                "is_helpful": True,
                "feedback_notes": "Very accurate detection of high daily returns.",
            },
        )
        assert feedback_resp.status_code == 200
        assert feedback_resp.json()["success"] is True
