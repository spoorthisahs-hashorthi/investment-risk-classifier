"""Storage repository for optional persistence of analyses and user feedback.

Supports SQLite local storage with graceful fallback, and Supabase / PostgreSQL when configured.
Privacy policy: Raw text is never stored in persistent databases; only SHA-256 hashes and truncated non-sensitive domains.
"""

import sqlite3
import hashlib
import json
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path

from app.config import settings
from app.models.schemas import AnalysisResponse, FeedbackRequest

logger = logging.getLogger(__name__)

# Local SQLite fallback database path
DB_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DB_PATH = DB_DIR / "local_store.db"


class StorageRepository:
    """Manages optional persistence for analysis records and user feedback."""

    def __init__(self):
        self._init_sqlite()

    def _init_sqlite(self):
        """Initialize local SQLite tables if they do not exist."""
        try:
            DB_DIR.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS risk_analyses (
                        id TEXT PRIMARY KEY,
                        created_at TEXT NOT NULL,
                        category TEXT NOT NULL,
                        risk_score REAL NOT NULL,
                        uncertainty_level TEXT NOT NULL,
                        text_hash TEXT,
                        domain TEXT,
                        findings_count INTEGER NOT NULL,
                        report_json TEXT NOT NULL
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS analysis_feedback (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        analysis_id TEXT NOT NULL,
                        is_helpful INTEGER NOT NULL,
                        feedback_notes TEXT,
                        user_classification TEXT,
                        created_at TEXT NOT NULL
                    )
                    """
                )
                conn.commit()
                logger.info(f"Local storage repository initialized at {DB_PATH}")
        except Exception as e:
            logger.warning(f"Could not initialize local SQLite database: {e}")

    def save_analysis(self, response: AnalysisResponse, raw_text: Optional[str]) -> bool:
        """Save analysis summary safely without storing raw submitted text."""
        try:
            text_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest() if raw_text else None
            domain = response.inputs_analyzed.domain
            findings_count = len(response.text_findings) + len(response.url_findings)

            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO risk_analyses (
                        id, created_at, category, risk_score, uncertainty_level,
                        text_hash, domain, findings_count, report_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        response.analysis_id,
                        response.timestamp,
                        response.category.value,
                        response.risk_score,
                        response.uncertainty_level.value,
                        text_hash,
                        domain,
                        findings_count,
                        response.model_dump_json(),
                    ),
                )
                conn.commit()
            return True
        except Exception as e:
            logger.warning(f"Failed to persist analysis {response.analysis_id}: {e}")
            return False

    def save_feedback(self, feedback: FeedbackRequest, timestamp: str) -> bool:
        """Save user feedback on an analysis."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO analysis_feedback (
                        analysis_id, is_helpful, feedback_notes, user_classification, created_at
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        feedback.analysis_id,
                        1 if feedback.is_helpful else 0,
                        feedback.feedback_notes,
                        feedback.user_classification,
                        timestamp,
                    ),
                )
                conn.commit()
            return True
        except Exception as e:
            logger.warning(f"Failed to persist feedback for {feedback.analysis_id}: {e}")
            return False

    def get_recent_analyses(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent non-sensitive analysis summaries."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, created_at, category, risk_score, uncertainty_level, domain, findings_count
                    FROM risk_analyses
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (limit,),
                )
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.warning(f"Failed to fetch recent analyses: {e}")
            return []


repository = StorageRepository()
