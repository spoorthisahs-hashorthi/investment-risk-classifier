/**
 * TypeScript type definitions for the Risk Classification of Online Investment Schemes application.
 * Mirrors Python backend Pydantic schemas.
 */

export type SeverityLevel = 'low' | 'medium' | 'high' | 'critical';

export type RiskCategory =
  | 'lower_concern'
  | 'needs_review'
  | 'elevated_concern'
  | 'insufficient_information';

export type UncertaintyLevel = 'low' | 'medium' | 'high';

export type FindingCategory =
  | 'financial_promise'
  | 'risk_claim'
  | 'urgency_scarcity'
  | 'recruitment_mlm'
  | 'payment_method'
  | 'authority_endorsement'
  | 'vague_mechanism'
  | 'domain_reputation'
  | 'lexical_anomaly'
  | 'network_security'
  | 'general';

export interface FindingItem {
  id: string;
  title: string;
  category: FindingCategory;
  severity: SeverityLevel;
  explanation: string;
  evidence: string;
  start_offset?: number | null;
  end_offset?: number | null;
  source: string;
}

export interface CheckStatusItem {
  name: string;
  display_name: string;
  status: 'completed' | 'unavailable' | 'skipped' | 'failed';
  details?: string | null;
}

export interface VerificationStep {
  step: number;
  title: string;
  description: string;
  action_url?: string | null;
  official_registry?: string | null;
}

export interface InputsAnalyzed {
  has_text: boolean;
  text_length: number;
  text_word_count: number;
  has_url: boolean;
  normalized_url?: string | null;
  domain?: string | null;
}

export interface AnalysisRequest {
  text?: string;
  url?: string;
  enable_network_check?: boolean;
}

export interface AnalysisResponse {
  analysis_id: string;
  timestamp: string;
  category: RiskCategory;
  category_display: string;
  risk_score: number;
  uncertainty_level: UncertaintyLevel;
  uncertainty_explanation: string;
  summary: string;
  disclaimer: string;
  inputs_analyzed: InputsAnalyzed;
  text_findings: FindingItem[];
  url_findings: FindingItem[];
  checks_performed: CheckStatusItem[];
  checks_unavailable: CheckStatusItem[];
  verification_checklist: VerificationStep[];
}

export interface FeedbackRequest {
  analysis_id: string;
  is_helpful: boolean;
  feedback_notes?: string;
  user_classification?: string;
}

export interface FeedbackResponse {
  success: boolean;
  message: string;
}

export interface SampleCase {
  id: string;
  title: string;
  description: string;
  sample_text?: string | null;
  sample_url?: string | null;
  expected_category: RiskCategory;
  learning_notes: string;
}
