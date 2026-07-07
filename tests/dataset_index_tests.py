#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.ingest.dataset_index import build_processable_dataset_index
from core.ingest.hand_extraction import build_hand_extraction_ledger, write_hand_extraction_ledger
from core.ingest.raw_manifest import build_raw_manifest, write_manifest


HAND_TEXT = """Poker Hand #TM1: Tournament #111, Test Event Hold'em No Limit - Level1(50/100(12)) - 2026/04/01 01:00:00
Table '1' 9-max Seat #1 is the button
Seat 1: Hero (10000 in chips)
*** SUMMARY ***
"""

SUMMARY_TEXT = """Tournament #222, Test Summary Event, Hold'em No Limit
Buy-in: $1+$0.10
10 Players
You finished the tournament in 1st place.
"""


def main() -> None:
    with TemporaryDirectory() as tmp:
        data_root = Path(tmp) / "data"
        source_dir = data_root / "tmp_uploads_public" / "expanded" / "dump-a"
        upload_dir = data_root / "tmp_uploads_public"
        source_dir.mkdir(parents=True)

        (source_dir / "GG20260401-0100 - hand test.txt").write_text(HAND_TEXT, encoding="utf-8")
        (source_dir / "GG20260402 - Tournament #222 - summary.txt").write_text(SUMMARY_TEXT, encoding="utf-8")
        (source_dir / "2026-04-03_ screenshot.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        (data_root / "hero_v2.sqlite3").write_bytes(b"sqlite")
        with ZipFile(upload_dir / "dump.zip", "w") as archive:
            archive.writestr("inside.txt", HAND_TEXT)

        raw_manifest = build_raw_manifest(data_root, generated_at="2026-07-07T00:00:00+00:00")
        raw_manifest_path = data_root / "manifests" / "raw_file_manifest.json"
        write_manifest(raw_manifest, raw_manifest_path)

        hand_ledger = build_hand_extraction_ledger(raw_manifest_path, generated_at="2026-07-07T00:00:00+00:00")
        hand_ledger_path = data_root / "manifests" / "hand_extraction_ledger.json"
        write_hand_extraction_ledger(hand_ledger, hand_ledger_path)

        index = build_processable_dataset_index(
            raw_manifest_path,
            hand_ledger_path,
            generated_at="2026-07-07T00:00:00+00:00",
        )
        totals = index["totals"]
        if totals["asset_count"] != 5:
            raise AssertionError(f"Expected 5 assets, got {totals['asset_count']}")
        expected_counts = {
            "hand_history_text": 1,
            "tournament_summary_text": 1,
            "image_evidence": 1,
            "processed_database": 1,
            "zip_archive": 1,
        }
        if totals["dataset_asset_kind_counts"] != expected_counts:
            raise AssertionError(totals["dataset_asset_kind_counts"])

        by_kind = {item["dataset_asset_kind"]: item for item in index["assets"]}
        if by_kind["hand_history_text"]["hand_occurrence_count"] != 1:
            raise AssertionError("Expected one extracted hand")
        if by_kind["tournament_summary_text"]["tournament_id"] != "222":
            raise AssertionError("Expected tournament summary id")
        if not by_kind["hand_history_text"]["canonical_relative_path"].startswith("dataset_v0/hero/2026/04/01/"):
            raise AssertionError("Expected GG filename date in canonical path")
        if by_kind["processed_database"]["dataset_date"] != "unknown-date":
            raise AssertionError("Expected unknown date for processed DB")

    print("Dataset index tests passed.")


if __name__ == "__main__":
    main()
