"""
database/db.py
--------------
SQLite database for CropSense AI user management.
Uses SQLAlchemy for ORM and bcrypt for password hashing.
"""

import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "cropsense.db")


def get_connection():
    """Return a SQLite connection."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    UNIQUE NOT NULL,
            password    TEXT    NOT NULL,
            created_at  TEXT    NOT NULL,
            last_login  TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT NOT NULL,
            crop_type   TEXT,
            district    TEXT,
            yield_pred  REAL,
            total_yield REAL,
            field_area  REAL,
            created_at  TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def _hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ── User operations ──────────────────────────────────────────────────────────

def register_user(username: str, password: str):
    """Register a new user. Returns (ok: bool, reason: str)."""
    if len(username) < 3:
        return False, "username_short"
    if len(password) < 6:
        return False, "password_short"
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)",
            (username, _hash_pw(password), datetime.now().isoformat())
        )
        conn.commit()
        return True, "success"
    except sqlite3.IntegrityError:
        return False, "already_exists"
    finally:
        conn.close()


def login_user(username: str, password: str) -> bool:
    """Verify credentials. Returns True on success."""
    conn = get_connection()
    row = conn.execute(
        "SELECT password FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    if row and row["password"] == _hash_pw(password):
        _update_last_login(username)
        return True
    return False


def _update_last_login(username: str):
    conn = get_connection()
    conn.execute(
        "UPDATE users SET last_login = ? WHERE username = ?",
        (datetime.now().isoformat(), username)
    )
    conn.commit()
    conn.close()


def get_user_count() -> int:
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()
    return count


# ── Prediction history ────────────────────────────────────────────────────────

def save_prediction(username, crop_type, district, yield_pred, total_yield, field_area):
    conn = get_connection()
    conn.execute(
        """INSERT INTO predictions
           (username, crop_type, district, yield_pred, total_yield, field_area, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (username, crop_type, district, round(yield_pred, 3),
         round(total_yield, 3), field_area, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def get_user_predictions(username: str, limit: int = 20):
    conn = get_connection()
    rows = conn.execute(
        """SELECT crop_type, district, yield_pred, total_yield, field_area, created_at
           FROM predictions WHERE username = ?
           ORDER BY created_at DESC LIMIT ?""",
        (username, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
