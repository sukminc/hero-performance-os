from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from app.api.conviction_review import get_conviction_review_payload
from app.api.field_ecology import get_field_ecology_payload
from app.api.hand_matrix import HERO_PLAYER_ID, _fetch_observations
from app.api.hud_trend import get_hud_trend_payload


SUPPORTED_WINDOWS = {"90d", "all"}


@dataclass
class TimingObservation:
    tournament_id: str
    session_id: str
    started_at: str | None
    format_tag: str
    hand_class: str
    position: str
    stack_bb: float | None
    bb_net: float
    first_preflop_action: str | None
    faced_action_preflop: bool
    entry_timing: str
    bullet_state: str


def _stack_band(stack_bb: float | None) -> str:
    if stack_bb is None:
        return "unknown"
    if stack_bb < 15:
        return "0-15bb"
    if stack_bb < 20:
        return "15-20bb"
    if stack_bb < 25:
        return "20-25bb"
    if stack_bb < 30:
        return "25-30bb"
    if stack_bb < 50:
        return "30-50bb"
    if stack_bb < 100:
        return "50-100bb"
    return "100bb+"


def _aof_family(hand_class: str, position: str, stack_bb: float | None, action: str | None) -> str | None:
    if stack_bb is None or stack_bb > 15 or action not in {"jam", "raise", "call"}:
        return None
    if hand_class in {"KJo", "KQo"} and position in {"UTG", "UTG+1", "UTG+2", "LJ", "HJ"}:
        return "offsuit_broadway_aof_watch"
    if hand_class in {"22", "33", "44", "55", "66"} and position in {"UTG", "UTG+1", "UTG+2", "LJ"}:
        return "small_pair_aof_watch"
    if hand_class in {"A2o", "A3o", "A4o", "A5o", "A6o", "A7o"} and position in {"UTG", "UTG+1", "UTG+2", "LJ", "HJ"}:
        return "low_ax_offsuit_aof_watch"
    return None


def _entry_bucket(index: int, total: int) -> str:
    if total <= 1:
        return "early"
    if total == 2:
        return "early" if index == 0 else "late"
    if index == 0:
        return "early"
    if index == total - 1:
        return "late"
    return "mid"


def _fetch_timing_observations(player_id: str, window: str) -> list[TimingObservation]:
    base_rows = _fetch_observations(
        player_id=player_id,
        window=window,
        format_filter="all",
        position_filter="all",
        stack_filter="all",
        min_active_seats=2,
    )

    tournament_sessions: dict[str, list[tuple[str, str | None]]] = defaultdict(list)
    seen_sessions: set[tuple[str, str]] = set()
    for row in base_rows:
        tournament_id = row.tournament_id
        key = (tournament_id, row.session_id)
        if key in seen_sessions:
            continue
        seen_sessions.add(key)
        tournament_sessions[tournament_id].append((row.session_id, row.started_at))

    session_context: dict[str, tuple[str, str]] = {}
    for tournament_id, session_rows in tournament_sessions.items():
        ordered = sorted(session_rows, key=lambda item: (item[1] or "", item[0]))
        total = len(ordered)
        for index, (session_id, _) in enumerate(ordered):
            entry_timing = _entry_bucket(index, total)
            bullet_state = "first_bullet" if index == 0 else "reentry_bullet"
            session_context[session_id] = (entry_timing, bullet_state)

    observations: list[TimingObservation] = []
    for row in base_rows:
        tournament_id = row.tournament_id
        entry_timing, bullet_state = session_context.get(row.session_id, ("early", "first_bullet"))
        observations.append(
            TimingObservation(
                tournament_id=tournament_id,
                session_id=row.session_id,
                started_at=row.started_at,
                format_tag=row.format_tag,
                hand_class=row.hand_class,
                position=row.position,
                stack_bb=row.stack_bb,
                bb_net=row.bb_net,
                first_preflop_action=row.first_preflop_action,
                faced_action_preflop=row.faced_action_preflop,
                entry_timing=entry_timing,
                bullet_state=bullet_state,
            )
        )
    return observations


def _safe_avg(total: float, count: int) -> float | None:
    if count <= 0:
        return None
    return round(total / count, 2)


