from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


AMOUNT_RE = re.compile(r"\((?P<amount>[\d,]+)\)")
TOTAL_POT_RE = re.compile(r"^Total pot (?P<amount>[\d,]+)")


@dataclass(frozen=True)
class MatrixResultHand:
    hand_fingerprint: str
    hand_fingerprint_12: str
    hand_class: str
    hero_cards: str
    outcome: str
    result_source: str
    source_relative_path: str
    line_start: int
    line_end: int
    hand_ref: str | None
    tournament_id: str | None
    played_at: str | None
    gross_collected_chips: int | None = None
    total_pot_chips: int | None = None
    hero_summary_line: str | None = None


def parse_amount(value: str) -> int:
    return int(value.replace(",", ""))


def _amount_in_parentheses(line: str) -> int | None:
    match = AMOUNT_RE.search(line)
    return parse_amount(match.group("amount")) if match else None


def _summary_lines(block_lines: list[str]) -> list[str]:
    for index, line in enumerate(block_lines):
        if line.startswith("*** SUMMARY ***"):
            return block_lines[index + 1 :]
    return []


def extract_hero_summary_result(block_lines: list[str]) -> dict[str, Any]:
    summary = _summary_lines(block_lines)
    total_pot = None
    hero_line = None

    for line in summary:
        total_match = TOTAL_POT_RE.match(line.strip())
        if total_match:
            total_pot = parse_amount(total_match.group("amount"))
        if line.startswith("Seat ") and "Hero" in line:
            hero_line = line.strip()

    if not hero_line:
        return {
            "outcome": "unknown",
            "result_source": "missing_hero_summary_line",
            "total_pot_chips": total_pot,
        }

    lower = hero_line.lower()
    gross_collected = _amount_in_parentheses(hero_line)
    if " collected " in lower or " collected (" in lower:
        outcome = "collected"
    elif " won " in lower or " and won " in lower:
        outcome = "won"
    elif " lost " in lower or " and lost " in lower:
        outcome = "lost"
    elif " folded " in lower:
        outcome = "folded"
    else:
        outcome = "unknown"

    return {
        "outcome": outcome,
        "result_source": "hero_summary_line",
        "gross_collected_chips": gross_collected if outcome in {"won", "collected"} else None,
        "total_pot_chips": total_pot,
        "hero_summary_line": hero_line,
    }


def _read_block(data_root: Path, hand: dict[str, Any]) -> list[str]:
    path = data_root / str(hand["source_relative_path"])
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return lines[int(hand["line_start"]) - 1 : int(hand["line_end"])]


def build_matrix_result_seed(
    matrix_count_seed_path: Path,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    matrix_count_seed_path = matrix_count_seed_path.expanduser().resolve()
    matrix_seed = json.loads(matrix_count_seed_path.read_text(encoding="utf-8"))
    data_root = Path(matrix_seed["data_root"]).expanduser().resolve()

    result_hands: list[MatrixResultHand] = []
    for hand in matrix_seed.get("hands", []):
        block_lines = _read_block(data_root, hand)
        result = extract_hero_summary_result(block_lines)
        result_hands.append(
            MatrixResultHand(
                hand_fingerprint=str(hand["hand_fingerprint"]),
                hand_fingerprint_12=str(hand["hand_fingerprint_12"]),
                hand_class=str(hand["hand_class"]),
                hero_cards=str(hand["hero_cards"]),
                outcome=str(result["outcome"]),
                result_source=str(result["result_source"]),
                gross_collected_chips=result.get("gross_collected_chips"),
                total_pot_chips=result.get("total_pot_chips"),
                hero_summary_line=result.get("hero_summary_line"),
                source_relative_path=str(hand["source_relative_path"]),
                line_start=int(hand["line_start"]),
                line_end=int(hand["line_end"]),
                hand_ref=hand.get("hand_ref"),
                tournament_id=hand.get("tournament_id"),
                played_at=hand.get("played_at"),
            )
        )

    outcome_counts = Counter(item.outcome for item in result_hands)
    by_class: dict[str, list[MatrixResultHand]] = defaultdict(list)
    for item in result_hands:
        by_class[item.hand_class].append(item)

    hand_class_results = {}
    for hand_class, items in sorted(by_class.items()):
        class_outcomes = Counter(item.outcome for item in items)
        hand_class_results[hand_class] = {
            "hand_class": hand_class,
            "result_observed_count": len(items),
            "outcome_counts": dict(sorted(class_outcomes.items())),
            "gross_collected_chips_sum": sum(item.gross_collected_chips or 0 for item in items),
            "total_pot_chips_sum": sum(item.total_pot_chips or 0 for item in items),
        }

    if generated_at is None:
        generated_at = datetime.now(timezone.utc).isoformat()

    return {
        "schema_version": "matrix_result_seed_v0",
        "generated_at": generated_at,
        "matrix_count_seed_path": str(matrix_count_seed_path),
        "data_root": str(data_root),
        "counting_policy": {
            "unit": "unique_raw_hand_fingerprint_with_hero_cards",
            "result_source": "GG summary Hero seat line",
            "amount_policy": "gross_collected_chips_not_net_profit",
            "interpretation_policy": "none",
        },
        "totals": {
            "result_hand_count": len(result_hands),
            "outcome_counts": dict(sorted(outcome_counts.items())),
            "gross_collected_chips_sum": sum(item.gross_collected_chips or 0 for item in result_hands),
            "total_pot_chips_sum": sum(item.total_pot_chips or 0 for item in result_hands),
            "distinct_hand_class_count": len(hand_class_results),
            "unknown_result_count": outcome_counts.get("unknown", 0),
        },
        "hand_class_results": hand_class_results,
        "hands": [
            {key: value for key, value in item.__dict__.items() if value is not None}
            for item in result_hands
        ],
    }


def write_matrix_result_seed(seed: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(seed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
