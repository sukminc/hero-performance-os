from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from core.storage.sqlite import get_sqlite_connection


HERO_PLAYER_ID = "4c9d1e29-1f6b-4e5f-92da-111111111111"
RANK_ORDER = "AKQJT98765432"
RANK_VALUE = {rank: len(RANK_ORDER) - index for index, rank in enumerate(reversed(RANK_ORDER))}
DEFAULT_SELECTED_HAND = "KJo"
SUPPORTED_WINDOWS = {"90d", "all"}
SUPPORTED_STACK_FILTERS = {"all", "lt15", "15to25", "gt25"}


@dataclass
class HandObservation:
    hand_id: str
    session_id: str
    tournament_id: str
    started_at: str | None
    format_tag: str
    hand_class: str
    position: str
    active_seats: int
    stack_bb: float | None
    bb_net: float
    hero_summary: str
    first_preflop_action: str | None
    faced_action_preflop: bool
    preflop_entry_type: str
    prior_raise_count: int
    faced_all_in_preflop: bool
    open_size_bb: float | None
    hero_3bet_size_bb: float | None
    hero_3bet_to_open_ratio: float | None
    faced_4bet_after_3bet: bool
    folded_to_4bet_after_3bet: bool


def _parse_json(raw: str | None, default: Any) -> Any:
    if not raw:
        return default
    return json.loads(raw)


def _parse_started_at(raw: str | None) -> datetime | None:
    if not raw:
        return None
    for fmt in ("%Y/%m/%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S"):
        try:
            parsed = datetime.strptime(raw, fmt)
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=UTC)
            return parsed.astimezone(UTC)
        except ValueError:
            continue
    return None


def _extract_big_blind(header: str) -> float | None:
    match = re.search(r"Level\d+\(([\d,]+)/([\d,]+)(?:\(([\d,]+)\))?\)", header)
    if not match:
        return None
    return float(match.group(2).replace(",", ""))


def _parse_int(raw: str) -> int:
    return int(raw.replace(",", ""))


def _extract_hand_class(block: list[str]) -> str | None:
    for row in block:
        if not row.startswith("Dealt to Hero"):
            continue
        match = re.search(r"\[([2-9TJQKA][shdc])\s+([2-9TJQKA][shdc])\]", row)
        if not match:
            continue
        first = match.group(1)
        second = match.group(2)
        first_rank = first[0]
        second_rank = second[0]
        if first_rank == second_rank:
            return first_rank * 2
        ordered = sorted([first_rank, second_rank], key=lambda rank: RANK_ORDER.index(rank))
        suited = "s" if first[1] == second[1] else "o"
        return f"{ordered[0]}{ordered[1]}{suited}"
    return None


def _extract_format_tag(header: str, session_metadata: dict[str, Any]) -> str:
    haystack = " ".join(
        part
        for part in [
            header.lower(),
            str(session_metadata.get("stakes", "")).lower(),
            str(session_metadata.get("tournament_name", "")).lower(),
        ]
        if part
    )
    if any(keyword in haystack for keyword in ("satellite", "mega", "seat", "step to", "qualifier")):
        return "satellite"
    if any(keyword in haystack for keyword in ("bounty", "pko", "ko", "mystery bounty")):
        return "pko"
    return "standard_mtt"


def _extract_active_seats(block: list[str]) -> int:
    return sum(1 for row in block if row.startswith("Seat "))


def _extract_hero_position(block: list[str]) -> str | None:
    button_seat = None
    hero_seat = None
    for row in block:
        button_match = re.search(r"Seat #(\d+) is the button", row)
        if button_match:
            button_seat = int(button_match.group(1))
            continue
        hero_match = re.match(r"Seat (\d+): Hero\b", row)
        if hero_match:
            hero_seat = int(hero_match.group(1))
    if button_seat is None or hero_seat is None:
        return None

    seat_order: list[int] = []
    seen_hole_cards = False
    for row in block:
        if row == "*** HOLE CARDS ***":
            seen_hole_cards = True
            break
        seat_match = re.match(r"Seat (\d+): ", row)
        if seat_match:
            seat_order.append(int(seat_match.group(1)))
    if not seen_hole_cards or hero_seat not in seat_order or button_seat not in seat_order:
        return None

    sorted_seats = sorted(seat_order)
    button_index = sorted_seats.index(button_seat)
    ordered_from_button = sorted_seats[button_index:] + sorted_seats[:button_index]
    if hero_seat not in ordered_from_button:
        return None
    relative_index = ordered_from_button.index(hero_seat)
    labels_by_count = {
        2: ["BTN", "SB"],
        3: ["BTN", "SB", "BB"],
        4: ["BTN", "SB", "BB", "CO"],
        5: ["BTN", "SB", "BB", "UTG", "CO"],
        6: ["BTN", "SB", "BB", "UTG", "HJ", "CO"],
        7: ["BTN", "SB", "BB", "UTG", "UTG+1", "HJ", "CO"],
        8: ["BTN", "SB", "BB", "UTG", "UTG+1", "LJ", "HJ", "CO"],
        9: ["BTN", "SB", "BB", "UTG", "UTG+1", "UTG+2", "LJ", "HJ", "CO"],
    }
    labels = labels_by_count.get(len(ordered_from_button))
    if not labels or relative_index >= len(labels):
        return None
    return labels[relative_index]


def _extract_preflop_pattern(block: list[str]) -> tuple[str | None, bool, str, int, bool]:
    in_preflop = False
    faced_action = False
    faced_all_in = False
    prior_raise_count = 0
    prior_call_count = 0
    for row in block:
        if row == "*** HOLE CARDS ***":
            in_preflop = True
            continue
        if not in_preflop:
            continue
        if row.startswith("*** FLOP ***") or row.startswith("*** SHOWDOWN ***") or row.startswith("*** SUMMARY ***"):
            break
        if row.startswith("Hero:"):
            action = "other"
            if " folds" in row:
                action = "fold"
            elif " calls " in row:
                action = "call"
            elif " raises " in row:
                action = "jam" if "all-in" in row else "raise"
            return (
                action,
                faced_action,
                _entry_type(action, prior_raise_count, prior_call_count, faced_all_in),
                prior_raise_count,
                faced_all_in,
            )
        if ":" in row and any(token in row for token in (" raises ", " calls ", " bets ")):
            actor = row.split(":", 1)[0]
            if actor != "Hero":
                faced_action = True
                if "all-in" in row or "all in" in row:
                    faced_all_in = True
                if " raises " in row:
                    prior_raise_count += 1
                elif " calls " in row:
                    prior_call_count += 1
    return (None, faced_action, "missing_hero_action", prior_raise_count, faced_all_in)


