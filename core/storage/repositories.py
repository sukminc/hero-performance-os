from __future__ import annotations

import os

from core.storage.sqlite_repository import SQLiteV2Repository

try:
    from core.storage.postgres_repository import PostgresV2Repository
except ImportError:  # pragma: no cover
    PostgresV2Repository = None


def get_storage_backend() -> str:
    backend = os.getenv("V2_STORAGE_BACKEND", "sqlite").strip().lower()
    return backend or "sqlite"


class V2Repository:
    def __init__(self) -> None:
        backend = get_storage_backend()
        if backend == "postgres":
            if PostgresV2Repository is None:
                raise RuntimeError("Postgres storage backend is not available.")
            self._impl = PostgresV2Repository()
        else:
            self._impl = SQLiteV2Repository()

    def __getattr__(self, item: str):
        return getattr(self._impl, item)
