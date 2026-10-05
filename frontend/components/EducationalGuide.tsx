'use client';

import React from 'react';
import { BookOpen, AlertTriangle, ShieldCheck, HelpCircle, Lock } from 'lucide-react';

export default function EducationalGuide() {
  return (
    <div id="educational-guide" className="bg-white rounded-2xl border border-slate-200 p-6 md:p-8 shadow-sm space-y-6">
      <div className="border-b border-slate-100 pb-4">
        <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-blue-600" />
          Educational Guide: Understanding Online Investment Risks
        </h3>
        <p className="text-xs text-slate-500 mt-1">
          How fraudulent schemes manipulate investors and how to spot warning signals early.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Card 1: Common Scheme Typologies */}
        <div className="p-5 rounded-xl bg-slate-50 border border-slate-200/80 space-y-3">
          <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-600" />
            Common Scheme Typologies
          </h4>
          <ul className="text-xs text-slate-600 space-y-2 leading-relaxed">
            <li>
              <strong className="text-slate-800">High-Yield Investment Programs (HYIPs):</strong> Claim fixed daily or weekly yields (e.g. 2% to 5% daily). Early payouts are financed solely by new deposits before the operator vanishes.
            </li>
            <li>
              <strong className="text-slate-800">Brand Impersonators & Clone Firms:</strong> Use misspelled domains or extra words (e.g. <code>binance-auth.top</code>) to mimic established brokerages and harvest deposits.
            </li>
            <li>
              <strong className="text-slate-800">Pyramid & Matrix Recruitment:</strong> Emphasize earning through inviting friends, downline bonuses, and binary commissions rather than verifiable commercial sales.
            </li>
            <li>
              <strong className="text-slate-800">Fake Algorithmic Bots:</strong> Attribute miraculous returns to secretive "Quantum AI" or "risk-free automated arbitrage" with no audited performance history.
            </li>
          </ul>
        </div>

        {/* Card 2: Crucial Safety Realities */}
        <div className="p-5 rounded-xl bg-blue-50/40 border border-blue-100 space-y-3">
          <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-blue-600" />
            Crucial Principles for Investors
          </h4>
          <ul className="text-xs text-slate-600 space-y-2 leading-relaxed">
            <li>
              <strong className="text-slate-800">HTTPS Does Not Mean Safe:</strong> The lock icon in the browser address bar only means connection encryption; today, nearly all scam websites use free automated SSL certificates.
            </li>
            <li>
              <strong className="text-slate-800">No Risk = High Risk:</strong> Genuine financial markets always entail risk of principal loss. Any claim of "zero risk" or "guaranteed profits" is deceptive.
            </li>
            <li>
              <strong className="text-slate-800">Crypto Transfers are Irreversible:</strong> If a firm asks you to deposit via direct USDT or Bitcoin wallet transfer, you lose all chargeback and bank insurance protections.
            </li>
            <li>
              <strong className="text-slate-800">Absence of Warnings is Not Safety:</strong> Scammers continuously update their pitches. A low concern screening score must never replace checking official government registers.
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
