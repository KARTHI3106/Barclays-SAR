import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
from src.config import CONFIG

logger = logging.getLogger(__name__)


class DatabaseManager:
    """SQLite-based database manager for audit trail and case storage."""

    def __init__(self):
        db_config = CONFIG.get("database", {})
        self.db_path = db_config.get("sqlite_path", "./data/sar_engine.db")
        self.conn = None

    def connect(self):
        """Connect to SQLite database and create tables if needed."""
        try:
            db_dir = Path(self.db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)

            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA journal_mode=WAL")
            self._create_tables()
            logger.info("SQLite database connected: %s", self.db_path)
        except Exception as e:
            logger.warning("Database connection failed: %s. Using in-memory fallback.", e)
            self.conn = None

    def _create_tables(self):
        """Create tables if they do not exist."""
        cursor = self.conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS sar_audit_trail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT NOT NULL,
                user_id TEXT DEFAULT 'system',
                input_data TEXT,
                retrieved_context TEXT,
                llm_reasoning TEXT,
                generated_output TEXT,
                human_edits TEXT,
                model_version TEXT,
                confidence_score REAL,
                metadata TEXT
            );

            CREATE TABLE IF NOT EXISTS sar_cases (
                case_id TEXT PRIMARY KEY,
                narrative_text TEXT,
                confidence_score REAL,
                typology TEXT,
                status TEXT DEFAULT 'draft',
                assigned_analyst TEXT DEFAULT 'system',
                approved_by TEXT,
                approved_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_audit_case_id ON sar_audit_trail(case_id);
            CREATE INDEX IF NOT EXISTS idx_audit_event_type ON sar_audit_trail(event_type);
            CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON sar_audit_trail(timestamp);
        """)
        self.conn.commit()

    def log_audit_event(
        self, case_id, event_type, user_id="system",
        input_data=None, retrieved_context=None,
        llm_reasoning=None, generated_output=None,
        human_edits=None, model_version=None,
        confidence_score=None, metadata=None
    ):
        """Log an audit event to the database."""
        if self.conn is None:
            logger.warning("No DB connection. Audit event logged to console only.")
            logger.info("AUDIT: %s | %s | %s", case_id, event_type, user_id)
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO sar_audit_trail
                (case_id, event_type, user_id, input_data, retrieved_context,
                 llm_reasoning, generated_output, human_edits, model_version,
                 confidence_score, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                case_id, event_type, user_id,
                json.dumps(input_data) if input_data else None,
                json.dumps(retrieved_context) if retrieved_context else None,
                llm_reasoning, generated_output,
                json.dumps(human_edits) if human_edits else None,
                model_version, confidence_score,
                json.dumps(metadata) if metadata else None,
            ))
            self.conn.commit()
            logger.info("Audit event logged: %s - %s", case_id, event_type)
        except Exception as e:
            logger.error("Failed to log audit event: %s", e)

    def get_audit_trail(self, case_id):
        """Retrieve audit trail for a case."""
        if self.conn is None:
            return []
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM sar_audit_trail WHERE case_id = ? ORDER BY timestamp ASC",
                (case_id,),
            )
            rows = cursor.fetchall()
            result = []
            for row in rows:
                event = dict(row)
                # Parse JSON fields back to dicts
                for field in ["input_data", "retrieved_context", "human_edits", "metadata"]:
                    if event.get(field):
                        try:
                            event[field] = json.loads(event[field])
                        except (json.JSONDecodeError, TypeError):
                            pass
                result.append(event)
            return result
        except Exception as e:
            logger.error("Failed to get audit trail: %s", e)
            return []

    def save_case(self, case_id, narrative_text, confidence_score,
                  typology, analyst="system"):
        """Save or update a case record."""
        if self.conn is None:
            return
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO sar_cases (case_id, narrative_text, confidence_score, typology, assigned_analyst)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(case_id) DO UPDATE SET
                    narrative_text = excluded.narrative_text,
                    confidence_score = excluded.confidence_score,
                    typology = excluded.typology,
                    updated_at = CURRENT_TIMESTAMP
            """, (case_id, narrative_text, confidence_score, typology, analyst))
            self.conn.commit()
        except Exception as e:
            logger.error("Failed to save case: %s", e)

    def update_case_status(self, case_id, status, approved_by=None):
        """Update the status of a case."""
        if self.conn is None:
            return
        try:
            cursor = self.conn.cursor()
            if status == "approved":
                cursor.execute("""
                    UPDATE sar_cases SET status = ?, approved_by = ?,
                    approved_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                    WHERE case_id = ?
                """, (status, approved_by, case_id))
            else:
                cursor.execute("""
                    UPDATE sar_cases SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE case_id = ?
                """, (status, case_id))
            self.conn.commit()
        except Exception as e:
            logger.error("Failed to update case status: %s", e)

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
