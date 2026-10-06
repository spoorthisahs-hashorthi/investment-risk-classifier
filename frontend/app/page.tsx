'use client';

import { useEffect, useState } from 'react';
import { ArrowDown, ArrowRight, FileSearch, Fingerprint, ShieldCheck } from 'lucide-react';
import AnalysisForm from '../components/AnalysisForm';
import FindingsList from '../components/FindingsList';
import HighlightedTextViewer from '../components/HighlightedTextViewer';
import RiskResultCard from '../components/RiskResultCard';
import SystemChecksAccordion from '../components/SystemChecksAccordion';
import VerificationChecklist from '../components/VerificationChecklist';
import { analyzeInvestment, ApiError, fetchSampleCases } from '../lib/api';
import { AnalysisRequest, AnalysisResponse, SampleCase } from '../lib/types';

export default function HomePage() {
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [submittedText, setSubmittedText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [sampleCases, setSampleCases] = useState<SampleCase[]>([]);

  useEffect(() => { void fetchSampleCases().then(setSampleCases).catch(() => setSampleCases([])); }, []);

  async function analyze(request: AnalysisRequest) {
    setLoading(true);
    setError('');
    setResult(null);
    setSubmittedText(request.text || '');
    try {
      const response = await analyzeInvestment(request);
      setResult(response);
      window.setTimeout(() => document.getElementById('analysis-results')?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 80);
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
    document.getElementById('screening-form')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  return (
    <div className="app-shell">
      <section className="hero-panel">
        <div className="hero-copy">
          <div className="eyebrow"><span className="eyebrow-dot" /> A clearer first step before you invest</div>
          <h2>Take a closer look<br /><span>before you send money.</span></h2>
          <p>Review an investment pitch for common warning signs. See the exact phrases that triggered a flag, understand the limits of this scan, and get practical steps for checking the firm yourself.</p>
          <a className="hero-link" href="#screening-form">Start a free screening <ArrowDown size={16} /></a>
          <div className="hero-proof"><span><ShieldCheck size={16} /> No account needed</span><i /><span><Fingerprint size={16} /> Analysis isn’t saved</span></div>
        </div>
        <div className="hero-art" aria-hidden="true">
          <div className="orbit orbit-one" /><div className="orbit orbit-two" />
          <div className="hero-icon"><FileSearch size={47} strokeWidth={1.4} /></div>
          <div className="float-card float-top"><span className="float-mark mark-amber">!</span><span><b>Claims reviewed</b><small>Returns · urgency · payments</small></span></div>
          <div className="float-card float-bottom"><span className="float-mark mark-green"><ShieldCheck size={17} /></span><span><b>Evidence explained</b><small>Transparent rule-based checks</small></span></div>
        </div>
      </section>

      <section className="how-strip" aria-label="How the screening works">
        <div><span className="step-number">01</span><span><b>Paste the pitch</b><small>Text, link, or both</small></span></div>
        <ArrowRight className="step-arrow" size={18} />
        <div><span className="step-number">02</span><span><b>Review indicators</b><small>See matched evidence</small></span></div>
        <ArrowRight className="step-arrow" size={18} />
        <div><span className="step-number">03</span><span><b>Verify independently</b><small>Use the checklist</small></span></div>
      </section>

      <div id="screening-form" className="scroll-anchor" />
      <AnalysisForm onAnalyze={analyze} isLoading={loading} sampleCases={sampleCases} />
      {loading && <div role="status" className="loading-notice"><span className="loading-spinner" /> <span><b>Reviewing the submitted material</b><small>Matching the text and URL structure against the screening rules…</small></span></div>}
      {error && <div role="alert" className="error-notice"><b>We couldn’t complete this screening.</b><span>{error}</span><small>Check that the API is running, then try again.</small></div>}
      {result && <section id="analysis-results" aria-live="polite" className="results-section">
        <div className="section-heading"><div><div className="eyebrow">Your screening report</div><h2>What we found</h2></div><p>Use these results as a starting point for your own checks.</p></div>
        <RiskResultCard result={result} onReset={reset} />
        <FindingsList textFindings={result.text_findings} urlFindings={result.url_findings} hasText={result.inputs_analyzed.has_text} hasUrl={result.inputs_analyzed.has_url} />
        {submittedText && <HighlightedTextViewer rawText={submittedText} findings={result.text_findings} />}
        <VerificationChecklist steps={result.verification_checklist} />
        <SystemChecksAccordion checksPerformed={result.checks_performed} checksUnavailable={result.checks_unavailable} />
      </section>}
      <section id="educational-guide" className="guide-section">
        <div className="section-heading"><div><div className="eyebrow">Know the boundaries</div><h2>How to read this screening</h2></div><p>A useful prompt for due diligence, never a final verdict.</p></div>
        <div className="guide-grid">
          <article className="guide-card guide-card-blue"><span className="guide-icon"><FileSearch size={20} /></span><h3>What it checks</h3><p>Rule-based indicators in wording and URL structure: return promises, pressure tactics, recruitment, payment requests, suspicious link patterns, and selected brand lookalikes.</p></article>
          <article className="guide-card guide-card-sand"><span className="guide-icon"><ShieldCheck size={20} /></span><h3>What it cannot confirm</h3><p>This version does not visit websites, check regulators or domain age, or determine whether an offer is legitimate. A warning is not proof of fraud; no warning is not proof of safety.</p></article>
          <article className="guide-card guide-card-green"><span className="guide-icon"><Fingerprint size={20} /></span><h3>Your information</h3><p>Submitted analysis is processed in memory and isn’t saved as a report. Avoid including account numbers, passwords, or other personal information in the text you paste.</p></article>
        </div>
      </section>
    </div>
  );
}
