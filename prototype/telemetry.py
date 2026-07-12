import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path(__file__).parent / "telemetry.db"

COLUMNS = [
    "timestamp",
    "question",
    "category",
    "risk_level",
    "confidence",
    "source",
    "action",
    "helpfulness",
    "time_saved_minutes",
    "rejection_reason",
    "answered_by",
]


def _connect() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def init_db():
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                question TEXT NOT NULL,
                category TEXT,
                risk_level TEXT,
                confidence TEXT,
                source TEXT,
                action TEXT,
                helpfulness INTEGER,
                time_saved_minutes INTEGER,
                rejection_reason TEXT,
                answered_by TEXT
            )
            """
        )


def log_event(event: dict):
    values = [event.get(col) for col in COLUMNS]
    placeholders = ", ".join("?" for _ in COLUMNS)
    with _connect() as conn:
        conn.execute(
            f"INSERT INTO events ({', '.join(COLUMNS)}) VALUES ({placeholders})",
            values,
        )


def load_events() -> pd.DataFrame:
    with _connect() as conn:
        return pd.read_sql_query(
            "SELECT * FROM events ORDER BY timestamp", conn
        )
