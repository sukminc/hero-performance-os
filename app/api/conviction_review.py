from __future__ import annotations

import argparse
import json
from collections import defaultdict
from typing import Any

from app.api.hand_matrix import HERO_PLAYER_ID, SUPPORTED_WINDOWS, _fetch_observations, _position_sort_key, build_hand_scores


def _family_for(hand_class: str) -> str:
    if len(hand_class) == 2:
        return "pair"
    if hand_class.endswith("s"):
        high = hand_class[0]
        low = hand_class[1]
        if high == "A" and low in {"2", "3", "4", "5", "6"}:
            return "low_ax_suited"
        if high in {"K", "Q", "J", "T"} and low in {"Q", "J", "T", "9"}:
            return "suited_broadway"
        if low in {"9", "8", "7", "6", "5"}:
            return "suited_connector_or_gap"
        return "suited_other"
    high = hand_class[0]
    low = hand_class[1]
    if high == "A" and low in {"2", "3", "4", "5", "6", "7", "8", "9"}:
        return "low_ax_offsuit"
    if high in {"K", "Q", "J", "T"} and low in {"Q", "J", "T", "9"}:
        return "offsuit_broadway"
    return "offsuit_other"


def _position_bucket(position: str) -> str:
    if position in {"UTG", "UTG+1", "UTG+2"}:
        return "early"
    if position in {"LJ", "HJ"}:
        return "middle"
    if position in {"CO", "BTN"}:
        return "late"
    if position in {"SB", "BB"}:
        return "blinds"
    return "other"


def _build_examples(rows: list[Any], limit: int = 5) -> list[dict[str, Any]]:
    ordered = sorted(rows, key=lambda row: (row.started_at or "", row.hand_id), reverse=True)
    return [
        {
            "hand_id": item.hand_id,
            "hand_class": item.hand_class,
            "position": item.position,
            "format_tag": item.format_tag,
            "stack_bb": round(item.stack_bb, 2) if item.stack_bb is not None else None,
            "action": item.first_preflop_action,
            "bb_net": round(item.bb_net, 2),
            "started_at": item.started_at,
            "hero_summary": item.hero_summary,
        }
        for item in ordered[:limit]
    ]


