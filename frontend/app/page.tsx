'use client';

import { useState } from 'react';
import AnalysisForm from '../components/AnalysisForm';
import FindingsList from '../components/FindingsList';
import HighlightedTextViewer from '../components/HighlightedTextViewer';
import RiskResultCard from '../components/RiskResultCard';
import SystemChecksAccordion from '../components/SystemChecksAccordion';
import VerificationChecklist from '../components/VerificationChecklist';
import { analyzeInvestment, ApiError } from '../lib/api';
import { AnalysisRequest, AnalysisResponse } from '../lib/types';

export default function HomePage() {
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [submittedText, setSubmittedText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function analyze(request: AnalysisRequest) {
    setLoading(true);
    setError('');
    setResult(null);
    setSubmittedText(request.text || '');
    try {
      setResult(await analyzeInvestment(request));
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : 'The analysis could not be completed. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setResult(null);
    setSubmittedText('');
    setError('');
  }

  return (
    <div className="mx-auto max-w-5xl space-y-8">
      <section className="space-y-3">
        <p className="text-sm font-semibold uppercase tracking-[0.16em] text-blue-700">A first-pass review</p>
        <h2 className="max-w-3xl text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">Pause. Check the claims. Verify the source.</h2>
        <p className="max-w-3xl text-base leading-7 text-slate-600">Screen an investment promotion for common language and URL warning signs. Results explain the evidence and what this tool could not verify.</p>
      </section>
      <AnalysisForm onAnalyze={analyze} isLoading={loading} sampleCases={[]} />
      {loading && <p role="status" className="rounded-xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-900">Reviewing the submitted text and link…</p>}
      {error && <div role="alert" className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-900">{error}</div>}
      {result && <section aria-live="polite" className="space-y-6">
        <RiskResultCard result={result} onReset={reset} />
        <FindingsList textFindings={result.text_findings} urlFindings={result.url_findings} hasText={result.inputs_analyzed.has_text} hasUrl={result.inputs_analyzed.has_url} />
        {submittedText && <HighlightedTextViewer rawText={submittedText} findings={result.text_findings} />}
        <VerificationChecklist steps={result.verification_checklist} />
        <SystemChecksAccordion checksPerformed={result.checks_performed} checksUnavailable={result.checks_unavailable} />
      </section>}
      <section id="educational-guide" className="grid gap-5 rounded-2xl border border-slate-200 bg-white p-6 sm:grid-cols-2">
        <div><h3 className="font-semibold text-slate-900">What this checks</h3><p className="mt-2 text-sm leading-6 text-slate-600">A transparent rules based scan for return promises, risk claims, urgency, recruitment language, payment requests, suspicious URL structure, and selected brand lookalikes.</p></div>
        <div><h3 className="font-semibold text-slate-900">What it cannot establish</h3><p className="mt-2 text-sm leading-6 text-slate-600">It does not determine whether an offer or firm is legitimate, check government registers, or fetch the linked page. One warning sign is not proof; no warning signs is not proof of safety.</p></div>
      </section>
    </div>
  );
}
