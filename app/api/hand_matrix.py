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


def _extract_preflop_pattern(block: list[str]) -> tuple[str | None, bool]:
    in_preflop = False
    faced_action = False
    for row in block:
        if row == "*** HOLE CARDS ***":
            in_preflop = True
            continue
        if not in_preflop:
            continue
        if row.startswith("*** FLOP ***") or row.startswith("*** SHOWDOWN ***") or row.startswith("*** SUMMARY ***"):
            break
        if row.startswith("Hero:"):
            if " folds" in row:
                return ("fold", faced_action)
            if " calls " in row:
                return ("call", faced_action)
            if " raises " in row:
                return ("jam" if "all-in" in row else "raise", faced_action)
            return ("other", faced_action)
        if ":" in row and any(token in row for token in (" raises ", " calls ", " bets ")):
            actor = row.split(":", 1)[0]
            if actor != "Hero":
                faced_action = True
    return (None, faced_action)


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

        first_preflop_action, faced_action_preflop = _extract_preflop_pattern(block)

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
            )
        )
    return rows


def build_hand_scores(observations: list[HandObservation]) -> list[dict[str, Any]]:
    by_hand: dict[str, list[HandObservation]] = defaultdict(list)
    for observation in observations:
        by_hand[observation.hand_class].append(observation)

    scored_hands: list[dict[str, Any]] = []
    for hand_class, hand_rows in by_hand.items():
        total = round(sum(item.bb_net for item in hand_rows), 2)
        avg = round(total / len(hand_rows), 2)
        positions = sorted({item.position for item in hand_rows}, key=_position_sort_key)
        format_mix = defaultdict(int)
        stack_bands = {"lt15": 0, "15to25": 0, "gt25": 0, "unknown": 0}
        action_mix = defaultdict(int)
        proactive_count = 0
        faced_count = 0
        unopened_count = 0
        for item in hand_rows:
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
                "hands_played": len(hand_rows),
                "actual_bb_net": total,
                "avg_bb_per_hand": avg,
                "sample_band": _sample_band(len(hand_rows)),
                "positions_observed": positions,
                "format_mix": dict(sorted(format_mix.items())),
                "stack_band_mix": stack_bands,
                "action_mix": dict(sorted(action_mix.items())),
                "proactive_rate": round(proactive_count / len(hand_rows), 4),
                "faced_action_rate": round(faced_count / len(hand_rows), 4),
                "unopened_rate": round(unopened_count / len(hand_rows), 4),
                "rows": hand_rows,
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

    scored_hands = build_hand_scores(observations)
    by_hand = {item["hand_class"]: item["rows"] for item in scored_hands}

    matrix_cells: dict[str, dict[str, Any]] = {}
    for hand_class in _matrix_order():
        hand_rows = by_hand.get(hand_class, [])
        hands_played = len(hand_rows)
        actual_bb_net = round(sum(item.bb_net for item in hand_rows), 2)
        avg_bb_per_hand = round(actual_bb_net / hands_played, 2) if hands_played else None
        matrix_cells[hand_class] = {
            "hand_class": hand_class,
            "hands_played": hands_played,
            "actual_bb_net": actual_bb_net,
            "avg_bb_per_hand": avg_bb_per_hand,
            "sample_band": _sample_band(hands_played) if hands_played else "none",
            "style_tone": _cell_style(avg_bb_per_hand or 0.0) if hands_played else "empty",
        }

    suspicious_hands = sorted(
        [item for item in scored_hands if item["hands_played"] >= 8 and item["avg_bb_per_hand"] <= -0.4],
        key=lambda item: (item["avg_bb_per_hand"], -item["hands_played"]),
    )[:8]
    standout_hands = sorted(
        [item for item in scored_hands if item["hands_played"] >= 8 and item["avg_bb_per_hand"] >= 0.4],
        key=lambda item: (-item["avg_bb_per_hand"], -item["hands_played"]),
    )[:8]

    resolved_selected_hand = selected_hand if selected_hand in by_hand else None
    if not resolved_selected_hand:
        resolved_selected_hand = DEFAULT_SELECTED_HAND if DEFAULT_SELECTED_HAND in by_hand else next(iter(by_hand), None)

    detail = None
    if resolved_selected_hand:
        detail_rows = by_hand[resolved_selected_hand]
        by_position_detail: dict[str, list[HandObservation]] = defaultdict(list)
        for item in detail_rows:
            by_position_detail[item.position].append(item)

        detail = {
            "hand_class": resolved_selected_hand,
            "summary": {
                "hands_played": len(detail_rows),
                "actual_bb_net": round(sum(item.bb_net for item in detail_rows), 2),
                "avg_bb_per_hand": round(sum(item.bb_net for item in detail_rows) / len(detail_rows), 2),
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
                    "actual_bb_net": round(sum(item.bb_net for item in items), 2),
                    "avg_bb_per_hand": round(sum(item.bb_net for item in items) / len(items), 2),
                    "sample_band": _sample_band(len(items)),
                }
                for position, items in sorted(by_position_detail.items(), key=lambda pair: _position_sort_key(pair[0]))
            ],
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
        "filters": {
            "window": resolved_window,
            "format_filter": format_filter,
            "position_filter": position_filter,
            "stack_filter": resolved_stack_filter,
            "min_active_seats": min_active_seats,
        },
        "summary": {
            "total_observations": len(observations),
            "distinct_hand_classes": len(by_hand),
            "positions_seen": sorted(by_position.keys(), key=_position_sort_key),
            "format_mix": dict(sorted(by_format.items())),
            "window_label": "Recent 90 days" if resolved_window == "90d" else "All available history",
        },
        "matrix_order": _matrix_order(),
        "matrix_cells": matrix_cells,
        "suspicious_hands": suspicious_hands,
        "standout_hands": standout_hands,
        "study_panels": study_panels,
        "selected_hand": resolved_selected_hand,
        "detail": detail,
    }


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
