from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ACTION_RE = re.compile(r"^(?P<player>[^:]+):\s+(?P<action>.+)$")
VOLUNTARY_ACTION_KEYWORDS = ("raises", "calls", "bets", "all-in", "all in")


@dataclass(frozen=True)
class PlayedPotHand:
    hand_fingerprint: str
    hand_fingerprint_12: str
    hand_class: str
    hero_cards: str
    is_played_pot: bool
    played_pot_reason: str
    first_hero_voluntary_action: str | None
    outcome: str
    source_relative_path: str
    line_start: int
    line_end: int
    hand_ref: str | None
    tournament_id: str | None
    played_at: str | None
    gross_collected_chips: int | None = None
    total_pot_chips: int | None = None


def _preflop_lines(block_lines: list[str]) -> list[str]:
    started = False
    lines: list[str] = []
    for line in block_lines:
        if line.startswith("*** HOLE CARDS ***"):
            started = True
            lines.append(line)
            continue
        if not started:
            continue
        if line.startswith("*** FLOP ***") or line.startswith("*** SHOWDOWN ***") or line.startswith("*** SUMMARY ***"):
            break
        lines.append(line)
    return lines


def _is_forced_or_nonentry(action: str) -> bool:
    lower = action.lower()
    return (
        "posts" in lower
        or "ante" in lower
        or lower.startswith("checks")
        or lower.startswith("folds")
        or lower.startswith("doesn't show")
        or lower.startswith("shows")
    )


def classify_hero_preflop_play(block_lines: list[str]) -> dict[str, Any]:
    saw_hero_action = False
    for line in _preflop_lines(block_lines):
        action_match = ACTION_RE.match(line.strip())
        if not action_match:
            continue
        player = action_match.group("player").strip()
        if player != "Hero":
            continue
        action = action_match.group("action").strip()
        lower = action.lower()
        if _is_forced_or_nonentry(action):
            saw_hero_action = True
            continue
        if any(keyword in lower for keyword in VOLUNTARY_ACTION_KEYWORDS):
            return {
                "is_played_pot": True,
                "played_pot_reason": "hero_voluntary_preflop_action",
                "first_hero_voluntary_action": action,
            }
        saw_hero_action = True
        return {
            "is_played_pot": False,
            "played_pot_reason": "hero_preflop_action_unclassified",
            "first_hero_voluntary_action": action,
        }

    return {
        "is_played_pot": False,
        "played_pot_reason": "no_hero_voluntary_preflop_action" if saw_hero_action else "no_hero_preflop_action",
        "first_hero_voluntary_action": None,
    }


def _read_block(data_root: Path, hand: dict[str, Any]) -> list[str]:
    path = data_root / str(hand["source_relative_path"])
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return lines[int(hand["line_start"]) - 1 : int(hand["line_end"])]


def build_matrix_played_pot_seed(
    matrix_result_seed_path: Path,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    matrix_result_seed_path = matrix_result_seed_path.expanduser().resolve()
    result_seed = json.loads(matrix_result_seed_path.read_text(encoding="utf-8"))
    data_root = Path(result_seed["data_root"]).expanduser().resolve()

    hands: list[PlayedPotHand] = []
    for hand in result_seed.get("hands", []):
        block_lines = _read_block(data_root, hand)
        played = classify_hero_preflop_play(block_lines)
        hands.append(
            PlayedPotHand(
                hand_fingerprint=str(hand["hand_fingerprint"]),
                hand_fingerprint_12=str(hand["hand_fingerprint_12"]),
                hand_class=str(hand["hand_class"]),
                hero_cards=str(hand["hero_cards"]),
                is_played_pot=bool(played["is_played_pot"]),
                played_pot_reason=str(played["played_pot_reason"]),
                first_hero_voluntary_action=played.get("first_hero_voluntary_action"),
                outcome=str(hand["outcome"]),
                gross_collected_chips=hand.get("gross_collected_chips"),
                total_pot_chips=hand.get("total_pot_chips"),
                source_relative_path=str(hand["source_relative_path"]),
                line_start=int(hand["line_start"]),
                line_end=int(hand["line_end"]),
                hand_ref=hand.get("hand_ref"),
                tournament_id=hand.get("tournament_id"),
                played_at=hand.get("played_at"),
            )
        )

    by_class: dict[str, list[PlayedPotHand]] = defaultdict(list)
    for hand in hands:
        by_class[hand.hand_class].append(hand)

    hand_class_results = {}
    for hand_class, items in sorted(by_class.items()):
        played_items = [item for item in items if item.is_played_pot]
        folded_exposure_items = [item for item in items if not item.is_played_pot]
        hand_class_results[hand_class] = {
            "hand_class": hand_class,
            "dealt_count": len(items),
            "played_pot_count": len(played_items),
            "folded_or_unplayed_exposure_count": len(folded_exposure_items),
            "played_pot_outcome_counts": dict(sorted(Counter(item.outcome for item in played_items).items())),
            "dealt_outcome_counts": dict(sorted(Counter(item.outcome for item in items).items())),
            "played_pot_gross_collected_chips_sum": sum(item.gross_collected_chips or 0 for item in played_items),
        }

    reason_counts = Counter(item.played_pot_reason for item in hands)
    played_items = [item for item in hands if item.is_played_pot]

    if generated_at is None:
        generated_at = datetime.now(timezone.utc).isoformat()

    return {
        "schema_version": "matrix_played_pot_seed_v0",
        "generated_at": generated_at,
        "matrix_result_seed_path": str(matrix_result_seed_path),
        "data_root": str(data_root),
        "counting_policy": {
            "dealt_unit": "unique_raw_hand_fingerprint_with_hero_cards",
            "played_pot_policy": "Hero voluntarily calls, raises, bets, or jams preflop",
            "excluded_from_played_pot": "forced antes, blind posts, folds, and big-blind checks",
            "interpretation_policy": "none",
        },
        "totals": {
            "dealt_hand_count": len(hands),
            "played_pot_count": len(played_items),
            "folded_or_unplayed_exposure_count": len(hands) - len(played_items),
            "played_pot_rate": round(len(played_items) / len(hands), 4) if hands else 0.0,
            "played_pot_reason_counts": dict(sorted(reason_counts.items())),
            "distinct_hand_class_count": len(hand_class_results),
        },
        "hand_class_results": hand_class_results,
        "hands": [
            {key: value for key, value in item.__dict__.items() if value is not None}
            for item in hands
        ],
    }


def write_matrix_played_pot_seed(seed: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(seed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
