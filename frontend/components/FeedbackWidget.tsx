'use client';

import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, Send, Check } from 'lucide-react';
import { submitFeedback } from '../lib/api';

interface FeedbackWidgetProps {
  analysisId: string;
}

export default function FeedbackWidget({ analysisId }: FeedbackWidgetProps) {
  const [isHelpful, setIsHelpful] = useState<boolean | null>(null);
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isHelpful === null) return;

    setIsSubmitting(true);
    setError(null);

    try {
      await submitFeedback({
        analysis_id: analysisId,
        is_helpful: isHelpful,
        feedback_notes: notes.trim() || undefined,
      });
      setSubmitted(true);
    } catch (err: any) {
      setError('Could not record feedback. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-center text-xs text-slate-600 flex items-center justify-center gap-2">
        <Check className="w-4 h-4 text-emerald-600" />
        <span>Thank you! Your feedback helps calibrate our screening indicators.</span>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold text-slate-800">
          Was this screening assessment helpful?
        </span>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setIsHelpful(true)}
            className={`p-2 rounded-lg border text-xs font-semibold flex items-center gap-1.5 transition ${
              isHelpful === true
                ? 'bg-blue-50 border-blue-400 text-blue-700'
                : 'border-slate-200 hover:bg-slate-50 text-slate-600'
            }`}
          >
            <ThumbsUp className="w-3.5 h-3.5" />
            Yes
          </button>
          <button
            type="button"
            onClick={() => setIsHelpful(false)}
            className={`p-2 rounded-lg border text-xs font-semibold flex items-center gap-1.5 transition ${
              isHelpful === false
                ? 'bg-rose-50 border-rose-400 text-rose-700'
                : 'border-slate-200 hover:bg-slate-50 text-slate-600'
            }`}
          >
            <ThumbsDown className="w-3.5 h-3.5" />
            No
          </button>
        </div>
      </div>

      {isHelpful !== null && (
        <form onSubmit={handleSubmit} className="pt-2 space-y-2">
          <input
            type="text"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Optional: What went well or what was missing?"
            maxLength={500}
            className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200 focus:border-blue-500 focus:outline-none"
          />
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={isSubmitting}
              className="text-xs px-3 py-1.5 rounded-lg bg-blue-600 text-white font-semibold hover:bg-blue-700 disabled:opacity-50 transition flex items-center gap-1.5"
            >
              <Send className="w-3 h-3" />
              {isSubmitting ? 'Submitting...' : 'Send Feedback'}
            </button>
          </div>
          {error && <p className="text-[11px] text-rose-600">{error}</p>}
        </form>
      )}
    </div>
  );
}