def _entry_type(action: str | None, prior_raise_count: int, prior_call_count: int, faced_all_in: bool = False) -> str:
    if action == "fold":
        if faced_all_in:
            return "fold_vs_jam"
        if prior_raise_count == 0 and prior_call_count == 0:
            return "open_fold"
        if prior_raise_count == 0:
            return "fold_vs_limp"
        if prior_raise_count == 1:
            return "fold_vs_open"
        if prior_raise_count == 2:
            return "fold_vs_3bet"
        return "fold_vs_4bet_plus"
    if action == "call":
        if prior_raise_count == 0 and prior_call_count == 0:
            return "open_limp_or_complete"
        if prior_raise_count == 0:
            return "limp_behind"
        if prior_raise_count == 1:
            return "call_vs_open"
        if prior_raise_count == 2:
            return "call_vs_3bet"
        return "call_vs_4bet_plus"
    if action in {"raise", "jam"}:
        suffix = "_jam" if action == "jam" else ""
        if prior_raise_count == 0 and prior_call_count == 0:
            return f"open_raise{suffix}"
        if prior_raise_count == 0:
            return f"iso_raise{suffix}"
        if prior_raise_count == 1:
            return f"three_bet{suffix}"
        if prior_raise_count == 2:
            return f"four_bet{suffix}"
        return f"five_bet_plus{suffix}"
    return "other"


def _raise_to_amount(row: str) -> int | None:
    match = re.search(r" raises [\d,]+ to ([\d,]+)", row)
    if not match:
        return None
    return _parse_int(match.group(1))


def _extract_3bet_line_features(block: list[str], big_blind: float) -> dict[str, Any]:
    in_preflop = False
    prior_raise_to: int | None = None
    prior_raise_count = 0
    hero_3bet_to: int | None = None
    hero_made_3bet = False
    faced_4bet = False
    folded_to_4bet = False

    for row in block:
        if row == "*** HOLE CARDS ***":
            in_preflop = True
            continue
        if not in_preflop:
            continue
        if row.startswith("*** FLOP ***") or row.startswith("*** SHOWDOWN ***") or row.startswith("*** SUMMARY ***"):
            break
        if ":" not in row:
            continue

        actor, action = row.split(":", 1)
        if " raises " in row:
            raise_to = _raise_to_amount(row)
            if actor != "Hero" and not hero_made_3bet:
                prior_raise_count += 1
                if raise_to is not None:
                    prior_raise_to = raise_to
            elif actor == "Hero" and prior_raise_count == 1:
                hero_made_3bet = True
                hero_3bet_to = raise_to
            elif actor != "Hero" and hero_made_3bet:
                faced_4bet = True
        elif actor == "Hero" and hero_made_3bet and faced_4bet and " folds" in action:
            folded_to_4bet = True

    open_size_bb = round(prior_raise_to / big_blind, 2) if prior_raise_to and big_blind else None
    hero_3bet_size_bb = round(hero_3bet_to / big_blind, 2) if hero_3bet_to and big_blind else None
    ratio = round(hero_3bet_to / prior_raise_to, 2) if hero_3bet_to and prior_raise_to else None
    return {
        "open_size_bb": open_size_bb,
        "hero_3bet_size_bb": hero_3bet_size_bb,
        "hero_3bet_to_open_ratio": ratio,
        "faced_4bet_after_3bet": faced_4bet,
        "folded_to_4bet_after_3bet": folded_to_4bet,
    }


def _compute_bb_net(block: list[str], big_blind: float) -> float:
    hero_total = 0
    hero_current_street = 0

    for row in block:
        if row.startswith("*** FLOP ***") or row.startswith("*** TURN ***") or row.startswith("*** RIVER ***"):
            hero_current_street = 0
            continue
        if row.startswith("*** SUMMARY ***"):
            break

        if row.startswith("Hero: posts the ante "):
            hero_total -= _parse_int(row.split("Hero: posts the ante ", 1)[1])
            hero_current_street += _parse_int(row.split("Hero: posts the ante ", 1)[1])
            continue
        if row.startswith("Hero: posts small blind "):
            amount = _parse_int(row.split("Hero: posts small blind ", 1)[1])
            hero_total -= amount
            hero_current_street += amount
            continue
        if row.startswith("Hero: posts big blind "):
            amount = _parse_int(row.split("Hero: posts big blind ", 1)[1])
            hero_total -= amount
            hero_current_street += amount
            continue
        if row.startswith("Hero: calls "):
            amount = _parse_int(row.split("Hero: calls ", 1)[1].split()[0])
            hero_total -= amount
            hero_current_street += amount
            continue
        if row.startswith("Hero: bets "):
            amount = _parse_int(row.split("Hero: bets ", 1)[1].split()[0])
            hero_total -= amount
            hero_current_street += amount
            continue
        if row.startswith("Hero: raises "):
            match = re.search(r"to ([\d,]+)", row)
            if not match:
                continue
            total_to = _parse_int(match.group(1))
            incremental = max(total_to - hero_current_street, 0)
            hero_total -= incremental
            hero_current_street = total_to
            continue
        if row.startswith("Uncalled bet (") and "returned to Hero" in row:
            match = re.search(r"Uncalled bet \(([\d,]+)\)", row)
            if not match:
                continue
            amount = _parse_int(match.group(1))
            hero_total += amount
            hero_current_street = max(hero_current_street - amount, 0)
            continue
        if row.startswith("Hero collected "):
            amount = _parse_int(row.split("Hero collected ", 1)[1].split()[0])
            hero_total += amount
            continue

    return round(hero_total / big_blind, 4)


def _sample_band(count: int) -> str:
    if count < 5:
        return "tiny"
    if count < 20:
        return "small"
    if count < 50:
        return "medium"
    return "large"


def _matrix_order() -> list[str]:
    cells: list[str] = []
    for row_rank in RANK_ORDER:
        for col_rank in RANK_ORDER:
            if row_rank == col_rank:
                cells.append(row_rank * 2)
            elif RANK_ORDER.index(row_rank) < RANK_ORDER.index(col_rank):
                cells.append(f"{row_rank}{col_rank}s")
            else:
                cells.append(f"{col_rank}{row_rank}o")
    return cells