def _safe_pct(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round((numerator / denominator) * 100, 1)


def _summarize_group(rows: list[TimingObservation]) -> dict[str, Any]:
    aof_rows = [row for row in rows if row.stack_bb is not None and row.stack_bb <= 15]
    aof_issues = [row for row in aof_rows if _aof_family(row.hand_class, row.position, row.stack_bb, row.first_preflop_action)]
    proactive = [row for row in rows if row.first_preflop_action in {"raise", "jam"}]
    return {
        "hands": len(rows),
        "total_bb_net": round(sum(row.bb_net for row in rows), 2),
        "avg_bb_per_hand": _safe_avg(sum(row.bb_net for row in rows), len(rows)),
        "median_stack_focus": round(sum((row.stack_bb or 0.0) for row in rows if row.stack_bb is not None) / max(1, sum(1 for row in rows if row.stack_bb is not None)), 1),
        "aof_hands": len(aof_rows),
        "aof_issue_rate": _safe_pct(len(aof_issues), len(aof_rows)),
        "proactive_rate": _safe_pct(len(proactive), len(rows)),
    }


def _build_entry_cards(observations: list[TimingObservation]) -> list[dict[str, Any]]:
    grouped: dict[str, list[TimingObservation]] = defaultdict(list)
    for row in observations:
        grouped[row.entry_timing].append(row)
    cards = []
    for timing in ("early", "mid", "late"):
        rows = grouped.get(timing, [])
        summary = _summarize_group(rows)
        cards.append(
            {
                "label": timing.title(),
                **summary,
                "meaning": (
                    "This entry timing proxy is derived from your first, middle, or last detected session start within the same tournament id."
                ),
            }
        )
    return cards


def _build_bullet_cards(observations: list[TimingObservation]) -> list[dict[str, Any]]:
    grouped: dict[str, list[TimingObservation]] = defaultdict(list)
    for row in observations:
        grouped[row.bullet_state].append(row)
    cards = []
    for bullet_state, label in (("first_bullet", "First Bullet"), ("reentry_bullet", "Re-Entry Bullet")):
        rows = grouped.get(bullet_state, [])
        summary = _summarize_group(rows)
        cards.append(
            {
                "label": label,
                **summary,
                "meaning": "Use this to see whether later bullets make you force spots harder or actually sharpen decision quality.",
            }
        )
    return cards


def _build_stack_cards(observations: list[TimingObservation]) -> list[dict[str, Any]]:
    grouped: dict[str, list[TimingObservation]] = defaultdict(list)
    for row in observations:
        grouped[_stack_band(row.stack_bb)].append(row)

    cards = []
    for band in ("0-15bb", "15-20bb", "20-25bb", "25-30bb", "30-50bb", "50-100bb", "100bb+"):
        rows = grouped.get(band, [])
        if not rows:
            cards.append({"label": band, "hands": 0, "avg_bb_per_hand": None, "aof_issue_rate": None, "conviction_pressure": 0, "meaning": "No sample yet."})
            continue
        concern_rows = [
            row for row in rows
            if row.hand_class in {"A5s", "98s", "QTs", "T9s", "KTo", "KJo", "KQo"}
            and row.first_preflop_action in {"raise", "jam", "call"}
        ]
        cards.append(
            {
                "label": band,
                **_summarize_group(rows),
                "conviction_pressure": len(concern_rows),
                "meaning": "This stack band helps test whether your comfort zone is also where your decision quality stays clean.",
            }
        )
    return cards


def _find_best_band(stack_cards: list[dict[str, Any]]) -> dict[str, Any] | None:
    eligible = [card for card in stack_cards if card.get("hands", 0) >= 30 and card.get("avg_bb_per_hand") is not None]
    if not eligible:
        return None
    return max(eligible, key=lambda card: ((card["avg_bb_per_hand"] or -999), -(card.get("aof_issue_rate") or 999)))


def _find_worst_band(stack_cards: list[dict[str, Any]]) -> dict[str, Any] | None:
    eligible = [card for card in stack_cards if card.get("hands", 0) >= 30 and card.get("avg_bb_per_hand") is not None]
    if not eligible:
        return None
    return min(eligible, key=lambda card: ((card["avg_bb_per_hand"] or 999), card.get("conviction_pressure", 0) * -1))


def _build_aof_leaks(observations: list[TimingObservation]) -> list[dict[str, Any]]:
    leak_groups: dict[str, list[TimingObservation]] = defaultdict(list)
    for row in observations:
        family = _aof_family(row.hand_class, row.position, row.stack_bb, row.first_preflop_action)
        if family:
            leak_groups[family].append(row)

    labels = {
        "offsuit_broadway_aof_watch": "Offsuit Broadway AOF Watch",
        "small_pair_aof_watch": "Small Pair Early AOF Watch",
        "low_ax_offsuit_aof_watch": "Low Ax Offsuit AOF Watch",
    }
    result = []
    for family, rows in sorted(leak_groups.items(), key=lambda item: (-len(item[1]), item[0])):
        result.append(
            {
                "label": labels.get(family, family),
                "repeats": len(rows),
                "avg_bb_per_hand": _safe_avg(sum(row.bb_net for row in rows), len(rows)),
                "positions": dict(sorted({position: sum(1 for row in rows if row.position == position) for position in {r.position for r in rows}}.items())),
                "examples": [
                    {
                        "hand_class": row.hand_class,
                        "position": row.position,
                        "stack_bb": round(row.stack_bb, 2) if row.stack_bb is not None else None,
                        "action": row.first_preflop_action,
                    }
                    for row in rows[:5]
                ],
            }
        )
    return result[:6]


def _build_conclusion_cards(
    stack_cards: list[dict[str, Any]],
    conviction_review: dict[str, Any],
    field_ecology: dict[str, Any],
    hud_trend: dict[str, Any],
) -> list[dict[str, Any]]:
    best_band = _find_best_band(stack_cards)
    worst_band = _find_worst_band(stack_cards)
    overtrust = conviction_review.get("overtrust_cards", [])
    field_headline = field_ecology.get("summary", {}).get("headline", "")
    river_metric = next((item for item in hud_trend.get("featured_metrics", []) if item.get("metric") == "river_aggression"), None)

    cards = []
    if best_band:
        cards.append(
            {
                "title": "Where You Operate Best",
                "summary": f"{best_band['label']} is currently your cleanest operating depth by realized result.",
                "why": f"Avg {best_band.get('avg_bb_per_hand')}bb/hand with AOF issue rate {best_band.get('aof_issue_rate')}% and conviction pressure {best_band.get('conviction_pressure')}.",
            }
        )
    if worst_band:
        cards.append(
            {
                "title": "Where You Get Pulled Off Baseline",
                "summary": f"{worst_band['label']} is the highest-friction depth in the current corpus.",
                "why": f"Avg {worst_band.get('avg_bb_per_hand')}bb/hand. This is where hand-class confidence and noisy field interaction should be reviewed first.",
            }
        )
    cards.append(
        {
            "title": "What To Adjust Next",
            "summary": "Use stack-band-specific approval, not global hand love.",
            "why": f"Current overtrust queue starts with {', '.join(card['hand_class'] for card in overtrust[:3]) or 'no hand class yet'}. Field note: {field_headline} HUD note: river aggression is {river_metric.get('current') if river_metric else 'n/a'}%.",
        }
    )
    return cards


def get_timing_stack_review_payload(player_id: str = HERO_PLAYER_ID, window: str = "all") -> dict[str, Any]:
    resolved_player_id = player_id or HERO_PLAYER_ID
    resolved_window = window if window in SUPPORTED_WINDOWS else "all"
    observations = _fetch_timing_observations(resolved_player_id, resolved_window)
    entry_cards = _build_entry_cards(observations)
    bullet_cards = _build_bullet_cards(observations)
    stack_cards = _build_stack_cards(observations)
    aof_leaks = _build_aof_leaks(observations)
    conviction_review = get_conviction_review_payload(player_id=resolved_player_id, window=resolved_window)
    field_ecology = get_field_ecology_payload(player_id=resolved_player_id, window=resolved_window)
    hud_trend = get_hud_trend_payload(player_id=resolved_player_id, window=resolved_window)
    best_band = _find_best_band(stack_cards)
    worst_band = _find_worst_band(stack_cards)

    return {
        "status": "ok",
        "player_id": resolved_player_id,
        "summary": {
            "window": resolved_window,
            "hands": len(observations),
            "headline": "This view tests whether your preferred operating depth and entry timing are actually where decision quality stays strongest.",
            "best_operating_zone": best_band["label"] if best_band else None,
            "highest_friction_zone": worst_band["label"] if worst_band else None,
            "comfort_hypothesis_20bb": next((card for card in stack_cards if card["label"] == "20-25bb"), None),
        },
        "entry_timing_cards": entry_cards,
        "bullet_state_cards": bullet_cards,
        "stack_comfort_cards": stack_cards,
        "aof_leak_queue": aof_leaks,
        "conviction_top": {
            "overtrust": conviction_review.get("overtrust_cards", [])[:4],
            "undertrust": conviction_review.get("undertrust_cards", [])[:3],
        },
        "field_context": {
            "summary": field_ecology.get("summary", {}),
            "ecology_cards": field_ecology.get("ecology_cards", []),
        },
        "hud_context": {
            "summary": hud_trend.get("summary", {}),
            "featured_metrics": hud_trend.get("featured_metrics", []),
            "change_notes": hud_trend.get("change_notes", []),
        },
        "conclusion_cards": _build_conclusion_cards(stack_cards, conviction_review, field_ecology, hud_trend),
        "operator_notes": [
            "Entry timing is a deterministic proxy derived from session start order inside the same tournament id, not official late-registration truth.",
            "Bullet state is first session versus later re-entry session within the same tournament id.",
            "Use this view to test whether your 20bb neighborhood really is your best operating depth, not just your preferred one.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Read tournament timing + stack comfort review payload.")
    parser.add_argument("--player-id", default=HERO_PLAYER_ID, help="Player id to inspect.")
    parser.add_argument("--window", default="all", choices=sorted(SUPPORTED_WINDOWS))
    args = parser.parse_args()
    payload = get_timing_stack_review_payload(player_id=args.player_id, window=args.window)
    print(json.dumps(payload, indent=2, default=str))


if __name__ == "__main__":
    main()
