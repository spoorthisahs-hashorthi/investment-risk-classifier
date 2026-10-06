# Supabase & PostgreSQL Persistence Configuration

This directory contains a draft database migration for a possible future persistence layer. The current analysis path does not use Supabase or store analysis submissions.

## Architecture & Privacy-First Persistence Policy

- Analysis requests currently run in memory and are not persisted. The migration is not automatically applied.
- The optional feedback API uses a legacy local SQLite repository; it is not backed by Supabase.

## Database Schema

- `risk_analyses`:
  - `id`: UUID primary key
  - `created_at`: UTC timestamp
  - `category`: Risk classification ('lower_concern', 'needs_review', 'elevated_concern', 'insufficient_information')
  - `risk_score`: Heuristic numeric indicator score (0.0 to 1.0), not a fraud probability
  - `uncertainty_level`: Uncertainty rating ('low', 'medium', 'high')
  - `text_hash`: SHA-256 hash of promotional text
  - `domain`: Evaluated domain host
  - `findings_count`: Integer count of detected warning indicators
  - `report_json`: Would contain structured findings and verification guidance if persistence is implemented
- `analysis_feedback`:
  - `id`: Auto-incrementing primary key
  - `analysis_id`: Foreign key reference to `risk_analyses`
  - `is_helpful`: Boolean
  - `feedback_notes`: Optional user commentary (max 1,000 chars)
  - `user_classification`: Optional user-suggested category

## Migration status

Do not apply this draft migration to a production project yet. It intentionally defines no client access policies, so a future backend integration still needs narrow server-side policies and an ownership model. Supabase credentials are not used by the current application. If persistent analysis history becomes a requirement, define authentication, ownership, retention, and row-level access rules before wiring a project or adding credentials.
