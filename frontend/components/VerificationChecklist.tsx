'use client';

import React, { useState } from 'react';
import { CheckSquare, ExternalLink, CheckCircle, ShieldCheck } from 'lucide-react';
import { VerificationStep } from '../lib/types';

interface VerificationChecklistProps {
  steps: VerificationStep[];
}

export default function VerificationChecklist({ steps }: VerificationChecklistProps) {
  const [completedSteps, setCompletedSteps] = useState<Record<number, boolean>>({});

  const toggleStep = (stepNumber: number) => {
    setCompletedSteps((prev) => ({
      ...prev,
      [stepNumber]: !prev[stepNumber],
    }));
  };

  const completedCount = Object.values(completedSteps).filter(Boolean).length;

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 md:p-8 shadow-sm space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
        <div>
          <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-600" />
            Recommended Due Diligence & Verification Steps
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Practical steps to independently verify the legitimacy of this entity or promoter.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-slate-50 px-3 py-1.5 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700 self-start sm:self-center">
          <CheckSquare className="w-4 h-4 text-emerald-600" />
          <span>
            {completedCount} of {steps.length} verified
          </span>
        </div>
      </div>

      <div className="space-y-4">
        {steps.map((step) => {
          const isDone = !!completedSteps[step.step];

          return (
            <div
              key={step.step}
              onClick={() => toggleStep(step.step)}
              className={`p-4 rounded-xl border transition cursor-pointer flex items-start gap-3.5 ${
                isDone
                  ? 'bg-emerald-50/40 border-emerald-200 text-slate-700'
                  : 'bg-white border-slate-200 hover:border-slate-300'
              }`}
            >
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  toggleStep(step.step);
                }}
                className={`w-5 h-5 rounded mt-0.5 flex items-center justify-center border transition ${
                  isDone
                    ? 'bg-emerald-600 border-emerald-600 text-white'
                    : 'border-slate-300 bg-white hover:border-blue-500'
                }`}
                aria-label={`Mark step ${step.step} as ${isDone ? 'incomplete' : 'complete'}`}
              >
                {isDone && <CheckCircle className="w-4 h-4" />}
              </button>

              <div className="flex-1 space-y-1">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <h4
                    className={`text-sm font-bold ${
                      isDone ? 'line-through text-slate-500' : 'text-slate-900'
                    }`}
                  >
                    Step {step.step}: {step.title}
                  </h4>

                  {step.action_url && (
                    <a
                      href={step.action_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      className="text-xs font-semibold text-blue-600 hover:text-blue-800 inline-flex items-center gap-1 hover:underline bg-blue-50 px-2 py-0.5 rounded border border-blue-200"
                    >
                      {step.official_registry || 'Official Registry'} <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>

                <p className="text-xs text-slate-600 leading-relaxed">
                  {step.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
