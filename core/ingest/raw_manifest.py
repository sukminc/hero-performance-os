from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zipfile import BadZipFile, ZipFile


TEXT_EXTENSIONS = {".txt"}
ZIP_EXTENSIONS = {".zip"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
SQLITE_EXTENSIONS = {".sqlite", ".sqlite3", ".db"}


@dataclass(frozen=True)
class RawFileFacts:
    path: Path
    relative_path: str
    filename: str
    extension: str
    size_bytes: int
    sha256: str
    input_kind: str
    source_bucket: str
    processing_status: str
    hand_block_count: int | None = None
    zip_member_count: int | None = None
    zip_member_extensions: dict[str, int] | None = None
    zip_error: str | None = None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_original_name(path: Path) -> str:
    safe = path.name.replace("/", "-").replace("\\", "-").strip()
    return safe or "unnamed"


def classify_input_kind(path: Path) -> str:
    extension = path.suffix.lower()
    if extension in TEXT_EXTENSIONS:
        return "text_hand_history_candidate"
    if extension in ZIP_EXTENSIONS:
        return "zip_archive"
    if extension in IMAGE_EXTENSIONS:
        return "image_evidence"
    if extension in SQLITE_EXTENSIONS:
        return "processed_sqlite"
    return "unsupported"


def classify_source_bucket(relative_path: str, input_kind: str) -> str:
    if relative_path == "hero_v2.sqlite3" or input_kind == "processed_sqlite":
        return "processed_database"
    if relative_path.startswith("tmp_uploads_public/expanded/"):
        return "expanded_upload_member"
    if relative_path.startswith("tmp_uploads_public/"):
        return "uploaded_source"
    if relative_path.startswith("raw_intake_legacy/"):
        return "legacy_raw_intake"
    return "data_other"


def processing_status_for(input_kind: str) -> str:
    if input_kind == "text_hand_history_candidate":
        return "text_candidate_unparsed"
    if input_kind == "zip_archive":
        return "archive_candidate_unexpanded"
    if input_kind == "image_evidence":
        return "image_preserved"
    if input_kind == "processed_sqlite":
        return "processed_db_preserved"
    return "unsupported_preserved"


def count_hand_blocks(path: Path) -> int:
    count = 0
    try:
        needle = b"Poker Hand #"
        overlap = len(needle) - 1
        previous_tail = b""
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                haystack = previous_tail + chunk
                count += haystack.count(needle)
                previous_tail = haystack[-overlap:] if overlap else b""
    except OSError:
        return 0
    return count


def inspect_zip(path: Path) -> tuple[int | None, dict[str, int] | None, str | None]:
    try:
        with ZipFile(path) as archive:
            members = [member for member in archive.infolist() if not member.is_dir()]
            extensions = Counter(Path(member.filename).suffix.lower() or "[none]" for member in members)
            return len(members), dict(sorted(extensions.items())), None
    except (BadZipFile, OSError) as exc:
        return None, None, exc.__class__.__name__


def iter_data_files(data_root: Path) -> list[Path]:
    return sorted(path for path in data_root.rglob("*") if path.is_file())


def build_raw_file_facts(
    data_root: Path,
    *,
    count_text_hands: bool = False,
    progress: bool = False,
    progress_every: int = 50,
) -> list[RawFileFacts]:
    data_root = data_root.expanduser().resolve()
    facts: list[RawFileFacts] = []
    paths = iter_data_files(data_root)
    for index, path in enumerate(paths, start=1):
        relative_path = path.relative_to(data_root).as_posix()
        should_print_progress = (
            progress
            and (index == 1 or index == len(paths) or index % max(progress_every, 1) == 0)
        )
        if should_print_progress:
            print(f"[{index}/{len(paths)}] {relative_path}", file=sys.stderr, flush=True)
        extension = path.suffix.lower()
        input_kind = classify_input_kind(path)
        source_bucket = classify_source_bucket(relative_path, input_kind)
        hand_block_count = (
            count_hand_blocks(path)
            if count_text_hands and input_kind == "text_hand_history_candidate"
            else None
        )
        zip_member_count = None
        zip_member_extensions = None
        zip_error = None
        if input_kind == "zip_archive":
            zip_member_count, zip_member_extensions, zip_error = inspect_zip(path)
        facts.append(
            RawFileFacts(
                path=path,
                relative_path=relative_path,
                filename=path.name,
                extension=extension or "[none]",
                size_bytes=path.stat().st_size,
                sha256=sha256_file(path),
                input_kind=input_kind,
                source_bucket=source_bucket,
                processing_status=processing_status_for(input_kind),
                hand_block_count=hand_block_count,
                zip_member_count=zip_member_count,
                zip_member_extensions=zip_member_extensions,
                zip_error=zip_error,
            )
        )
    return facts


def _duplicate_groups(facts: list[RawFileFacts]) -> dict[str, str]:
    by_hash: dict[str, list[RawFileFacts]] = defaultdict(list)
    for item in facts:
        by_hash[item.sha256].append(item)
    duplicate_group_by_hash: dict[str, str] = {}
    for sha256, items in sorted(by_hash.items()):
        if len(items) > 1:
            duplicate_group_by_hash[sha256] = f"dup-{sha256[:12]}"
    return duplicate_group_by_hash


def _record_for(item: RawFileFacts, duplicate_group_by_hash: dict[str, str]) -> dict[str, Any]:
    record = {
        "file_id": item.sha256,
        "sha256": item.sha256,
        "sha256_12": item.sha256[:12],
        "duplicate_group_id": duplicate_group_by_hash.get(item.sha256),
        "relative_path": item.relative_path,
        "filename": item.filename,
        "safe_original_name": safe_original_name(item.path),
        "extension": item.extension,
        "size_bytes": item.size_bytes,
        "input_kind": item.input_kind,
        "source_bucket": item.source_bucket,
        "processing_status": item.processing_status,
        "hand_block_count": item.hand_block_count,
        "zip_member_count": item.zip_member_count,
        "zip_member_extensions": item.zip_member_extensions,
        "zip_error": item.zip_error,
    }
    return {key: value for key, value in record.items() if value is not None}


def build_raw_manifest(
    data_root: Path,
    *,
    generated_at: str | None = None,
    count_text_hands: bool = False,
    progress: bool = False,
    progress_every: int = 50,
) -> dict[str, Any]:
    data_root = data_root.expanduser().resolve()
    facts = build_raw_file_facts(
        data_root,
        count_text_hands=count_text_hands,
        progress=progress,
        progress_every=progress_every,
    )
    duplicate_group_by_hash = _duplicate_groups(facts)
    input_counts = Counter(item.input_kind for item in facts)
    bucket_counts = Counter(item.source_bucket for item in facts)
    status_counts = Counter(item.processing_status for item in facts)
    extension_counts = Counter(item.extension for item in facts)
    duplicate_file_count = sum(1 for item in facts if item.sha256 in duplicate_group_by_hash)
    text_hand_block_count = (
        sum(item.hand_block_count or 0 for item in facts)
        if count_text_hands
        else None
    )

    if generated_at is None:
        generated_at = datetime.now(timezone.utc).isoformat()

    return {
        "schema_version": "raw_file_manifest_v0",
        "generated_at": generated_at,
        "data_root": str(data_root),
        "totals": {
            "file_count": len(facts),
            "total_size_bytes": sum(item.size_bytes for item in facts),
            "input_kind_counts": dict(sorted(input_counts.items())),
            "source_bucket_counts": dict(sorted(bucket_counts.items())),
            "processing_status_counts": dict(sorted(status_counts.items())),
            "extension_counts": dict(sorted(extension_counts.items())),
            "duplicate_group_count": len(duplicate_group_by_hash),
            "duplicate_file_count": duplicate_file_count,
            "text_hand_block_count": text_hand_block_count,
            "text_hand_block_count_mode": "counted" if count_text_hands else "skipped",
        },
        "files": [_record_for(item, duplicate_group_by_hash) for item in facts],
    }


def write_manifest(manifest: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
