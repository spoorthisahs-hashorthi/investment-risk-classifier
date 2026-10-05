"""Synthesis module: Combines text and URL findings into an explainable, uncertainty-calibrated assessment."""

import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple

from app.models.schemas import (
    AnalysisResponse,
    FindingItem,
    FindingCategory,
    CheckStatusItem,
    RiskCategory,
    SeverityLevel,
    UncertaintyLevel,
    VerificationStep,
    InputsAnalyzed,
)

# Standard official regulatory registers
STANDARD_REGISTERS = [
    {
        "name": "US SEC EDGAR & FINRA BrokerCheck",
        "url": "https://brokercheck.finra.org/",
        "jurisdiction": "United States",
    },
    {
        "name": "UK FCA Financial Services Register",
        "url": "https://register.fca.org.uk/",
        "jurisdiction": "United Kingdom",
    },
    {
        "name": "Australian Securities and Investments Commission (ASIC)",
        "url": "https://moneysmart.gov.au/check-and-report-scams/investor-alert-list",
        "jurisdiction": "Australia",
    },
    {
        "name": "SEBI / Reserve Bank Registry",
        "url": "https://www.sebi.gov.in/",
        "jurisdiction": "India",
    },
    {
        "name": "IOSCO International Investor Alerts Portal",
        "url": "https://www.iosco.org/investor_protection/?subsection=investor_alerts_portal",
        "jurisdiction": "International",
    },
]

MANDATORY_DISCLAIMER = (
    "This automated screening report is strictly an educational tool to help users identify potential warning signs. "
    "It is NOT financial advice, legal advice, a definitive fraud determination, or a guarantee of safety. "
    "Scammers continuously evolve their language, and legitimate firms may occasionally trigger pattern matches. "
    "The absence of detected indicators does NOT prove an investment is safe. Always verify the entity directly with "
    "your national securities regulator before transferring funds."
)


