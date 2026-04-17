#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.ingest.legacy_corpus import build_legacy_corpus_summary, collect_legacy_raw_gg_files


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        first = root / "data/tmp_uploads/zip_intake_runs/run_a/extracted/archive_1/GG20260329-0552 - test.txt"
        second = root / "data/tmp_uploads/zip_intake_runs/run_b/extracted/archive_2/GG20260329 - Tournament #6165727 - test.txt"
        duplicate = root / "data/tmp_uploads/another/GG20260329-0552 - test.txt"

        first.parent.mkdir(parents=True, exist_ok=True)
        second.parent.mkdir(parents=True, exist_ok=True)
        duplicate.parent.mkdir(parents=True, exist_ok=True)

        first.write_text("Poker Hand #1\n", encoding="utf-8")
        second.write_text("Tournament #1\nPoker Hand #2\n", encoding="utf-8")
        duplicate.write_text("Tournament summary only\n", encoding="utf-8")

        files = collect_legacy_raw_gg_files(old_repo_root=root)
        summary = build_legacy_corpus_summary(old_repo_root=root)

        if len(files) != 2:
            raise AssertionError(f"Expected 2 discovered txt files, got {len(files)}")
        if summary["raw_gg_txt_count"] != 2:
            raise AssertionError("Summary raw_gg_txt_count mismatch")
        if not summary["sample_files"]:
            raise AssertionError("Expected sample files in summary")

    print("Legacy corpus tests passed.")


if __name__ == "__main__":
    main()
