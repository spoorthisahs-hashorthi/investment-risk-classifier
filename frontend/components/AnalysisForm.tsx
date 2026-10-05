'use client';

import React, { useState } from 'react';
import {
  FileText,
  Globe,
  Sparkles,
  ShieldCheck,
  AlertCircle,
  RotateCcw,
  Search,
} from 'lucide-react';
import { AnalysisRequest, SampleCase } from '../lib/types';

interface AnalysisFormProps {
  onAnalyze: (req: AnalysisRequest) => void;
  isLoading: boolean;
  sampleCases: SampleCase[];
}

export default function AnalysisForm({
  onAnalyze,
  isLoading,
  sampleCases,
}: AnalysisFormProps) {
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');
  const [enableNetworkCheck, setEnableNetworkCheck] = useState(true);
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    const trimmedText = text.trim();
    const trimmedUrl = url.trim();

    if (!trimmedText && !trimmedUrl) {
      setValidationError('Please provide promotional text, a website URL, or both to evaluate.');
      return;
    }

    onAnalyze({
      text: trimmedText || undefined,
      url: trimmedUrl || undefined,
      enable_network_check: enableNetworkCheck,
    });
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      handleSubmit(e);
    }
  };

  const handleLoadSample = (sample: SampleCase) => {
    setText(sample.sample_text || '');
    setUrl(sample.sample_url || '');
    setValidationError(null);
  };

  const handleReset = () => {
    setText('');
    setUrl('');
    setValidationError(null);
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 md:p-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-100 pb-5 mb-6">
        <div>
          <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <Search className="w-5 h-5 text-blue-600" />
            Analyze Investment Opportunity
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            Paste promotional marketing text, social media copy, or a website link for multi-signal risk screening.
          </p>
        </div>

        {/* Sample Case Selector Chips */}
        {sampleCases.length > 0 && (
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-semibold text-slate-500 flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5 text-amber-500" /> Sample Cases:
            </span>
            <div className="flex flex-wrap gap-1.5">
              {sampleCases.slice(0, 4).map((sample) => (
                <button
                  key={sample.id}
                  type="button"
                  onClick={() => handleLoadSample(sample)}
                  className="text-xs bg-slate-100 hover:bg-blue-50 hover:text-blue-700 text-slate-700 font-medium py-1 px-2.5 rounded-lg border border-slate-200 transition"
                  title={sample.description}
                >
                  {sample.title}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Promotional Text Input */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label
              htmlFor="promo-text"
              className="text-sm font-semibold text-slate-800 flex items-center gap-2"
            >
              <FileText className="w-4 h-4 text-blue-600" />
              Promotional Text / Marketing Pitch
            </label>
            <div className="flex items-center gap-3">
              <span className="text-xs text-slate-400">
                {text.length.toLocaleString()} / 20,000 chars
              </span>
              {text && (
                <button
                  type="button"
                  onClick={() => setText('')}
                  className="text-xs text-slate-400 hover:text-red-500 transition"
                >
                  Clear text
                </button>
              )}
            </div>
          </div>
          <textarea
            id="promo-text"
            rows={5}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Paste text from Telegram, WhatsApp, social media ads, email newsletters, or website marketing... (e.g., 'Guaranteed 5% daily returns, risk-free AI bot, double your crypto in 48 hours!')"
            className="w-full px-4 py-3 rounded-xl border border-slate-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 text-sm text-slate-800 placeholder-slate-400 resize-y transition"
            maxLength={20000}
          />
        </div>

        {/* Website URL Input */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label
              htmlFor="website-url"
              className="text-sm font-semibold text-slate-800 flex items-center gap-2"
            >
              <Globe className="w-4 h-4 text-blue-600" />
              Website URL / Link
            </label>
            {url && (
              <button
                type="button"
                onClick={() => setUrl('')}
                className="text-xs text-slate-400 hover:text-red-500 transition"
              >
                Clear URL
              </button>
            )}
          </div>
          <div className="relative">
            <input
              type="text"
              id="website-url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example-investment-portal.com"
              className="w-full pl-4 pr-10 py-3 rounded-xl border border-slate-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 text-sm text-slate-800 placeholder-slate-400 transition"
            />
          </div>
          <p className="text-xs text-slate-400 mt-1.5">
            Checks for typosquatting, lookalike financial brands, suspicious TLDs, and URL shorteners.
          </p>
        </div>

        <p className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-xs leading-5 text-slate-600">Only the URL text is inspected here. This version does not visit the website, follow redirects, or check domain age.</p>

        {/* Validation Error banner */}
        {validationError && (
          <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0 text-red-500" />
            <span>{validationError}</span>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
          <div className="text-xs text-slate-400">
            Press <kbd className="px-1.5 py-0.5 bg-slate-100 border border-slate-300 rounded text-slate-600 font-mono text-[10px]">Ctrl</kbd> + <kbd className="px-1.5 py-0.5 bg-slate-100 border border-slate-300 rounded text-slate-600 font-mono text-[10px]">Enter</kbd> to analyze
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            {(text || url) && (
              <button
                type="button"
                onClick={handleReset}
                disabled={isLoading}
                className="px-4 py-2.5 rounded-xl border border-slate-300 text-slate-700 hover:bg-slate-100 text-sm font-medium transition flex items-center justify-center gap-1.5"
              >
                <RotateCcw className="w-4 h-4" />
                Reset
              </button>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 sm:flex-none px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold shadow-md shadow-blue-500/20 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Evaluating Signals...
                </>
              ) : (
                <>
                  <Search className="w-4 h-4" />
                  Screen Offer
                </>
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
