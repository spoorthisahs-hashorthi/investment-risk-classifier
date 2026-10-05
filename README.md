# Risk Classification of Online Investment Schemes Using Text and URL Analysis

An educational, early-warning web application that analyzes user-submitted promotional text and website links for potential investment risk indicators, brand impersonation, and deceptive guarantees.

---

## 🚀 Key Features

- **Multi-Signal Screening**: Accepts pasted marketing copy, social media pitches, website links, or both.
- **Explainable Indicators**: Flags specific warning patterns (guaranteed returns, unrealistic compound interest, urgency pressure, recruitment incentives, lookalike domains, suspicious TLDs, and URL shorteners) with exact quotes and character offsets.
- **SSRF-Protected Network Inspection**: Safely probes target links while defending against Server-Side Request Forgery (SSRF), private IP ranges, loopback targets, cloud metadata endpoints, and redirect loops.
- **Explicit Uncertainty Awareness**: Calibrates uncertainty (High / Medium / Low) and provides an explicit **Insufficient Information** state when input is too sparse.
- **Actionable Due Diligence Checklist**: Generates custom verification steps tailored to the detected risk signals, linking directly to official securities regulators (FINRA BrokerCheck, SEC EDGAR, UK FCA, ASIC).
- **Privacy by Design**: Raw promotional text is **never** stored in persistent databases. Only one-way SHA-256 hashes and truncated domain names are retained.
- **Zero-Friction Local Development**: Operates out-of-the-box with embedded SQLite storage if cloud Supabase credentials are not supplied.

---

## 🛠️ Technology Stack

| Layer | Technology | Primary Role |
|---|---|---|
| **Frontend** | Next.js 15 (App Router), TypeScript, Tailwind CSS, Lucide | User experience, validation, interactive highlights, accessible presentation |
| **Backend API** | Python 3.11+, FastAPI, Pydantic v2, HTTPX, BeautifulSoup4 | Authoritative risk scoring, indicator extraction, SSRF-safe probing, synthesis |
| **Persistence** | Supabase PostgreSQL (Production) / SQLite (Local Fallback) | Non-sensitive analysis logs, feedback collection, RLS policies |

---

## 📦 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints.py       # API endpoints (/analyze, /sample-cases, /feedback)
│   │   ├── analyzers/
│   │   │   ├── text_analyzer.py      # Linguistic indicator detection & offset extraction
│   │   │   ├── url_analyzer.py       # Lexical, brand typosquatting & TLD checks
│   │   │   ├── network_inspector.py  # SSRF-protected DNS & HTTP redirect inspection
│   │   │   └── synthesis.py          # Category assignment & uncertainty calibration
│   │   ├── models/schemas.py         # Typed Pydantic request/response contracts
│   │   ├── storage/repository.py     # SQLite fallback & Supabase repository
│   │   ├── config.py                 # Application settings & environment vars
│   │   └── main.py                   # FastAPI app entrypoint, CORS & error handlers
│   ├── tests/                        # 26 comprehensive pytest unit & integration tests
│   └── requirements.txt              # Backend dependencies
├── frontend/
│   ├── app/                          # Next.js App Router (layout.tsx, page.tsx, globals.css)
│   ├── components/                   # Modular React UI components
│   │   ├── AnalysisForm.tsx          # Dual-input form with samples & shortcuts
│   │   ├── RiskResultCard.tsx        # Category banner, uncertainty gauge, summary
│   │   ├── FindingsList.tsx          # Text & URL findings with severity tags
│   │   ├── HighlightedTextViewer.tsx # Interactive text span highlighter
│   │   ├── VerificationChecklist.tsx # Interactive regulator verification steps
│   │   ├── SystemChecksAccordion.tsx # Completed vs. unavailable checks audit log
│   │   ├── FeedbackWidget.tsx        # User feedback collection
│   │   └── EducationalGuide.tsx      # Investor safety guidelines & scheme typologies
│   ├── lib/                          # API client & TypeScript interfaces
│   └── package.json                  # Next.js dependencies & scripts
├── supabase/
│   └── migrations/                   # SQL migration with Row Level Security (RLS)
└── docs/                             # Technical architecture, security, and rule specifications
    ├── ARCHITECTURE.md
    ├── SECURITY_PRIVACY.md
    └── ANALYSIS_RULES.md
```

---

## 🏃 Quickstart Guide

### 1. Backend Setup (Python FastAPI)

```bash
cd backend

# Create virtual environment and activate
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend tests
PYTHONPATH=. pytest tests/ -v

# Start FastAPI server on port 8000
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The FastAPI documentation will be available at `http://127.0.0.1:8000/docs`.

### 2. Frontend Setup (Next.js + TypeScript)

In a new terminal window:

```bash
cd frontend

# Install dependencies
npm install

# Typecheck and build
npm run typecheck
npm run build

# Start Next.js development server on port 3000
npm run dev
```

Open `http://localhost:3000` in your web browser.

---

## ⚙️ Environment Variables

### Backend (`backend/.env` optional)
```env
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
NETWORK_INSPECTION_ENABLED=true
NETWORK_TIMEOUT_SECONDS=4.0
MAX_REDIRECTS=3

# Optional Supabase persistence
SUPABASE_URL=
SUPABASE_KEY=
```

### Frontend (`frontend/.env.local` optional)
```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api/v1
```

---

## 🧪 Validation & Test Commands

Run the backend verification suite:
```bash
PYTHONPATH=backend backend/.venv/bin/pytest backend/tests/ -v
```

Run frontend typecheck:
```bash
cd frontend && npm run typecheck
```

Run frontend build:
```bash
cd frontend && npm run build
```

---

## ⚖️ Important Disclaimer

This application is strictly an educational screening aid. It is **not** a financial advisor, credit bureau, law enforcement system, or definitive fraud detector. Indicators do not prove fraud, and the absence of detected indicators does not guarantee safety. Always consult official national securities regulators before committing funds.
