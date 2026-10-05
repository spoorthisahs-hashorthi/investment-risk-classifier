import './globals.css';
import type { Metadata } from 'next';
import React from 'react';
import { ShieldAlert, ExternalLink, HelpCircle } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Investment Risk Screener | Text & URL Analysis',
  description:
    'Educational and early-warning screening tool for evaluating online investment promotions, high-yield schemes, and lookalike domains.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col antialiased bg-slate-50 text-slate-900">
        <header className="border-b border-slate-200 bg-white sticky top-0 z-40 shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
                <ShieldAlert className="w-6 h-6" aria-hidden="true" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-slate-900 leading-tight">
                  Investment Risk Screener
                </h1>
                <p className="text-xs text-slate-500">
                  Early-Warning Analysis for Online Investment Promotions & URLs
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-200">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse"></span>
                Educational Screening Aid
              </span>
              <a
                href="#educational-guide"
                className="text-xs text-slate-600 hover:text-blue-600 font-medium inline-flex items-center gap-1 py-1 px-2 rounded-lg hover:bg-slate-100 transition"
              >
                <HelpCircle className="w-4 h-4" />
                How It Works
              </a>
            </div>
          </div>
        </header>

        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>

        <footer className="border-t border-slate-200 bg-white mt-16 py-8 text-xs text-slate-500">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-100 pb-6 mb-6">
              <div>
                <p className="font-semibold text-slate-700">Official Regulatory Registers:</p>
                <p className="mt-0.5 text-slate-500">
                  Before investing capital, independently verify the promoter with official national regulators.
                </p>
              </div>
              <div className="flex flex-wrap gap-4 text-blue-600 font-medium">
                <a
                  href="https://brokercheck.finra.org/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:underline inline-flex items-center gap-1"
                >
                  FINRA BrokerCheck <ExternalLink className="w-3 h-3" />
                </a>
                <a
                  href="https://www.sec.gov/edgar/searchedgar/companysearch"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:underline inline-flex items-center gap-1"
                >
                  SEC EDGAR <ExternalLink className="w-3 h-3" />
                </a>
                <a
                  href="https://register.fca.org.uk/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:underline inline-flex items-center gap-1"
                >
                  UK FCA Register <ExternalLink className="w-3 h-3" />
                </a>
                <a
                  href="https://moneysmart.gov.au/check-and-report-scams/investor-alert-list"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:underline inline-flex items-center gap-1"
                >
                  ASIC Alert List <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>

            <p className="text-center text-slate-400 leading-relaxed">
              <strong>Statutory Disclaimer:</strong> This application is strictly an educational screening tool and does not provide financial advice, legal counsel, or investment recommendations. Detection of risk indicators does not constitute definitive proof of fraud, and absence of detected indicators does not guarantee that an investment is safe. Always conduct independent due diligence.
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
