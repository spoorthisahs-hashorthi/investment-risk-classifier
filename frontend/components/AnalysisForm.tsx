'use client';

import React, { useState } from 'react';
import { AlertCircle, ArrowRight, FileText, Globe2, RotateCcw, Sparkles } from 'lucide-react';
import { AnalysisRequest, SampleCase } from '../lib/types';

interface AnalysisFormProps {
  onAnalyze: (req: AnalysisRequest) => void;
  isLoading: boolean;
  sampleCases: SampleCase[];
}

export default function AnalysisForm({ onAnalyze, isLoading, sampleCases }: AnalysisFormProps) {
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');
  const [validationError, setValidationError] = useState<string | null>(null);
  const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const cleanText = text.trim();
    const cleanUrl = url.trim();
    if (!cleanText && !cleanUrl) {
      setValidationError('Add promotional text, a website link, or both to start your screening.');
      return;
    }
    setValidationError(null);
    onAnalyze({ text: cleanText || undefined, url: cleanUrl || undefined, enable_network_check: false });
  };

  const handleLoadSample = (sample: SampleCase) => {
    setText(sample.sample_text || '');
    setUrl(sample.sample_url || '');
    setValidationError(null);
  };

  const clearInputs = () => { setText(''); setUrl(''); setValidationError(null); };

  return (
    <section className="analysis-card" aria-labelledby="form-title">
      <div className="form-heading">
        <div className="form-heading-icon"><FileText size={21} /></div>
        <div><span className="eyebrow">Start here</span><h2 id="form-title">Screen an investment offer</h2><p>Paste what you received. You can check the message, the link, or both together.</p></div>
      </div>

      {sampleCases.length > 0 && <div className="samples-area"><div className="samples-label"><Sparkles size={15} /> Try an example <span>See how the screener responds</span></div><div className="sample-list">{sampleCases.map((sample) => <button key={sample.id} type="button" title={sample.description} onClick={() => handleLoadSample(sample)} className="sample-chip">{sample.title}<span>Try</span></button>)}</div></div>}

      <form onSubmit={handleSubmit} className="screening-form">
        <div className="input-block">
          <div className="input-label-row"><label htmlFor="promo-text"><span className="field-icon"><FileText size={16} /></span><span><b>Promotion or message</b><small>Copy the wording from an ad, email, chat, or website</small></span></label><span className={`character-count ${text.length > 18000 ? 'count-warning' : ''}`}>{text.length.toLocaleString()} <i>/ 20,000</i></span></div>
          <textarea id="promo-text" rows={6} value={text} onChange={(e) => { setText(e.target.value); if (validationError) setValidationError(null); }} onKeyDown={(e) => { if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') { e.preventDefault(); e.currentTarget.form?.requestSubmit(); } }} placeholder={'Paste the message exactly as you received it…\n\nFor example: “Earn guaranteed daily returns with our automated trading platform.”'} maxLength={20000} />
          <div className="input-foot"><span>{wordCount} {wordCount === 1 ? 'word' : 'words'} · Matching phrases will be highlighted in your report</span>{text && <button type="button" onClick={() => setText('')} className="text-button">Clear text</button>}</div>
        </div>

        <div className="input-block url-block">
          <div className="input-label-row"><label htmlFor="website-url"><span className="field-icon field-icon-green"><Globe2 size={16} /></span><span><b>Website or profile link <em>Optional</em></b><small>Include the link mentioned in the promotion, if there is one</small></span></label><span className="character-count">{url.length.toLocaleString()} <i>/ 2,048</i></span></div>
          <div className="url-entry"><Globe2 size={17} /><input type="text" id="website-url" value={url} onChange={(e) => { setUrl(e.target.value); if (validationError) setValidationError(null); }} placeholder="example.com or https://example.com" maxLength={2048} autoCapitalize="none" autoCorrect="off" spellCheck={false} /></div>
          <p className="field-note">We inspect the characters in the link only. The website won’t be opened or contacted.</p>
        </div>

        <div className="privacy-note"><span className="privacy-icon"><ShieldMini /></span><span><b>Private by design</b><small>Text and links are analyzed in memory, not saved as reports. Don’t paste passwords or personal account details.</small></span></div>

        {validationError && <div role="alert" className="form-error"><AlertCircle size={17} /><span>{validationError}</span></div>}

        <div className="form-actions"><div className="shortcut-hint">Tip: press <kbd>⌘</kbd> or <kbd>Ctrl</kbd> + <kbd>Enter</kbd> to screen</div><div className="action-buttons">{(text || url) && <button type="button" className="reset-button" onClick={clearInputs} disabled={isLoading}><RotateCcw size={15} /> Clear all</button>}<button type="submit" className="submit-button" disabled={isLoading}>{isLoading ? <><span className="button-spinner" /> Screening…</> : <>Screen this offer <ArrowRight size={17} /></>}</button></div></div>
        <p className="form-disclaimer">This tool provides educational warning signs only, not financial advice or a fraud determination.</p>
      </form>
    </section>
  );
}

function ShieldMini() { return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11Z"/><path d="m9 12 2 2 4-4"/></svg>; }
