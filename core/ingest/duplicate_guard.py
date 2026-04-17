from __future__ import annotations

import hashlib
from pathlib import Path

from core.storage.repositories import V2Repository


def compute_file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_duplicate_file_id(repository: V2Repository, file_hash: str) -> str | None:
    existing = repository.get_ingest_file_by_hash(file_hash)
    if not existing:
        return None
    return str(existing["id"])

