#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.ingest.raw_manifest import build_raw_manifest


def main() -> None:
    with TemporaryDirectory() as tmp:
        data_root = Path(tmp) / "data"
        upload_dir = data_root / "tmp_uploads_public"
        expanded_dir = upload_dir / "expanded" / "dump-a"
        legacy_dir = data_root / "raw_intake_legacy" / "drop"
        upload_dir.mkdir(parents=True)
        expanded_dir.mkdir(parents=True)
        legacy_dir.mkdir(parents=True)

        text = "Poker Hand #1: test\nDealt to Hero [As Ah]\n\nPoker Hand #2: test\n"
        first_txt = expanded_dir / "GG20260101 - test.txt"
        duplicate_txt = legacy_dir / "duplicate.txt"
        image = legacy_dir / "screen.png"
        db = data_root / "hero_v2.sqlite3"
        archive = upload_dir / "dump.zip"

        first_txt.write_text(text, encoding="utf-8")
        duplicate_txt.write_text(text, encoding="utf-8")
        image.write_bytes(b"\x89PNG\r\n\x1a\n")
        db.write_bytes(b"sqlite bytes")
        with ZipFile(archive, "w") as zip_file:
            zip_file.writestr("one.txt", "Poker Hand #3\n")
            zip_file.writestr("screen.png", b"png")

        manifest = build_raw_manifest(
            data_root,
            generated_at="2026-07-07T00:00:00+00:00",
            count_text_hands=True,
        )
        totals = manifest["totals"]

        if totals["file_count"] != 5:
            raise AssertionError(f"Expected 5 files, got {totals['file_count']}")
        if totals["input_kind_counts"].get("text_hand_history_candidate") != 2:
            raise AssertionError("Expected 2 text candidates")
        if totals["input_kind_counts"].get("zip_archive") != 1:
            raise AssertionError("Expected 1 zip archive")
        if totals["input_kind_counts"].get("image_evidence") != 1:
            raise AssertionError("Expected 1 image evidence file")
        if totals["input_kind_counts"].get("processed_sqlite") != 1:
            raise AssertionError("Expected 1 processed sqlite file")
        if totals["duplicate_group_count"] != 1:
            raise AssertionError("Expected one duplicate hash group")
        if totals["duplicate_file_count"] != 2:
            raise AssertionError("Expected two files inside duplicate groups")
        if totals["text_hand_block_count"] != 4:
            raise AssertionError(f"Expected 4 text hand blocks, got {totals['text_hand_block_count']}")

        files_by_name = {item["filename"]: item for item in manifest["files"]}
        if files_by_name["dump.zip"]["zip_member_count"] != 2:
            raise AssertionError("Expected zip member count")
        if files_by_name["GG20260101 - test.txt"]["source_bucket"] != "expanded_upload_member":
            raise AssertionError("Expected expanded upload bucket")
        if files_by_name["screen.png"]["processing_status"] != "image_preserved":
            raise AssertionError("Expected image preservation status")

    print("Raw manifest tests passed.")


if __name__ == "__main__":
    main()