class RiskSynthesizer:
    """Synthesizes multiple finding streams, calibrates uncertainty, and builds explainable output."""

    def synthesize(
        self,
        text_findings: List[FindingItem],
        url_findings: List[FindingItem],
        network_findings: List[FindingItem],
        text_meta: Dict[str, Any],
        url_meta: Dict[str, Any],
        network_status: Optional[CheckStatusItem],
        raw_text: Optional[str],
        raw_url: Optional[str],
    ) -> AnalysisResponse:
        now_iso = datetime.now(timezone.utc).isoformat()
        analysis_id = str(uuid.uuid4())

        # Merge network findings into url_findings collection
        all_url_findings = list(url_findings) + list(network_findings)

        has_text = bool(raw_text and raw_text.strip())
        has_url = bool(raw_url and raw_url.strip())
        word_count = text_meta.get("word_count", 0)

        # 1. Determine Insufficient Information condition
        # If no input provided, or text is extremely minimal (< 8 words) with no URL
        if (not has_text and not has_url) or (has_text and word_count < 8 and not has_url and not text_findings):
            return self._build_insufficient_info_response(
                analysis_id=analysis_id,
                timestamp=now_iso,
                has_text=has_text,
                text_meta=text_meta,
                has_url=has_url,
                url_meta=url_meta,
                network_status=network_status,
                raw_url=raw_url,
            )

        # 2. Score Calculation (Diminishing returns weighted sum)
        weights = {
            SeverityLevel.CRITICAL: 0.40,
            SeverityLevel.HIGH: 0.25,
            SeverityLevel.MEDIUM: 0.12,
            SeverityLevel.LOW: 0.05,
        }

        all_findings = text_findings + all_url_findings
        total_raw_weight = sum(weights.get(f.severity, 0.05) for f in all_findings)
        
        # Non-linear asymptotic curve: 1.0 - 1.0 / (1.0 + raw_weight)
        normalized_risk_score = round(1.0 - (1.0 / (1.0 + total_raw_weight * 1.5)), 3)

        critical_count = sum(1 for f in all_findings if f.severity == SeverityLevel.CRITICAL)
        high_count = sum(1 for f in all_findings if f.severity == SeverityLevel.HIGH)
        medium_count = sum(1 for f in all_findings if f.severity == SeverityLevel.MEDIUM)

        # 3. Categorization logic
        if critical_count >= 1 or normalized_risk_score >= 0.48 or (high_count >= 2):
            category = RiskCategory.ELEVATED_CONCERN
            category_display = "Elevated Concern"
        elif high_count >= 1 or medium_count >= 2 or normalized_risk_score >= 0.20:
            category = RiskCategory.NEEDS_REVIEW
            category_display = "Needs Review"
        else:
            category = RiskCategory.LOWER_CONCERN
            category_display = "Lower Concern"

        # 4. Uncertainty Calibration
        uncertainty_level, uncertainty_explanation = self._calibrate_uncertainty(
            has_text=has_text,
            has_url=has_url,
            word_count=word_count,
            network_status=network_status,
            category=category,
        )

        # 5. Explanatory Summary Generation
        summary = self._generate_summary(
            category=category,
            critical_count=critical_count,
            high_count=high_count,
            medium_count=medium_count,
            text_findings=text_findings,
            url_findings=all_url_findings,
            has_text=has_text,
            has_url=has_url,
        )

        # 6. Checks performed and unavailable status
        checks_performed: List[CheckStatusItem] = []
        checks_unavailable: List[CheckStatusItem] = []

        if has_text:
            checks_performed.append(
                CheckStatusItem(
                    name="text_indicator_scan",
                    display_name="Text Language & Indicator Analysis",
                    status="completed",
                    details=f"Analyzed {word_count} words; identified {len(text_findings)} notable indicator(s).",
                )
            )

        if has_url:
            checks_performed.append(
                CheckStatusItem(
                    name="url_lexical_analysis",
                    display_name="URL Structure & Domain Brand Analysis",
                    status="completed",
                    details=f"Analyzed scheme, host, TLD, brand similarity, and syntax; found {len(url_findings)} link signal(s).",
                )
            )
            if network_status:
                checks_performed.append(network_status)

        # Explicitly document unavailable external checks so users know what was not checked
        checks_unavailable.append(
            CheckStatusItem(
                name="official_regulatory_api_lookup",
                display_name="Automated Government Regulatory Database Lookup",
                status="unavailable",
                details="Authoritative national registers (e.g. SEC EDGAR, FINRA, UK FCA) require jurisdiction-specific entity IDs and manual legal review.",
            )
        )
        checks_unavailable.append(
            CheckStatusItem(
                name="domain_whois_registration_age",
                display_name="Authoritative WHOIS Domain Age Lookup",
                status="unavailable",
                details="Direct WHOIS queries are restricted or rate-limited by registry RDAP quotas in default configuration.",
            )
        )

        # 7. Actionable Verification Checklist
        verification_checklist = self._build_verification_checklist(
            category=category,
            text_findings=text_findings,
            url_findings=all_url_findings,
            domain=url_meta.get("registered_domain") or url_meta.get("host"),
        )

        inputs_analyzed = InputsAnalyzed(
            has_text=has_text,
            text_length=text_meta.get("length", 0),
            text_word_count=word_count,
            has_url=has_url,
            normalized_url=url_meta.get("normalized_url"),
            domain=url_meta.get("host"),
        )

        return AnalysisResponse(
            analysis_id=analysis_id,
            timestamp=now_iso,
            category=category,
            category_display=category_display,
            risk_score=normalized_risk_score,
            uncertainty_level=uncertainty_level,
            uncertainty_explanation=uncertainty_explanation,
            summary=summary,
            disclaimer=MANDATORY_DISCLAIMER,
            inputs_analyzed=inputs_analyzed,
            text_findings=text_findings,
            url_findings=all_url_findings,
            checks_performed=checks_performed,
            checks_unavailable=checks_unavailable,
            verification_checklist=verification_checklist,
        )

    def _build_insufficient_info_response(
        self,
        analysis_id: str,
        timestamp: str,
        has_text: bool,
        text_meta: Dict[str, Any],
        has_url: bool,
        url_meta: Dict[str, Any],
        network_status: Optional[CheckStatusItem],
        raw_url: Optional[str],
    ) -> AnalysisResponse:
        summary = (
            "Insufficient information provided to conduct a meaningful risk screening. "
            "Please provide detailed promotional text (such as marketing emails, social media pitches, or chat messages) "
            "or a complete website URL so linguistic and domain patterns can be evaluated."
        )

        return AnalysisResponse(
            analysis_id=analysis_id,
            timestamp=timestamp,
            category=RiskCategory.INSUFFICIENT_INFORMATION,
            category_display="Insufficient Information",
            risk_score=0.0,
            uncertainty_level=UncertaintyLevel.HIGH,
            uncertainty_explanation="Uncertainty is very high because the submitted content lacks sufficient text or link context to evaluate against risk patterns.",
            summary=summary,
            disclaimer=MANDATORY_DISCLAIMER,
            inputs_analyzed=InputsAnalyzed(
                has_text=has_text,
                text_length=text_meta.get("length", 0),
                text_word_count=text_meta.get("word_count", 0),
                has_url=has_url,
                normalized_url=raw_url,
                domain=url_meta.get("host"),
            ),
            text_findings=[],
            url_findings=[],
            checks_performed=[
                CheckStatusItem(
                    name="input_validation",
                    display_name="Input Sufficiency Check",
                    status="completed",
                    details="Evaluated input length and content suitability.",
                )
            ],
            checks_unavailable=[
                CheckStatusItem(
                    name="risk_analysis",
                    display_name="Risk Indicator Scan",
                    status="skipped",
                    details="Skipped due to lack of substantive input.",
                )
            ],
            verification_checklist=[
                VerificationStep(
                    step=1,
                    title="Obtain Written Documentation",
                    description="Request a formal prospectus, registered product disclosure statement, or company registration details from the offering party.",
                ),
                VerificationStep(
                    step=2,
                    title="Search National Regulators",
                    description="Check the official financial regulator in your country to confirm if the promoter or firm is authorized.",
                    action_url="https://brokercheck.finra.org/",
                    official_registry="FINRA BrokerCheck / SEC",
                ),
            ],
        )

    def _calibrate_uncertainty(
        self,
        has_text: bool,
        has_url: bool,
        word_count: int,
        network_status: Optional[CheckStatusItem],
        category: RiskCategory,
    ) -> Tuple[UncertaintyLevel, str]:
        if has_text and has_url and word_count >= 50 and network_status and network_status.status == "completed":
            return (
                UncertaintyLevel.LOW,
                "Both comprehensive promotional text and a reachable URL were evaluated. Uncertainty regarding pattern detection is low, although official regulator status still requires manual confirmation.",
            )
        elif (has_text and word_count >= 30) or (has_url and network_status and network_status.status == "completed"):
            return (
                UncertaintyLevel.MEDIUM,
                "Partial information was evaluated (either text without a link, or a link with limited surrounding promotional context). Uncertainty is moderate.",
            )
        else:
            return (
                UncertaintyLevel.HIGH,
                "Limited data was submitted. While preliminary indicators have been scanned, lack of complete promotional context or live website content leaves notable uncertainty.",
            )

    def _generate_summary(
        self,
        category: RiskCategory,
        critical_count: int,
        high_count: int,
        medium_count: int,
        text_findings: List[FindingItem],
        url_findings: List[FindingItem],
        has_text: bool,
        has_url: bool,
    ) -> str:
        total = critical_count + high_count + medium_count

        if category == RiskCategory.ELEVATED_CONCERN:
            top_reasons = []
            for f in (text_findings + url_findings)[:3]:
                top_reasons.append(f.title.lower())
            reasons_str = ", ".join(top_reasons)
            return (
                f"Elevated concern identified. The submission triggered {total} significant warning indicator(s), "
                f"including {reasons_str}. Such patterns are strongly characteristic of high-risk investment schemes, "
                f"unrealistic return guarantees, or brand impersonation. Exercise extreme caution and do not commit funds "
                f"without independent regulatory verification."
            )

        elif category == RiskCategory.NEEDS_REVIEW:
            return (
                f"Needs careful review. The analysis detected {total} moderate risk indicator(s) that warrant further due diligence "
                f"(such as aggressive promotion, urgency tactics, or non-standard link properties). "
                f"While these patterns do not prove fraud, they deviate from standard institutional practices."
            )

        else:  # LOWER_CONCERN
            return (
                "Lower concern based on available pattern analysis. No prominent high-risk promotional triggers or suspicious "
                "domain anomalies were identified in the submitted material. IMPORTANT: Absence of detected indicators does NOT "
                "guarantee the safety or legitimacy of an investment. Fraudulent entities can use polished language and standard domains. "
                "Always verify registration on official government databases."
            )

    def _build_verification_checklist(
        self,
        category: RiskCategory,
        text_findings: List[FindingItem],
        url_findings: List[FindingItem],
        domain: Optional[str],
    ) -> List[VerificationStep]:
        steps: List[VerificationStep] = []
        step_num = 1

        # Check for specific triggers
        has_crypto = any(f.category == FindingCategory.PAYMENT_METHOD for f in text_findings)
        has_impersonation = any(f.id in ("url_brand_impersonation", "url_typosquatting") for f in url_findings)
        has_guarantee = any(f.id in ("text_guaranteed_profit", "text_unrealistic_rate") for f in text_findings)
        has_mlm = any(f.category == FindingCategory.RECRUITMENT_MLM for f in text_findings)

        # Step 1: Regulatory Verification
        steps.append(
            VerificationStep(
                step=step_num,
                title="Verify on Official Regulatory Registry",
                description=(
                    "Check whether the company and its representatives are authorized to offer securities or financial products. "
                    "In the US, use FINRA BrokerCheck or SEC EDGAR; in the UK, use the FCA Register; in other regions, consult your national securities authority."
                ),
                action_url="https://brokercheck.finra.org/",
                official_registry="Securities Regulator Register",
            )
        )
        step_num += 1

        # Step 2: Domain verification / Impersonation check
        if has_impersonation:
            steps.append(
                VerificationStep(
                    step=step_num,
                    title="Direct Domain & Contact Verification",
                    description=(
                        "Do not click links received in messages. Independently search for the official organization through a trusted search engine "
                        "and compare the exact domain name. Impersonators register lookalikes with extra words or foreign TLDs."
                    ),
                    action_url=None,
                )
            )
            step_num += 1
        elif domain:
            steps.append(
                VerificationStep(
                    step=step_num,
                    title=f"Verify Contact Details on Official Domain ({domain})",
                    description=(
                        "Cross-reference the phone numbers and physical address listed on the official regulator's filing "
                        "with the contact details provided in the promotion. Fraudsters often clone real firm names but provide their own contact channels."
                    ),
                )
            )
            step_num += 1

        # Step 3: Crypto / Payment Warning
        if has_crypto:
            steps.append(
                VerificationStep(
                    step=step_num,
                    title="Scrutinize Cryptocurrency & Direct Wallet Payments",
                    description=(
                        "Cryptocurrency transactions are irrevocable. Once assets leave your personal wallet, no bank, ombudsman, "
                        "or regulator can reverse the transfer. Legitimate investment managers rarely require direct crypto deposit to individual addresses."
                    ),
                )
            )
            step_num += 1

        # Step 4: Guarantee & Math reality check
        if has_guarantee:
            steps.append(
                VerificationStep(
                    step=step_num,
                    title="Independent Mathematical Reality Check",
                    description=(
                        "Remember that central bank risk-free rates (e.g., US Treasury yields) typically range around 4-5% annually. "
                        "Any scheme offering 1% daily, 10% weekly, or 'guaranteed' high returns is offering yields hundreds of times market rates, "
                        "which is statistically unsustainable without using incoming investor funds (Ponzi mechanics)."
                    ),
                )
            )
            step_num += 1

        # Step 5: MLM / Pyramid check
        if has_mlm:
            steps.append(
                VerificationStep(
                    step=step_num,
                    title="Examine Revenue Source (Product vs. Recruitment)",
                    description=(
                        "Determine whether profits stem from genuine commercial sales or from fees paid by new participants. "
                        "If you are paid primarily for recruiting others into tiers or binary trees, the structure exhibits classic pyramid scheme characteristics."
                    ),
                )
            )
            step_num += 1

        # Final Step: Consult Licensed Advisor
        steps.append(
            VerificationStep(
                step=step_num,
                title="Consult an Independent Licensed Financial Advisor",
                description=(
                    "Speak with an independent, fee-only financial planner or legal counsel who is not affiliated with the promoter before signing contracts or transferring capital."
                ),
            )
        )

        return steps
