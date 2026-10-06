"""API v1 router for risk analysis, educational sample cases, and optional feedback."""

from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, HTTPException, status

from app.models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    APIErrorResponse,
    SampleCase,
    RiskCategory,
    FeedbackRequest,
    FeedbackResponse,
)
from app.analyzers.text_analyzer import TextAnalyzer
from app.analyzers.url_analyzer import URLAnalyzer
from app.analyzers.synthesis import RiskSynthesizer
from app.storage.repository import repository

router = APIRouter()

text_analyzer = TextAnalyzer()
url_analyzer = URLAnalyzer()
synthesizer = RiskSynthesizer()

# Curated benchmark educational sample cases
SAMPLE_CASES: List[SampleCase] = [
    SampleCase(
        id="sample_hyip_guarantee",
        title="High-Yield Investment Program (HYIP)",
        description="A promotional message guaranteeing 3% daily returns with zero risk and urgent sign-up pressure.",
        sample_text=(
            "🚀 EXCLUSIVE CRYPTO WEALTH SYSTEM! Guaranteed 3% daily profits paid directly to your wallet. "
            "Our automated AI trading bot exploits quantum arbitrage with ZERO RISK to your capital! "
            "Double your money in just 24 days. Act now! Only 7 slots remaining before doors close forever. "
            "Send USDT (TRC-20) to our automated contract to start earning passive income today!"
        ),
        sample_url=None,
        expected_category=RiskCategory.ELEVATED_CONCERN,
        learning_notes="Exhibits multiple critical red flags: guaranteed high daily profits (mathematically absurd), claims of zero risk, urgency/scarcity, and irreversible crypto transfers.",
    ),
    SampleCase(
        id="sample_brand_impersonation",
        title="Lookalike Brand Impersonation Link",
        description="A deceptive domain using a high-abuse TLD and brand name to mimic a recognized cryptocurrency exchange.",
        sample_text="Claim your Binance anniversary giveaway! Log in now to double your BTC balance.",
        sample_url="https://binance-login-verify.top/claim-airdrop",
        expected_category=RiskCategory.ELEVATED_CONCERN,
        learning_notes="Demonstrates lookalike domain spoofing ('binance' on a non-official '.top' TLD) combined with suspicious path keywords ('claim-airdrop').",
    ),
    SampleCase(
        id="sample_pyramid_recruitment",
        title="Multi-Level Recruitment & Downline Scheme",
        description="A marketing pitch prioritizing tier commissions and recruiting downlines over any genuine asset management.",
        sample_text=(
            "Join our Global Wealth Matrix! Earn massive passive income not just from trades, but from your team. "
            "Receive a 15% direct referral bonus for every friend you invite, plus 5% downline override commissions "
            "across our 5-tier binary tree structure. Build your financial freedom empire!"
        ),
        sample_url=None,
        expected_category=RiskCategory.NEEDS_REVIEW,
        learning_notes="Highlights heavy reliance on recruitment, downlines, and multi-tier commissions, which is the foundational structure of Ponzi and pyramid schemes.",
    ),
    SampleCase(
        id="sample_lower_concern_legitimate",
        title="Standard Regulated Offering Prospectus",
        description="A realistic investment communication acknowledging market risks, asset volatility, and regulatory disclosures.",
        sample_text=(
            "The Vanguard S&P 500 Index Fund seeks to track the performance of a benchmark index that measures the "
            "investment return of large-capitalization stocks. Investments are subject to market risk, including the possible "
            "loss of principal. Past performance does not guarantee future results. Please read the summary prospectus "
            "carefully to review investment objectives, risks, charges, and expenses before investing."
        ),
        sample_url="https://investor.vanguard.com",
        expected_category=RiskCategory.LOWER_CONCERN,
        learning_notes="Demonstrates balanced disclosures and acknowledgement of principal risk. The URL is not checked for ownership or official status by this tool.",
    ),
    SampleCase(
        id="sample_insufficient_info",
        title="Vague / Insufficient Input",
        description="A very brief, ambiguous submission that lacks enough detail for a definitive assessment.",
        sample_text="Invest now for great returns!",
        sample_url=None,
        expected_category=RiskCategory.INSUFFICIENT_INFORMATION,
        learning_notes="Illustrates uncertainty handling. When input is too sparse to evaluate, the system flags insufficient information rather than guessing.",
    ),
]


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    responses={422: {"model": APIErrorResponse}},
)
async def analyze_investment_offer(request: AnalysisRequest) -> AnalysisResponse:
    """
    Analyze promotional text and URL structure without contacting submitted websites.
    Returns a heuristic assessment with evidence and uncertainty.
    """
    raw_text = request.text
    raw_url = request.url

    # Validate that at least one input is provided
    if (not raw_text or not raw_text.strip()) and (not raw_url or not raw_url.strip()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one input (promotional text or website URL) must be supplied for analysis.",
        )

    # 1. Text Analysis
    text_findings = []
    text_meta = {"length": 0, "word_count": 0, "is_sufficient": False}
    if raw_text:
        text_findings, text_meta = text_analyzer.analyze(raw_text)

    # 2. URL Lexical Analysis
    url_findings = []
    url_meta = {"is_valid": False}
    if raw_url:
        url_findings, url_meta = url_analyzer.analyze(raw_url)

    # Live retrieval is intentionally unavailable: lexical analysis never contacts submitted hosts.
    network_findings = []
    network_status = None
    if raw_url:
        from app.models.schemas import CheckStatusItem
        network_status = CheckStatusItem(
            name="url_network_inspection",
            display_name="Live URL Network Inspection",
            status="skipped",
            details="Not performed in this version; the submitted website is not contacted.",
        )

    # 4. Synthesize all observations into final calibrated response
    response = synthesizer.synthesize(
        text_findings=text_findings,
        url_findings=url_findings,
        network_findings=network_findings,
        text_meta=text_meta,
        url_meta=url_meta,
        network_status=network_status,
        raw_text=raw_text,
        raw_url=raw_url,
    )

    return response


@router.get("/sample-cases", response_model=List[SampleCase])
async def get_sample_cases() -> List[SampleCase]:
    """Retrieve educational sample cases for testing and demonstration."""
    return SAMPLE_CASES


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackRequest) -> FeedbackResponse:
    """Store optional user feedback; analysis input itself is not persisted."""
    success = repository.save_feedback(feedback, datetime.now(timezone.utc).isoformat())
    if not success:
        raise HTTPException(status_code=500, detail="Feedback could not be recorded.")
    return FeedbackResponse(success=True, message="Thank you. Your feedback was recorded.")
