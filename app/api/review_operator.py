from __future__ import annotations

import argparse
import json
from typing import Any

from app.api.field_ecology import get_field_ecology_payload
from app.api.hand_matrix import HERO_PLAYER_ID, get_hand_matrix_payload
from app.api.hud_trend import get_hud_trend_payload


def _take(items: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    return items[:limit] if items else []


def _build_review_cards(hand_matrix: dict[str, Any], hud_trend: dict[str, Any], field_ecology: dict[str, Any]) -> list[dict[str, Any]]:
    study_cards = hand_matrix.get("study_panels", {}).get("study_worthy_spots", [])
    mistake_cards = hand_matrix.get("study_panels", {}).get("clear_repeated_mistakes", [])
    belief_cards = hand_matrix.get("study_panels", {}).get("belief_driven_patterns", [])

    river_metric = next(
        (item for item in hud_trend.get("featured_metrics", []) if item.get("metric") == "river_aggression"),
        None,
    )
    pfr_metric = next(
        (item for item in hud_trend.get("featured_metrics", []) if item.get("metric") == "pfr"),
        None,
    )
    vpip_metric = next(
        (item for item in hud_trend.get("featured_metrics", []) if item.get("metric") == "vpip"),
        None,
    )

    ecology_cards = field_ecology.get("ecology_cards", [])
    limper_card = next((item for item in ecology_cards if item.get("label") == "Limpers"), None)
    open4x_card = next((item for item in ecology_cards if item.get("label") == "Open 4x"), None)
    multiway_card = next((item for item in ecology_cards if item.get("label") == "Multiway Flop"), None)

    review_cards: list[dict[str, Any]] = []

    for item in _take(study_cards, 3):
        action = "Tighten the exact approval threshold for this family before the next session."
        if item.get("family") == "KJo":
            action = "Re-check where KJo is still being approved under 15bb, especially outside cleaner late-position lanes."
        elif item.get("family") == "KQo":
            action = "Lock the KQo jam / raise boundary so it does not drift from pressure hand into over-approval hand."
        review_cards.append(
            {
                "title": item.get("title"),
                "type": "Study-Worthy Spot",
                "what_happened": item.get("why_it_matters"),
                "environment": f"Limpers {limper_card.get('value') if limper_card else 'n/a'}%, Open 4x {open4x_card.get('value') if open4x_card else 'n/a'}%, Multiway flop {multiway_card.get('value') if multiway_card else 'n/a'}%.",
                "trend_context": f"VPIP {vpip_metric.get('current') if vpip_metric else 'n/a'}%, PFR {pfr_metric.get('current') if pfr_metric else 'n/a'}%, River Agg {river_metric.get('current') if river_metric else 'n/a'}%.",
                "fix_direction": action,
                "examples": item.get("examples", []),
            }
        )

    for item in _take(mistake_cards, 3):
        review_cards.append(
            {
                "title": item.get("title"),
                "type": "Clear Repeated Mistake",
                "what_happened": item.get("why_it_matters"),
                "environment": f"Field ecology matters here because limp-heavy or wide opener pools can make loose approvals feel normal. Hero passive limp-multiway rate is {field_ecology.get('hero_limp_multiway', {}).get('passive_rate', 'n/a')}%.",
                "trend_context": f"Current trend mix: VPIP {vpip_metric.get('current') if vpip_metric else 'n/a'}%, PFR {pfr_metric.get('current') if pfr_metric else 'n/a'}%. If both are up, some repeated mistakes may be coming from broader widening rather than one hand class alone.",
                "fix_direction": "Treat this as a family-level correction job, not a one-hand cooler review.",
                "examples": item.get("examples", []),
            }
        )

    for item in _take(belief_cards, 2):
        review_cards.append(
            {
                "title": item.get("title"),
                "type": "Belief-Driven Pattern",
                "what_happened": item.get("why_it_matters"),
                "environment": f"Recent field ecology: limpers {limper_card.get('value') if limper_card else 'n/a'}%, donk flop {next((card.get('value') for card in ecology_cards if card.get('label') == 'Donk Flop'), 'n/a')}%. Loose pools can reinforce blocker-pressure beliefs if not separated from baseline.",
                "trend_context": f"HUD trend says VPIP delta {vpip_metric.get('delta') if vpip_metric else 'n/a'} pts and River Agg delta {river_metric.get('delta') if river_metric else 'n/a'} pts. That means style drift and belief drift should be read together.",
                "fix_direction": "Review whether this belief is exploit choice, autopilot habit, or contamination from loose field ecology.",
                "examples": item.get("examples", []),
            }
        )

    return review_cards


def get_review_operator_payload(player_id: str = HERO_PLAYER_ID, window: str = "90d") -> dict[str, Any]:
    resolved_player_id = player_id or HERO_PLAYER_ID
    hand_matrix = get_hand_matrix_payload(player_id=resolved_player_id, window=window, min_active_seats=5)
    hud_trend = get_hud_trend_payload(player_id=resolved_player_id, window=window)
    field_ecology = get_field_ecology_payload(player_id=resolved_player_id, window=window)
    review_cards = _build_review_cards(hand_matrix, hud_trend, field_ecology)
    return {
        "status": "ok",
        "player_id": resolved_player_id,
        "summary": {
            "window": window,
            "headline": "Use these cards to feel the link between repeated decision, field environment, and current style drift.",
            "card_count": len(review_cards),
        },
        "review_cards": review_cards,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Read the review operator payload.")
    parser.add_argument("--player-id", default=HERO_PLAYER_ID, help="Player id to inspect.")
    parser.add_argument("--window", default="90d", choices=["90d", "all"])
    args = parser.parse_args()
    payload = get_review_operator_payload(player_id=args.player_id, window=args.window)
    print(json.dumps(payload, indent=2, default=str))


if __name__ == "__main__":
    main()
