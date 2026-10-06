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
        # Repeated phrase matches remain visible as evidence, but a single rule type
        # from one source contributes only once to the aggregate risk indicator.
        scored_findings = self._unique_indicators(all_findings)
        total_raw_weight = sum(weights.get(f.severity, 0.05) for f in scored_findings)
        
        # Non-linear asymptotic curve: 1.0 - 1.0 / (1.0 + raw_weight)
        normalized_risk_score = round(1.0 - (1.0 / (1.0 + total_raw_weight * 1.5)), 3)

        critical_count = sum(1 for f in scored_findings if f.severity == SeverityLevel.CRITICAL)
        high_count = sum(1 for f in scored_findings if f.severity == SeverityLevel.HIGH)
        medium_count = sum(1 for f in scored_findings if f.severity == SeverityLevel.MEDIUM)

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
            text_findings=self._unique_indicators(text_findings),
            url_findings=self._unique_indicators(all_url_findings),
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
                if network_status.status == "completed":
                    checks_performed.append(network_status)
                else:
                    checks_unavailable.append(network_status)

        # Explicitly document unavailable external checks so users know what was not checked
        checks_unavailable.append(
            CheckStatusItem(
                name="official_regulatory_api_lookup",
                display_name="Automated Government Regulatory Database Lookup",
                status="unavailable",
                details="No jurisdiction was selected and no official registry integration is configured; check the relevant regulator directly.",
            )
        )
        checks_unavailable.append(
            CheckStatusItem(
                name="domain_whois_registration_age",
                display_name="Authoritative WHOIS Domain Age Lookup",
                status="unavailable",
                details="No authoritative WHOIS/RDAP domain-age source is configured for this project.",
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

    @staticmethod
    def _unique_indicators(findings: List[FindingItem]) -> List[FindingItem]:
        unique: List[FindingItem] = []
        seen = set()
        for finding in findings:
            key = (finding.source, finding.id)
            if key not in seen:
                seen.add(key)
                unique.append(finding)
        return unique

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
                normalized_url=url_meta.get("normalized_url"),
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
                    official_registry="Your national securities regulator",
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
                "Substantial promotional text and a live URL inspection were completed. This level reflects pattern coverage only; official authorization still requires separate confirmation.",
            )
        elif (has_text and word_count >= 30) or (has_url and network_status and network_status.status == "completed"):
            return (
                UncertaintyLevel.MEDIUM,
                "A substantial text sample was evaluated, but official status and any unvisited web page remain unverified. Uncertainty is moderate.",
            )
        else:
            return (
                UncertaintyLevel.HIGH,
                "Limited data was submitted. The URL was not visited, and complete promotional context or official status remains unverified.",
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
                f"Elevated concern under this heuristic. The submission matched {total} distinct higher-severity indicator type(s), "
                f"including {reasons_str}. These observations warrant careful independent verification but do not establish fraud. "
                f"Do not transfer funds until you have verified the offer and recipient through trusted sources."
            )

        elif category == RiskCategory.NEEDS_REVIEW:
            return (
                f"Needs review under this heuristic. The analysis detected {total} distinct indicator type(s) that warrant further due diligence "
                f"(such as aggressive promotion, urgency tactics, or non-standard link properties). These patterns do not prove fraud."
            )

        else:  # LOWER_CONCERN
            observed = self._unique_indicators(text_findings + url_findings)
            if observed:
                signal_names = ", ".join(f.title.lower() for f in observed[:3])
                return (
                    f"Lower concern overall under the current heuristic, with {len(observed)} lower-severity indicator type(s) observed, "
                    f"including {signal_names}. These signals do not prove fraud; verify the offer independently. "
                    "No critical or high-severity rule was triggered."
                )
            return (
                "Lower concern under the rules applied to the submitted material. No listed warning indicator was detected, "
                "but this does not establish that the offer or firm is legitimate or safe. Independently verify the firm and the specific offer with your regulator."
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
                official_registry="Your national securities regulator",
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
                        "Compare the promised return, timeframe, and stated risks with independent information from your regulator or a qualified adviser. "
                        "Very high fixed returns described as guaranteed warrant careful scrutiny, but this pattern alone does not reveal how the offer is funded."
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