def _score_conviction_items(scored_hands: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    family_rows: dict[str, list[float]] = defaultdict(list)
    for item in scored_hands:
        if item["hands_played"] >= 5:
            family_rows[_family_for(item["hand_class"])].append(item["avg_bb_per_hand"])
    family_avg = {
        family: round(sum(values) / len(values), 4)
        for family, values in family_rows.items()
        if values
    }

    overtrust: list[dict[str, Any]] = []
    undertrust: list[dict[str, Any]] = []
    context_cards: list[dict[str, Any]] = []

    for item in scored_hands:
        hands_played = item["hands_played"]
        if hands_played < 5:
            continue
        rows = item["rows"]
        hand_class = item["hand_class"]
        avg_bb = item["avg_bb_per_hand"]
        family = _family_for(hand_class)
        family_baseline = family_avg.get(family, 0.0)
        proactive_rate = item["proactive_rate"]
        position_mix = defaultdict(int)
        stack_loss = {"lt15": 0.0, "15to25": 0.0, "gt25": 0.0}
        stack_count = {"lt15": 0, "15to25": 0, "gt25": 0}
        for row in rows:
            position_mix[_position_bucket(row.position)] += 1
            if row.stack_bb is None:
                continue
            if row.stack_bb < 15:
                stack_key = "lt15"
            elif row.stack_bb <= 25:
                stack_key = "15to25"
            else:
                stack_key = "gt25"
            stack_loss[stack_key] += row.bb_net
            stack_count[stack_key] += 1

        worst_stack = None
        worst_stack_avg = None
        for stack_key in ("lt15", "15to25", "gt25"):
            if stack_count[stack_key] < 3:
                continue
            stack_avg = stack_loss[stack_key] / stack_count[stack_key]
            if worst_stack_avg is None or stack_avg < worst_stack_avg:
                worst_stack = stack_key
                worst_stack_avg = stack_avg

        early_middle_share = round((position_mix["early"] + position_mix["middle"]) / hands_played, 4)
        late_share = round(position_mix["late"] / hands_played, 4)
        family_gap = round(avg_bb - family_baseline, 2)
        confidence = round(min(1.0, hands_played / 18), 2)

        common_payload = {
            "hand_class": hand_class,
            "family": family,
            "hands_played": hands_played,
            "actual_bb_net": item["actual_bb_net"],
            "avg_bb_per_hand": avg_bb,
            "family_avg_bb_per_hand": round(family_baseline, 2),
            "family_gap_bb_per_hand": family_gap,
            "proactive_rate": round(proactive_rate * 100, 1),
            "early_middle_share": round(early_middle_share * 100, 1),
            "late_share": round(late_share * 100, 1),
            "position_mix": dict(sorted(position_mix.items())),
            "stack_band_mix": item["stack_band_mix"],
            "action_mix": item["action_mix"],
            "confidence": confidence,
            "worst_stack_band": worst_stack,
            "worst_stack_avg_bb_per_hand": round(worst_stack_avg, 2) if worst_stack_avg is not None else None,
            "examples": _build_examples(rows),
        }

        if hands_played >= 8 and avg_bb <= -1.5 and proactive_rate >= 0.45:
            overtrust.append(
                {
                    **common_payload,
                    "title": f"{hand_class} looks overtrusted",
                    "classification": "overtrust",
                    "reason": f"{hand_class} keeps getting real volume and proactive approval, but the realized result is materially below both zero and its family baseline.",
                    "correction_direction": "Narrow where you auto-approve this hand. Re-check whether this confidence should live only in later positions, better field conditions, or cleaner stack bands.",
                }
            )

        if hands_played >= 6 and avg_bb >= 0.75 and proactive_rate <= 0.4 and late_share >= 0.35:
            undertrust.append(
                {
                    **common_payload,
                    "title": f"{hand_class} may be undertrusted",
                    "classification": "undertrust",
                    "reason": f"{hand_class} is not showing up as a high-volume proactive hand, yet when it does get used it is performing well enough to deserve a closer look.",
                    "correction_direction": "Study whether this hand deserves more confident use in the exact lanes where it already wins instead of staying globally cautious.",
                }
            )

        if hands_played >= 7 and avg_bb <= -0.6 and family_gap <= -0.75 and worst_stack is not None:
            context_cards.append(
                {
                    **common_payload,
                    "title": f"{hand_class} is context-sensitive, not always wrong",
                    "classification": "context_sensitive",
                    "reason": f"The hand is not just losing overall; the damage clusters hardest in one stack band or lane, which suggests overgeneralization more than pure hand misunderstanding.",
                    "correction_direction": f"Keep this hand in your toolkit, but stop treating it as universal approval. The current pain point is strongest in `{worst_stack}`.",
                }
            )

    overtrust = sorted(overtrust, key=lambda item: (item["avg_bb_per_hand"], -item["hands_played"]))[:8]
    undertrust = sorted(undertrust, key=lambda item: (-item["avg_bb_per_hand"], -item["hands_played"]))[:8]
    context_cards = sorted(context_cards, key=lambda item: (item["family_gap_bb_per_hand"], item["avg_bb_per_hand"]))[:8]
    return overtrust, undertrust, context_cards


def get_conviction_review_payload(
    player_id: str = HERO_PLAYER_ID,
    window: str = "all",
) -> dict[str, Any]:
    resolved_player_id = player_id or HERO_PLAYER_ID
    resolved_window = window if window in SUPPORTED_WINDOWS else "all"
    observations = _fetch_observations(
        player_id=resolved_player_id,
        window=resolved_window,
        format_filter="all",
        position_filter="all",
        stack_filter="all",
        min_active_seats=2,
    )
    scored_hands = build_hand_scores(observations)
    overtrust, undertrust, context_cards = _score_conviction_items(scored_hands)
    reviewed_hands = overtrust + undertrust + context_cards
    positions_seen = sorted({item.position for item in observations}, key=_position_sort_key)

    return {
        "status": "ok",
        "player_id": resolved_player_id,
        "summary": {
            "window": resolved_window,
            "hands": len(observations),
            "distinct_hand_classes": len(scored_hands),
            "headline": "Conviction Review surfaces hand classes you may be trusting too much, not enough, or too generally across the full corpus.",
            "review_card_count": len(reviewed_hands),
            "positions_seen": positions_seen,
        },
        "operator_notes": [
            "This surface is not saying the hand itself is bad. It is saying your approval pattern around that hand may be too automatic or too narrow.",
            "Cards are ranked by repeated usage plus realized outcome gap, so one-off coolers should lose priority against repeated structural patterns.",
            "Use these cards as study queues, then cross-check with 13x13 filters and later solver work where needed.",
        ],
        "overtrust_cards": overtrust,
        "undertrust_cards": undertrust,
        "context_cards": context_cards,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Read conviction review payload.")
    parser.add_argument("--player-id", default=HERO_PLAYER_ID, help="Player id to inspect.")
    parser.add_argument("--window", default="all", choices=sorted(SUPPORTED_WINDOWS))
    args = parser.parse_args()
    payload = get_conviction_review_payload(
        player_id=args.player_id,
        window=args.window,
    )
    print(json.dumps(payload, indent=2, default=str))


if __name__ == "__main__":
    main()
