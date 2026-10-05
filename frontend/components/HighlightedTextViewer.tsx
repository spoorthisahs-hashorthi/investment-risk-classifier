'use client';

import React from 'react';
import { Eye, FileText } from 'lucide-react';
import { FindingItem } from '../lib/types';

interface HighlightedTextViewerProps {
  rawText: string;
  findings: FindingItem[];
}

interface TextSpan {
  text: string;
  finding?: FindingItem;
}

export default function HighlightedTextViewer({
  rawText,
  findings,
}: HighlightedTextViewerProps) {
  if (!rawText || !rawText.trim()) return null;

  // Filter findings that have valid offsets
  const offsetFindings = findings
    .filter((f) => f.start_offset !== null && f.end_offset !== null && f.start_offset !== undefined && f.end_offset !== undefined)
    .sort((a, b) => (a.start_offset! - b.start_offset!));

  // Build segmented text array
  const segments: TextSpan[] = [];
  let currentIndex = 0;

  for (const finding of offsetFindings) {
    const start = finding.start_offset!;
    const end = finding.end_offset!;

    if (start < currentIndex) {
      // Overlapping finding, skip to prevent duplicated text
      continue;
    }

    // Add un-highlighted prefix
    if (start > currentIndex) {
      segments.push({
        text: rawText.slice(currentIndex, start),
      });
    }

    // Add highlighted match
    segments.push({
      text: rawText.slice(start, end),
      finding: finding,
    });

    currentIndex = end;
  }

  // Trailing text
  if (currentIndex < rawText.length) {
    segments.push({
      text: rawText.slice(currentIndex),
    });
  }

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
        <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
          <Eye className="w-4 h-4 text-blue-600" />
          Text Evidence Explorer (Interactive Highlights)
        </h4>
        <span className="text-xs text-slate-400">
          Hover or tap highlighted phrases to inspect detected patterns
        </span>
      </div>

      <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 font-sans text-sm text-slate-800 leading-relaxed whitespace-pre-wrap selection:bg-blue-100">
        {segments.map((seg, idx) => {
          if (!seg.finding) {
            return <span key={idx}>{seg.text}</span>;
          }

          const sev = seg.finding.severity;
          let highlightClass = 'bg-amber-100 text-amber-900 border-b-2 border-amber-400';
          if (sev === 'critical') {
            highlightClass = 'bg-rose-100 text-rose-900 border-b-2 border-rose-500 font-semibold';
          } else if (sev === 'high') {
            highlightClass = 'bg-orange-100 text-orange-900 border-b-2 border-orange-500';
          }

          return (
            <mark
              key={idx}
              className={`rounded px-1 py-0.5 mx-0.5 relative group cursor-pointer transition ${highlightClass}`}
              title={`${seg.finding.title} (${seg.finding.severity.toUpperCase()}): ${seg.finding.explanation}`}
            >
              {seg.text}
              <span className="sr-only"> [{seg.finding.title}] </span>
            </mark>
          );
        })}
      </div>

      <div className="flex items-center gap-4 text-[11px] text-slate-500 pt-1">
        <span className="font-semibold text-slate-700">Legend:</span>
        <span className="inline-flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded bg-rose-400"></span> Critical indicator
        </span>
        <span className="inline-flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded bg-orange-400"></span> High indicator
        </span>
        <span className="inline-flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded bg-amber-400"></span> Medium indicator
        </span>
      </div>
    </div>
  );
}
