from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:  # pragma: no cover
    psycopg2 = None
    RealDictCursor = None


def get_db_url() -> str:
    return os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")


@contextmanager
def get_db_connection() -> Iterator:
    if psycopg2 is None or RealDictCursor is None:
        raise RuntimeError(
            "psycopg2 is not installed. Install psycopg2/psycopg2-binary before using the V2 Postgres storage layer."
        )

    conn = None
    try:
        conn = psycopg2.connect(get_db_url(), cursor_factory=RealDictCursor)
        conn.autocommit = False
        yield conn
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

