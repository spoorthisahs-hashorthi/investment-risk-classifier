"""Pydantic schemas and typed contracts for Risk Classification API."""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from urllib.parse import urlparse


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskCategory(str, Enum):
    LOWER_CONCERN = "lower_concern"
    NEEDS_REVIEW = "needs_review"
    ELEVATED_CONCERN = "elevated_concern"
    INSUFFICIENT_INFORMATION = "insufficient_information"


class UncertaintyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class FindingCategory(str, Enum):
    FINANCIAL_PROMISE = "financial_promise"
    RISK_CLAIM = "risk_claim"
    URGENCY_SCARCITY = "urgency_scarcity"
    RECRUITMENT_MLM = "recruitment_mlm"
    PAYMENT_METHOD = "payment_method"
    AUTHORITY_ENDORSEMENT = "authority_endorsement"
    VAGUE_MECHANISM = "vague_mechanism"
    DOMAIN_REPUTATION = "domain_reputation"
    LEXICAL_ANOMALY = "lexical_anomaly"
    NETWORK_SECURITY = "network_security"
    GENERAL = "general"


class FindingItem(BaseModel):
    id: str = Field(..., description="Unique machine-readable identifier for the finding rule")
    title: str = Field(..., description="Short user-friendly headline for the finding")
    category: FindingCategory = Field(..., description="The functional category of the indicator")
    severity: SeverityLevel = Field(..., description="Assessed indicator severity")
    explanation: str = Field(..., description="Plain-language explanation of why this is a warning signal")
    evidence: str = Field(..., description="Observable evidence snippet or property observed")
    start_offset: Optional[int] = Field(None, description="Start character offset in source text if applicable")
    end_offset: Optional[int] = Field(None, description="End character offset in source text if applicable")
    source: str = Field(..., description="Analysis module that emitted this finding: 'text_analysis', 'url_analysis', or 'network_inspection'")


class CheckStatusItem(BaseModel):
    name: str = Field(..., description="System identifier of the check")
    display_name: str = Field(..., description="Human-readable title of the check")
    status: str = Field(..., description="'completed', 'unavailable', 'skipped', or 'failed'")
    details: Optional[str] = Field(None, description="Summary of outcome or reason check was skipped/unavailable")


class VerificationStep(BaseModel):
    step: int = Field(..., description="Sequential order number")
    title: str = Field(..., description="Title of the recommended step")
    description: str = Field(..., description="Actionable advice on how to verify this aspect")
    action_url: Optional[str] = Field(None, description="Optional official link to regulator or check tool")
    official_registry: Optional[str] = Field(None, description="Name of the official register or resource")


class InputsAnalyzed(BaseModel):
    has_text: bool
    text_length: int
    text_word_count: int
    has_url: bool
    normalized_url: Optional[str] = None
    domain: Optional[str] = None


class AnalysisRequest(BaseModel):
    text: Optional[str] = Field(None, max_length=20000, description="Pasted promotional or marketing text to evaluate")
    url: Optional[str] = Field(None, max_length=2048, description="URL of investment website or social link")
    enable_network_check: bool = Field(True, description="Whether to perform bounded SSRF-safe network probing for URL")

    @field_validator("text", mode="before")
    @classmethod
    def clean_text(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and isinstance(v, str):
            v_stripped = v.strip()
            return v_stripped if v_stripped else None
        return None

    @field_validator("url", mode="before")
    @classmethod
    def clean_url(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and isinstance(v, str):
            v_stripped = v.strip()
            if not v_stripped:
                return None
            candidate = v_stripped if "://" in v_stripped else f"https://{v_stripped}"
            parsed = urlparse(candidate)
            if parsed.scheme.lower() not in ("http", "https") or not parsed.hostname:
                raise ValueError("Enter a complete HTTP or HTTPS website URL")
            if parsed.username is not None or parsed.password is not None:
                raise ValueError("URLs containing embedded username or password are not accepted")
            try:
                parsed.port
            except ValueError as exc:
                raise ValueError("The URL port is invalid") from exc
            return candidate
        return None


class AnalysisResponse(BaseModel):
    analysis_id: str = Field(..., description="Unique UUID for this analysis event")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    category: RiskCategory = Field(..., description="Assigned risk category")
    category_display: str = Field(..., description="Human-readable category badge text")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Calibrated heuristic risk indicator score between 0.0 and 1.0")
    uncertainty_level: UncertaintyLevel = Field(..., description="Assessment uncertainty")
    uncertainty_explanation: str = Field(..., description="Plain-language explanation of why uncertainty is at this level")
    summary: str = Field(..., description="Comprehensive plain-language synthesis of observations")
    disclaimer: str = Field(..., description="Mandatory educational and legal limitation disclaimer")
    
    inputs_analyzed: InputsAnalyzed
    text_findings: List[FindingItem] = Field(default_factory=list, description="Findings extracted from promotional text")
    url_findings: List[FindingItem] = Field(default_factory=list, description="Findings extracted from URL and domain analysis")
    
    checks_performed: List[CheckStatusItem] = Field(default_factory=list)
    checks_unavailable: List[CheckStatusItem] = Field(default_factory=list)
    verification_checklist: List[VerificationStep] = Field(default_factory=list)


class FeedbackRequest(BaseModel):
    analysis_id: str
    is_helpful: bool
    feedback_notes: Optional[str] = Field(None, max_length=1000)
    user_classification: Optional[str] = None


class FeedbackResponse(BaseModel):
    success: bool
    message: str


class SampleCase(BaseModel):
    id: str
    title: str
    description: str
    sample_text: Optional[str] = None
    sample_url: Optional[str] = None
    expected_category: RiskCategory
    learning_notes: str
