# Supabase & PostgreSQL Persistence Configuration

This directory contains the database migration scripts and schema definitions for the **Online Investment Scheme Risk Classification** platform.

## Architecture & Privacy-First Persistence Policy

- **No Raw Submitted Content**: In accordance with user privacy guidelines, raw user-submitted promotional text and sensitive query parameters are **never** stored in the database.
- **Auditable Records**: The database stores a SHA-256 hash of the input, the non-sensitive registered domain, category, risk score, uncertainty rating, and structured findings.
- **Graceful Fallback**: If Supabase or PostgreSQL credentials are not provided in environment variables, the Python backend automatically uses a local SQLite repository (`backend/data/local_store.db`), ensuring zero downtime or deployment blockers during local evaluation.

## Database Schema

- `risk_analyses`:
  - `id`: UUID primary key
  - `created_at`: UTC timestamp
  - `category`: Risk classification ('lower_concern', 'needs_review', 'elevated_concern', 'insufficient_information')
  - `risk_score`: Calibrated numeric score (0.0 to 1.0)
  - `uncertainty_level`: Uncertainty rating ('low', 'medium', 'high')
  - `text_hash`: SHA-256 hash of promotional text
  - `domain`: Evaluated domain host
  - `findings_count`: Integer count of detected warning indicators
  - `report_json`: Structured JSON containing findings and verification checklist
- `analysis_feedback`:
  - `id`: Auto-incrementing primary key
  - `analysis_id`: Foreign key reference to `risk_analyses`
  - `is_helpful`: Boolean
  - `feedback_notes`: Optional user commentary (max 1,000 chars)
  - `user_classification`: Optional user-suggested category

## How to Apply Migrations

### Option 1: Supabase CLI (Recommended)
```bash
# Link to your Supabase project
supabase link --project-ref <your-project-ref>

# Apply migrations
supabase db push
```

### Option 2: Supabase Web Console
1. Open the Supabase dashboard for your project.
2. Navigate to **SQL Editor**.
3. Open `supabase/migrations/20261005_init_schema.sql` and run the script.

## Backend Environment Configuration
To enable Supabase persistence, set these variables in `backend/.env`:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-service-role-or-anon-key
```
