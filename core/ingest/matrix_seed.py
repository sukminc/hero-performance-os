from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RANKS_DESC = "AKQJT98765432"
RANK_ORDER = "23456789TJQKA"
DEALT_TO_HERO_RE = re.compile(
    r"^Dealt to Hero \[(?P<card1>(?:10|[2-9TJQKA])[cdhs]) (?P<card2>(?:10|[2-9TJQKA])[cdhs])\]"
)


@dataclass(frozen=True)
class MatrixSeedHand:
    hand_fingerprint: str
    hand_fingerprint_12: str
    hand_class: str
    hero_cards: str
    source_relative_path: str
    line_start: int
    line_end: int
    hand_ref: str | None
    tournament_id: str | None
    played_at: str | None


def _rank(card: str) -> str:
    rank = card[:-1].upper()
    return "T" if rank == "10" else rank


def classify_hole_cards(card1: str, card2: str) -> str | None:
    rank1 = _rank(card1)
    rank2 = _rank(card2)
    if rank1 not in RANK_ORDER or rank2 not in RANK_ORDER:
        return None
    if rank1 == rank2:
        return f"{rank1}{rank2}"
    high, low = sorted([rank1, rank2], key=lambda item: RANK_ORDER.index(item), reverse=True)
    suited = card1[-1].lower() == card2[-1].lower()
    return f"{high}{low}{'s' if suited else 'o'}"


def extract_hero_cards(block_lines: list[str]) -> tuple[str | None, str | None]:
    for line in block_lines:
        match = DEALT_TO_HERO_RE.match(line.strip())
        if not match:
            continue
        card1 = match.group("card1")
        card2 = match.group("card2")
        hand_class = classify_hole_cards(card1, card2)
        return f"{card1} {card2}", hand_class
    return None, None


def _matrix_hand_class(row_rank: str, column_rank: str) -> str:
    if row_rank == column_rank:
        return f"{row_rank}{column_rank}"
    row_is_higher = RANK_ORDER.index(row_rank) > RANK_ORDER.index(column_rank)
    high = row_rank if row_is_higher else column_rank
    low = column_rank if row_is_higher else row_rank
    return f"{high}{low}{'s' if row_is_higher else 'o'}"


def _empty_matrix_cells() -> dict[str, dict[str, Any]]:
    cells: dict[str, dict[str, Any]] = {}
    for row_rank in RANKS_DESC:
        for column_rank in RANKS_DESC:
            hand_class = _matrix_hand_class(row_rank, column_rank)
            cells[hand_class] = {
                "hand_class": hand_class,
                "row_rank": row_rank,
                "column_rank": column_rank,
                "unique_hand_count": 0,
            }
    return cells


def _read_block(data_root: Path, hand: dict[str, Any]) -> list[str]:
    path = data_root / str(hand["source_relative_path"])
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return lines[int(hand["line_start"]) - 1 : int(hand["line_end"])]


def _hand_history_file_ids(dataset_index: dict[str, Any]) -> set[str]:
    return {
        str(asset["file_id"])
        for asset in dataset_index.get("assets", [])
        if asset.get("dataset_asset_kind") == "hand_history_text"
    }


def build_matrix_count_seed(
    hand_ledger_path: Path,
    dataset_index_path: Path,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    hand_ledger_path = hand_ledger_path.expanduser().resolve()
    dataset_index_path = dataset_index_path.expanduser().resolve()
    hand_ledger = json.loads(hand_ledger_path.read_text(encoding="utf-8"))
    dataset_index = json.loads(dataset_index_path.read_text(encoding="utf-8"))
    data_root = Path(hand_ledger["data_root"]).expanduser().resolve()
    allowed_file_ids = _hand_history_file_ids(dataset_index)

    seen_fingerprints: set[str] = set()
    duplicate_occurrences_skipped = 0
    missing_hero_cards: list[dict[str, Any]] = []
    classified_hands: list[MatrixSeedHand] = []

    for hand in hand_ledger.get("hands", []):
        if str(hand["source_file_id"]) not in allowed_file_ids:
            continue
        fingerprint = str(hand["hand_fingerprint"])
        if fingerprint in seen_fingerprints:
            duplicate_occurrences_skipped += 1
            continue
        seen_fingerprints.add(fingerprint)

        block_lines = _read_block(data_root, hand)
        hero_cards, hand_class = extract_hero_cards(block_lines)
        if not hero_cards or not hand_class:
            missing_hero_cards.append(
                {
                    "hand_fingerprint": fingerprint,
                    "hand_fingerprint_12": str(hand["hand_fingerprint_12"]),
                    "source_relative_path": str(hand["source_relative_path"]),
                    "line_start": int(hand["line_start"]),
                    "line_end": int(hand["line_end"]),
                    "hand_ref": hand.get("hand_ref"),
                }
            )
            continue

        classified_hands.append(
            MatrixSeedHand(
                hand_fingerprint=fingerprint,
                hand_fingerprint_12=str(hand["hand_fingerprint_12"]),
                hand_class=hand_class,
                hero_cards=hero_cards,
                source_relative_path=str(hand["source_relative_path"]),
                line_start=int(hand["line_start"]),
                line_end=int(hand["line_end"]),
                hand_ref=hand.get("hand_ref"),
                tournament_id=hand.get("tournament_id"),
                played_at=hand.get("played_at"),
            )
        )

    hand_class_counts = Counter(item.hand_class for item in classified_hands)
    matrix_cells = _empty_matrix_cells()
    for hand_class, count in hand_class_counts.items():
        matrix_cells[hand_class]["unique_hand_count"] = count

    if generated_at is None:
        generated_at = datetime.now(timezone.utc).isoformat()

    return {
        "schema_version": "matrix_count_seed_v0",
        "generated_at": generated_at,
        "hand_ledger_path": str(hand_ledger_path),
        "dataset_index_path": str(dataset_index_path),
        "data_root": str(data_root),
        "counting_policy": {
            "unit": "unique_raw_hand_fingerprint",
            "card_source": "Dealt to Hero line",
            "result_policy": "not_extracted_in_v0",
            "interpretation_policy": "none",
        },
        "totals": {
            "source_hand_occurrence_count": len(
                [
                    hand
                    for hand in hand_ledger.get("hands", [])
                    if str(hand["source_file_id"]) in allowed_file_ids
                ]
            ),
            "unique_hand_fingerprint_count": len(seen_fingerprints),
            "duplicate_occurrences_skipped": duplicate_occurrences_skipped,
            "classified_unique_hand_count": len(classified_hands),
            "missing_hero_cards_unique_hand_count": len(missing_hero_cards),
            "distinct_hand_class_count": len(hand_class_counts),
        },
        "hand_class_counts": dict(sorted(hand_class_counts.items())),
        "matrix_cells": dict(sorted(matrix_cells.items())),
        "hands": [
            {key: value for key, value in item.__dict__.items() if value is not None}
            for item in classified_hands
        ],
        "missing_hero_cards": missing_hero_cards[:200],
    }


def write_matrix_count_seed(seed: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(seed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
