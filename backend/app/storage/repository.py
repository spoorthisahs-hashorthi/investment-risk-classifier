"""Legacy optional feedback storage. Analysis submissions are not persisted."""

import logging
import sqlite3
from pathlib import Path

from app.models.schemas import FeedbackRequest

logger = logging.getLogger(__name__)
DB_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DB_PATH = DB_DIR / "local_store.db"


class StorageRepository:
    """Stores only optional feedback in local SQLite; no analysis-history API exists."""

    def __init__(self):
        try:
            DB_DIR.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute(
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
        except Exception as exc:
            logger.warning("Could not initialize optional feedback storage: %s", exc)

    def save_feedback(self, feedback: FeedbackRequest, timestamp: str) -> bool:
        """Persist optional feedback; callers should apply retention and access controls."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute(
                    """
                    INSERT INTO analysis_feedback (
                        analysis_id, is_helpful, feedback_notes, user_classification, created_at
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        feedback.analysis_id,
                        int(feedback.is_helpful),
                        feedback.feedback_notes,
                        feedback.user_classification,
                        timestamp,
                    ),
                )
                conn.commit()
            return True
        except Exception as exc:
            logger.warning("Failed to persist feedback for %s: %s", feedback.analysis_id, exc)
            return False


repository = StorageRepository()