def _position_sort_key(position: str) -> tuple[int, str]:
    order = ["UTG", "UTG+1", "UTG+2", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
    try:
        return (order.index(position), position)
    except ValueError:
        return (999, position)


def _cell_style(metric_value: float) -> str:
    if metric_value >= 1.0:
        return "very-good"
    if metric_value >= 0.25:
        return "good"
    if metric_value > -0.25:
        return "neutral"
    if metric_value > -1.0:
        return "bad"
    return "very-bad"


def _pct_style(metric_value: float) -> str:
    if metric_value >= 12.0:
        return "very-good"
    if metric_value >= 3.0:
        return "good"
    if metric_value > -3.0:
        return "neutral"
    if metric_value > -12.0:
        return "bad"
    return "very-bad"


def _stack_realization_pct(item: HandObservation) -> float | None:
    if item.stack_bb is None or item.stack_bb <= 0:
        return None
    return round((item.bb_net / item.stack_bb) * 100, 4)


def _avg(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 2)


def _stack_metrics(rows: list[HandObservation]) -> dict[str, Any]:
    realizations = [value for item in rows if (value := _stack_realization_pct(item)) is not None]
    full_stack_losses = [item for item in rows if (value := _stack_realization_pct(item)) is not None and value <= -80]
    double_ups = [item for item in rows if (value := _stack_realization_pct(item)) is not None and value >= 80]
    short_rows = [item for item in rows if item.stack_bb is not None and item.stack_bb < 15]
    mid_rows = [item for item in rows if item.stack_bb is not None and 15 <= item.stack_bb <= 25]
    deep_rows = [item for item in rows if item.stack_bb is not None and item.stack_bb > 25]
    return {
        "avg_stack_realization_pct": _avg(realizations),
        "full_stack_loss_count": len(full_stack_losses),
        "full_stack_loss_rate": round(len(full_stack_losses) / len(realizations), 4) if realizations else None,
        "double_up_count": len(double_ups),
        "double_up_rate": round(len(double_ups) / len(realizations), 4) if realizations else None,
        "short_stack_realization_pct": _avg([value for item in short_rows if (value := _stack_realization_pct(item)) is not None]),
        "mid_stack_realization_pct": _avg([value for item in mid_rows if (value := _stack_realization_pct(item)) is not None]),
        "deep_stack_realization_pct": _avg([value for item in deep_rows if (value := _stack_realization_pct(item)) is not None]),
    }


def _three_bet_line_summary(rows: list[HandObservation]) -> dict[str, Any]:
    three_bet_rows = [item for item in rows if item.preflop_entry_type in {"three_bet", "three_bet_jam"}]
    two_x_open_rows = [
        item
        for item in three_bet_rows
        if item.open_size_bb is not None and 1.8 <= item.open_size_bb <= 2.3
    ]
    six_x_3bet_rows = [
        item
        for item in two_x_open_rows
        if item.hero_3bet_size_bb is not None and 5.5 <= item.hero_3bet_size_bb <= 6.8
    ]
    faced_4bet_rows = [item for item in three_bet_rows if item.faced_4bet_after_3bet]
    folded_to_4bet_rows = [item for item in three_bet_rows if item.folded_to_4bet_after_3bet]
    return {
        "three_bet_count": len(three_bet_rows),
        "three_bet_vs_2x_open_count": len(two_x_open_rows),
        "three_bet_6x_vs_2x_open_count": len(six_x_3bet_rows),
        "faced_4bet_after_3bet_count": len(faced_4bet_rows),
        "folded_to_4bet_after_3bet_count": len(folded_to_4bet_rows),
        "fold_to_4bet_after_3bet_rate": round(len(folded_to_4bet_rows) / len(faced_4bet_rows), 4) if faced_4bet_rows else None,
        "avg_open_size_bb_when_3bet": _avg([item.open_size_bb for item in three_bet_rows if item.open_size_bb is not None]),
        "avg_3bet_size_bb": _avg([item.hero_3bet_size_bb for item in three_bet_rows if item.hero_3bet_size_bb is not None]),
        "avg_3bet_to_open_ratio": _avg([
            item.hero_3bet_to_open_ratio for item in three_bet_rows if item.hero_3bet_to_open_ratio is not None
        ]),
    }


def _is_played_pot(item: HandObservation) -> bool:
    # Forced antes/blinds and BB free-check paths are not voluntary hand-class decisions.
    return item.first_preflop_action in {"call", "raise", "jam"}


def _active_rows(rows: list[HandObservation]) -> list[HandObservation]:
    return [item for item in rows if _is_played_pot(item)]


def _count_attr(rows: list[HandObservation], attr: str) -> dict[str, int]:
    counter: dict[str, int] = defaultdict(int)
    for item in rows:
        counter[str(getattr(item, attr))] += 1
    return dict(sorted(counter.items()))


def _action_depth_summary(rows: list[HandObservation]) -> dict[str, Any]:
    return {
        "entry_type_mix": _count_attr(rows, "preflop_entry_type"),
        "open_count": sum(1 for item in rows if item.preflop_entry_type in {"open_raise", "open_raise_jam", "open_limp_or_complete"}),
        "open_limp_count": sum(1 for item in rows if item.preflop_entry_type == "open_limp_or_complete"),
        "open_raise_count": sum(1 for item in rows if item.preflop_entry_type in {"open_raise", "open_raise_jam"}),
        "limp_behind_count": sum(1 for item in rows if item.preflop_entry_type == "limp_behind"),
        "call_vs_open_count": sum(1 for item in rows if item.preflop_entry_type == "call_vs_open"),
        "three_bet_count": sum(1 for item in rows if item.preflop_entry_type in {"three_bet", "three_bet_jam"}),
        "four_bet_plus_count": sum(
            1
            for item in rows
            if item.preflop_entry_type in {"four_bet", "four_bet_jam", "five_bet_plus", "five_bet_plus_jam"}
        ),
    }


def _fold_exposure_breakdown(rows: list[HandObservation]) -> list[dict[str, Any]]:
    fold_rows = [item for item in rows if item.first_preflop_action == "fold"]
    by_entry: dict[str, list[HandObservation]] = defaultdict(list)
    for item in fold_rows:
        by_entry[item.preflop_entry_type].append(item)
    return [
        {
            "entry_type": entry_type,
            "count": len(items),
            "positions": _count_attr(items, "position"),
            "formats": _count_attr(items, "format_tag"),
            "faced_all_in_count": sum(1 for item in items if item.faced_all_in_preflop),
            "examples": [
                {
                    "hand_id": item.hand_id,
                    "started_at": item.started_at,
                    "position": item.position,
                    "format_tag": item.format_tag,
                    "stack_bb": round(item.stack_bb, 2) if item.stack_bb is not None else None,
                    "faced_all_in_preflop": item.faced_all_in_preflop,
                    "hero_summary": item.hero_summary,
                }
                for item in sorted(items, key=lambda row: (row.started_at or "", row.hand_id), reverse=True)[:4]
            ],
        }
        for entry_type, items in sorted(by_entry.items(), key=lambda item: (-len(item[1]), item[0]))
    ]


def _action_depth_breakdown(rows: list[HandObservation]) -> list[dict[str, Any]]:
    by_entry: dict[str, list[HandObservation]] = defaultdict(list)
    for item in rows:
        by_entry[item.preflop_entry_type].append(item)
    return [
        {
            "entry_type": entry_type,
            "played_count": len(items),
            "actual_bb_net": round(sum(item.bb_net for item in items), 2),
            "avg_bb_per_hand": round(sum(item.bb_net for item in items) / len(items), 2),
            **_stack_metrics(items),
            "positions": _count_attr(items, "position"),
            "formats": _count_attr(items, "format_tag"),
            "three_bet_line_summary": _three_bet_line_summary(items),
            "examples": [
                {
                    "hand_id": item.hand_id,
                    "started_at": item.started_at,
                    "position": item.position,
                    "format_tag": item.format_tag,
                    "stack_bb": round(item.stack_bb, 2) if item.stack_bb is not None else None,
                    "bb_net": round(item.bb_net, 2),
                    "open_size_bb": item.open_size_bb,
                    "hero_3bet_size_bb": item.hero_3bet_size_bb,
                    "hero_3bet_to_open_ratio": item.hero_3bet_to_open_ratio,
                    "faced_4bet_after_3bet": item.faced_4bet_after_3bet,
                    "folded_to_4bet_after_3bet": item.folded_to_4bet_after_3bet,
                    "hero_summary": item.hero_summary,
                }
                for item in sorted(items, key=lambda row: (row.started_at or "", row.hand_id), reverse=True)[:4]
            ],
        }
        for entry_type, items in sorted(by_entry.items(), key=lambda item: (-len(item[1]), item[0]))
    ]


def _cell_action_lines(rows: list[HandObservation], limit: int = 5) -> list[str]:
    lines: list[str] = []
    for item in _action_depth_breakdown(rows)[:limit]:
        stack_pct = item.get("avg_stack_realization_pct")
        stack_text = "n/a" if stack_pct is None else f"{stack_pct}% stack"
        lines.append(
            f"{item['entry_type']}: {item['played_count']}x, {item['avg_bb_per_hand']}bb/hand, {stack_text}"
        )
    return lines


def _cell_action_breakdown(rows: list[HandObservation], limit: int = 5) -> list[dict[str, Any]]:
    return [
        {
            "entry_type": item["entry_type"],
            "played_count": item["played_count"],
            "avg_bb_per_hand": item["avg_bb_per_hand"],
            "avg_stack_realization_pct": item.get("avg_stack_realization_pct"),
            "three_bet_line_summary": item.get("three_bet_line_summary"),
        }
        for item in _action_depth_breakdown(rows)[:limit]
    ]


def _build_mandatory_correction_cards(scored_hands: list[dict[str, Any]], limit: int = 10) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for hand in scored_hands:
        hand_class = hand["hand_class"]
        rows = hand.get("rows") or []
        for entry in _action_depth_breakdown(rows):
            count = entry["played_count"]
            stack_pct = entry.get("avg_stack_realization_pct")
            avg_bb = entry.get("avg_bb_per_hand")
            if count < 2 or stack_pct is None or avg_bb is None:
                continue
            if stack_pct > -15 and avg_bb > -5:
                continue
            severity_score = abs(min(stack_pct, 0)) * min(count, 12)
            candidates.append(
                {
                    "hand_class": hand_class,
                    "entry_type": entry["entry_type"],
                    "played_count": count,
                    "avg_bb_per_hand": avg_bb,
                    "avg_stack_realization_pct": stack_pct,
                    "full_stack_loss_count": entry.get("full_stack_loss_count"),
                    "positions": entry.get("positions"),
                    "formats": entry.get("formats"),
                    "severity_score": round(severity_score, 2),
                    "title": f"{hand_class} · {entry['entry_type']}",
                    "read": _correction_read(hand_class, entry["entry_type"], count, avg_bb, stack_pct),
                    "recommended_correction": _correction_recommendation(hand_class, entry["entry_type"]),
                    "examples": entry.get("examples", [])[:3],
                }
            )
    return sorted(candidates, key=lambda item: item["severity_score"], reverse=True)[:limit]


def _build_hidden_value_cards(scored_hands: list[dict[str, Any]], limit: int = 8) -> list[dict[str, Any]]:
    premium_hands = {"AA", "KK", "QQ", "AKs", "AKo", "AQs", "AQo"}
    candidates: list[dict[str, Any]] = []
    for hand in scored_hands:
        hand_class = hand["hand_class"]
        if hand_class in premium_hands:
            continue
        rows = hand.get("rows") or []
        for entry in _action_depth_breakdown(rows):
            count = entry["played_count"]
            stack_pct = entry.get("avg_stack_realization_pct")
            avg_bb = entry.get("avg_bb_per_hand")
            if count < 5 or stack_pct is None or avg_bb is None:
                continue
            if stack_pct < 8 and avg_bb < 2:
                continue
            full_stack_losses = entry.get("full_stack_loss_count") or 0
            value_score = (max(stack_pct, 0) * min(count, 25)) + (max(avg_bb, 0) * 8) - (full_stack_losses * 18)
            if value_score <= 0:
                continue
            candidates.append(
                {
                    "hand_class": hand_class,
                    "entry_type": entry["entry_type"],
                    "played_count": count,
                    "avg_bb_per_hand": avg_bb,
                    "avg_stack_realization_pct": stack_pct,
                    "full_stack_loss_count": full_stack_losses,
                    "positions": entry.get("positions"),
                    "formats": entry.get("formats"),
                    "value_score": round(value_score, 2),
                    "title": f"{hand_class} · {entry['entry_type']}",
                    "read": _hidden_value_read(hand_class, entry["entry_type"], count, avg_bb, stack_pct),
                    "recommended_keep": _hidden_value_recommendation(hand_class, entry["entry_type"]),
                    "examples": entry.get("examples", [])[:3],
                }
            )
    return sorted(candidates, key=lambda item: item["value_score"], reverse=True)[:limit]


def _correction_read(hand_class: str, entry_type: str, count: int, avg_bb: float, stack_pct: float) -> str:
    return (
        f"{hand_class} has {count} repeated {entry_type} spots with {avg_bb}bb/hand and {stack_pct}% stack realization. "
        "This is a stronger correction candidate than a raw matrix color alone."
    )


def _correction_recommendation(hand_class: str, entry_type: str) -> str:
    if "three_bet" in entry_type or "four_bet" in entry_type or "five_bet" in entry_type:
        return f"Stop promoting {hand_class} into {entry_type} without a clear stack/position/format reason."
    if "iso_raise" in entry_type:
        return f"Do not iso-pressure {hand_class} by default; require fold equity and a clean stack plan."
    if "open_raise_jam" in entry_type:
        return f"Move {hand_class} open-jam spots into review before treating them as default AOF pressure."
    if "call_vs" in entry_type:
        return f"Review {hand_class} calls versus prior aggression; calling may be the leak node, not the hand itself."
    return f"Review {hand_class} in {entry_type} before approving it as a baseline action."


def _hidden_value_read(hand_class: str, entry_type: str, count: int, avg_bb: float, stack_pct: float) -> str:
    return (
        f"{hand_class} has {count} repeated {entry_type} spots with {avg_bb}bb/hand and {stack_pct}% stack realization. "
        "This is not a correction target by default; it is a keep-or-study pattern that may explain where Hero is realizing value."
    )


def _hidden_value_recommendation(hand_class: str, entry_type: str) -> str:
    if "jam" in entry_type:
        return f"Keep {hand_class} {entry_type} available, but verify the stack/position gate before promoting it into an AOF default."
    if "three_bet" in entry_type or "four_bet" in entry_type:
        return f"Study why {hand_class} works in {entry_type}; preserve the exact contexts instead of blindly expanding the range."
    if "call_vs" in entry_type:
        return f"Keep reviewing {hand_class} calls versus opens; the result is positive enough to avoid over-correcting into pure folding."
    return f"Treat {hand_class} {entry_type} as a positive execution candidate and compare it against nearby hand classes."


def _build_study_panels(observations: list[HandObservation]) -> dict[str, list[dict[str, Any]]]:
    relevant = [
        item
        for item in observations
        if item.stack_bb is not None
        and item.stack_bb <= 15
        and item.position in {"UTG", "UTG+1", "UTG+2", "LJ", "HJ"}
        and item.first_preflop_action in {"jam", "raise", "call"}
    ]

    grouped: dict[str, list[HandObservation]] = defaultdict(list)
    for item in relevant:
        family_key = None
        if item.hand_class == "KJo":
            family_key = "kjo_pressure"
        elif item.hand_class == "KQo":
            family_key = "kqo_pressure"
        elif item.hand_class in {"A2o", "A3o", "A4o", "A5o", "A6o", "A7o"}:
            family_key = "low_ax_offsuit_pressure"
        elif item.hand_class in {"22", "33", "44"} and item.first_preflop_action == "jam":
            family_key = "small_pair_early_jam_watch"
        if family_key:
            grouped[family_key].append(item)
        if item.hand_class in {"22", "33", "44", "55", "66"} and item.first_preflop_action in {"jam", "raise", "call"}:
            grouped["small_pair_early_aggression"].append(item)
        if item.hand_class in {"KJo", "KQo", "QJo", "KTo", "QTo", "JTo"} and item.first_preflop_action in {"jam", "raise", "call"}:
            grouped["offsuit_broadway_pressure"].append(item)

    def make_examples(rows: list[HandObservation], limit: int = 4) -> list[dict[str, Any]]:
        return [
            {
                "hand_class": item.hand_class,
                "position": item.position,
                "format_tag": item.format_tag,
                "stack_bb": round(item.stack_bb, 2) if item.stack_bb is not None else None,
                "action": item.first_preflop_action,
                "faced_action_preflop": item.faced_action_preflop,
                "started_at": item.started_at,
                "hand_id": item.hand_id,
                "hero_summary": item.hero_summary,
            }
            for item in sorted(rows, key=lambda row: (row.started_at or "", row.hand_id), reverse=True)[:limit]
        ]

    def count_by(rows: list[HandObservation], attr: str) -> dict[str, int]:
        counter = defaultdict(int)
        for item in rows:
            counter[str(getattr(item, attr))] += 1
        return dict(sorted(counter.items()))

    panels = {
        "study_worthy_spots": [],
        "clear_repeated_mistakes": [],
        "belief_driven_patterns": [],
    }

    kjo_rows = grouped.get("kjo_pressure", [])
    if len(kjo_rows) >= 3:
        panels["study_worthy_spots"].append(
            {
                "title": "KJo under-15bb pressure approval",
                "family": "KJo",
                "classification": "threshold_study",
                "repeated_count": len(kjo_rows),
                "why_it_matters": "KJo keeps appearing as an early or mid-position pressure hand under 15bb, so the jam/open threshold needs to be locked down instead of left to feel.",
                "positions": count_by(kjo_rows, "position"),
                "formats": count_by(kjo_rows, "format_tag"),
                "actions": count_by(kjo_rows, "first_preflop_action"),
                "examples": make_examples(kjo_rows),
            }
        )

    kqo_rows = grouped.get("kqo_pressure", [])
    if len(kqo_rows) >= 3:
        panels["study_worthy_spots"].append(
            {
                "title": "KQo under-15bb pressure approval",
                "family": "KQo",
                "classification": "threshold_study",
                "repeated_count": len(kqo_rows),
                "why_it_matters": "KQo appears repeatedly as an under-15bb proactive hand in early and mid lanes, which makes it a clean boundary-study candidate rather than a one-off result story.",
                "positions": count_by(kqo_rows, "position"),
                "formats": count_by(kqo_rows, "format_tag"),
                "actions": count_by(kqo_rows, "first_preflop_action"),
                "examples": make_examples(kqo_rows),
            }
        )

    low_ax_rows = grouped.get("low_ax_offsuit_pressure", [])
    if len(low_ax_rows) >= 4:
        panels["belief_driven_patterns"].append(
            {
                "title": "Low Ax offsuit under-15bb pressure family",
                "family": "A2o-A7o",
                "classification": "belief_driven",
                "repeated_count": len(low_ax_rows),
                "why_it_matters": "Low offsuit aces keep getting proactive approval in early and mid-position short-stack lanes, which looks more like a recurring blocker-pressure belief than random distribution.",
                "positions": count_by(low_ax_rows, "position"),
                "formats": count_by(low_ax_rows, "format_tag"),
                "actions": count_by(low_ax_rows, "first_preflop_action"),
                "examples": make_examples(low_ax_rows),
            }
        )

    small_pair_rows = [
        item for item in grouped.get("small_pair_early_aggression", [])
        if item.position in {"UTG", "UTG+1", "UTG+2", "LJ"}
    ]
    if len(small_pair_rows) >= 4:
        panels["clear_repeated_mistakes"].append(
            {
                "title": "Small pair early under-15bb aggression",
                "family": "22-66",
                "classification": "red_flag_family",
                "repeated_count": len(small_pair_rows),
                "why_it_matters": "Small and mid-small pairs keep getting proactively approved in early short-stack lanes. Even when individual combos differ, the repeated family suggests the threshold may be drifting too loose.",
                "positions": count_by(small_pair_rows, "position"),
                "formats": count_by(small_pair_rows, "format_tag"),
                "actions": count_by(small_pair_rows, "first_preflop_action"),
                "examples": make_examples(small_pair_rows),
            }
        )

    offsuit_broadway_rows = [
        item for item in grouped.get("offsuit_broadway_pressure", [])
        if item.position in {"UTG", "UTG+1", "UTG+2", "LJ", "HJ"}
    ]
    if len(offsuit_broadway_rows) >= 6:
        panels["clear_repeated_mistakes"].append(
            {
                "title": "Offsuit broadway short-stack pressure drift",
                "family": "KJo-KQo-QJo-KTo-QTo-JTo",
                "classification": "red_flag_family",
                "repeated_count": len(offsuit_broadway_rows),
                "why_it_matters": "Offsuit broadways are repeatedly getting proactive approval under 15bb in early and middle lanes. This is broad enough to look like a real family-level drift, not one hot hand class.",
                "positions": count_by(offsuit_broadway_rows, "position"),
                "formats": count_by(offsuit_broadway_rows, "format_tag"),
                "actions": count_by(offsuit_broadway_rows, "first_preflop_action"),
                "examples": make_examples(offsuit_broadway_rows),
            }
        )

    if len(low_ax_rows) >= 8:
        panels["clear_repeated_mistakes"].append(
            {
                "title": "Low Ax offsuit early pressure overuse",
                "family": "A2o-A7o",
                "classification": "red_flag_family",
                "repeated_count": len(low_ax_rows),
                "why_it_matters": "Low Ax offsuit pressure is not only a belief pattern anymore; the family is repeated enough that it should also appear in the red-flag queue for direct study and correction.",
                "positions": count_by(low_ax_rows, "position"),
                "formats": count_by(low_ax_rows, "format_tag"),
                "actions": count_by(low_ax_rows, "first_preflop_action"),
                "examples": make_examples(low_ax_rows),
            }
        )

    pair_rows = grouped.get("small_pair_early_jam_watch", [])
    if len(pair_rows) >= 3:
        panels["clear_repeated_mistakes"].append(
            {
                "title": "Small pair early jam watch",
                "family": "22-44",
                "classification": "repeated_mistake_watch",
                "repeated_count": len(pair_rows),
                "why_it_matters": "Small-pair early jams under 15bb are the kind of obvious approval mistake that should stand out when repetition becomes real enough.",
                "positions": count_by(pair_rows, "position"),
                "formats": count_by(pair_rows, "format_tag"),
                "actions": count_by(pair_rows, "first_preflop_action"),
                "examples": make_examples(pair_rows),
            }
        )

    return panels


def _fetch_observations(
    player_id: str,
    window: str,
    format_filter: str,
    position_filter: str,
    stack_filter: str,
    min_active_seats: int,
) -> list[HandObservation]:
    cutoff = None
    if window == "90d":
        cutoff = datetime.now(UTC) - timedelta(days=90)

    rows: list[HandObservation] = []
    with get_sqlite_connection() as conn:
        query_rows = conn.execute(
            """
            SELECT
                hands.id,
                hands.session_id,
                hands.effective_stack_bb,
                hands.result_summary,
                hands.raw_payload,
                sessions.player_id,
                sessions.started_at,
                sessions.session_metadata
            FROM hands
            JOIN sessions ON sessions.id = hands.session_id
            WHERE sessions.player_id = ?
            ORDER BY sessions.started_at DESC, hands.id DESC
            """,
            (player_id,),
        ).fetchall()

    for row in query_rows:
        started_at = _parse_started_at(row["started_at"])
        if cutoff and started_at and started_at < cutoff:
            continue

        raw_payload = _parse_json(row["raw_payload"], {})
        session_metadata = _parse_json(row["session_metadata"], {})
        result_summary = _parse_json(row["result_summary"], {})
        block = raw_payload.get("block") or []
        header = raw_payload.get("header") or ""
        big_blind = _extract_big_blind(header)
        hand_class = _extract_hand_class(block)
        position = _extract_hero_position(block)
        active_seats = _extract_active_seats(block)
        stack_bb = row["effective_stack_bb"]

        if not big_blind or not hand_class or not position or active_seats < min_active_seats:
            continue

        format_tag = _extract_format_tag(header, session_metadata)
        if format_filter != "all" and format_tag != format_filter:
            continue
        if position_filter != "all" and position != position_filter:
            continue
        if stack_filter == "lt15" and not (stack_bb is not None and stack_bb < 15):
            continue
        if stack_filter == "15to25" and not (stack_bb is not None and 15 <= stack_bb <= 25):
            continue
        if stack_filter == "gt25" and not (stack_bb is not None and stack_bb > 25):
            continue

        (
            first_preflop_action,
            faced_action_preflop,
            preflop_entry_type,
            prior_raise_count,
            faced_all_in_preflop,
        ) = _extract_preflop_pattern(block)
        three_bet_features = _extract_3bet_line_features(block, big_blind)

        rows.append(
            HandObservation(
                hand_id=row["id"],
                session_id=row["session_id"],
                tournament_id=str(session_metadata.get("tournament_id") or "unknown_tournament"),
                started_at=row["started_at"],
                format_tag=format_tag,
                hand_class=hand_class,
                position=position,
                active_seats=active_seats,
                stack_bb=stack_bb,
                bb_net=_compute_bb_net(block, big_blind),
                hero_summary=result_summary.get("hero_summary") or "",
                first_preflop_action=first_preflop_action,
                faced_action_preflop=faced_action_preflop,
                preflop_entry_type=preflop_entry_type,
                prior_raise_count=prior_raise_count,
                faced_all_in_preflop=faced_all_in_preflop,
                open_size_bb=three_bet_features["open_size_bb"],
                hero_3bet_size_bb=three_bet_features["hero_3bet_size_bb"],
                hero_3bet_to_open_ratio=three_bet_features["hero_3bet_to_open_ratio"],
                faced_4bet_after_3bet=three_bet_features["faced_4bet_after_3bet"],
                folded_to_4bet_after_3bet=three_bet_features["folded_to_4bet_after_3bet"],
            )
        )
    return rows


def build_hand_scores(observations: list[HandObservation]) -> list[dict[str, Any]]:
    by_hand: dict[str, list[HandObservation]] = defaultdict(list)
    for observation in observations:
        by_hand[observation.hand_class].append(observation)

    scored_hands: list[dict[str, Any]] = []
    for hand_class, hand_rows in by_hand.items():
        active_hand_rows = _active_rows(hand_rows)
        if not active_hand_rows:
            total = 0.0
            avg = None
        else:
            total = round(sum(item.bb_net for item in active_hand_rows), 2)
            avg = round(total / len(active_hand_rows), 2)
        stack_metrics = _stack_metrics(active_hand_rows)
        positions = sorted({item.position for item in active_hand_rows}, key=_position_sort_key)
        format_mix = defaultdict(int)
        stack_bands = {"lt15": 0, "15to25": 0, "gt25": 0, "unknown": 0}
        action_mix = defaultdict(int)
        proactive_count = 0
        faced_count = 0
        unopened_count = 0
        for item in active_hand_rows:
            format_mix[item.format_tag] += 1
            action_key = item.first_preflop_action or "unknown"
            action_mix[action_key] += 1
            if action_key in {"raise", "jam", "call"}:
                proactive_count += 1
            if item.faced_action_preflop:
                faced_count += 1
            else:
                unopened_count += 1
            if item.stack_bb is None:
                stack_bands["unknown"] += 1
            elif item.stack_bb < 15:
                stack_bands["lt15"] += 1
            elif item.stack_bb <= 25:
                stack_bands["15to25"] += 1
            else:
                stack_bands["gt25"] += 1

        scored_hands.append(
            {
                "hand_class": hand_class,
                "dealt_count": len(hand_rows),
                "played_count": len(active_hand_rows),
                "hands_played": len(active_hand_rows),
                "actual_bb_net": total,
                "avg_bb_per_hand": avg,
                **stack_metrics,
                **_action_depth_summary(active_hand_rows),
                "sample_band": _sample_band(len(active_hand_rows)),
                "positions_observed": positions,
                "format_mix": dict(sorted(format_mix.items())),
                "stack_band_mix": stack_bands,
                "action_mix": dict(sorted(action_mix.items())),
                "proactive_rate": round(proactive_count / len(active_hand_rows), 4) if active_hand_rows else None,
                "faced_action_rate": round(faced_count / len(active_hand_rows), 4) if active_hand_rows else None,
                "unopened_rate": round(unopened_count / len(active_hand_rows), 4) if active_hand_rows else None,
                "rows": active_hand_rows,
            }
        )
    return scored_hands


def get_hand_matrix_payload(
    player_id: str = HERO_PLAYER_ID,
    window: str = "90d",
    format_filter: str = "all",
    position_filter: str = "all",
    stack_filter: str = "all",
    min_active_seats: int = 5,
    selected_hand: str | None = None,
) -> dict[str, Any]:
    resolved_player_id = player_id or HERO_PLAYER_ID
    resolved_window = window if window in SUPPORTED_WINDOWS else "90d"
    resolved_stack_filter = stack_filter if stack_filter in SUPPORTED_STACK_FILTERS else "all"
    observations = _fetch_observations(
        player_id=resolved_player_id,
        window=resolved_window,
        format_filter=format_filter,
        position_filter=position_filter,
        stack_filter=resolved_stack_filter,
        min_active_seats=min_active_seats,
    )

    by_format: dict[str, int] = defaultdict(int)
    by_position: dict[str, int] = defaultdict(int)

    for observation in observations:
        by_format[observation.format_tag] += 1
        by_position[observation.position] += 1

    dealt_by_hand: dict[str, list[HandObservation]] = defaultdict(list)
    for observation in observations:
        dealt_by_hand[observation.hand_class].append(observation)
    scored_hands = build_hand_scores(observations)
    played_by_hand = {item["hand_class"]: item["rows"] for item in scored_hands}

    matrix_cells: dict[str, dict[str, Any]] = {}
    for hand_class in _matrix_order():
        hand_rows = dealt_by_hand.get(hand_class, [])
        dealt_count = len(hand_rows)
        played_rows = played_by_hand.get(hand_class, [])
        hands_played = len(played_rows)
        actual_bb_net = round(sum(item.bb_net for item in played_rows), 2)
        avg_bb_per_hand = round(actual_bb_net / hands_played, 2) if hands_played else None
        stack_metrics = _stack_metrics(played_rows)
        stack_realization = stack_metrics["avg_stack_realization_pct"]
        matrix_cells[hand_class] = {
            "hand_class": hand_class,
            "dealt_count": dealt_count,
            "non_played_count": max(dealt_count - hands_played, 0),
            "parsed_preflop_fold_count": sum(1 for item in hand_rows if item.first_preflop_action == "fold"),
            "played_count": hands_played,
            "hands_played": hands_played,
            "actual_bb_net": actual_bb_net,
            "avg_bb_per_hand": avg_bb_per_hand,
            **stack_metrics,
            **_action_depth_summary(played_rows),
            "hover_action_lines": _cell_action_lines(played_rows),
            "hover_action_breakdown": _cell_action_breakdown(played_rows),
            "fold_exposure_breakdown": _fold_exposure_breakdown(hand_rows),
            "sample_band": _sample_band(hands_played) if hands_played else "none",
            "style_tone": _cell_style(avg_bb_per_hand or 0.0) if hands_played else "empty",
            "stack_style_tone": _pct_style(stack_realization or 0.0) if hands_played else "empty",
        }

    suspicious_hands = sorted(
        [item for item in scored_hands if item["hands_played"] >= 8 and item["avg_bb_per_hand"] <= -0.4],
        key=lambda item: (item["avg_bb_per_hand"], -item["hands_played"]),
    )[:8]
    standout_hands = sorted(
        [item for item in scored_hands if item["hands_played"] >= 8 and item["avg_bb_per_hand"] >= 0.4],
        key=lambda item: (-item["avg_bb_per_hand"], -item["hands_played"]),
    )[:8]
    stack_realization_leaks = sorted(
        [
            item
            for item in scored_hands
            if item["hands_played"] >= 8 and item.get("avg_stack_realization_pct") is not None and item["avg_stack_realization_pct"] <= -5
        ],
        key=lambda item: (item["avg_stack_realization_pct"], -item["hands_played"]),
    )[:8]
    raw_vs_stack_mismatches = sorted(
        [
            item
            for item in scored_hands
            if item["hands_played"] >= 8
            and item.get("avg_stack_realization_pct") is not None
            and (
                (item["avg_bb_per_hand"] >= 0.25 and item["avg_stack_realization_pct"] <= -3)
                or (item["avg_bb_per_hand"] <= -0.4 and item["avg_stack_realization_pct"] >= 3)
            )
        ],
        key=lambda item: abs(item["avg_stack_realization_pct"]),
        reverse=True,
    )[:8]
    suspicious_hands = [_without_rows(item) for item in suspicious_hands]
    standout_hands = [_without_rows(item) for item in standout_hands]
    stack_realization_leaks = [_without_rows(item) for item in stack_realization_leaks]
    raw_vs_stack_mismatches = [_without_rows(item) for item in raw_vs_stack_mismatches]

    resolved_selected_hand = selected_hand if selected_hand in dealt_by_hand else None
    if not resolved_selected_hand:
        resolved_selected_hand = DEFAULT_SELECTED_HAND if DEFAULT_SELECTED_HAND in dealt_by_hand else next(iter(dealt_by_hand), None)

    detail = None
    if resolved_selected_hand:
        dealt_detail_rows = dealt_by_hand[resolved_selected_hand]
        detail_rows = played_by_hand.get(resolved_selected_hand, [])
        by_position_detail: dict[str, list[HandObservation]] = defaultdict(list)
        for item in detail_rows:
            by_position_detail[item.position].append(item)

        detail = {
            "hand_class": resolved_selected_hand,
            "summary": {
                "dealt_count": len(dealt_detail_rows),
                "non_played_count": max(len(dealt_detail_rows) - len(detail_rows), 0),
                "parsed_preflop_fold_count": sum(1 for item in dealt_detail_rows if item.first_preflop_action == "fold"),
                "hands_played": len(detail_rows),
                "played_count": len(detail_rows),
                "actual_bb_net": round(sum(item.bb_net for item in detail_rows), 2),
                "avg_bb_per_hand": round(sum(item.bb_net for item in detail_rows) / len(detail_rows), 2) if detail_rows else None,
                **_stack_metrics(detail_rows),
                **_action_depth_summary(detail_rows),
                **_three_bet_line_summary(detail_rows),
                "sample_band": _sample_band(len(detail_rows)),
                "formats": dict(sorted((fmt, count) for fmt, count in defaultdict(int, {
                    item.format_tag: sum(1 for row in detail_rows if row.format_tag == item.format_tag)
                    for item in detail_rows
                }).items())),
            },
            "position_breakdown": [
                {
                    "position": position,
                    "hands_played": len(items),
                    "played_count": len(items),
                    "actual_bb_net": round(sum(item.bb_net for item in items), 2),
                    "avg_bb_per_hand": round(sum(item.bb_net for item in items) / len(items), 2),
                    **_stack_metrics(items),
                    "sample_band": _sample_band(len(items)),
                }
                for position, items in sorted(by_position_detail.items(), key=lambda pair: _position_sort_key(pair[0]))
            ],
            "action_depth_breakdown": _action_depth_breakdown(detail_rows),
            "fold_exposure_breakdown": _fold_exposure_breakdown(dealt_detail_rows),
            "recent_examples": [
                {
                    "hand_id": item.hand_id,
                    "started_at": item.started_at,
                    "position": item.position,
                    "format_tag": item.format_tag,
                    "stack_bb": round(item.stack_bb, 2) if item.stack_bb is not None else None,
                    "bb_net": round(item.bb_net, 2),
                    "hero_summary": item.hero_summary,
                }
                for item in sorted(
                    detail_rows,
                    key=lambda row: (row.started_at or "", row.hand_id),
                    reverse=True,
                )[:12]
            ],
        }

    study_panels = _build_study_panels(observations)

    return {
        "status": "ok",
        "player_id": resolved_player_id,
        "counting_policy": {
            "dealt_count": "times Hero was dealt this hand class",
            "played_count": "times Hero voluntarily entered the pot or took a non-fold action",
            "default_metric_count": "played_count",
            "truth_policy": "Hero Baseline performance metrics are based on played pots; dealt folds remain available only as exposure context.",
        },
        "filters": {
            "window": resolved_window,
            "format_filter": format_filter,
            "position_filter": position_filter,
            "stack_filter": resolved_stack_filter,
            "min_active_seats": min_active_seats,
        },
        "summary": {
            "total_observations": len(observations),
            "distinct_hand_classes": len(dealt_by_hand),
            "positions_seen": sorted(by_position.keys(), key=_position_sort_key),
            "format_mix": dict(sorted(by_format.items())),
            "window_label": "Recent 90 days" if resolved_window == "90d" else "All available history",
        },
        "matrix_order": _matrix_order(),
        "matrix_cells": matrix_cells,
        "suspicious_hands": suspicious_hands,
        "standout_hands": standout_hands,
        "stack_realization_leaks": stack_realization_leaks,
        "raw_vs_stack_mismatches": raw_vs_stack_mismatches,
        "mandatory_correction_cards": _build_mandatory_correction_cards(scored_hands),
        "hidden_value_cards": _build_hidden_value_cards(scored_hands),
        "baseline_insight_cards": _build_baseline_insight_cards(
            selected_hand=resolved_selected_hand,
            detail=detail,
            stack_realization_leaks=stack_realization_leaks,
            raw_vs_stack_mismatches=raw_vs_stack_mismatches,
        ),
        "study_panels": study_panels,
        "selected_hand": resolved_selected_hand,
        "detail": detail,
    }


def _without_rows(item: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in item.items() if key != "rows"}


def _build_baseline_insight_cards(
    *,
    selected_hand: str | None,
    detail: dict[str, Any] | None,
    stack_realization_leaks: list[dict[str, Any]],
    raw_vs_stack_mismatches: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    if detail:
        summary = detail["summary"]
        hand = selected_hand or detail["hand_class"]
        cards.append(
            {
                "title": f"{hand} raw BB vs stack realization",
                "metric": f"{summary.get('avg_bb_per_hand')}bb/hand · {summary.get('avg_stack_realization_pct')}% stack",
                "why_it_matters": "Raw BB shows chip result, while stack realization shows how much of Hero's starting stack was gained or lost.",
                "read": _selected_hand_read(hand, summary),
                "next_review": "Split this hand by position, stack band, and first preflop action before deciding whether it is a real execution leak.",
            }
        )
    if stack_realization_leaks:
        top = stack_realization_leaks[0]
        cards.append(
            {
                "title": f"{top['hand_class']} is the top stack-normalized leak",
                "metric": f"{top['avg_stack_realization_pct']}% stack · {top['avg_bb_per_hand']}bb/hand",
                "why_it_matters": "This hand may not only be losing chips; it is losing a meaningful share of the stack when it appears.",
                "read": "Prioritize this over raw-BB-only leaks when the goal is finding hands whose GTO realization may be failing in real tournament stack geometry.",
                "next_review": "Review the biggest stack-loss examples and separate bad implementation from unavoidable all-in/cooler outcomes.",
            }
        )
    if raw_vs_stack_mismatches:
        top = raw_vs_stack_mismatches[0]
        cards.append(
            {
                "title": f"{top['hand_class']} disagrees between raw BB and stack %",
                "metric": f"{top['avg_bb_per_hand']}bb/hand · {top['avg_stack_realization_pct']}% stack",
                "why_it_matters": "Raw BB and stack-normalized result are telling different stories, so a simple heatmap could mislead the review.",
                "read": "This is exactly why Hero Baseline should compare both views before judging a hand class.",
                "next_review": "Check whether deep-stack pots or short-stack all-ins are dominating the average.",
            }
        )
    return cards


def _selected_hand_read(hand: str, summary: dict[str, Any]) -> str:
    raw = summary.get("avg_bb_per_hand")
    stack = summary.get("avg_stack_realization_pct")
    if raw is None or stack is None:
        return f"{hand} needs more complete stack data before normalized interpretation."
    if raw < -0.4 and stack < -5:
        return f"{hand} is negative in both raw BB and stack-normalized terms, making it a real review candidate."
    if raw < -0.4 and stack >= -3:
        return f"{hand} is raw-BB negative, but stack-normalized damage is less severe; a few bigger pots may be distorting the matrix."
    if raw >= 0.25 and stack < -3:
        return f"{hand} wins raw BB but loses stack share, so the wins may come from deep stacks while short-stack implementation leaks."
    if raw >= 0.25 and stack >= 3:
        return f"{hand} is positive in both views and may be a stable execution baseline."
    return f"{hand} is close enough to neutral that position/action splits matter more than the headline number."


def main() -> None:
    parser = argparse.ArgumentParser(description="Read the 13x13 hand matrix payload.")
    parser.add_argument("--player-id", default=HERO_PLAYER_ID, help="Player id to inspect.")
    parser.add_argument("--window", default="90d", choices=sorted(SUPPORTED_WINDOWS))
    parser.add_argument("--format-filter", default="all")
    parser.add_argument("--position-filter", default="all")
    parser.add_argument("--stack-filter", default="all", choices=sorted(SUPPORTED_STACK_FILTERS))
    parser.add_argument("--min-active-seats", type=int, default=5)
    parser.add_argument("--selected-hand", default=None)
    args = parser.parse_args()
    payload = get_hand_matrix_payload(
        player_id=args.player_id,
        window=args.window,
        format_filter=args.format_filter,
        position_filter=args.position_filter,
        stack_filter=args.stack_filter,
        min_active_seats=args.min_active_seats,
        selected_hand=args.selected_hand,
    )
    print(json.dumps(payload, indent=2, default=str))


if __name__ == "__main__":
    main()
