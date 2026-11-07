"""SQLite connection and reusable database helpers for MediCore."""
import os
import sqlite3
from pathlib import Path
from flask import g

BASE_DIR = Path(__file__).resolve().parent
# Set MEDICORE_DB_PATH=/var/data/medicore.db when using a Render persistent disk.
DB_PATH = Path(os.environ.get('MEDICORE_DB_PATH', str(BASE_DIR / 'medicore.db'))).expanduser()


def get_db():
    """Return one SQLite connection per Flask request."""
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db


def close_db(_error=None):
    """Close the request-scoped database connection."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Create schema and insert demo data on the first launch."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.execute('PRAGMA foreign_keys = ON')
    db.executescript((BASE_DIR / 'schema.sql').read_text(encoding='utf-8'))
    count = db.execute('SELECT COUNT(*) FROM patients').fetchone()[0]
    if count == 0:
        db.executescript((BASE_DIR / 'seed.sql').read_text(encoding='utf-8'))
    db.commit()
    db.close()


def query_db(sql, args=(), one=False):
    """Execute a parameterized SELECT and return rows."""
    cursor = get_db().execute(sql, args)
    rows = cursor.fetchall()
    return (rows[0] if rows else None) if one else rows


def execute_db(sql, args=()):
    """Execute a parameterized write and return its generated row ID."""
    db = get_db()
    cursor = db.execute(sql, args)
    db.commit()
    return cursor.lastrowid
