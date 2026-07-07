#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.ingest.dataset_index import build_processable_dataset_index, write_processable_dataset_index
from core.ingest.hand_extraction import build_hand_extraction_ledger, write_hand_extraction_ledger
from core.ingest.matrix_seed import build_matrix_count_seed, classify_hole_cards
from core.ingest.raw_manifest import build_raw_manifest, write_manifest


HAND_AQS = """Poker Hand #TM1: Tournament #111, Test Event Hold'em No Limit - Level1(50/100(12)) - 2026/04/01 01:00:00
Table '1' 9-max Seat #1 is the button
Seat 1: Hero (10000 in chips)
*** HOLE CARDS ***
Dealt to Hero [As Qs]
Hero: raises 200 to 300
*** SUMMARY ***
"""

HAND_77 = """Poker Hand #TM2: Tournament #111, Test Event Hold'em No Limit - Level1(50/100(12)) - 2026/04/01 01:00:10
Table '1' 9-max Seat #2 is the button
Seat 1: Hero (9900 in chips)
*** HOLE CARDS ***
Dealt to Hero [7d 7c]
Hero: folds
*** SUMMARY ***
"""

HAND_KTO = """Poker Hand #TM3: Tournament #111, Test Event Hold'em No Limit - Level1(50/100(12)) - 2026/04/01 01:00:20
Table '1' 9-max Seat #3 is the button
Seat 1: Hero (9900 in chips)
*** HOLE CARDS ***
Dealt to Hero [Td Kh]
Hero: folds
*** SUMMARY ***
"""

HAND_MISSING_CARDS = """Poker Hand #TM4: Tournament #111, Test Event Hold'em No Limit - Level1(50/100(12)) - 2026/04/01 01:00:30
Table '1' 9-max Seat #4 is the button
Seat 1: Hero (9900 in chips)
*** HOLE CARDS ***
Hero: folds
*** SUMMARY ***
"""


def main() -> None:
    if classify_hole_cards("As", "Qs") != "AQs":
        raise AssertionError("Expected AQs")
    if classify_hole_cards("Td", "Kh") != "KTo":
        raise AssertionError("Expected KTo")
    if classify_hole_cards("7d", "7c") != "77":
        raise AssertionError("Expected 77")

    with TemporaryDirectory() as tmp:
        data_root = Path(tmp) / "data"
        source_dir = data_root / "tmp_uploads_public" / "expanded" / "dump-a"
        source_dir.mkdir(parents=True)
        (source_dir / "GG20260401-0100 - first.txt").write_text(
            "\n".join([HAND_AQS, HAND_77, HAND_KTO, HAND_MISSING_CARDS]),
            encoding="utf-8",
        )
        (source_dir / "GG20260401-0100 - duplicate.txt").write_text(HAND_AQS, encoding="utf-8")

        raw_manifest = build_raw_manifest(data_root, generated_at="2026-07-07T00:00:00+00:00")
        raw_manifest_path = data_root / "manifests" / "raw_file_manifest.json"
        write_manifest(raw_manifest, raw_manifest_path)

        hand_ledger = build_hand_extraction_ledger(raw_manifest_path, generated_at="2026-07-07T00:00:00+00:00")
        hand_ledger_path = data_root / "manifests" / "hand_extraction_ledger.json"
        write_hand_extraction_ledger(hand_ledger, hand_ledger_path)

        dataset_index = build_processable_dataset_index(
            raw_manifest_path,
            hand_ledger_path,
            generated_at="2026-07-07T00:00:00+00:00",
        )
        dataset_index_path = data_root / "manifests" / "processable_dataset_index.json"
        write_processable_dataset_index(dataset_index, dataset_index_path)

        seed = build_matrix_count_seed(
            hand_ledger_path,
            dataset_index_path,
            generated_at="2026-07-07T00:00:00+00:00",
        )

        totals = seed["totals"]
        if totals["source_hand_occurrence_count"] != 5:
            raise AssertionError(totals)
        if totals["unique_hand_fingerprint_count"] != 4:
            raise AssertionError(totals)
        if totals["duplicate_occurrences_skipped"] != 1:
            raise AssertionError(totals)
        if totals["classified_unique_hand_count"] != 3:
            raise AssertionError(totals)
        if totals["missing_hero_cards_unique_hand_count"] != 1:
            raise AssertionError(totals)
        if seed["hand_class_counts"] != {"77": 1, "AQs": 1, "KTo": 1}:
            raise AssertionError(seed["hand_class_counts"])
        if len(seed["matrix_cells"]) != 169:
            raise AssertionError("Expected 169 matrix cells")
        if seed["matrix_cells"]["AQs"]["unique_hand_count"] != 1:
            raise AssertionError("Expected AQs count")

    print("Matrix seed tests passed.")


if __name__ == "__main__":
    main()
