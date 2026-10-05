'use client';

import React, { useState } from 'react';
import { ChevronDown, ChevronUp, CheckCircle, AlertCircle, HelpCircle } from 'lucide-react';
import { CheckStatusItem } from '../lib/types';

interface SystemChecksAccordionProps {
  checksPerformed: CheckStatusItem[];
  checksUnavailable: CheckStatusItem[];
}

export default function SystemChecksAccordion({
  checksPerformed,
  checksUnavailable,
}: SystemChecksAccordionProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-slate-50 transition"
      >
        <div className="flex items-center gap-2">
          <HelpCircle className="w-4 h-4 text-slate-500" />
          <span className="text-sm font-bold text-slate-800">
            System Inspection Coverage & Limitations ({checksPerformed.length} completed, {checksUnavailable.length} unavailable)
          </span>
        </div>
        <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-500">
          <span>{isOpen ? 'Hide Audit Log' : 'View Inspection Coverage'}</span>
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {isOpen && (
        <div className="px-6 pb-6 pt-2 border-t border-slate-100 space-y-4 text-xs">
          <div>
            <h5 className="font-bold text-slate-800 uppercase tracking-wider mb-2">
              Checks Performed:
            </h5>
            <div className="space-y-2">
              {checksPerformed.map((chk) => (
                <div
                  key={chk.name}
                  className="flex items-start gap-2.5 p-3 rounded-lg bg-emerald-50/50 border border-emerald-100"
                >
                  <CheckCircle className="w-4 h-4 text-emerald-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <span className="font-semibold text-slate-900">{chk.display_name}: </span>
                    <span className="text-slate-600">{chk.details || 'Completed successfully.'}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {checksUnavailable.length > 0 && (
            <div>
              <h5 className="font-bold text-slate-800 uppercase tracking-wider mb-2">
                Checks Unavailable or Not Conducted:
              </h5>
              <div className="space-y-2">
                {checksUnavailable.map((chk) => (
                  <div
                    key={chk.name}
                    className="flex items-start gap-2.5 p-3 rounded-lg bg-slate-50 border border-slate-200"
                  >
                    <AlertCircle className="w-4 h-4 text-slate-400 mt-0.5 flex-shrink-0" />
                    <div>
                      <span className="font-semibold text-slate-800">{chk.display_name}: </span>
                      <span className="text-slate-500">{chk.details}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <p className="text-[11px] text-slate-400 italic pt-1">
            Note: To ensure unbiased evaluation, the screener reports exact coverage without guessing or asserting facts that could not be authoritatively verified.
          </p>
        </div>
      )}
    </div>
  );
}
