-- Supabase Migration: 20261005_init_schema.sql
-- Scheme Risk Classification: Schema, Constraints, Indexes, and Row Level Security

-- 1. Table: risk_analyses
CREATE TABLE IF NOT EXISTS public.risk_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    category TEXT NOT NULL CHECK (category IN ('lower_concern', 'needs_review', 'elevated_concern', 'insufficient_information')),
    risk_score NUMERIC(4, 3) NOT NULL CHECK (risk_score >= 0.0 AND risk_score <= 1.0),
    uncertainty_level TEXT NOT NULL CHECK (uncertainty_level IN ('low', 'medium', 'high')),
    text_hash TEXT, -- SHA-256 hash of submitted text for privacy (raw text is not retained)
    domain TEXT,    -- Truncated domain host evaluated
    findings_count INTEGER NOT NULL DEFAULT 0,
    report_json JSONB NOT NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_risk_analyses_created_at ON public.risk_analyses (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_risk_analyses_category ON public.risk_analyses (category);
CREATE INDEX IF NOT EXISTS idx_risk_analyses_domain ON public.risk_analyses (domain);

-- 2. Table: analysis_feedback
CREATE TABLE IF NOT EXISTS public.analysis_feedback (
    id BIGSERIAL PRIMARY KEY,
    analysis_id UUID NOT NULL REFERENCES public.risk_analyses(id) ON DELETE CASCADE,
    is_helpful BOOLEAN NOT NULL,
    feedback_notes TEXT CHECK (char_length(feedback_notes) <= 1000),
    user_classification TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_analysis_feedback_analysis_id ON public.analysis_feedback (analysis_id);

-- 3. Row Level Security (RLS)
ALTER TABLE public.risk_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analysis_feedback ENABLE ROW LEVEL SECURITY;

-- No public or authenticated-client policies are defined. Analysis reports and
-- feedback remain inaccessible through client roles; a future backend service
-- must define narrow insert/read policies before this draft is used.
