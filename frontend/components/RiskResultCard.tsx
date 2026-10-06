'use client';

import React, { useState } from 'react';
import {
  AlertTriangle,
  AlertCircle,
  CheckCircle2,
  HelpCircle,
  Copy,
  Check,
  Download,
  Shield,
  Info,
} from 'lucide-react';
import { AnalysisResponse, RiskCategory, UncertaintyLevel } from '../lib/types';

interface RiskResultCardProps {
  result: AnalysisResponse;
  onReset: () => void;
}

export default function RiskResultCard({ result, onReset }: RiskResultCardProps) {
  const [copied, setCopied] = useState(false);

  const getCategoryConfig = (category: RiskCategory) => {
    switch (category) {
      case 'elevated_concern':
        return {
          title: 'Elevated Concern',
          badgeBg: 'bg-rose-100 text-rose-800 border-rose-300',
          containerBg: 'border-rose-200 bg-rose-50/40',
          icon: <AlertTriangle className="w-6 h-6 text-rose-600" />,
          accentBar: 'bg-rose-600',
          accentText: 'text-rose-700',
        };
      case 'needs_review':
        return {
          title: 'Needs Review',
          badgeBg: 'bg-amber-100 text-amber-800 border-amber-300',
          containerBg: 'border-amber-200 bg-amber-50/40',
          icon: <AlertCircle className="w-6 h-6 text-amber-600" />,
          accentBar: 'bg-amber-500',
          accentText: 'text-amber-700',
        };
      case 'lower_concern':
        return {
          title: 'Lower Concern',
          badgeBg: 'bg-emerald-100 text-emerald-800 border-emerald-300',
          containerBg: 'border-emerald-200 bg-emerald-50/40',
          icon: <CheckCircle2 className="w-6 h-6 text-emerald-600" />,
          accentBar: 'bg-emerald-500',
          accentText: 'text-emerald-700',
        };
      case 'insufficient_information':
      default:
        return {
          title: 'Insufficient Information',
          badgeBg: 'bg-slate-100 text-slate-800 border-slate-300',
          containerBg: 'border-slate-200 bg-slate-50/60',
          icon: <HelpCircle className="w-6 h-6 text-slate-600" />,
          accentBar: 'bg-slate-400',
          accentText: 'text-slate-700',
        };
    }
  };

  const getUncertaintyConfig = (level: UncertaintyLevel) => {
    switch (level) {
      case 'low':
        return {
          label: 'Low Uncertainty',
          color: 'bg-slate-100 text-slate-700 border-slate-200',
        };
      case 'medium':
        return {
          label: 'Medium Uncertainty',
          color: 'bg-amber-50 text-amber-800 border-amber-200',
        };
      case 'high':
      default:
        return {
          label: 'High Uncertainty',
          color: 'bg-blue-50 text-blue-800 border-blue-200',
        };
    }
  };

  const config = getCategoryConfig(result.category);
  const uncertainty = getUncertaintyConfig(result.uncertainty_level);

  const handleCopySummary = async () => {
    const textToCopy = `INVESTMENT RISK SCREENING REPORT
Category: ${result.category_display}
Risk Indicator Score: ${(result.risk_score * 100).toFixed(0)}%
Uncertainty: ${result.uncertainty_level.toUpperCase()}

SUMMARY:
${result.summary}

TEXT FINDINGS:
${result.text_findings.length === 0 ? 'None detected' : result.text_findings.map((f) => `- ${f.title} (${f.severity.toUpperCase()}): "${f.evidence}"`).join('\n')}

URL FINDINGS:
${result.url_findings.length === 0 ? 'None detected' : result.url_findings.map((f) => `- ${f.title} (${f.severity.toUpperCase()}): ${f.evidence}`).join('\n')}

IMPORTANT DISCLAIMER:
${result.disclaimer}`;

    try {
      await navigator.clipboard.writeText(textToCopy);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch (err) {
      console.error('Failed to copy summary:', err);
    }
  };

  const handleDownloadJson = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(result, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `risk-analysis-${result.analysis_id.slice(0, 8)}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className={`rounded-2xl border ${config.containerBg} shadow-sm p-6 md:p-8 space-y-6 transition-all`}>
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200/70 pb-5">
        <div className="flex items-center gap-3.5">
          <div className="p-3 bg-white rounded-xl shadow-sm border border-slate-100 flex-shrink-0">
            {config.icon}
          </div>
          <div>
            <div className="flex items-center gap-2.5 flex-wrap">
              <span
                className={`text-sm font-bold px-3 py-1 rounded-full border ${config.badgeBg}`}
              >
                {result.category_display}
              </span>
              <span
                className={`text-xs font-semibold px-2.5 py-0.5 rounded-full border ${uncertainty.color}`}
              >
                {uncertainty.label}
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Analysis ID: <span className="font-mono">{result.analysis_id.slice(0, 13)}...</span> • {new Date(result.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} UTC
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2 self-start sm:self-center">
          <button
            onClick={handleCopySummary}
            className="text-xs font-semibold py-1.5 px-3 rounded-lg border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 transition flex items-center gap-1.5 shadow-sm"
            title="Copy structured summary to clipboard"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5 text-slate-500" />}
            {copied ? 'Copied!' : 'Copy Summary'}
          </button>
          <button
            onClick={handleDownloadJson}
            className="text-xs font-semibold py-1.5 px-3 rounded-lg border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 transition flex items-center gap-1.5 shadow-sm"
            title="Download full JSON report"
          >
            <Download className="w-3.5 h-3.5 text-slate-500" />
            JSON
          </button>
          <button
            onClick={onReset}
            className="text-xs font-semibold py-1.5 px-3 rounded-lg border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 transition shadow-sm"
          >
            New Screening
          </button>
        </div>
      </div>

      {/* Uncertainty Driver Box */}
      <div className="bg-white/80 rounded-xl p-4 border border-slate-200/80 text-xs flex items-start gap-3">
        <Info className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
        <div className="space-y-1">
          <p className="font-semibold text-slate-800">
            Uncertainty Assessment ({uncertainty.label}):
          </p>
          <p className="text-slate-600 leading-relaxed">
            {result.uncertainty_explanation}
          </p>
        </div>
      </div>

      {/* Synthesis Summary */}
      <div className="space-y-2">
        <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider">
          Synthesis & Analysis Summary
        </h3>
        <p className="text-sm md:text-base text-slate-800 leading-relaxed font-normal bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          {result.summary}
        </p>
      </div>

      {/* Metric Bars */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-700 mb-1.5">
            <span>Aggregated Risk Indicator Score</span>
            <span className="font-mono font-bold text-slate-900">
              {(result.risk_score * 100).toFixed(0)}%
            </span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
            <div
              className={`h-2.5 rounded-full transition-all duration-500 ${config.accentBar}`}
              style={{ width: `${Math.max(5, result.risk_score * 100)}%` }}
            ></div>
          </div>
          <p className="text-[11px] text-slate-400 mt-1.5">
            Heuristic weighted indicator score. Not a legal verdict or fraud probability.
          </p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-700">Inputs Processed</p>
            <p className="text-xs text-slate-500 mt-0.5">
              {result.inputs_analyzed.has_text ? `${result.inputs_analyzed.text_word_count} words text` : 'No text'} •{' '}
              {result.inputs_analyzed.has_url ? (result.inputs_analyzed.domain || 'URL link') : 'No link'}
            </p>
          </div>
          <div className="text-right">
            <p className="text-xs font-semibold text-slate-700">Warning Signals</p>
            <p className="text-sm font-bold text-slate-900">
              {result.text_findings.length + result.url_findings.length} signal(s)
            </p>
          </div>
        </div>
      </div>

      {/* Mandatory Disclaimer Callout */}
      <div className="p-4 rounded-xl bg-amber-50/70 border border-amber-200 text-xs text-amber-900 flex items-start gap-3">
        <Shield className="w-4 h-4 text-amber-700 mt-0.5 flex-shrink-0" />
        <p className="leading-relaxed">
          <strong>Screening Disclaimer:</strong> {result.disclaimer}
        </p>
      </div>
    </div>
  );
}
