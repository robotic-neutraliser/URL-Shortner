"""
database.py — Handles all SQLite storage

Table structure:
  urls
  ├── code        TEXT  (the 6-char short code, e.g. "aa747c")
  ├── long_url    TEXT  (the original URL)
  ├── clicks      INT   (how many times this short URL was visited)
  └── created_at  TEXT  (when it was created)

Why SQLite?
  - No installation needed, just a file on disk
  - Perfect for projects and demos
  - Easy to inspect with any DB viewer
"""

import sqlite3
from datetime import datetime

DB_FILE = "urls.db"


def get_connection():
    """Open a connection to the SQLite database file."""
    return sqlite3.connect(DB_FILE)


def init_db():
    """Create the urls table if it doesn't exist yet."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                code       TEXT PRIMARY KEY,
                long_url   TEXT NOT NULL,
                clicks     INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)


def save_url(code: str, long_url: str):
    """Store a new short code + long URL in the database."""
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO urls (code, long_url, created_at) VALUES (?, ?, ?)",
            (code, long_url, datetime.now().isoformat())
        )
        # INSERT OR IGNORE — if this URL was already shortened, just skip


def get_url(code: str) -> dict | None:
    """Look up a short code and return the full row, or None if not found."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT code, long_url, clicks, created_at FROM urls WHERE code = ?",
            (code,)
        ).fetchone()

    if row is None:
        return None

    return {
        "code":       row[0],
        "long_url":   row[1],
        "clicks":     row[2],
        "created_at": row[3],
    }


def increment_clicks(code: str):
    """Add 1 to the click counter every time someone visits the short URL."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE urls SET clicks = clicks + 1 WHERE code = ?",
            (code,)
        )
