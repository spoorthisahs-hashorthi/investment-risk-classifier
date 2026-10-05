'use client';

import React, { useState } from 'react';
import {
  FileText,
  Globe,
  AlertTriangle,
  Info,
  CheckCircle,
  ExternalLink,
  ChevronRight,
} from 'lucide-react';
import { FindingItem, SeverityLevel } from '../lib/types';

interface FindingsListProps {
  textFindings: FindingItem[];
  urlFindings: FindingItem[];
  hasText: boolean;
  hasUrl: boolean;
}

export default function FindingsList({
  textFindings,
  urlFindings,
  hasText,
  hasUrl,
}: FindingsListProps) {
  const [activeTab, setActiveTab] = useState<'all' | 'text' | 'url'>('all');

  const getSeverityBadge = (severity: SeverityLevel) => {
    switch (severity) {
      case 'critical':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-100 text-rose-800 border border-rose-300">
            CRITICAL
          </span>
        );
      case 'high':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-orange-100 text-orange-800 border border-orange-300">
            HIGH
          </span>
        );
      case 'medium':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-100 text-amber-800 border border-amber-300">
            MEDIUM
          </span>
        );
      case 'low':
      default:
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-blue-100 text-blue-800 border border-blue-300">
            LOW
          </span>
        );
    }
  };

  const renderFindingCard = (finding: FindingItem) => {
    const isUrl = finding.source.includes('url') || finding.source.includes('network');

    return (
      <div
        key={`${finding.id}-${finding.evidence.slice(0, 20)}`}
        className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5 shadow-sm space-y-3 hover:border-slate-300 transition"
      >
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-2.5">
            <div className="p-2 rounded-lg bg-slate-100 text-slate-600 mt-0.5">
              {isUrl ? <Globe className="w-4 h-4 text-blue-600" /> : <FileText className="w-4 h-4 text-purple-600" />}
            </div>
            <div>
              <h4 className="text-sm font-bold text-slate-900 leading-snug">
                {finding.title}
              </h4>
              <p className="text-xs text-slate-400 mt-0.5">
                Category: <span className="font-medium text-slate-600 capitalize">{finding.category.replace('_', ' ')}</span> • Source: <span className="font-mono text-[11px] text-slate-500">{finding.source}</span>
              </p>
            </div>
          </div>
          <div className="flex-shrink-0">
            {getSeverityBadge(finding.severity)}
          </div>
        </div>

        {/* Observable Evidence Quote */}
        <div className="bg-slate-50 rounded-lg p-3 border border-slate-200/80">
          <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1">
            Observed Evidence:
          </p>
          <p className="text-xs font-mono text-slate-800 bg-white p-2 rounded border border-slate-200 break-all select-all">
            "{finding.evidence}"
          </p>
        </div>

        {/* Plain-Language Explanation */}
        <div className="text-xs text-slate-700 leading-relaxed bg-blue-50/40 p-3 rounded-lg border border-blue-100">
          <span className="font-semibold text-blue-900">Why this is an indicator: </span>
          {finding.explanation}
        </div>
      </div>
    );
  };

  const totalCount = textFindings.length + urlFindings.length;

  return (
    <div className="space-y-4">
      {/* Header and Filter Tabs */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 pb-3">
        <div>
          <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-500" />
            Detected Risk Indicators ({totalCount})
          </h3>
          <p className="text-xs text-slate-500">
            Detailed signals extracted from language patterns and link properties.
          </p>
        </div>

        {/* Filter Navigation */}
        <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl self-start sm:self-center">
          <button
            onClick={() => setActiveTab('all')}
            className={`text-xs font-semibold py-1 px-3 rounded-lg transition ${
              activeTab === 'all'
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            All Signals ({totalCount})
          </button>
          <button
            onClick={() => setActiveTab('text')}
            className={`text-xs font-semibold py-1 px-3 rounded-lg transition ${
              activeTab === 'text'
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Text ({textFindings.length})
          </button>
          <button
            onClick={() => setActiveTab('url')}
            className={`text-xs font-semibold py-1 px-3 rounded-lg transition ${
              activeTab === 'url'
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            URL & Domain ({urlFindings.length})
          </button>
        </div>
      </div>

      {/* Render Findings */}
      <div className="space-y-3">
        {activeTab === 'all' && (
          <>
            {totalCount === 0 ? (
              <div className="p-8 text-center bg-white rounded-2xl border border-slate-200 text-slate-500 space-y-2">
                <CheckCircle className="w-8 h-8 text-emerald-500 mx-auto" />
                <p className="font-semibold text-slate-800">No Notable Warning Indicators Detected</p>
                <p className="text-xs text-slate-500 max-w-md mx-auto">
                  Neither promotional text nor domain patterns matched known high-risk rules. Remember: Absence of detected indicators does not guarantee safety.
                </p>
              </div>
            ) : (
              <>
                {textFindings.map(renderFindingCard)}
                {urlFindings.map(renderFindingCard)}
              </>
            )}
          </>
        )}

        {activeTab === 'text' && (
          <>
            {!hasText ? (
              <div className="p-6 text-center bg-white rounded-xl border border-slate-200 text-slate-400 text-xs">
                No promotional text was supplied for text analysis.
              </div>
            ) : textFindings.length === 0 ? (
              <div className="p-6 text-center bg-white rounded-xl border border-slate-200 text-emerald-700 text-xs flex items-center justify-center gap-2">
                <CheckCircle className="w-4 h-4 text-emerald-600" />
                No suspicious linguistic indicators identified in the promotional text.
              </div>
            ) : (
              textFindings.map(renderFindingCard)
            )}
          </>
        )}

        {activeTab === 'url' && (
          <>
            {!hasUrl ? (
              <div className="p-6 text-center bg-white rounded-xl border border-slate-200 text-slate-400 text-xs">
                No website URL was supplied for domain analysis.
              </div>
            ) : urlFindings.length === 0 ? (
              <div className="p-6 text-center bg-white rounded-xl border border-slate-200 text-emerald-700 text-xs flex items-center justify-center gap-2">
                <CheckCircle className="w-4 h-4 text-emerald-600" />
                No suspicious lexical or domain anomalies identified for this link.
              </div>
            ) : (
              urlFindings.map(renderFindingCard)
            )}
          </>
        )}
      </div>
    </div>
  );
}
