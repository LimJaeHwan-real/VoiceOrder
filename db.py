from __future__ import annotations

import os
import sqlite3
import tempfile
from pathlib import Path

from init_db import initialize_database

BASE_DIR = Path(__file__).resolve().parent
DB_READY = False


def resolve_db_path() -> Path:
    configured_path = os.getenv("KIOSK_DB_PATH")
    if configured_path:
        return Path(configured_path)

    if os.getenv("VERCEL"):
        # Vercel can only write safely into /tmp unless an external durable path is provided.
        return Path(tempfile.gettempdir()) / "kiosk.db"

    return BASE_DIR / "kiosk.db"


DB_PATH = resolve_db_path()


def ensure_database() -> None:
    global DB_READY
    if DB_READY:
        return
    initialize_database(DB_PATH)
    DB_READY = True


def get_connection() -> sqlite3.Connection:
    ensure_database()
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection
