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
from core.ingest.matrix_played_pot_seed import build_matrix_played_pot_seed, classify_hero_preflop_play
from core.ingest.matrix_result_seed import build_matrix_result_seed, write_matrix_result_seed
from core.ingest.matrix_seed import build_matrix_count_seed, write_matrix_count_seed
from core.ingest.raw_manifest import build_raw_manifest, write_manifest


def hand(ref: str, cards: str, action_lines: list[str], summary_line: str) -> str:
    actions = "\n".join(action_lines)
    return f"""Poker Hand #{ref}: Tournament #111, Test Event Hold'em No Limit - Level1(50/100(12)) - 2026/04/01 01:00:00
Table '1' 9-max Seat #1 is the button
Seat 1: Hero (10000 in chips)
Seat 2: Villain (10000 in chips)
Hero: posts the ante 12
Hero: posts big blind 100
*** HOLE CARDS ***
Dealt to Hero [{cards}]
{actions}
*** SUMMARY ***
Total pot 1,500 | Rake 0 | Jackpot 0 | Bingo 0 | Fortune 0 | Tax 0
{summary_line}
"""


HAND_RAISE = hand("TM1", "As Qs", ["Hero: raises 200 to 300"], "Seat 1: Hero won (1,500)")
HAND_CALL = hand("TM2", "7d 7c", ["Villain: raises 200 to 300", "Hero: calls 200"], "Seat 1: Hero folded on the Flop")
HAND_ALL_IN = hand("TM3", "Td Kh", ["Hero: raises 900 to 1,000 and is all-in"], "Seat 1: Hero lost with King high")
HAND_FOLD = hand("TM4", "2c 3d", ["Villain: raises 200 to 300", "Hero: folds"], "Seat 1: Hero folded before Flop")
HAND_CHECK = hand("TM5", "4c 5d", ["Hero: checks"], "Seat 1: Hero folded on the Flop")


def main() -> None:
    if not classify_hero_preflop_play(HAND_RAISE.splitlines())["is_played_pot"]:
        raise AssertionError("Expected raise to be played")
    if classify_hero_preflop_play(HAND_FOLD.splitlines())["is_played_pot"]:
        raise AssertionError("Expected fold to be unplayed")
    if classify_hero_preflop_play(HAND_CHECK.splitlines())["is_played_pot"]:
        raise AssertionError("Expected check to be unplayed")

    with TemporaryDirectory() as tmp:
        data_root = Path(tmp) / "data"
        source_dir = data_root / "tmp_uploads_public" / "expanded" / "dump-a"
        source_dir.mkdir(parents=True)
        (source_dir / "GG20260401-0100 - played pot test.txt").write_text(
            "\n".join([HAND_RAISE, HAND_CALL, HAND_ALL_IN, HAND_FOLD, HAND_CHECK]),
            encoding="utf-8",
        )

        raw_manifest = build_raw_manifest(data_root, generated_at="2026-07-07T00:00:00+00:00")
        raw_manifest_path = data_root / "manifests" / "raw_file_manifest.json"
        write_manifest(raw_manifest, raw_manifest_path)

        hand_ledger = build_hand_extraction_ledger(raw_manifest_path, generated_at="2026-07-07T00:00:00+00:00")
        hand_ledger_path = data_root / "manifests" / "hand_extraction_ledger.json"
        write_hand_extraction_ledger(hand_ledger, hand_ledger_path)

        dataset_index = build_processable_dataset_index(raw_manifest_path, hand_ledger_path, generated_at="2026-07-07T00:00:00+00:00")
        dataset_index_path = data_root / "manifests" / "processable_dataset_index.json"
        write_processable_dataset_index(dataset_index, dataset_index_path)

        matrix_seed = build_matrix_count_seed(hand_ledger_path, dataset_index_path, generated_at="2026-07-07T00:00:00+00:00")
        matrix_seed_path = data_root / "manifests" / "matrix_count_seed.json"
        write_matrix_count_seed(matrix_seed, matrix_seed_path)

        result_seed = build_matrix_result_seed(matrix_seed_path, generated_at="2026-07-07T00:00:00+00:00")
        result_seed_path = data_root / "manifests" / "matrix_result_seed.json"
        write_matrix_result_seed(result_seed, result_seed_path)

        played_seed = build_matrix_played_pot_seed(result_seed_path, generated_at="2026-07-07T00:00:00+00:00")
        totals = played_seed["totals"]
        if totals["dealt_hand_count"] != 5:
            raise AssertionError(totals)
        if totals["played_pot_count"] != 3:
            raise AssertionError(totals)
        if totals["folded_or_unplayed_exposure_count"] != 2:
            raise AssertionError(totals)
        if played_seed["hand_class_results"]["AQs"]["played_pot_count"] != 1:
            raise AssertionError(played_seed["hand_class_results"]["AQs"])
        if played_seed["hand_class_results"]["54o"]["played_pot_count"] != 0:
            raise AssertionError(played_seed["hand_class_results"]["54o"])

    print("Matrix played-pot seed tests passed.")


if __name__ == "__main__":
    main()
