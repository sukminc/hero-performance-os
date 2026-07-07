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
from core.ingest.matrix_result_seed import build_matrix_result_seed, extract_hero_summary_result
from core.ingest.matrix_seed import build_matrix_count_seed, write_matrix_count_seed
from core.ingest.raw_manifest import build_raw_manifest, write_manifest


def hand(ref: str, cards: str, summary_line: str) -> str:
    return f"""Poker Hand #{ref}: Tournament #111, Test Event Hold'em No Limit - Level1(50/100(12)) - 2026/04/01 01:00:00
Table '1' 9-max Seat #1 is the button
Seat 1: Hero (10000 in chips)
*** HOLE CARDS ***
Dealt to Hero [{cards}]
Hero: checks
*** SUMMARY ***
Total pot 1,500 | Rake 0 | Jackpot 0 | Bingo 0 | Fortune 0 | Tax 0
{summary_line}
"""


HAND_WON = hand("TM1", "As Qs", "Seat 1: Hero (button) showed [As Qs] and won (1,500) with a pair of Aces")
HAND_COLLECTED = hand("TM2", "7d 7c", "Seat 1: Hero (big blind) collected (800)")
HAND_LOST = hand("TM3", "Td Kh", "Seat 1: Hero showed [Td Kh] and lost with King high")
HAND_FOLDED = hand("TM4", "2c 3d", "Seat 1: Hero (small blind) folded before Flop")
HAND_UNKNOWN = hand("TM5", "4c 5d", "Seat 1: Hero has an unsupported summary shape")


def main() -> None:
    won = extract_hero_summary_result(HAND_WON.splitlines())
    if won["outcome"] != "won" or won["gross_collected_chips"] != 1500:
        raise AssertionError(won)
    folded = extract_hero_summary_result(HAND_FOLDED.splitlines())
    if folded["outcome"] != "folded" or folded.get("gross_collected_chips") is not None:
        raise AssertionError(folded)

    with TemporaryDirectory() as tmp:
        data_root = Path(tmp) / "data"
        source_dir = data_root / "tmp_uploads_public" / "expanded" / "dump-a"
        source_dir.mkdir(parents=True)
        (source_dir / "GG20260401-0100 - result test.txt").write_text(
            "\n".join([HAND_WON, HAND_COLLECTED, HAND_LOST, HAND_FOLDED, HAND_UNKNOWN]),
            encoding="utf-8",
        )

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

        matrix_seed = build_matrix_count_seed(
            hand_ledger_path,
            dataset_index_path,
            generated_at="2026-07-07T00:00:00+00:00",
        )
        matrix_seed_path = data_root / "manifests" / "matrix_count_seed.json"
        write_matrix_count_seed(matrix_seed, matrix_seed_path)

        result_seed = build_matrix_result_seed(
            matrix_seed_path,
            generated_at="2026-07-07T00:00:00+00:00",
        )

        expected = {"collected": 1, "folded": 1, "lost": 1, "unknown": 1, "won": 1}
        if result_seed["totals"]["outcome_counts"] != expected:
            raise AssertionError(result_seed["totals"]["outcome_counts"])
        if result_seed["totals"]["gross_collected_chips_sum"] != 2300:
            raise AssertionError(result_seed["totals"])
        if result_seed["hand_class_results"]["AQs"]["outcome_counts"] != {"won": 1}:
            raise AssertionError(result_seed["hand_class_results"]["AQs"])

    print("Matrix result seed tests passed.")


if __name__ == "__main__":
    main()
